from __future__ import annotations

import ast
import hashlib
import re
from typing import Any


_MISSING_LIST_PATTERN = re.compile(r"missing=(\[[^\]]*\])", re.IGNORECASE)
_TRANSIENT_ERROR_PATTERN = re.compile(
    r"timeout|timed out|connection|remote end closed|temporar|rate limit|429|502|503|504|网络|超时|连接",
    re.IGNORECASE,
)


def diagnose_translation_failures(
    *,
    record_id: str,
    report_type: str,
    failed_rows: list[dict[str, Any]],
    protected_terms: dict[str, Any] | None = None,
    tuning: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Turn failed translation rows into deduplicated, actionable experience suggestions.

    The classifier intentionally reasons from generic error families and current
    configuration. It does not embed drilling-specific units or names in code.
    """
    terms = protected_terms if isinstance(protected_terms, dict) else {}
    known_units = _folded_values(terms.get("units"))
    known_acronyms = _folded_values(terms.get("acronyms"))
    known_proper_nouns = _folded_values(terms.get("proper_nouns"))
    suggestions: dict[str, dict[str, Any]] = {}

    for row in failed_rows:
        error = str(row.get("error_message", "") or "").strip()
        source_text = str(row.get("source_text", "") or "").strip()
        field_code = str(row.get("field_code", "") or "").strip()
        for issue in _diagnose_error(
            error=error,
            source_text=source_text,
            report_type=report_type,
            field_code=field_code,
            known_units=known_units,
            known_acronyms=known_acronyms,
            known_proper_nouns=known_proper_nouns,
        ):
            fingerprint = experience_fingerprint(issue)
            evidence = {
                "record_id": record_id,
                "field_code": field_code,
                "source_text": source_text[:800],
                "error_message": error[:800],
            }
            current = suggestions.get(fingerprint)
            if current:
                current["occurrence_count"] += 1
                current["evidence"].append(evidence)
                continue
            suggestions[fingerprint] = {
                **issue,
                "fingerprint": fingerprint,
                "record_ids": [record_id] if record_id else [],
                "field_codes": [field_code] if field_code else [],
                "occurrence_count": 1,
                "evidence": [evidence],
            }
    return list(suggestions.values())


def experience_fingerprint(issue: dict[str, Any]) -> str:
    identity = "|".join([
        str(issue.get("category", "") or ""),
        str(issue.get("action_type", "") or ""),
        str(issue.get("token", "") or "").casefold(),
        str(issue.get("report_type", "") or "").casefold(),
        str(issue.get("field_code", "") or "").casefold(),
    ])
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _diagnose_error(
    *,
    error: str,
    source_text: str,
    report_type: str,
    field_code: str,
    known_units: set[str],
    known_acronyms: set[str],
    known_proper_nouns: set[str],
) -> list[dict[str, Any]]:
    folded_error = error.casefold()
    missing_values = _missing_values(error)
    issues: list[dict[str, Any]] = []

    if _TRANSIENT_ERROR_PATTERN.search(error):
        return [_issue(
            category="transient_provider",
            action_type="retry_current_rules",
            title="模型或网络临时异常",
            cause="错误属于超时、连接或上游服务异常，写入词库不会解决。",
            recommendation="保留当前经验配置并自动重跑；若连续出现，再升级模型降级策略。",
            report_type=report_type,
            field_code="",
            confidence="high",
        )]

    if "unit" in folded_error and missing_values:
        for token in missing_values:
            folded_token = token.casefold()
            if folded_token not in known_units:
                issues.append(_issue(
                    category="missing_protected_unit",
                    action_type="add_protected_unit",
                    token=token,
                    title=f"建议把 {token} 加入全局单位保护",
                    cause="质量校验识别到单位缺失，但当前全局单位保护池没有该写法。",
                    recommendation="加入全局单位保护后采用确定性保留，并重跑受影响日报。",
                    report_type="",
                    field_code="",
                    confidence="high",
                ))
            else:
                issues.append(_issue(
                    category="contextual_unit_regression",
                    action_type="retry_current_rules",
                    token=token,
                    title=f"上下文单位保护需要重跑（{token}）",
                    cause=f"{token} 已在全局单位保护范围内，失败应作为保护或校验边界问题排查。",
                    recommendation="使用当前上下文保护规则重跑。若仍复现，应作为单位恢复逻辑回归处理。",
                    report_type=report_type,
                    field_code=field_code,
                    confidence="high",
                ))
        return issues

    if "numeric" in folded_error or "数字" in error:
        return [_issue(
            category="contextual_numeric_regression",
            action_type="retry_current_rules",
            token="数字与精度",
            title="上下文数字保护需要重跑",
            cause="结果校验发现日期或计量值发生变化。",
            recommendation="按当前规则重跑；若仍复现，应修复数字恢复或校验边界。",
            report_type=report_type,
            field_code=field_code,
            confidence="high",
        )]

    if "protected placeholder" in folded_error:
        return [_issue(
            category="placeholder_provider_regression",
            action_type="retry_current_rules",
            title="模型改动了内部保护标记",
            cause="上下文保护已命中，但模型返回时删除、复制或改写了内部保护标记。",
            recommendation="使用已有分段恢复机制自动重跑；重复出现时升级为模型兼容性回归。",
            report_type=report_type,
            field_code=field_code,
            confidence="high",
        )]

    if "protected-part" in folded_error and "source text was returned unchanged" in folded_error:
        return [_issue(
            category="deterministic_protected_fragment",
            action_type="retry_current_rules",
            title="受保护技术片段被误判为未翻译",
            cause="内部片段仅包含占位值、排版符号和技术标识，本身没有可翻译的自然语言，但被原文回显校验误判。",
            recommendation="使用确定性片段识别跳过无意义模型调用，并按当前规则自动重跑；无需添加字段 Prompt 或逐句记忆。",
            report_type=report_type,
            field_code=field_code,
            confidence="high",
        )]

    if "protected term" in folded_error and missing_values:
        for token in missing_values:
            token_folded = token.casefold()
            if token_folded in known_acronyms or token_folded in known_proper_nouns:
                action_type = "retry_current_rules"
                category = "protected_term_regression"
                title = f"已保护内容 {token} 仍被改写"
                recommendation = "按当前保护规则重跑一次；不向正式 Prompt 追加限制。"
                report_scope = report_type
                field_scope = field_code
            elif _looks_like_acronym(token):
                action_type = "add_protected_acronym"
                category = "missing_protected_acronym"
                title = f"建议把 {token} 加入全局缩写保护"
                recommendation = "加入全局缩写保护后原样保留，并重跑受影响日报。"
                report_scope = ""
                field_scope = ""
            else:
                action_type = "add_protected_proper_noun"
                category = "missing_protected_proper_noun"
                title = f"建议把 {token} 加入全局专名保护"
                recommendation = "加入全局专名保护后原样保留，并重跑受影响日报。"
                report_scope = ""
                field_scope = ""
            issues.append(_issue(
                category=category,
                action_type=action_type,
                token=token,
                title=title,
                cause="模型改写或遗漏了质量校验要求保留的内容。",
                recommendation=recommendation,
                report_type=report_scope,
                field_code=field_scope,
                confidence="high",
            ))
        return issues

    return [_issue(
        category="semantic_or_completeness",
        action_type="retry_current_rules",
        title="建议人工复核本次翻译",
        cause="本次失败不属于可直接加入单位、缩写或专名池的确定性错误。",
        recommendation="保留错误证据并按当前稳定策略重跑一次；不自动修改 Prompt。",
        report_type=report_type,
        field_code=field_code,
        confidence="medium",
    )]


def _issue(
    *,
    category: str,
    action_type: str,
    title: str,
    cause: str,
    recommendation: str,
    report_type: str,
    field_code: str,
    confidence: str,
    token: str = "",
    instruction: str = "",
) -> dict[str, Any]:
    proposed_change: dict[str, str] = {"action": action_type}
    if token:
        proposed_change["token"] = token
    if instruction:
        proposed_change["instruction"] = instruction
    return {
        "category": category,
        "action_type": action_type,
        "token": token,
        "title": title,
        "cause": cause,
        "recommendation": recommendation,
        "report_type": report_type,
        "field_code": field_code,
        "confidence": confidence,
        "proposed_change": proposed_change,
    }


def _missing_values(error: str) -> list[str]:
    values: list[str] = []
    for raw in _MISSING_LIST_PATTERN.findall(error):
        try:
            parsed = ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            continue
        if not isinstance(parsed, list):
            continue
        values.extend(str(item or "").strip() for item in parsed if str(item or "").strip())
    return list(dict.fromkeys(values))[:20]


def _folded_values(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item or "").strip().casefold() for item in value if str(item or "").strip()}


def _looks_like_acronym(value: str) -> bool:
    token = re.sub(r"[^A-Za-z0-9&/-]", "", value)
    letters = re.sub(r"[^A-Za-z]", "", token)
    return bool(token and letters and len(token) <= 20 and letters.upper() == letters)
