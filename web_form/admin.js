const toast = document.querySelector("#toast");
const adminState = {
  authenticated: false,
  user: null,
  permissions: {},
  tab: "overview",
  users: [],
  roles: [],
  config: {},
  aiModels: { models: [], default_model_id: "" },
  aiExtraction: { rules: [], catalog: { report_types: [], target_fields: [], output_formats: [] } },
  aiExtractionQueue: { records: [], pending_count: 0, processing_count: 0, current_version: "" },
  aiExtractionView: "rules",
  selectedAiExtractionRuleId: "",
  aiExtractionTestRecordId: "",
  aiExtractionTestSource: "",
  aiExtractionTestResult: null,
  aiExtractionTestRunning: false,
  selectedAiModelId: "",
  aiModelTestResult: null,
  projectTeams: { teams: [], projects: [], pending_wells: [] },
  translationTerms: { terms: [], protected_terms: {} },
  translationTuning: { scope_rules: [], scope_catalog: { report_types: [] }, target_languages: ["zh-CN"], prompt: {}, protections: {} },
  translationTuningView: "fields",
  translationScopeDraft: { report_type: "drilling", section: "report_fields", field_name: "currentOps" },
  translationTermImport: { running: false, result: null, duplicates: [] },
  translationTermCategory: "all",
  translationTermPage: 1,
  translationTermPageSize: 10,
  translationQueue: { records: [], pending_count: 0, processing_count: 0, current_version: "" },
  translationTestResult: null,
  translationTestRunning: false,
  translationTestSource: "05:30-07:30, BAJA BHA #5 DIRECCIONAL HASTA 4125 ft. PERFORA DE 4125 ft A 4140 ft CON ROP 90 ft/hr, WOB 18 klb Y SPP 12.5 MPa.",
  translationTestModelId: "",
  translationTestLanguage: "zh-CN",
  translationTestFieldCode: "",
  translationTermSearch: "",
  dataStatus: null,
  records: [],
  logs: [],
  logsPage: 1,
  logsPageSize: 20
};

function escapeHtml(value = "") {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" })[char]);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

async function adminRequest(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || "后台请求失败");
  return payload;
}

async function loadAdminSession() {
  try {
    const payload = await adminRequest("/api/admin/session");
    adminState.authenticated = payload.authenticated;
    adminState.user = payload.user || null;
    adminState.permissions = payload.permissions || {};
    if (!payload.authenticated) {
      window.location.href = "/login/?next=/admin/";
      return;
    }
    if (!adminState.permissions.admin) {
      renderNoPermission();
      return;
    }
    await loadAdminData();
  } catch (error) {
    showToast(error.message);
  }
}

async function loadAdminData() {
  try {
    const [users, config, aiModels, aiExtraction, aiExtractionQueue, projectTeams, translationTerms, translationTuning, translationQueue, dataStatus, records, logs] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/ai-models"),
      adminRequest("/api/admin/ai-extraction-rules"),
      adminRequest("/api/admin/ai-extractions"),
      adminRequest("/api/admin/project-teams"),
      adminRequest("/api/admin/translation-terms"),
      adminRequest("/api/admin/translation-tuning"),
      adminRequest("/api/admin/translations"),
      adminRequest("/api/admin/data-status"),
      adminRequest("/api/records"),
      adminRequest("/api/admin/audit-logs"),
    ]);
    adminState.users = users.users || [];
    adminState.roles = users.roles || [];
    adminState.config = config.config || {};
    adminState.aiModels = { models: aiModels.models || [], default_model_id: aiModels.default_model_id || "" };
    adminState.aiExtraction = aiExtraction || adminState.aiExtraction;
    adminState.aiExtractionQueue = aiExtractionQueue || adminState.aiExtractionQueue;
    adminState.selectedAiExtractionRuleId = adminState.aiExtraction.rules?.[0]?.id || "";
    adminState.selectedAiModelId = adminState.aiModels.default_model_id || adminState.aiModels.models?.[0]?.id || "";
    adminState.projectTeams = { teams: projectTeams.teams || [], projects: projectTeams.projects || [], pending_wells: projectTeams.pending_wells || [] };
    adminState.translationTerms = { terms: translationTerms.terms || [], protected_terms: translationTerms.protected_terms || {} };
    adminState.translationTuning = translationTuning || adminState.translationTuning;
    adminState.translationQueue = translationQueue || adminState.translationQueue;
    adminState.dataStatus = dataStatus;
    adminState.records = records.records || [];
    adminState.logs = logs.logs || [];
    adminState.logsPage = 1;
    renderAdminPanels();
  } catch (error) {
    showToast(error.message);
  }
}

function renderNoPermission() {
  document.querySelector(".admin-sidebar-nav")?.setAttribute("hidden", "");
  document.querySelector('[data-admin-panel="overview"]').hidden = false;
  document.querySelector('[data-admin-panel="overview"]').innerHTML = `<section class="panel admin-empty-panel"><div><h2>无后台权限</h2><p>当前账号可以登录前台，但没有系统后台管理权限。</p></div></section>`;
  document.querySelectorAll('[data-admin-panel]:not([data-admin-panel="overview"])').forEach((panel) => panel.hidden = true);
}

function renderAdminPanels() {
  renderAdminOverview();
  renderAdminUsers();
  renderAdminRoles();
  renderAdminAiModels();
  renderAdminAiExtraction();
  renderAdminProjects();
  renderAdminTranslationTuning();
  renderAdminConfig();
  renderAdminData();
  renderAdminLogs();
  switchAdminTab(adminState.tab || "overview");
}

function renderAdminOverview() {
  const host = document.querySelector('[data-admin-panel="overview"]');
  const status = adminState.dataStatus || {};
  const user = adminState.user || {};
  host.innerHTML = `
    <section class="admin-kpi-grid">
      ${adminKpi("当前账号", user.display_name || user.username || "-", roleLabel(user.role), "users")}
      ${adminKpi("日报记录", status.records || 0, "MySQL记录数", "database")}
      ${adminKpi("源PDF", status.source_pdf_count || 0, "本地保存数量", "logs")}
      ${adminKpi("MySQL", status.mysql?.available ? "可用" : "不可用", `${status.database_host || ""}:${status.database_port || ""}/${status.database_name || ""}`, "settings")}
    </section>
    <section class="panel admin-overview-panel">
      <div class="panel-heading"><h2>后台范围</h2><span class="panel-note">独立管理入口，轻量 JSON 配置</span></div>
      <div class="admin-note-grid">
        <span><strong>账号与角色</strong><small>新增、启停账号并分配固定角色</small></span>
        <span><strong>项目队伍</strong><small>维护合同、队伍和项目井号归属</small></span>
        <span><strong>系统参数</strong><small>维护记录分页、语言和源文件策略</small></span>
        <span><strong>数据维护</strong><small>查看 MySQL 连接和记录状态</small></span>
      </div>
    </section>
  `;
}

function adminKpi(label, value, caption, icon, attributes = "") {
  const interactive = attributes ? " interactive" : "";
  return `<div class="admin-kpi-card${interactive}" ${attributes}><span class="admin-kpi-icon icon-${escapeHtml(icon)}" aria-hidden="true"></span><div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(caption || "")}</small></div></div>`;
}

function renderAdminUsers() {
  const host = document.querySelector('[data-admin-panel="users"]');
  const roles = adminState.roles || [];
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>新增 / 编辑账号</h2><span class="panel-note">不允许停用或降级最后一个管理员</span></div>
      <div class="admin-user-form">
        <label>用户名<input name="adminUserUsername" placeholder="username" /></label>
        <label>姓名<input name="adminUserDisplay" placeholder="显示姓名" /></label>
        <label>邮箱<input name="adminUserEmail" placeholder="name@company.com" /></label>
        <label>角色<select name="adminUserRole">${roles.map((role) => `<option value="${escapeHtml(role.value)}">${escapeHtml(role.label)}</option>`).join("")}</select></label>
        <label>状态<select name="adminUserStatus"><option value="active">启用</option><option value="disabled">停用</option></select></label>
        <label>密码<input name="adminUserPassword" type="password" placeholder="新账号必填，留空不改" /></label>
        <button class="button" type="button" data-admin-save-user>保存账号</button>
      </div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>账号列表</h2><span class="panel-note">共 ${(adminState.users || []).length} 个账号</span></div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>用户名</th><th>姓名</th><th>邮箱</th><th>角色</th><th>状态</th><th>最后登录</th><th>操作</th></tr></thead>
        <tbody>${(adminState.users || []).map((user) => `<tr><td><strong>${escapeHtml(user.username)}</strong></td><td>${escapeHtml(user.display_name)}</td><td>${escapeHtml(user.email || "-")}</td><td><span class="type-pill">${escapeHtml(roleLabel(user.role))}</span></td><td><span class="status-pill ${user.status === "active" ? "uploaded" : "failed"}">${user.status === "active" ? "启用" : "停用"}</span></td><td>${escapeHtml(user.last_login || "-")}</td><td><button class="link-button" type="button" data-admin-edit-user="${escapeHtml(user.username)}">编辑</button></td></tr>`).join("")}</tbody>
      </table></div>
    </section>
  `;
}

function renderAdminRoles() {
  const host = document.querySelector('[data-admin-panel="roles"]');
  const actions = [["view", "查看"], ["import", "导入"], ["edit", "编辑"], ["save", "保存"], ["export", "导出"], ["admin", "后台"]];
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>新增角色</h2><span class="panel-note">角色编码保存后不可重复，建议使用英文小写</span></div>
      <div class="admin-role-form">
        <label>角色名称<input name="adminRoleLabel" placeholder="例如：现场监督" /></label>
        <label>角色编码<input name="adminRoleValue" placeholder="例如：supervisor" /></label>
        <button class="button" type="button" data-admin-add-role>添加角色</button>
      </div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>角色权限</h2><span class="panel-note">管理员角色受保护，避免后台入口被锁死</span></div>
      <div class="table-wrap"><table class="record-table admin-table permission-table">
        <thead><tr><th>角色</th>${actions.map(([, label]) => `<th>${label}</th>`).join("")}</tr></thead>
        <tbody>${(adminState.roles || []).map((role) => {
          const roleValue = escapeHtml(role.value);
          const protectedRole = role.value === "admin";
          return `<tr data-role-row="${roleValue}">
            <td>
              <input class="role-label-input" value="${escapeHtml(role.label)}" data-role-label="${roleValue}" ${protectedRole ? "disabled" : ""} />
              <small>${roleValue}${protectedRole ? " / 系统保护" : ""}</small>
            </td>
            ${actions.map(([key]) => `<td>
              <select class="permission-select" data-role-permission="${roleValue}" data-permission-key="${key}" ${protectedRole ? "disabled" : ""}>
                <option value="true" ${role.permissions?.[key] ? "selected" : ""}>允许</option>
                <option value="false" ${!role.permissions?.[key] ? "selected" : ""}>禁止</option>
              </select>
            </td>`).join("")}
          </tr>`;
        }).join("")}</tbody>
      </table></div>
      <div class="admin-actions"><button class="button" type="button" data-admin-save-roles>保存角色权限</button></div>
    </section>`;
}

function renderAdminAiModels() {
  const host = document.querySelector('[data-admin-panel="aiModels"]');
  if (!host) return;
  const models = adminState.aiModels.models || [];
  const selected = models.find((item) => item.id === adminState.selectedAiModelId) || models[0] || emptyAiModel();
  adminState.selectedAiModelId = selected.id || "";
  const enabledCount = models.filter((item) => item.enabled !== false).length;
  const pendingCount = adminState.records.filter(translationNeedsProcessing).length;
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("模型配置", models.length, "公网 / 局域网 / 本地", "database")}
      ${adminKpi("已启用", enabledCount, "可被翻译任务调用", "overview")}
      ${adminKpi("默认模型", defaultAiModelName(), "日报翻译优先使用", "shield")}
      ${adminKpi("密钥存储", "本机JSON", "仅后端保存", "settings")}
    </section>
    <section class="panel">
      <div class="panel-heading">
        <div><h2>模型接入配置</h2><span class="panel-note">支持 OpenAI-Compatible 公网模型和局域网本地模型；保存后日报翻译会使用默认启用模型</span></div>
        <div class="admin-actions">
          <button class="button secondary small" type="button" data-admin-reset-translations>清空译文</button>
          <button class="button secondary small" type="button" data-admin-queue-translations ${pendingCount ? "" : "disabled"}>翻译待处理 (${pendingCount})</button>
          <button class="button small" type="button" data-admin-new-ai-model>新增模型</button>
        </div>
      </div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>配置名称</th><th>接口类型</th><th>API地址</th><th>模型名称</th><th>超时</th><th>启用</th><th>默认</th><th>更新时间</th><th>操作</th></tr></thead>
        <tbody>${models.map(aiModelRow).join("") || `<tr><td colspan="9">暂无模型配置</td></tr>`}</tbody>
      </table></div>
    </section>
    <section class="admin-project-layout">
      <section class="panel">
        <div class="panel-heading"><h2>模型配置详情</h2><span class="panel-note">API Key 留空表示沿用已保存密钥；本地模型可不填 Key</span></div>
        ${aiModelForm(selected)}
      </section>
      <section class="panel">
        <div class="panel-heading"><h2>连接测试结果</h2><span class="panel-note">测试会向模型发送最小请求，不写入业务数据</span></div>
        ${aiModelTestResultMarkup()}
      </section>
    </section>`;
}

function aiModelRow(model = {}) {
  const isSelected = model.id === adminState.selectedAiModelId;
  return `<tr class="${isSelected ? "selected-row" : ""}">
    <td><strong>${escapeHtml(model.name || "-")}</strong></td>
    <td>${escapeHtml(apiTypeLabel(model.api_type))}</td>
    <td>${escapeHtml(model.base_url || "-")}</td>
    <td>${escapeHtml(model.model || "-")}</td>
    <td>${escapeHtml(model.timeout_seconds || 60)}s</td>
    <td><span class="status-pill ${model.enabled !== false ? "uploaded" : "failed"}">${model.enabled !== false ? "启用" : "停用"}</span></td>
    <td>${model.is_default ? "默认" : "-"}</td>
    <td>${escapeHtml(model.updated_at || "-")}</td>
    <td><button class="link-button" type="button" data-admin-edit-ai-model="${escapeHtml(model.id)}">编辑</button></td>
  </tr>`;
}

function aiModelForm(model = {}) {
  const apiType = model.api_type || "openai-compatible";
  return `<div class="admin-config-grid ai-model-form">
    <input type="hidden" name="aiModelId" value="${escapeHtml(model.id || "")}" />
    <label>配置名称<input name="aiModelName" value="${escapeHtml(model.name || "")}" placeholder="例如：主模型-DeepSeek-V3" /></label>
    <label>接口类型<select name="aiModelApiType"><option value="openai-compatible" ${apiType !== "ollama" ? "selected" : ""}>OpenAI Compatible</option><option value="ollama" ${apiType === "ollama" ? "selected" : ""}>Ollama</option></select></label>
    <label class="wide">API地址<input name="aiModelBaseUrl" value="${escapeHtml(model.base_url || "")}" placeholder="https://api.example.com/v1 或 http://10.10.1.12:8000/v1" /></label>
    <label>模型名称<input name="aiModelModel" value="${escapeHtml(model.model || "")}" placeholder="deepseek-chat / qwen-plus / llama3" /></label>
    <label>API Key<input name="aiModelApiKey" type="password" value="${model.api_key_set ? "********" : ""}" placeholder="${model.api_key_set ? "已保存，留空不改" : "本地模型可留空"}" /></label>
    <label>超时秒数<input name="aiModelTimeout" type="number" min="5" max="600" value="${escapeHtml(model.timeout_seconds || 60)}" /></label>
    <label>Temperature<input name="aiModelTemperature" type="number" min="0" max="2" step="0.1" value="${escapeHtml(model.temperature ?? 0)}" /></label>
    <label>重试次数<input name="aiModelRetry" type="number" min="0" max="10" value="${escapeHtml(model.retry_count ?? 2)}" /></label>
    <label>启用状态<select name="aiModelEnabled"><option value="true" ${model.enabled !== false ? "selected" : ""}>启用</option><option value="false" ${model.enabled === false ? "selected" : ""}>停用</option></select></label>
    <label>默认模型<select name="aiModelDefault"><option value="true" ${model.is_default ? "selected" : ""}>设为默认</option><option value="false" ${!model.is_default ? "selected" : ""}>非默认</option></select></label>
    <div class="admin-actions wide">
      <button class="button secondary" type="button" data-admin-test-ai-model>测试连接</button>
      <button class="button" type="button" data-admin-save-ai-models>保存配置</button>
      <button class="button secondary" type="button" data-admin-delete-ai-model ${model.id ? "" : "disabled"}>删除</button>
    </div>
  </div>`;
}

function aiModelTestResultMarkup() {
  const result = adminState.aiModelTestResult;
  if (!result) return `<div class="admin-empty-panel"><p>尚未测试当前模型连接。</p></div>`;
  if (result.ok === false) return `<div class="ai-test-result failed"><strong>连接失败</strong><small>${escapeHtml(result.error || "未知错误")}</small></div>`;
  return `<div class="ai-test-result success">
    <strong>连接成功，响应耗时 ${escapeHtml(result.elapsed_seconds)}s</strong>
    <small>测试时间：${escapeHtml(result.tested_at || "-")}</small>
    <small>接口地址：${escapeHtml(result.api_url || "-")}</small>
    <small>模型名称：${escapeHtml(result.model || "-")}</small>
    <small>响应状态：${escapeHtml(result.status || "-")}</small>
    <small>响应长度：${escapeHtml(result.response_length || 0)} bytes</small>
    ${result.response_preview ? `<pre>${escapeHtml(result.response_preview)}</pre>` : ""}
  </div>`;
}

function emptyAiModel() {
  return { id: newClientId(), name: "新模型配置", api_type: "openai-compatible", base_url: "", model: "", timeout_seconds: 60, temperature: 0, retry_count: 2, enabled: true, is_default: !(adminState.aiModels.models || []).length };
}

function apiTypeLabel(value) {
  return value === "ollama" ? "Ollama" : "OpenAI Compatible";
}

function defaultAiModelName() {
  const found = (adminState.aiModels.models || []).find((item) => item.id === adminState.aiModels.default_model_id);
  return found?.name || "-";
}

function renderAdminAiExtraction() {
  const host = document.querySelector('[data-admin-panel="aiExtraction"]');
  if (!host) return;
  const config = adminState.aiExtraction || { rules: [], catalog: {} };
  const rules = config.rules || [];
  let selected = rules.find((item) => item.id === adminState.selectedAiExtractionRuleId) || rules[0] || emptyAiExtractionRule();
  adminState.selectedAiExtractionRuleId = selected.id;
  const enabledCount = rules.filter((item) => item.enabled !== false).length;
  const queue = adminState.aiExtractionQueue || {};
  const view = adminState.aiExtractionView || "rules";
  const content = view === "queue" ? aiExtractionQueueMarkup() : view === "test" ? `
    <section class="panel"><div class="panel-heading"><h2>测试工作台</h2><span class="panel-note">只展示提炼结果，不写入生产报表</span></div>${aiExtractionTestMarkup()}</section>` : `
    <section class="panel">
      <div class="panel-heading">
        <div><h2>AI 数据提炼规则</h2><span class="panel-note">从指定日报字段提炼关键数据，并映射到生产报表目标字段</span></div>
        <div class="admin-actions"><label class="inline-check"><input type="checkbox" name="aiExtractionAutoExecute" ${config.auto_execute !== false ? "checked" : ""} /> 上传后自动执行</label><button class="button small" type="button" data-admin-new-extraction-rule>新增规则</button></div>
      </div>
      <div class="table-wrap"><table class="record-table admin-table extraction-rule-table">
        <thead><tr><th>规则名称</th><th>日报类型</th><th>来源字段</th><th>目标字段</th><th>输出</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>${rules.map(aiExtractionRuleRow).join("") || `<tr><td colspan="7">暂无提炼规则</td></tr>`}</tbody>
      </table></div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>规则配置</h2><span class="panel-note">保存后历史结果标记为规则已更新，可在任务队列重新提炼</span></div>
      ${aiExtractionRuleForm(selected)}
    </section>`;
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("提炼规则", rules.length, `${enabledCount} 条启用`, "sliders")}
      ${adminKpi("待处理日报", queue.pending_count || 0, "可继续或覆盖提炼", "logs", 'role="button" tabindex="0" data-ai-extraction-view="queue"')}
      ${adminKpi("执行中", queue.processing_count || 0, `${queue.worker_count || 0} 个并发任务`, "overview")}
      ${adminKpi("默认模型", defaultAiModelName(), "可按规则覆盖", "shield")}
    </section>
    <nav class="tuning-tabs" aria-label="数据提炼视图">
      ${aiExtractionTab("rules", "规则配置")}${aiExtractionTab("queue", "任务队列")}${aiExtractionTab("test", "测试工作台")}
    </nav>
    <div class="translation-tuning-content">${content}</div>`;
}

function aiExtractionTab(value, label) {
  return `<button type="button" class="${adminState.aiExtractionView === value ? "active" : ""}" data-ai-extraction-view="${value}">${label}</button>`;
}

function aiExtractionQueueMarkup() {
  const queue = adminState.aiExtractionQueue || {};
  const rows = queue.records || [];
  return `<section class="panel">
    <div class="panel-heading"><div><h2>数据提炼任务</h2><span class="panel-note">规则版本 ${escapeHtml(queue.current_version || "-")}；失败重试不会清除上次成功值</span></div>
      <div class="admin-actions"><button class="button small" type="button" data-admin-queue-extractions="continue">执行待处理</button><button class="button secondary small" type="button" data-admin-queue-extractions="overwrite">按当前规则覆盖执行</button></div>
    </div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th><input type="checkbox" data-ai-extraction-check-all /></th><th>日期 / 井号</th><th>井队</th><th>状态</th><th>进度</th><th>更新时间</th></tr></thead>
      <tbody>${rows.map((row) => `<tr><td><input type="checkbox" data-ai-extraction-record value="${escapeHtml(row.record_id)}" ${row.needs_extraction ? "checked" : ""} /></td><td><strong>${escapeHtml(row.report_date || "-")} / ${escapeHtml(row.wellbore || "-")}</strong><small>${escapeHtml(row.report_no || "")}</small></td><td>${escapeHtml(row.rig || "-")}</td><td><span class="status-pill ${aiQueueStatusTone(row.status)}" title="${escapeHtml(row.error || "")}">${escapeHtml(aiQueueStatusLabel(row.status))}</span></td><td>${escapeHtml(row.progress || "0")}%</td><td>${escapeHtml(row.updated_at || "-")}</td></tr>`).join("") || `<tr><td colspan="6">当前没有符合启用规则的日报</td></tr>`}</tbody>
    </table></div></section>`;
}

function aiQueueStatusLabel(status = "") {
  return ({ PENDING: "待提炼", QUEUED: "排队中", IN_PROGRESS: "提炼中", COMPLETED: "已提炼", FAILED: "失败", STALE: "规则已更新", NOT_REQUIRED: "无需提炼" })[String(status).toUpperCase()] || "待提炼";
}

function aiQueueStatusTone(status = "") {
  const value = String(status).toUpperCase();
  return value === "COMPLETED" ? "uploaded" : value === "FAILED" ? "failed" : value === "IN_PROGRESS" || value === "QUEUED" ? "processing" : "pending";
}

function aiExtractionRuleRow(rule = {}) {
  const catalog = adminState.aiExtraction.catalog || {};
  return `<tr class="${rule.id === adminState.selectedAiExtractionRuleId ? "selected-row" : ""}">
    <td><strong>${escapeHtml(rule.name)}</strong></td>
    <td>${escapeHtml(aiExtractionReportLabel(rule.report_type))}</td>
    <td><code>${escapeHtml(`${rule.source_section}.${rule.source_field}`)}</code></td>
    <td>${escapeHtml(aiExtractionCatalogLabel(catalog.target_fields, rule.target_field))}</td>
    <td>${escapeHtml(aiExtractionCatalogLabel(catalog.output_formats, rule.output_format))}</td>
    <td><span class="status-pill ${rule.enabled !== false ? "uploaded" : "failed"}">${rule.enabled !== false ? "启用" : "停用"}</span></td>
    <td><button class="link-button" type="button" data-admin-edit-extraction-rule="${escapeHtml(rule.id)}">编辑</button></td>
  </tr>`;
}

function aiExtractionRuleForm(rule = {}) {
  const catalog = adminState.aiExtraction.catalog || {};
  const report = (catalog.report_types || []).find((item) => item.value === rule.report_type) || catalog.report_types?.[0] || { sections: [] };
  const section = (report.sections || []).find((item) => item.value === rule.source_section) || report.sections?.[0] || { fields: [] };
  const field = (section.fields || []).find((item) => item.value === rule.source_field) || section.fields?.[0] || {};
  return `<div class="ai-extraction-form">
    <input type="hidden" name="aiExtractionRuleId" value="${escapeHtml(rule.id || "")}" />
    <label class="wide">规则名称<input name="aiExtractionRuleName" value="${escapeHtml(rule.name || "")}" placeholder="例如：NPT责任方识别" /></label>
    <label>日报类型<select name="aiExtractionReportType">${(catalog.report_types || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === report.value ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>来源模块<select name="aiExtractionSourceSection">${(report.sections || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === section.value ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>来源字段<select name="aiExtractionSourceField">${(section.fields || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === field.value ? "selected" : ""}>${escapeHtml(item.label)} (${escapeHtml(item.value)})</option>`).join("")}</select></label>
    <label>目标生产报表字段<select name="aiExtractionTargetField">${(catalog.target_fields || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === rule.target_field ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>输出格式<select name="aiExtractionOutputFormat">${(catalog.output_formats || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === rule.output_format ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>使用模型<select name="aiExtractionModelId"><option value="">默认模型</option>${(adminState.aiModels.models || []).filter((item) => item.enabled !== false).map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === rule.model_id ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}</select></label>
    <label>状态<select name="aiExtractionEnabled"><option value="true" ${rule.enabled !== false ? "selected" : ""}>启用</option><option value="false" ${rule.enabled === false ? "selected" : ""}>停用</option></select></label>
    <label class="wide">适用条件<textarea name="aiExtractionCondition" rows="3" placeholder="例如：仅处理作业类型为 NPT 的明细">${escapeHtml(rule.condition || "")}</textarea></label>
    <label class="wide">提炼要求<textarea name="aiExtractionInstruction" rows="4" placeholder="说明需要识别什么、无法判断时如何处理">${escapeHtml(rule.instruction || "")}</textarea></label>
    <div class="admin-actions wide"><button class="button" type="button" data-admin-save-extraction-rules>保存规则</button><button class="button secondary" type="button" data-admin-delete-extraction-rule>删除规则</button></div>
  </div>`;
}

function aiExtractionTestMarkup() {
  const selectedRule = (adminState.aiExtraction.rules || []).find((item) => item.id === adminState.selectedAiExtractionRuleId) || {};
  const matchingRecords = (adminState.records || []).filter((record) => !selectedRule.report_type || record.report_type === selectedRule.report_type);
  if (!matchingRecords.some((record) => record.record_id === adminState.aiExtractionTestRecordId)) {
    adminState.aiExtractionTestRecordId = matchingRecords[0]?.record_id || "";
  }
  const result = adminState.aiExtractionTestResult;
  const output = !result ? `<div class="admin-empty-panel"><p>默认读取所选日报的来源字段；也可以粘贴原文覆盖测试数据。</p></div>` : result.ok === false ? `<div class="ai-test-result failed"><strong>提炼失败</strong><small>${escapeHtml(result.error || "未知错误")}</small></div>` : `<div class="ai-test-result success"><strong>${escapeHtml(result.target_field)} = ${escapeHtml(result.result || "(空值)")}</strong><small>模型：${escapeHtml(result.model_name || "-")}，耗时 ${escapeHtml(result.elapsed_ms || 0)} ms，读取 ${escapeHtml(result.source_count || 0)} 条来源内容</small>${result.source_preview ? `<details><summary>查看测试原文</summary><pre>${escapeHtml(result.source_preview)}</pre></details>` : ""}</div>`;
  return `<div class="ai-extraction-test">
    <label>测试日报<select name="aiExtractionTestRecord">${matchingRecords.map((record) => `<option value="${escapeHtml(record.record_id)}" ${record.record_id === adminState.aiExtractionTestRecordId ? "selected" : ""}>${escapeHtml([record.reportDate, record.wellbore, record.rig, record.reportNo].filter(Boolean).join(" / ") || record.record_id)}</option>`).join("") || `<option value="">没有匹配的已入库日报</option>`}</select></label>
    <label>临时测试原文（可选）<textarea name="aiExtractionTestSource" rows="7" placeholder="留空时自动读取所选日报的来源字段">${escapeHtml(adminState.aiExtractionTestSource || "")}</textarea></label>
    <button class="button" type="button" data-admin-test-extraction-rule ${adminState.aiExtractionTestRunning ? "disabled" : ""}>${adminState.aiExtractionTestRunning ? "提炼中..." : "试运行"}</button>${output}
  </div>`;
}

function aiExtractionReportLabel(value) {
  return aiExtractionCatalogLabel(adminState.aiExtraction.catalog?.report_types, value);
}

function aiExtractionCatalogLabel(items = [], value = "") {
  return (items || []).find((item) => item.value === value)?.label || value || "-";
}

function emptyAiExtractionRule() {
  return { id: newClientId(), name: "新提炼规则", report_type: "drilling", source_section: "report_fields", source_field: "currentOps", condition: "", instruction: "", target_field: "remarks", output_format: "text", model_id: "", enabled: false };
}

function renderAdminProjects() {
  const host = document.querySelector('[data-admin-panel="projects"]');
  const config = adminState.projectTeams || { teams: [], projects: [], pending_wells: [] };
  const teams = config.teams || [];
  const projects = config.projects || [];
  const activeProjects = projects.filter((project) => project.status === "active");
  const teamProjectMap = teamProjectAssignments(config, teams);
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("项目合同", projects.length, `${activeProjects.length} 个启用`, "database")}
      ${adminKpi("队伍", teams.length, "全局队伍库", "users")}
      ${adminKpi("项目井号", projectWellCount(projects), "已归属井号", "overview")}
      ${adminKpi("待调整", (config.pending_wells || []).length, "需要人工确认", "logs")}
    </section>
    <section class="panel">
      <div class="panel-heading">
        <div><h2>项目合同列表</h2><span class="panel-note">编辑项目时维护绑定队伍、合同周期和井号</span></div>
        <button class="button small" type="button" data-admin-new-project>新增项目合同</button>
      </div>
      <div class="table-wrap"><table class="record-table admin-table project-table">
        <thead><tr><th>项目名称</th><th>合同号</th><th>合同周期</th><th>状态</th><th>队伍 / 井</th><th>操作</th></tr></thead>
        <tbody>${projects.map((project) => `<tr><td><strong>${escapeHtml(project.project_name || "-")}</strong></td><td>${escapeHtml(project.contract_no || "-")}</td><td>${escapeHtml(projectPeriodText(project))}</td><td><span class="status-pill ${project.status === "active" ? "uploaded" : "failed"}">${project.status === "active" ? "启用" : "关闭"}</span></td><td>${projectTeamSummary(project)}</td><td><button class="link-button" type="button" data-admin-edit-project="${escapeHtml(project.id)}">编辑</button></td></tr>`).join("") || `<tr><td colspan="6">暂无项目合同</td></tr>`}</tbody>
      </table></div>
    </section>
    ${teamListPanel(teams, teamProjectMap, "新增钻井队伍")}
    <section class="panel">
      <div class="panel-heading"><h2>井号列表</h2><span class="panel-note">井号自动从日报中建立归属关系；井队已绑定项目时自动带出归属项目</span></div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>井号</th><th>队伍</th><th>归属项目</th><th>来源报表</th><th>操作</th></tr></thead>
        <tbody>${wellAssignmentRows(config).map((item, index) => `<tr><td><strong>${escapeHtml(item.wellbore)}</strong></td><td>${escapeHtml(item.rig || "-")}</td><td>${escapeHtml(item.project_label || "未归属")}</td><td>${escapeHtml(item.source_report || "-")}</td><td><button class="link-button" type="button" data-admin-edit-well-assignment="${index}">编辑</button></td></tr>`).join("") || `<tr><td colspan="5">暂无井号</td></tr>`}</tbody>
      </table></div>
    </section>
  `;
}

function wellAssignmentRows(config = {}) {
  const sourceMap = wellSourceReportMap();
  const rows = [];
  (config.projects || []).forEach((project) => {
    (project.rigs || []).forEach((rig) => {
      (rig.wells || []).forEach((wellbore) => {
        const source = sourceMap.get(wellSourceKey(rig.rig || "", wellbore));
        rows.push({
          kind: "assigned",
          project_id: project.id || "",
          project_label: projectLabel(project),
          rig: rig.rig || "",
          wellbore,
          source_report: sourceReportText(source),
        });
      });
    });
  });
  (config.pending_wells || []).forEach((item, pending_index) => {
    const source = sourceMap.get(wellSourceKey(item.rig || "", item.wellbore || ""));
    rows.push({
      kind: "pending",
      pending_index,
      project_id: "",
      project_label: "",
      rig: item.rig || "",
      wellbore: item.wellbore || "",
      source_report: sourceReportText(source),
    });
  });
  rows.sort((left, right) => String(left.wellbore).localeCompare(String(right.wellbore), "zh-Hans-CN", { numeric: true }) || String(left.rig).localeCompare(String(right.rig), "zh-Hans-CN", { numeric: true }));
  adminState.wellAssignmentRows = rows;
  return rows;
}

function wellSourceReportMap() {
  const map = new Map();
  (adminState.records || []).forEach((record) => {
    const key = wellSourceKey(record.rig || "", record.wellbore || "");
    if (!key) return;
    const current = map.get(key);
    const reportDate = record.reportDate || "";
    const updatedAt = record.updated_at || "";
    const type = record.report_type || "";
    if (!current) {
      map.set(key, { report_type: type, reportDate, updated_at: updatedAt, all_types: new Set([type].filter(Boolean)) });
      return;
    }
    if (type) current.all_types.add(type);
    if (`${reportDate} ${updatedAt}` < `${current.reportDate || ""} ${current.updated_at || ""}`) {
      current.report_type = type || current.report_type;
      current.reportDate = reportDate;
      current.updated_at = updatedAt;
    }
  });
  return map;
}

function wellSourceKey(rig, wellbore) {
  const left = String(rig || "").trim();
  const right = String(wellbore || "").trim();
  return left && right ? `${left}||${right}` : "";
}

function sourceReportText(source) {
  if (!source?.report_type) return "-";
  const first = reportTypeLabel(source.report_type);
  const others = [...(source.all_types || [])].filter((type) => type && type !== source.report_type).map(reportTypeLabel);
  return others.length ? `${first}（另有${others.join("、")}）` : first;
}

function reportTypeLabel(type = "") {
  return ({ drilling: "钻井日报", completion: "完井日报", workover: "修井日报", move: "搬迁日报" })[type] || type || "-";
}

function projectLabel(project = {}) {
  return [project.project_name, project.contract_no].filter(Boolean).join(" / ") || project.id || "-";
}

function projectPeriodText(project = {}) {
  return `${project.start_date || "-"} 至 ${project.end_date || "-"}`;
}

function teamProjectAssignments(config = {}, teams = []) {
  const result = new Map();
  const teamLookup = new Map();
  teams.forEach((team) => {
    [team.name, ...(Array.isArray(team.aliases) ? team.aliases : [])].forEach((value) => {
      const key = String(value || "").trim();
      if (key) teamLookup.set(key, team.name);
    });
  });
  (config.projects || []).forEach((project) => {
    (project.rigs || []).forEach((rig) => {
      if (!rig.rig) return;
      const teamName = teamLookup.get(String(rig.rig).trim()) || rig.rig;
      const rows = result.get(teamName) || [];
      const projectKey = project.id || `${project.project_name || ""}|${project.contract_no || ""}|${project.start_date || ""}|${project.end_date || ""}`;
      if (!rows.some((item) => item.key === projectKey)) {
        rows.push({ key: projectKey, name: project.project_name || project.contract_no || "-", period: projectPeriodText(project) });
      }
      result.set(teamName, rows);
    });
  });
  return result;
}

function teamListPanel(teams = [], teamProjectMap = new Map(), buttonText = "新增队伍") {
  return `
    <section class="panel">
      <div class="panel-heading">
        <div><h2>队伍列表</h2><span class="panel-note">维护全局队伍库，项目配置中可选择绑定</span></div>
        <button class="button small" type="button" data-admin-new-team>${escapeHtml(buttonText)}</button>
      </div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>队伍</th><th>承包商</th><th>识别别名</th><th>状态</th><th>归属项目</th><th>项目合同周期</th><th>操作</th></tr></thead>
        <tbody>${teams.map((team) => {
          const assignments = teamProjectMap.get(team.name) || [];
          return `<tr><td><strong>${escapeHtml(team.name)}</strong></td><td>${escapeHtml(team.contractor || "-")}</td><td>${escapeHtml(teamAliasText(team))}</td><td><span class="status-pill ${team.status === "active" ? "uploaded" : "failed"}">${team.status === "active" ? "启用" : "停用"}</span></td><td>${teamProjectCell(assignments, "name")}</td><td>${teamProjectCell(assignments, "period")}</td><td><button class="link-button" type="button" data-admin-edit-team="${escapeHtml(team.id)}">编辑</button></td></tr>`;
        }).join("") || `<tr><td colspan="7">暂无队伍</td></tr>`}</tbody>
      </table></div>
    </section>
  `;
}

function teamProjectCell(assignments = [], field = "name") {
  if (!assignments.length) return "未绑定";
  return assignments.map((item) => `<div>${escapeHtml(item[field] || "-")}</div>`).join("");
}

function teamAliasText(team = {}) {
  const aliases = Array.isArray(team.aliases) ? team.aliases.filter(Boolean) : [];
  return aliases.length ? aliases.join("、") : "-";
}

function renderAdminTranslationTuning() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host) return;
  const tuning = adminState.translationTuning || {};
  const terms = adminState.translationTerms?.terms || [];
  const enabledFields = (tuning.scope_rules || []).filter((item) => item.enabled !== false).length;
  const pendingCount = adminState.records.filter(translationNeedsProcessing).length;
  const view = adminState.translationTuningView || "fields";
  const content = view === "terms" ? translationTermsMarkup() : view === "queue" ? translationQueuePanelMarkup() : view === "test" ? translationTestWorkbenchMarkup() : translationFieldPoliciesMarkup();
  host.innerHTML = `
    <section class="admin-kpi-grid compact tuning-kpis">
      ${adminKpi("翻译范围", enabledFields, `共 ${(tuning.scope_rules || []).length} 条精确规则`, "sliders")}
      ${adminKpi("术语词库", terms.filter((term) => term.enabled !== false).length, `总计 ${terms.length} 条`, "database")}
      ${adminKpi("目标语言", (tuning.target_languages || []).length, translationLanguageNames(tuning.target_languages), "overview")}
      ${adminKpi("待处理日报", pendingCount, "点击查看、选择或覆盖翻译", "logs", 'role="button" tabindex="0" data-admin-open-translation-queue')}
    </section>
    <nav class="tuning-tabs" aria-label="翻译调优视图">
      ${translationTuningTab("fields", "字段与 Prompt")}
      ${translationTuningTab("terms", "术语词库")}
      ${translationTuningTab("queue", "任务队列")}
      ${translationTuningTab("test", "测试工作台")}
    </nav>
    <div class="translation-tuning-content">${content}</div>`;
}

function translationTuningTab(value, label) {
  return `<button type="button" class="${adminState.translationTuningView === value ? "active" : ""}" data-translation-tuning-view="${value}">${label}</button>`;
}

function translationLanguageNames(values = []) {
  const labels = { "zh-CN": "中文" };
  return values.map((value) => labels[value] || value).join(" / ") || "未配置";
}

function translationNeedsProcessing(record = {}) {
  const status = String(record.translation_status || "").toUpperCase();
  const version = String(record.translation_version || "");
  const currentVersion = String(adminState.translationTuning?.version || "");
  if (["QUEUED", "IN_PROGRESS", "NOT_REQUIRED"].includes(status)) return false;
  return ["PENDING", "FAILED"].includes(status) || Boolean(currentVersion && version !== currentVersion);
}

function translationQueuePanelMarkup() {
  const queue = adminState.translationQueue || {};
  const records = queue.records || [];
  return `<section class="panel"><div class="panel-heading"><div><h2>日报翻译任务</h2><span class="panel-note">当前策略版本 ${escapeHtml(queue.current_version || "-")}</span></div><div class="admin-actions"><button class="button secondary small" type="button" data-admin-queue-selected="overwrite">覆盖重译选中</button><button class="button small" type="button" data-admin-queue-selected="continue">继续翻译选中</button></div></div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th><input type="checkbox" data-translation-queue-select-all /></th><th>类型</th><th>日期 / 报告号</th><th>井号</th><th>队伍</th><th>状态</th><th>原因</th></tr></thead><tbody>${records.map(translationQueueRowMarkup).join("") || `<tr><td colspan="7">暂无日报记录</td></tr>`}</tbody></table></div></section>`;
}

function translationFieldPoliciesMarkup() {
  const tuning = adminState.translationTuning || {};
  const prompt = tuning.prompt || {};
  const protections = tuning.protections || {};
  const rules = tuning.scope_rules || [];
  return `
    <section class="panel tuning-policy-panel">
      <div class="panel-heading">
        <div><h2>翻译策略</h2><span class="panel-note">按日报类型、模块和字段精确控制翻译范围</span></div>
        <button class="button small" type="button" data-admin-save-translation-tuning>保存策略</button>
      </div>
      <div class="tuning-policy-layout">
        <div class="tuning-prompt-form">
          <label>系统角色<textarea name="translationSystemPrompt" rows="3" maxlength="1200">${escapeHtml(prompt.system_prompt || "")}</textarea></label>
          <label>翻译要求<textarea name="translationInstruction" rows="4" maxlength="2400">${escapeHtml(prompt.translation_instruction || "")}</textarea></label>
        </div>
        <div class="tuning-option-panel">
          <fieldset><legend>目标语言</legend>${translationTargetOptions(tuning.target_languages || [])}</fieldset>
          <fieldset><legend>内容保护</legend>${translationProtectionOptions(protections)}</fieldset>
          <p>术语词库中的锁定词会强制采用目标译法；缩写、单位和专名会写入模型保护清单。</p>
        </div>
      </div>
      ${translationScopeBuilderMarkup()}
      <div class="table-wrap tuning-field-table-wrap">
        <table class="record-table admin-table tuning-field-table">
          <thead><tr><th>日报类型</th><th>模块 / 部分</th><th>字段</th><th>字段编码</th><th>处理方式</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>${rules.map((rule) => `<tr data-translation-scope-rule="${escapeHtml(rule.id)}">
            <td><strong>${escapeHtml(rule.report_type_label || rule.report_type)}</strong></td>
            <td>${escapeHtml(rule.section_label || rule.section)}</td>
            <td>${escapeHtml(rule.label || rule.field_name)}</td>
            <td><code>${escapeHtml(rule.field_code)}</code></td>
            <td><span class="type-pill">大模型 + 术语</span></td>
            <td><label class="compact-toggle"><input type="checkbox" name="translationPolicyEnabled" ${rule.enabled !== false ? "checked" : ""} /><span>${rule.enabled !== false ? "启用" : "停用"}</span></label></td>
            <td><button class="link-button danger-link" type="button" data-admin-remove-translation-scope="${escapeHtml(rule.id)}">移除</button></td>
          </tr>`).join("") || `<tr><td colspan="7">尚未配置翻译范围</td></tr>`}</tbody>
        </table>
      </div>
    </section>`;
}

function translationScopeBuilderMarkup() {
  const catalog = adminState.translationTuning?.scope_catalog?.report_types || [];
  let report = catalog.find((item) => item.value === adminState.translationScopeDraft.report_type) || catalog[0] || { sections: [] };
  let section = (report.sections || []).find((item) => item.value === adminState.translationScopeDraft.section) || report.sections?.[0] || { fields: [] };
  let field = (section.fields || []).find((item) => item.value === adminState.translationScopeDraft.field_name) || section.fields?.[0] || {};
  adminState.translationScopeDraft = { report_type: report.value || "", section: section.value || "", field_name: field.value || "" };
  return `<section class="translation-scope-builder">
    <div><strong>新增翻译范围</strong><span>数值、日期、深度和井号等非文本字段不在可选范围内</span></div>
    <label>日报类型<select name="translationScopeReportType">${catalog.map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === report.value ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>模块 / 部分<select name="translationScopeSection">${(report.sections || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === section.value ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <label>字段<select name="translationScopeField">${(section.fields || []).map((item) => `<option value="${escapeHtml(item.value)}" ${item.value === field.value ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")}</select></label>
    <button class="button secondary small" type="button" data-admin-add-translation-scope>新增范围</button>
  </section>`;
}

function translationTargetOptions(selected = []) {
  return [["zh-CN", "中文"]].map(([value, label]) => `<label><input type="checkbox" name="translationTargetLanguage" value="${value}" ${selected.includes(value) ? "checked" : ""} />${label}</label>`).join("");
}

function translationProtectionOptions(protections = {}) {
  return [["numbers", "数字与精度"], ["units", "计量单位"], ["acronyms", "专业缩写"], ["proper_nouns", "公司与专名"]].map(([value, label]) => `<label><input type="checkbox" name="translationProtection" value="${value}" ${protections[value] !== false ? "checked" : ""} />${label}</label>`).join("");
}

function translationTermsMarkup() {
  const terms = adminState.translationTerms?.terms || [];
  const query = String(adminState.translationTermSearch || "").trim().toLowerCase();
  const category = adminState.translationTermCategory || "all";
  const filteredTerms = terms.filter((term) => {
    const categoryMatches = category === "all" || term.category === category;
    const queryMatches = !query || [term.zh, term.en, term.es, translationTermCategoryLabel(term.category)].some((value) => String(value || "").toLowerCase().includes(query));
    return categoryMatches && queryMatches;
  });
  const pageSize = Number(adminState.translationTermPageSize || 10);
  const pageCount = Math.max(1, Math.ceil(filteredTerms.length / pageSize));
  adminState.translationTermPage = Math.min(Math.max(1, adminState.translationTermPage || 1), pageCount);
  const start = (adminState.translationTermPage - 1) * pageSize;
  const visibleTerms = filteredTerms.slice(start, start + pageSize);
  return `
    <section class="panel">
      <div class="panel-heading tuning-term-heading">
        <div><h2>术语词库</h2><span class="panel-note">术语对全部日报字段生效，作业类型仅用于分类管理</span></div>
        <div class="admin-actions tuning-term-actions"><input type="file" accept=".xlsx,.xls,.xlsm,.xltx,.xltm" data-translation-term-file hidden /><a class="button secondary small" href="/api/admin/translation-terms/template">下载模板</a><button class="button secondary small" type="button" data-admin-import-translation-terms ${adminState.translationTermImport.running ? "disabled" : ""}>${adminState.translationTermImport.running ? "分析中..." : "导入 Excel"}</button><a class="button secondary small" href="/api/admin/translation-terms/export">导出 Excel</a><button class="button small" type="button" data-admin-add-translation-term>新增术语</button></div>
      </div>
      ${translationTermImportSummaryMarkup()}
      <div class="translation-term-toolbar"><input class="tuning-term-search" type="search" value="${escapeHtml(adminState.translationTermSearch)}" placeholder="搜索中文、英文或西班牙语" aria-label="搜索术语" data-translation-term-search /><div class="translation-term-segments" role="group" aria-label="作业类型筛选">${translationTermCategorySegments(category)}</div></div>
      <div class="table-wrap tuning-term-table-wrap"><table class="record-table admin-table tuning-term-table">
        <thead><tr><th>作业类型</th><th>中文</th><th>English</th><th>Español</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>${visibleTerms.map(translationTermListRow).join("") || `<tr><td colspan="6">没有匹配的术语</td></tr>`}</tbody>
      </table></div>
      <div class="translation-term-pagination"><span>共 ${filteredTerms.length} 条，第 ${adminState.translationTermPage} / ${pageCount} 页</span><div><select aria-label="每页术语数量" data-translation-term-page-size><option value="10" ${pageSize === 10 ? "selected" : ""}>10 条/页</option><option value="20" ${pageSize === 20 ? "selected" : ""}>20 条/页</option><option value="50" ${pageSize === 50 ? "selected" : ""}>50 条/页</option></select><button class="button secondary small term-page-button" type="button" title="上一页" data-translation-term-page="${adminState.translationTermPage - 1}" ${adminState.translationTermPage <= 1 ? "disabled" : ""}><span aria-hidden="true">‹</span>上一页</button><button class="button secondary small term-page-button" type="button" title="下一页" data-translation-term-page="${adminState.translationTermPage + 1}" ${adminState.translationTermPage >= pageCount ? "disabled" : ""}>下一页<span aria-hidden="true">›</span></button></div></div>
    </section>
    <section class="panel tuning-protection-panel">
      <div class="panel-heading"><div><h2>全局保护项</h2><span class="panel-note">缩写、单位和专名会随 Prompt 发送给模型并要求保持原样</span></div><button class="button small" type="button" data-admin-save-translation-terms>保存保护项</button></div>
      ${protectedTermsMarkup()}
    </section>`;
}

function translationTermCategoryLabel(value = "general") {
  return { general: "通用", drilling: "钻井", completion: "完井", workover: "修井", move: "搬迁" }[value] || "通用";
}

function translationTermCategoryOptions(selected = "general", includeAll = false) {
  const options = [["general", "通用"], ["drilling", "钻井"], ["completion", "完井"], ["workover", "修井"], ["move", "搬迁"]];
  return `${includeAll ? `<option value="all" ${selected === "all" ? "selected" : ""}>全部作业类型</option>` : ""}${options.map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`).join("")}`;
}

function translationTermCategorySegments(selected = "all") {
  const options = [["all", "全部"], ["general", "通用"], ["drilling", "钻井"], ["completion", "完井"], ["workover", "修井"], ["move", "搬迁"]];
  return options.map(([value, label]) => `<button type="button" class="${selected === value ? "active" : ""}" aria-pressed="${selected === value ? "true" : "false"}" data-translation-term-category-value="${value}">${label}</button>`).join("");
}

function translationTermImportSummaryMarkup() {
  const result = adminState.translationTermImport?.result;
  if (!result) return "";
  const hasDuplicates = Number(result.duplicate_count || 0) > 0;
  return `<div class="term-import-summary ${hasDuplicates ? "warning" : "success"}">
    <div><strong>${escapeHtml(result.filename || "Excel")}</strong><span>AI 识别 ${escapeHtml(result.analyzed_terms || 0)} 条，已导入 ${escapeHtml(result.imported_count || 0)} 条，跳过重复 ${escapeHtml(result.duplicate_count || 0)} 条</span><small>${escapeHtml(result.model_name || "默认模型")} · ${escapeHtml(result.workbook?.sheet_count || 0)} 个工作表</small></div>
    ${hasDuplicates ? `<button class="button secondary small" type="button" data-admin-review-term-duplicates>查看重复项</button>` : ""}
  </div>`;
}

function translationTermListRow(term = {}) {
  return `<tr>
    <td><span class="type-pill">${escapeHtml(translationTermCategoryLabel(term.category))}</span></td><td><strong>${escapeHtml(term.zh || "-")}</strong></td><td>${escapeHtml(term.en || "-")}</td><td>${escapeHtml(term.es || "-")}</td>
    <td><span class="status-pill ${term.enabled !== false ? "uploaded" : "failed"}">${term.enabled !== false ? (term.protected !== false ? "启用 / 锁定" : "启用") : "停用"}</span></td>
    <td><button class="link-button" type="button" data-admin-edit-translation-term="${escapeHtml(term.id)}">编辑</button><button class="link-button danger-link" type="button" data-admin-delete-translation-term="${escapeHtml(term.id)}">删除</button></td>
  </tr>`;
}

function protectedTermsMarkup() {
  const protectedTerms = adminState.translationTerms?.protected_terms || {};
  return `<div class="protected-terms-form">
    <label>专业缩写<textarea name="protectedAcronyms" rows="4">${escapeHtml((protectedTerms.acronyms || []).join(", "))}</textarea></label>
    <label>计量单位<textarea name="protectedUnits" rows="3">${escapeHtml((protectedTerms.units || []).join(", "))}</textarea></label>
    <label>公司、地层与专名<textarea name="protectedProperNouns" rows="5">${escapeHtml((protectedTerms.proper_nouns || []).join("\n"))}</textarea></label>
  </div>`;
}

function translationTestWorkbenchMarkup() {
  const models = (adminState.aiModels.models || []).filter((model) => model.enabled !== false);
  const policies = (adminState.translationTuning?.scope_rules || []).filter((policy) => policy.enabled !== false);
  const result = adminState.translationTestResult;
  return `<section class="tuning-test-layout">
    <section class="panel tuning-test-input">
      <div class="panel-heading"><h2>测试输入</h2><span class="panel-note">测试会调用模型，但不会写入日报数据库</span></div>
      <div class="tuning-test-controls">
        <label>模型<select name="translationTestModel">${models.map((model) => `<option value="${escapeHtml(model.id)}" ${model.id === (adminState.translationTestModelId || adminState.aiModels.default_model_id) ? "selected" : ""}>${escapeHtml(model.name)} / ${escapeHtml(model.model)}</option>`).join("")}</select></label>
        <label>目标语言<select name="translationTestLanguage"><option value="zh-CN" selected>中文</option></select></label>
        <label>模拟字段<select name="translationTestField">${policies.map((policy) => `<option value="${escapeHtml(policy.id)}" ${policy.id === adminState.translationTestFieldCode ? "selected" : ""}>${escapeHtml(policy.report_type_label)} / ${escapeHtml(policy.section_label)} / ${escapeHtml(policy.label)}</option>`).join("")}</select></label>
      </div>
      <label class="tuning-test-source">日报原文<textarea name="translationTestSource" rows="10" maxlength="8000">${escapeHtml(adminState.translationTestSource || "")}</textarea></label>
      <div class="admin-actions"><button class="button" type="button" data-admin-run-translation-test ${adminState.translationTestRunning ? "disabled" : ""}>${adminState.translationTestRunning ? "测试中..." : "运行测试"}</button></div>
      <details class="prompt-preview" ${result?.prompt_preview ? "open" : ""}><summary>实际 Prompt 预览</summary><pre>${escapeHtml(result?.prompt_preview || "运行测试后显示最终发送给模型的 Prompt。")}</pre></details>
    </section>
    <section class="panel tuning-test-output">
      <div class="panel-heading"><h2>输出与校验</h2><span class="panel-note">${result ? `${escapeHtml(result.model_name || "-")} / ${escapeHtml(result.elapsed_ms || 0)} ms` : "等待测试"}</span></div>
      ${translationTestResultMarkup(result)}
    </section>
  </section>`;
}

function translationTestResultMarkup(result) {
  if (!result) return `<div class="admin-empty-panel tuning-test-empty"><p>输入一段真实日报描述，运行后可查看译文、Prompt 和质量检查。</p></div>`;
  return `<div class="translation-test-result ${result.ok ? "success" : "failed"}">
    <div class="translation-output-text"><span>译文</span><p>${escapeHtml(result.translated_text || result.error || "模型未返回译文")}</p></div>
    <div class="translation-test-meta"><span>源语言 <strong>${escapeHtml(result.source_language || "-")}</strong></span><span>目标语言 <strong>${escapeHtml(result.target_language || "-")}</strong></span><span>Prompt版本 <strong>${escapeHtml(result.prompt_version || "-")}</strong></span></div>
    <div class="translation-checks">${(result.checks || []).map((check) => `<div class="${escapeHtml(check.status || "warning")}"><span aria-hidden="true"></span><div><strong>${escapeHtml(check.label)}</strong>${check.detail ? `<small>${escapeHtml(check.detail)}</small>` : ""}</div></div>`).join("")}</div>
  </div>`;
}

function aliasInputValue(value) {
  return Array.isArray(value) ? value.join("\n") : "";
}

function projectWellCount(projects) {
  return (projects || []).reduce((sum, project) => sum + (project.rigs || []).reduce((inner, rig) => inner + (rig.wells || []).length, 0), 0);
}

function projectTeamSummary(project) {
  const rigs = project.rigs || [];
  return `${rigs.length} 队 / ${projectWellCount([project])} 井`;
}

function projectSelectOptions(projects, selected = "") {
  const active = (projects || []).filter((project) => project.status !== "closed");
  return active.map((project) => `<option value="${escapeHtml(project.id)}" ${project.id === selected ? "selected" : ""}>${escapeHtml(projectLabel(project))}</option>`).join("") || `<option value="">请先新增项目</option>`;
}

function closeAdminModal() {
  document.querySelector(".admin-modal")?.remove();
}

function openAdminModal(title, body, footer) {
  closeAdminModal();
  const wrapper = document.createElement("div");
  wrapper.className = "admin-modal";
  wrapper.innerHTML = `
    <div class="admin-modal-backdrop" data-admin-modal-close></div>
    <section class="admin-modal-panel" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">
      <header class="admin-modal-header">
        <h2>${escapeHtml(title)}</h2>
        <button class="icon-button" type="button" data-admin-modal-close aria-label="关闭">×</button>
      </header>
      <div class="admin-modal-body">${body}</div>
      <footer class="admin-modal-footer">${footer}</footer>
    </section>
  `;
  document.body.appendChild(wrapper);
  wrapper.querySelector("input, select, textarea")?.focus();
}

function teamSelectOptions(selected = "") {
  const teams = adminState.projectTeams?.teams || [];
  return teams.map((team) => `<option value="${escapeHtml(team.name)}" ${team.name === selected ? "selected" : ""}>${escapeHtml(team.name)}</option>`).join("");
}

function projectRigRow(rig = {}, index = 0) {
  const wells = Array.isArray(rig.wells) ? rig.wells.join("\n") : "";
  const teamOptions = teamSelectOptions(rig.rig || "");
  return `<div class="admin-project-rig-row" data-project-rig-row>
    <label>队伍
      <select name="projectRigName">
        <option value="">选择队伍</option>
        ${teamOptions}
      </select>
    </label>
    <label>开始日期<input name="projectRigStart" type="date" value="${escapeHtml(rig.start_date || "")}" /></label>
    <label>结束日期<input name="projectRigEnd" type="date" value="${escapeHtml(rig.end_date || "")}" /></label>
    <label>井号<textarea name="projectRigWells" placeholder="多个井号可换行或用逗号分隔">${escapeHtml(wells)}</textarea></label>
    <label>备注<input name="projectRigNote" value="${escapeHtml(rig.note || "")}" placeholder="队伍范围说明" /></label>
    <button class="icon-button" type="button" data-admin-remove-project-rig aria-label="移除队伍">×</button>
  </div>`;
}

function projectRigRows(project = {}) {
  const rigs = Array.isArray(project.rigs) && project.rigs.length ? project.rigs : [{}];
  return rigs.map((rig, index) => projectRigRow(rig, index)).join("");
}

function openProjectModal(id = "") {
  const project = (adminState.projectTeams.projects || []).find((item) => item.id === id) || {};
  const isEdit = Boolean(project.id);
  openAdminModal(
    isEdit ? "编辑项目合同" : "新增项目合同",
    `<input name="projectId" type="hidden" value="${escapeHtml(project.id || "")}" />
    <div class="admin-modal-form">
      <label>合同号<input name="projectContractNo" value="${escapeHtml(project.contract_no || "")}" placeholder="例如：EC-2026-001" /></label>
      <label>项目名称<input name="projectName" value="${escapeHtml(project.project_name || "")}" placeholder="项目名称" /></label>
      <label>状态
        <select name="projectStatus">
          <option value="active" ${project.status !== "closed" ? "selected" : ""}>启用</option>
          <option value="closed" ${project.status === "closed" ? "selected" : ""}>关闭</option>
        </select>
      </label>
      <label>项目开始日期<input name="projectStartDate" type="date" value="${escapeHtml(project.start_date || "")}" /></label>
      <label>项目结束日期<input name="projectEndDate" type="date" value="${escapeHtml(project.end_date || "")}" /></label>
      <label class="wide">备注<input name="projectNote" value="${escapeHtml(project.note || "")}" placeholder="合同范围、甲方或区域说明" /></label>
    </div>
    <section class="admin-modal-subsection">
      <div class="panel-heading compact-heading">
        <div><h3>绑定队伍</h3><span class="panel-note">为项目添加队伍、服务日期和井号范围</span></div>
        <button class="button secondary small" type="button" data-admin-add-project-rig>添加队伍</button>
      </div>
      <div class="admin-project-rig-list" data-project-rig-list>${projectRigRows(project)}</div>
    </section>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button>
    <button class="button" type="button" data-admin-save-project-modal>${isEdit ? "保存项目" : "新增项目"}</button>`
  );
}

function openTeamModal(id = "") {
  const team = (adminState.projectTeams.teams || []).find((item) => item.id === id) || {};
  const isEdit = Boolean(team.id);
  openAdminModal(
    isEdit ? "编辑队伍" : "新增队伍",
    `<input name="teamId" type="hidden" value="${escapeHtml(team.id || "")}" />
    <input name="teamOriginalName" type="hidden" value="${escapeHtml(team.name || "")}" />
    <div class="admin-modal-form compact">
      <label>队伍名称<input name="teamName" value="${escapeHtml(team.name || "")}" placeholder="例如：SINOPEC 248" /></label>
      <label>队伍编号<input name="teamCode" value="${escapeHtml(team.code || "")}" placeholder="可选" /></label>
      <label>承包商<input name="teamContractor" value="${escapeHtml(team.contractor || "")}" placeholder="例如：SINOPEC" /></label>
      <label>状态
        <select name="teamStatus">
          <option value="active" ${team.status !== "inactive" ? "selected" : ""}>启用</option>
          <option value="inactive" ${team.status === "inactive" ? "selected" : ""}>停用</option>
        </select>
      </label>
      <label class="wide">识别别名<textarea name="teamAliases" placeholder="日报中识别到的旧队伍名或其他写法，每行一个">${escapeHtml(aliasInputValue(team.aliases || []))}</textarea></label>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button>
    <button class="button" type="button" data-admin-save-team-modal>${isEdit ? "保存队伍" : "新增队伍"}</button>`
  );
}

function openWellAssignmentModal(index = 0) {
  const row = (adminState.wellAssignmentRows || wellAssignmentRows(adminState.projectTeams))[Number(index)];
  if (!row) return showToast("井号记录不存在");
  openAdminModal(
    "编辑井号归属",
    `<input name="wellAssignmentIndex" type="hidden" value="${Number(index)}" />
    <input name="wellAssignmentOriginalProject" type="hidden" value="${escapeHtml(row.project_id || "")}" />
    <input name="wellAssignmentOriginalRig" type="hidden" value="${escapeHtml(row.rig || "")}" />
    <input name="wellAssignmentOriginalWell" type="hidden" value="${escapeHtml(row.wellbore || "")}" />
    <input name="wellAssignmentKind" type="hidden" value="${escapeHtml(row.kind || "")}" />
    <input name="wellAssignmentPendingIndex" type="hidden" value="${escapeHtml(String(row.pending_index ?? ""))}" />
    <div class="admin-modal-form compact">
      <label>井号<input name="wellAssignmentWell" value="${escapeHtml(row.wellbore || "")}" /></label>
      <label>队伍<select name="wellAssignmentRig"><option value="">未选择队伍</option>${teamSelectOptions(row.rig || "")}</select></label>
      <label class="wide">归属项目<select name="wellAssignmentProject"><option value="">未归属</option>${projectSelectOptions(adminState.projectTeams.projects || [], row.project_id || "")}</select></label>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button>
    <button class="button" type="button" data-admin-save-well-assignment>保存井号归属</button>`
  );
}

function renderAdminConfig() {
  const host = document.querySelector('[data-admin-panel="config"]');
  const config = adminState.config || {};
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>系统配置</h2><span class="panel-note">保存基础配置和日报运行参数</span></div>
      <div class="admin-config-grid">
        <label>系统名称<input name="system_name" value="${escapeHtml(config.system_name)}" /></label>
        <label>默认语言<select name="default_language"><option value="zh">中文</option><option value="es">ES</option></select></label>
        <label>每页记录数<input name="records_per_page" type="number" min="5" max="100" value="${escapeHtml(config.records_per_page)}" /></label>
        <label>数据库类型<input name="database_engine" value="${escapeHtml(config.database_engine || "mysql")}" readonly /></label>
        <label>数据库名<input name="database_name" value="${escapeHtml(config.database_name || "")}" readonly /></label>
        <label>源PDF保存<select name="save_source_pdf"><option value="true">开启</option><option value="false">关闭</option></select></label>
        <label>PDF保留天数<input name="source_pdf_retention_days" type="number" min="1" value="${escapeHtml(config.source_pdf_retention_days)}" /></label>
      </div>
      <div class="admin-actions"><button class="button" type="button" data-admin-save-config>保存配置</button></div>
    </section>`;
  host.querySelector('[name="default_language"]').value = config.default_language || "zh";
  host.querySelector('[name="save_source_pdf"]').value = String(config.save_source_pdf !== false);
}

function renderAdminData() {
  const host = document.querySelector('[data-admin-panel="data"]');
  const status = adminState.dataStatus || {};
  const byType = status.by_type || {};
  host.innerHTML = `
    <section class="admin-kpi-grid">${adminKpi("总记录", status.records || 0, "全部日报", "database")}${adminKpi("钻井日报", byType.drilling || 0, "drilling", "overview")}${adminKpi("完井日报", byType.completion || 0, "completion", "shield")}${adminKpi("修井 / 搬迁", `${byType.workover || 0} / ${byType.move || 0}`, "workover / move", "logs")}</section>
    <section class="panel"><div class="panel-heading"><h2>数据维护</h2><span class="panel-note">当前运行时只使用 MySQL；Excel 文件库已移除</span></div><div class="admin-note-grid"><span><strong>数据库</strong><small>${escapeHtml(status.database_name || "-")}</small></span><span><strong>连接</strong><small>${escapeHtml(`${status.database_host || ""}:${status.database_port || ""}`)}</small></span><span><strong>状态</strong><small>${status.mysql?.available ? "可用" : escapeHtml(status.mysql?.error || "不可用")}</small></span></div></section>`;
}

function renderAdminLogs() {
  const host = document.querySelector('[data-admin-panel="logs"]');
  const logs = adminState.logs || [];
  const pageSize = Number(adminState.logsPageSize || 20);
  const totalPages = Math.max(1, Math.ceil(logs.length / pageSize));
  const currentPage = Math.min(Math.max(1, Number(adminState.logsPage || 1)), totalPages);
  adminState.logsPage = currentPage;
  const pageRows = logs.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading">
        <h2>日志审计</h2>
        <span class="panel-note">最近 ${logs.length} 条后台操作</span>
      </div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>时间</th><th>用户</th><th>动作</th><th>模块</th><th>对象</th><th>结果</th><th>备注</th></tr></thead>
        <tbody>${pageRows.map((log) => `<tr><td>${escapeHtml(log.time)}</td><td>${escapeHtml(log.user)}</td><td>${escapeHtml(log.action)}</td><td>${escapeHtml(log.module)}</td><td>${escapeHtml(log.target)}</td><td>${escapeHtml(log.result)}</td><td>${escapeHtml(log.note)}</td></tr>`).join("") || `<tr><td colspan="7">暂无日志</td></tr>`}</tbody>
      </table></div>
      ${adminLogPagination(logs.length, currentPage, totalPages, pageSize)}
    </section>`;
}

function adminLogPagination(totalRows, currentPage, totalPages, pageSize) {
  const start = totalRows ? (currentPage - 1) * pageSize + 1 : 0;
  const end = Math.min(totalRows, currentPage * pageSize);
  return `
    <div class="record-pagination admin-log-pagination">
      <span>共 ${totalRows} 条，显示 ${start}-${end}</span>
      <div class="admin-log-page-controls">
        <label>每页
          <select data-admin-log-page-size>
            ${[10, 20, 50].map((size) => `<option value="${size}" ${size === pageSize ? "selected" : ""}>${size} 条</option>`).join("")}
          </select>
        </label>
        <div class="record-page-buttons">
          <button class="icon-button" type="button" data-admin-log-page="${currentPage - 1}" ${currentPage <= 1 ? "disabled" : ""} aria-label="上一页">‹</button>
          <span>${currentPage} / ${totalPages}</span>
          <button class="icon-button" type="button" data-admin-log-page="${currentPage + 1}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="下一页">›</button>
        </div>
      </div>
    </div>`;
}

function switchAdminTab(tab) {
  if (tab === "teams") tab = "projects";
  adminState.tab = tab;
  document.querySelectorAll("[data-admin-tab]").forEach((button) => button.classList.toggle("active", button.dataset.adminTab === tab));
  document.querySelectorAll("[data-admin-panel]").forEach((panel) => panel.hidden = panel.dataset.adminPanel !== tab);
}

function roleLabel(value) {
  return (adminState.roles || []).find((role) => role.value === value)?.label || value || "-";
}

function fileSize(value) {
  const size = Number(value) || 0;
  if (size > 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
  if (size > 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${size} B`;
}

function normalizeRoleValue(value) {
  return String(value || "").trim().toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40);
}

function newClientId() {
  return crypto.randomUUID ? crypto.randomUUID() : `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function addAdminRole() {
  const labelInput = document.querySelector('[name="adminRoleLabel"]');
  const valueInput = document.querySelector('[name="adminRoleValue"]');
  const label = labelInput?.value.trim() || "";
  const value = normalizeRoleValue(valueInput?.value || label);
  if (!label || !value) return showToast("请填写角色名称和角色编码");
  if ((adminState.roles || []).some((role) => role.value === value)) return showToast("角色编码已存在");
  adminState.roles = [
    ...(adminState.roles || []),
    { value, label, permissions: { view: true, import: false, edit: false, save: false, export: false, admin: false } }
  ];
  renderAdminRoles();
}

function collectAdminRoles() {
  return [...document.querySelectorAll("[data-role-row]")].map((row) => {
    const value = row.dataset.roleRow;
    const label = row.querySelector("[data-role-label]")?.value.trim() || value;
    const permissions = {};
    row.querySelectorAll("[data-role-permission]").forEach((control) => {
      permissions[control.dataset.permissionKey] = control.value === "true";
    });
    if (value === "admin") {
      Object.keys(permissions).forEach((key) => permissions[key] = true);
    }
    return { value, label, permissions };
  });
}

function fillAdminUserForm(username) {
  const user = (adminState.users || []).find((item) => item.username === username);
  if (!user) return;
  document.querySelector('[name="adminUserUsername"]').value = user.username || "";
  document.querySelector('[name="adminUserDisplay"]').value = user.display_name || "";
  document.querySelector('[name="adminUserEmail"]').value = user.email || "";
  document.querySelector('[name="adminUserRole"]').value = user.role || "viewer";
  document.querySelector('[name="adminUserStatus"]').value = user.status || "active";
  document.querySelector('[name="adminUserPassword"]').value = "";
}

async function saveAdminUser() {
  const payload = {
    username: document.querySelector('[name="adminUserUsername"]')?.value.trim(),
    display_name: document.querySelector('[name="adminUserDisplay"]')?.value.trim(),
    email: document.querySelector('[name="adminUserEmail"]')?.value.trim(),
    role: document.querySelector('[name="adminUserRole"]')?.value,
    status: document.querySelector('[name="adminUserStatus"]')?.value,
    password: document.querySelector('[name="adminUserPassword"]')?.value,
  };
  try {
    const response = await adminRequest("/api/admin/users", { method: "POST", body: JSON.stringify(payload) });
    adminState.users = response.users || [];
    showToast("账号已保存");
    renderAdminUsers();
  } catch (error) {
    showToast(error.message);
  }
}

async function saveAdminRoles() {
  try {
    const response = await adminRequest("/api/admin/roles", { method: "POST", body: JSON.stringify({ roles: collectAdminRoles() }) });
    adminState.roles = response.roles || [];
    showToast("角色权限已保存");
    renderAdminRoles();
    renderAdminUsers();
  } catch (error) {
    showToast(error.message);
  }
}

async function saveAdminConfig() {
  const host = document.querySelector('[data-admin-panel="config"]');
  const payload = {};
  host.querySelectorAll("[name]").forEach((control) => {
    let value = control.value;
    if (control.type === "number") value = Number(value);
    if (control.name === "save_source_pdf") value = value === "true";
    payload[control.name] = value;
  });
  try {
    const response = await adminRequest("/api/admin/config", { method: "POST", body: JSON.stringify(payload) });
    adminState.config = response.config || {};
    showToast("配置已保存");
    renderAdminConfig();
  } catch (error) {
    showToast(error.message);
  }
}

function collectAiModelForm() {
  const host = document.querySelector('[data-admin-panel="aiModels"]');
  return {
    id: host?.querySelector('[name="aiModelId"]')?.value || newClientId(),
    name: host?.querySelector('[name="aiModelName"]')?.value.trim() || "未命名模型",
    api_type: host?.querySelector('[name="aiModelApiType"]')?.value || "openai-compatible",
    base_url: host?.querySelector('[name="aiModelBaseUrl"]')?.value.trim() || "",
    api_key: host?.querySelector('[name="aiModelApiKey"]')?.value || "",
    model: host?.querySelector('[name="aiModelModel"]')?.value.trim() || "",
    timeout_seconds: Number(host?.querySelector('[name="aiModelTimeout"]')?.value || 60),
    temperature: Number(host?.querySelector('[name="aiModelTemperature"]')?.value || 0),
    retry_count: Number(host?.querySelector('[name="aiModelRetry"]')?.value || 2),
    enabled: host?.querySelector('[name="aiModelEnabled"]')?.value !== "false",
    is_default: host?.querySelector('[name="aiModelDefault"]')?.value === "true",
  };
}

function aiModelsWithCurrentForm() {
  const current = collectAiModelForm();
  const others = (adminState.aiModels.models || []).filter((item) => item.id !== current.id);
  const models = [...others, current];
  if (current.is_default || !adminState.aiModels.default_model_id) {
    models.forEach((item) => item.is_default = item.id === current.id);
    adminState.aiModels.default_model_id = current.id;
  }
  return models;
}

async function saveAiModels() {
  const models = aiModelsWithCurrentForm();
  const defaultModel = models.find((item) => item.is_default) || models.find((item) => item.enabled !== false) || models[0];
  try {
    const response = await adminRequest("/api/admin/ai-models", {
      method: "POST",
      body: JSON.stringify({ models, default_model_id: defaultModel?.id || "" }),
    });
    adminState.aiModels = { models: response.models || [], default_model_id: response.default_model_id || "" };
    adminState.selectedAiModelId = response.default_model_id || defaultModel?.id || "";
    adminState.aiModelTestResult = null;
    showToast("模型配置已保存");
    renderAdminAiModels();
    renderAdminOverview();
  } catch (error) {
    showToast(error.message);
  }
}

async function testAiModel() {
  const model = collectAiModelForm();
  adminState.aiModelTestResult = null;
  renderAdminAiModels();
  try {
    adminState.aiModelTestResult = await adminRequest("/api/admin/ai-models/test", { method: "POST", body: JSON.stringify({ model }) });
  } catch (error) {
    adminState.aiModelTestResult = { ok: false, error: error.message };
  }
  renderAdminAiModels();
}

async function resetTranslations() {
  if (!window.confirm("确认清空全部日报译文、错误和翻译进度？原始日报不会删除。")) return;
  try {
    const result = await adminRequest("/api/admin/translations/reset", { method: "POST", body: "{}" });
    showToast(`已清空译文，重置 ${result.reset_records || 0} 条日报`);
    await loadAdminData();
  } catch (error) {
    showToast(error.message);
  }
}

async function queueTranslations(mode = "continue", recordIds = null) {
  const countText = Array.isArray(recordIds) ? `${recordIds.length} 条选中日报` : "全部待处理日报";
  const actionText = mode === "overwrite" ? "清除现有译文并覆盖重译" : "继续翻译";
  if (!window.confirm(`确认对 ${countText}${actionText}？这会调用当前默认模型。`)) return;
  try {
    const body = { mode };
    if (Array.isArray(recordIds)) body.record_ids = recordIds;
    const result = await adminRequest("/api/admin/translations/queue", { method: "POST", body: JSON.stringify(body) });
    showToast(`已加入翻译队列：${result.queued_records || 0} 条${result.skipped_records ? `，跳过 ${result.skipped_records} 条` : ""}`);
    closeAdminModal();
    await loadAdminData();
  } catch (error) {
    showToast(error.message);
  }
}

async function openTranslationQueue() {
  try {
    adminState.translationQueue = await adminRequest("/api/admin/translations");
    const records = (adminState.translationQueue.records || []).filter((record) => record.needs_translation || ["QUEUED", "IN_PROGRESS"].includes(record.status));
    openAdminModal(
      `待翻译日报（${adminState.translationQueue.pending_count || 0}）`,
      `<div class="translation-queue-toolbar"><label><input type="checkbox" data-translation-queue-select-all checked />全选待处理日报</label><span>继续翻译会跳过已完成的当前版本；覆盖重译会先删除选中日报的现有译文。</span></div>
      <div class="table-wrap translation-queue-table-wrap"><table class="record-table admin-table translation-queue-table">
        <thead><tr><th>选择</th><th>类型</th><th>日期 / 报告号</th><th>井号</th><th>队伍</th><th>状态</th><th>待处理原因</th></tr></thead>
        <tbody>${records.map(translationQueueRowMarkup).join("") || `<tr><td colspan="7">当前没有待翻译日报</td></tr>`}</tbody>
      </table></div>`,
      `<button class="button secondary" type="button" data-admin-modal-close>取消</button>
       <button class="button secondary" type="button" data-admin-queue-selected="overwrite" ${records.length ? "" : "disabled"}>覆盖重译选中</button>
       <button class="button" type="button" data-admin-queue-selected="continue" ${records.length ? "" : "disabled"}>继续翻译选中</button>`
    );
  } catch (error) {
    showToast(error.message);
  }
}

function translationQueueRowMarkup(record = {}) {
  const processing = ["QUEUED", "IN_PROGRESS"].includes(record.status);
  return `<tr>
    <td><input type="checkbox" name="translationQueueRecord" value="${escapeHtml(record.record_id)}" ${record.needs_translation && !processing ? "checked" : ""} ${processing ? "disabled" : ""} /></td>
    <td><strong>${escapeHtml(record.report_type_label || record.report_type)}</strong></td>
    <td>${escapeHtml(record.report_date || "-")}<small class="table-subtext">${escapeHtml(record.report_no || "-")}</small></td>
    <td>${escapeHtml(record.wellbore || "-")}</td><td>${escapeHtml(record.rig || "-")}</td>
    <td><span class="status-pill ${record.status === "FAILED" ? "failed" : record.status === "COMPLETED" ? "uploaded" : "pending"}">${escapeHtml(translationQueueStatusLabel(record.status))}${record.progress ? ` ${escapeHtml(record.progress)}%` : ""}</span></td>
    <td>${escapeHtml(record.reason || "-")}</td>
  </tr>`;
}

function translationQueueStatusLabel(status = "") {
  return { PENDING: "待处理", FAILED: "失败", QUEUED: "已排队", IN_PROGRESS: "翻译中", COMPLETED: "已完成", NOT_REQUIRED: "无需翻译" }[status] || status || "待处理";
}

function selectedTranslationQueueIds() {
  return [...document.querySelectorAll('[name="translationQueueRecord"]:checked')].map((input) => input.value);
}

function queueSelectedTranslations(mode) {
  const recordIds = selectedTranslationQueueIds();
  if (!recordIds.length) return showToast("请至少选择一条日报");
  return queueTranslations(mode, recordIds);
}

function newAiModel() {
  const model = emptyAiModel();
  adminState.aiModels.models = [...(adminState.aiModels.models || []), model];
  adminState.selectedAiModelId = model.id;
  adminState.aiModelTestResult = null;
  renderAdminAiModels();
}

function deleteSelectedAiModel() {
  const id = collectAiModelForm().id;
  adminState.aiModels.models = (adminState.aiModels.models || []).filter((item) => item.id !== id);
  if (adminState.aiModels.default_model_id === id) {
    adminState.aiModels.default_model_id = adminState.aiModels.models.find((item) => item.enabled !== false)?.id || adminState.aiModels.models[0]?.id || "";
  }
  adminState.selectedAiModelId = adminState.aiModels.default_model_id || adminState.aiModels.models[0]?.id || "";
  adminState.aiModelTestResult = null;
  renderAdminAiModels();
}

async function saveProjectTeamConfig(message = "业务配置已保存") {
  const response = await adminRequest("/api/admin/project-teams", { method: "POST", body: JSON.stringify(adminState.projectTeams || {}) });
  adminState.projectTeams = { teams: response.teams || [], projects: response.projects || [], pending_wells: response.pending_wells || [] };
  showToast(message);
  renderAdminProjects();
  renderAdminOverview();
}

function parseAliasList(value) {
  return [...new Set(String(value || "").split(/[\n,，;；]+/).map((item) => item.trim()).filter(Boolean))];
}

function captureTranslationTuningForm() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host || adminState.translationTuningView !== "fields") return adminState.translationTuning;
  const current = adminState.translationTuning || {};
  const scopeRules = (current.scope_rules || []).map((rule) => {
    const row = host.querySelector(`[data-translation-scope-rule="${CSS.escape(rule.id)}"]`);
    return { ...rule, enabled: row?.querySelector('[name="translationPolicyEnabled"]')?.checked ?? rule.enabled !== false };
  });
  const targetLanguages = [...host.querySelectorAll('[name="translationTargetLanguage"]:checked')].map((input) => input.value);
  const protectionInputs = [...host.querySelectorAll('[name="translationProtection"]')];
  const protections = Object.fromEntries(protectionInputs.map((input) => [input.value, input.checked]));
  adminState.translationTuning = {
    ...current,
    scope_rules: scopeRules,
    target_languages: targetLanguages.length ? targetLanguages : ["zh-CN"],
    prompt: {
      system_prompt: host.querySelector('[name="translationSystemPrompt"]')?.value.trim() || "",
      translation_instruction: host.querySelector('[name="translationInstruction"]')?.value.trim() || "",
    },
    protections,
  };
  return adminState.translationTuning;
}

function scopeCatalogSelection(reportType, sectionValue = "", fieldValue = "") {
  const catalog = adminState.translationTuning?.scope_catalog?.report_types || [];
  const report = catalog.find((item) => item.value === reportType) || catalog[0] || { sections: [] };
  const section = (report.sections || []).find((item) => item.value === sectionValue) || report.sections?.[0] || { fields: [] };
  const field = (section.fields || []).find((item) => item.value === fieldValue) || section.fields?.[0] || {};
  return { report, section, field };
}

function refreshTranslationScopeBuilder(changedName = "") {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host) return;
  const reportType = host.querySelector('[name="translationScopeReportType"]')?.value || adminState.translationScopeDraft.report_type;
  const requestedSection = changedName === "translationScopeReportType" ? "" : host.querySelector('[name="translationScopeSection"]')?.value || "";
  const requestedField = changedName === "translationScopeField" ? host.querySelector('[name="translationScopeField"]')?.value || "" : "";
  const { report, section, field } = scopeCatalogSelection(reportType, requestedSection, requestedField);
  adminState.translationScopeDraft = { report_type: report.value || "", section: section.value || "", field_name: field.value || "" };
  captureTranslationTuningForm();
  renderAdminTranslationTuning();
}

function addTranslationScope() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host) return;
  captureTranslationTuningForm();
  const reportType = host.querySelector('[name="translationScopeReportType"]')?.value || "";
  const sectionValue = host.querySelector('[name="translationScopeSection"]')?.value || "";
  const fieldValue = host.querySelector('[name="translationScopeField"]')?.value || "";
  const { report, section, field } = scopeCatalogSelection(reportType, sectionValue, fieldValue);
  if (!report.value || !section.value || !field.value) return showToast("请选择完整的翻译范围");
  const id = `${report.value}:${section.value}:${field.value}`;
  const rules = adminState.translationTuning.scope_rules || [];
  if (rules.some((rule) => rule.report_type === report.value && rule.section === section.value && rule.field_name === field.value)) return showToast("该翻译范围已存在");
  rules.push({ id, report_type: report.value, report_type_label: report.label, section: section.value, section_label: section.label, field_name: field.value, field_code: `${section.value}.${field.value}`, label: field.label, enabled: true });
  adminState.translationTuning.scope_rules = rules;
  renderAdminTranslationTuning();
}

function removeTranslationScope(id) {
  captureTranslationTuningForm();
  adminState.translationTuning.scope_rules = (adminState.translationTuning.scope_rules || []).filter((rule) => rule.id !== id);
  renderAdminTranslationTuning();
}

function captureProtectedTerms() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host || adminState.translationTuningView !== "terms") return adminState.translationTerms?.protected_terms || {};
  return {
    acronyms: parseAliasList(host.querySelector('[name="protectedAcronyms"]')?.value || ""),
    units: parseAliasList(host.querySelector('[name="protectedUnits"]')?.value || ""),
    proper_nouns: parseAliasList(host.querySelector('[name="protectedProperNouns"]')?.value || ""),
  };
}

function addTranslationTerm() {
  openTranslationTermModal();
}

function openTranslationTermModal(id = "") {
  const existing = (adminState.translationTerms?.terms || []).find((term) => term.id === id);
  const term = existing || { id: "", category: "general", zh: "", en: "", es: "", aliases: { zh: [], en: [], es: [] }, protected: true, enabled: true };
  const aliases = term.aliases || {};
  openAdminModal(
    existing ? "编辑术语" : "新增术语",
    `<div class="translation-term-modal-form">
      <input type="hidden" name="termModalId" value="${escapeHtml(term.id)}" />
      <label>作业类型<select name="termModalCategory">${translationTermCategoryOptions(term.category || "general")}</select></label>
      <label>中文<input name="termModalZh" value="${escapeHtml(term.zh || "")}" /></label>
      <label>English<input name="termModalEn" value="${escapeHtml(term.en || "")}" /></label>
      <label>Español<input name="termModalEs" value="${escapeHtml(term.es || "")}" /></label>
      <label>中文别名<textarea name="termModalAliasesZh" rows="3">${escapeHtml(aliasInputValue(aliases.zh))}</textarea></label>
      <label>英文别名<textarea name="termModalAliasesEn" rows="3">${escapeHtml(aliasInputValue(aliases.en))}</textarea></label>
      <label>西语别名<textarea name="termModalAliasesEs" rows="3">${escapeHtml(aliasInputValue(aliases.es))}</textarea></label>
      <div class="tuning-term-switches"><label><input type="checkbox" name="termModalEnabled" ${term.enabled !== false ? "checked" : ""} />启用</label><label><input type="checkbox" name="termModalProtected" ${term.protected !== false ? "checked" : ""} />锁定译法</label></div>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button" type="button" data-admin-save-translation-term-modal>保存术语</button>`
  );
}

function saveTranslationTermModal() {
  const modal = document.querySelector(".admin-modal");
  const id = modal?.querySelector('[name="termModalId"]')?.value || "";
  const zh = modal?.querySelector('[name="termModalZh"]')?.value.trim() || "";
  const en = modal?.querySelector('[name="termModalEn"]')?.value.trim() || "";
  const es = modal?.querySelector('[name="termModalEs"]')?.value.trim() || "";
  if (sumTruthy([zh, en, es]) < 2) return showToast("每条术语至少填写两种语言");
  const terms = adminState.translationTerms?.terms || [];
  let term = terms.find((item) => item.id === id);
  if (!term) {
    term = { id: newClientId() };
    terms.push(term);
  }
  term.category = modal.querySelector('[name="termModalCategory"]')?.value || "general";
  term.zh = zh;
  term.en = en;
  term.es = es;
  term.aliases = {
    zh: parseAliasList(modal.querySelector('[name="termModalAliasesZh"]')?.value || ""),
    en: parseAliasList(modal.querySelector('[name="termModalAliasesEn"]')?.value || ""),
    es: parseAliasList(modal.querySelector('[name="termModalAliasesEs"]')?.value || ""),
  };
  term.enabled = modal.querySelector('[name="termModalEnabled"]')?.checked ?? true;
  term.protected = modal.querySelector('[name="termModalProtected"]')?.checked ?? true;
  term.updated_at = new Date().toISOString().slice(0, 19);
  adminState.translationTerms.terms = terms;
  closeAdminModal();
  return saveTranslationTerms();
}

function sumTruthy(values = []) {
  return values.reduce((sum, value) => sum + (value ? 1 : 0), 0);
}

async function saveTranslationTerms() {
  const payload = {
    terms: (adminState.translationTerms?.terms || []).filter((term) => term.zh || term.en || term.es),
    protected_terms: captureProtectedTerms(),
  };
  try {
    const response = await adminRequest("/api/admin/translation-terms", { method: "POST", body: JSON.stringify(payload) });
    adminState.translationTerms = { terms: response.terms || [], protected_terms: response.protected_terms || {} };
    showToast("术语词库已保存");
    renderAdminTranslationTuning();
    renderAdminOverview();
  } catch (error) {
    showToast(error.message);
  }
}

function chooseTranslationTermWorkbook() {
  document.querySelector("[data-translation-term-file]")?.click();
}

async function importTranslationTermWorkbook(file) {
  if (!file) return;
  const allowed = /\.(xlsx|xlsm|xltx|xltm|xls)$/i.test(file.name || "");
  if (!allowed) return showToast("仅支持 Excel 文件");
  adminState.translationTermImport = { running: true, result: null, duplicates: [] };
  renderAdminTranslationTuning();
  const form = new FormData();
  form.append("workbook", file);
  try {
    const result = await adminRequest("/api/admin/translation-terms/import", { method: "POST", body: form });
    adminState.translationTerms = { terms: result.terms || [], protected_terms: result.protected_terms || {} };
    adminState.translationTermImport = { running: false, result, duplicates: result.duplicates || [] };
    adminState.translationTermSearch = "";
    adminState.translationTermCategory = "all";
    adminState.translationTermPage = Math.max(1, Math.ceil(adminState.translationTerms.terms.length / adminState.translationTermPageSize));
    showToast(`已导入 ${result.imported_count || 0} 条术语，跳过 ${result.duplicate_count || 0} 条重复项`);
  } catch (error) {
    adminState.translationTermImport = { running: false, result: null, duplicates: [] };
    showToast(error.message);
  }
  renderAdminTranslationTuning();
}

function openTranslationTermDuplicateReview() {
  const duplicates = adminState.translationTermImport?.duplicates || [];
  if (!duplicates.length) return showToast("没有需要处理的重复术语");
  openAdminModal(
    `重复术语复核（${duplicates.length}）`,
    `<div class="duplicate-review-note">重复项已跳过，不会自动改写现有译法。勾选后才会使用 Excel 识别结果覆盖对应语言。</div>
    <div class="term-duplicate-list">${duplicates.map(translationTermDuplicateMarkup).join("")}</div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>保留全部现有术语</button><button class="button" type="button" data-admin-resolve-term-duplicates>覆盖选中项</button>`
  );
}

function translationTermDuplicateMarkup(item = {}) {
  const existing = item.existing || {};
  const candidate = item.candidate || {};
  return `<section class="term-duplicate-item">
    <label class="duplicate-choice"><input type="checkbox" name="translationTermDuplicate" value="${escapeHtml(item.id)}" /><span>使用导入译法</span></label>
    <div class="term-duplicate-compare"><div><strong>现有术语</strong>${termLanguageLines(existing)}</div><div><strong>Excel 识别</strong>${termLanguageLines(candidate)}</div></div>
    <p>${escapeHtml(item.suggestion || "请核对后决定是否覆盖。")}</p>
  </section>`;
}

function termLanguageLines(term = {}) {
  return `<span>中文：${escapeHtml(term.zh || "-")}</span><span>English：${escapeHtml(term.en || "-")}</span><span>Español：${escapeHtml(term.es || "-")}</span>`;
}

async function resolveTranslationTermDuplicates() {
  const selected = new Set([...document.querySelectorAll('[name="translationTermDuplicate"]:checked')].map((input) => input.value));
  if (!selected.size) return showToast("请勾选需要覆盖的重复术语");
  const duplicates = adminState.translationTermImport?.duplicates || [];
  const replacements = duplicates.filter((item) => selected.has(item.id)).map((item) => ({ existing_id: item.existing_id, candidate: item.candidate }));
  try {
    const result = await adminRequest("/api/admin/translation-terms/import/resolve", { method: "POST", body: JSON.stringify({ replacements }) });
    adminState.translationTerms = { terms: result.terms || [], protected_terms: result.protected_terms || {} };
    adminState.translationTermImport.duplicates = duplicates.filter((item) => !selected.has(item.id));
    if (adminState.translationTermImport.result) adminState.translationTermImport.result.duplicate_count = adminState.translationTermImport.duplicates.length;
    closeAdminModal();
    renderAdminTranslationTuning();
    showToast(`已覆盖 ${result.updated_count || 0} 条术语`);
  } catch (error) {
    showToast(error.message);
  }
}

async function saveTranslationTuning() {
  const payload = captureTranslationTuningForm();
  try {
    const response = await adminRequest("/api/admin/translation-tuning", { method: "POST", body: JSON.stringify(payload) });
    adminState.translationTuning = response;
    showToast("翻译策略已保存");
    renderAdminTranslationTuning();
  } catch (error) {
    showToast(error.message);
  }
}

function captureAiExtractionRuleForm() {
  const host = document.querySelector('[data-admin-panel="aiExtraction"]');
  if (!host) return null;
  return {
    id: host.querySelector('[name="aiExtractionRuleId"]')?.value || newClientId(),
    name: host.querySelector('[name="aiExtractionRuleName"]')?.value.trim() || "未命名提炼规则",
    report_type: host.querySelector('[name="aiExtractionReportType"]')?.value || "drilling",
    source_section: host.querySelector('[name="aiExtractionSourceSection"]')?.value || "report_fields",
    source_field: host.querySelector('[name="aiExtractionSourceField"]')?.value || "currentOps",
    condition: host.querySelector('[name="aiExtractionCondition"]')?.value.trim() || "",
    instruction: host.querySelector('[name="aiExtractionInstruction"]')?.value.trim() || "",
    target_field: host.querySelector('[name="aiExtractionTargetField"]')?.value || "remarks",
    output_format: host.querySelector('[name="aiExtractionOutputFormat"]')?.value || "text",
    model_id: host.querySelector('[name="aiExtractionModelId"]')?.value || "",
    enabled: host.querySelector('[name="aiExtractionEnabled"]')?.value === "true",
  };
}

function updateAiExtractionDraft() {
  const rule = captureAiExtractionRuleForm();
  if (!rule) return null;
  const rules = [...(adminState.aiExtraction.rules || [])];
  const index = rules.findIndex((item) => item.id === rule.id);
  if (index >= 0) rules[index] = rule;
  else rules.push(rule);
  adminState.aiExtraction.rules = rules;
  adminState.selectedAiExtractionRuleId = rule.id;
  return rule;
}

async function saveAiExtractionRules() {
  const rule = updateAiExtractionDraft();
  if (!rule?.instruction) return showToast("请填写提炼要求");
  try {
    const autoExecute = document.querySelector('[name="aiExtractionAutoExecute"]')?.checked ?? adminState.aiExtraction.auto_execute !== false;
    const response = await adminRequest("/api/admin/ai-extraction-rules", { method: "POST", body: JSON.stringify({ rules: adminState.aiExtraction.rules, auto_execute: autoExecute }) });
    adminState.aiExtraction = response;
    adminState.aiExtractionQueue = await adminRequest("/api/admin/ai-extractions");
    adminState.selectedAiExtractionRuleId = rule.id;
    renderAdminAiExtraction();
    showToast("AI提炼规则已保存");
  } catch (error) {
    showToast(error.message);
  }
}

async function queueAiExtractions(mode = "continue") {
  const recordIds = [...document.querySelectorAll("[data-ai-extraction-record]:checked")].map((input) => input.value);
  if (!recordIds.length) return showToast("请至少选择一条日报");
  const action = mode === "overwrite" ? "按当前规则覆盖提炼" : "执行待处理提炼";
  if (!window.confirm(`确认对 ${recordIds.length} 条日报${action}？`)) return;
  try {
    const result = await adminRequest("/api/admin/ai-extractions/queue", { method: "POST", body: JSON.stringify({ mode, record_ids: recordIds }) });
    showToast(`已加入提炼队列：${result.queued_records || 0} 条`);
    adminState.aiExtractionQueue = await adminRequest("/api/admin/ai-extractions");
    renderAdminAiExtraction();
  } catch (error) {
    showToast(error.message);
  }
}

function newAiExtractionRule() {
  updateAiExtractionDraft();
  const rule = emptyAiExtractionRule();
  adminState.aiExtraction.rules = [...(adminState.aiExtraction.rules || []), rule];
  adminState.selectedAiExtractionRuleId = rule.id;
  adminState.aiExtractionTestResult = null;
  renderAdminAiExtraction();
}

function editAiExtractionRule(id) {
  updateAiExtractionDraft();
  adminState.selectedAiExtractionRuleId = id;
  adminState.aiExtractionTestResult = null;
  renderAdminAiExtraction();
}

function deleteAiExtractionRule() {
  const id = document.querySelector('[name="aiExtractionRuleId"]')?.value || adminState.selectedAiExtractionRuleId;
  if (!id || !window.confirm("确认删除这条AI提炼规则？")) return;
  adminState.aiExtraction.rules = (adminState.aiExtraction.rules || []).filter((item) => item.id !== id);
  adminState.selectedAiExtractionRuleId = adminState.aiExtraction.rules[0]?.id || "";
  adminState.aiExtractionTestResult = null;
  renderAdminAiExtraction();
}

function refreshAiExtractionSource(changedName) {
  const rule = updateAiExtractionDraft();
  if (!rule) return;
  const catalog = adminState.aiExtraction.catalog || {};
  const report = (catalog.report_types || []).find((item) => item.value === rule.report_type) || catalog.report_types?.[0];
  if (changedName === "aiExtractionReportType") {
    rule.source_section = report?.sections?.[0]?.value || "report_fields";
    rule.source_field = report?.sections?.[0]?.fields?.[0]?.value || "event";
  } else if (changedName === "aiExtractionSourceSection") {
    const section = report?.sections?.find((item) => item.value === rule.source_section) || report?.sections?.[0];
    rule.source_field = section?.fields?.[0]?.value || "event";
  }
  const index = adminState.aiExtraction.rules.findIndex((item) => item.id === rule.id);
  if (index >= 0) adminState.aiExtraction.rules[index] = rule;
  renderAdminAiExtraction();
}

async function runAiExtractionTest() {
  const source = document.querySelector('[name="aiExtractionTestSource"]')?.value.trim() || "";
  const recordId = document.querySelector('[name="aiExtractionTestRecord"]')?.value || "";
  if (!source && !recordId) {
    adminState.aiExtractionTestResult = { ok: false, error: "没有匹配的已入库日报，请粘贴临时测试原文。" };
    return renderAdminAiExtraction();
  }
  const rule = updateAiExtractionDraft();
  if (!rule?.instruction) {
    adminState.aiExtractionTestResult = { ok: false, error: "请先填写提炼要求。" };
    return renderAdminAiExtraction();
  }
  adminState.aiExtractionTestRecordId = recordId;
  adminState.aiExtractionTestSource = source;
  adminState.aiExtractionTestRunning = true;
  adminState.aiExtractionTestResult = null;
  renderAdminAiExtraction();
  try {
    adminState.aiExtractionTestResult = await adminRequest("/api/admin/ai-extraction-rules/test", { method: "POST", body: JSON.stringify({ rule, record_id: recordId, source_text: source, model_id: rule.model_id || adminState.aiModels.default_model_id }) });
  } catch (error) {
    adminState.aiExtractionTestResult = { ok: false, error: error.message };
  } finally {
    adminState.aiExtractionTestRunning = false;
    renderAdminAiExtraction();
  }
}

function switchTranslationTuningView(view) {
  if (adminState.translationTuningView === "fields") captureTranslationTuningForm();
  if (adminState.translationTuningView === "terms") {
    adminState.translationTerms.protected_terms = captureProtectedTerms();
  }
  adminState.translationTuningView = view;
  renderAdminTranslationTuning();
}

async function runTranslationTuningTest() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  const sourceText = host?.querySelector('[name="translationTestSource"]')?.value.trim() || "";
  if (!sourceText) return showToast("请输入需要测试的日报文本");
  adminState.translationTestSource = sourceText;
  adminState.translationTestModelId = host.querySelector('[name="translationTestModel"]')?.value || adminState.aiModels.default_model_id;
  adminState.translationTestLanguage = host.querySelector('[name="translationTestLanguage"]')?.value || "zh-CN";
  adminState.translationTestFieldCode = host.querySelector('[name="translationTestField"]')?.value || "";
  adminState.translationTestRunning = true;
  adminState.translationTestResult = null;
  const payload = {
    source_text: sourceText,
    target_language: adminState.translationTestLanguage,
    model_id: adminState.translationTestModelId,
    field_code: adminState.translationTestFieldCode,
    tuning: adminState.translationTuning,
  };
  renderAdminTranslationTuning();
  try {
    adminState.translationTestResult = await adminRequest("/api/admin/translation-tuning/test", { method: "POST", body: JSON.stringify(payload) });
  } catch (error) {
    adminState.translationTestResult = { ok: false, error: error.message, checks: [{ label: "模型调用", status: "failed", detail: error.message }] };
  } finally {
    adminState.translationTestRunning = false;
    renderAdminTranslationTuning();
  }
}

function saveProjectContract() {
  const modal = document.querySelector(".admin-modal");
  const id = modal?.querySelector('[name="projectId"]')?.value || "";
  const contractNo = modal?.querySelector('[name="projectContractNo"]')?.value.trim() || "";
  const projectName = modal?.querySelector('[name="projectName"]')?.value.trim() || "";
  if (!contractNo && !projectName) return showToast("请填写合同号或项目名称");
  const projects = [...(adminState.projectTeams.projects || [])];
  let project = projects.find((item) => item.id === id);
  if (!project) {
    project = { id: newClientId(), rigs: [], created_at: new Date().toISOString().slice(0, 19) };
    projects.push(project);
  }
  project.contract_no = contractNo;
  project.project_name = projectName;
  project.status = modal?.querySelector('[name="projectStatus"]')?.value || "active";
  project.start_date = modal?.querySelector('[name="projectStartDate"]')?.value || "";
  project.end_date = modal?.querySelector('[name="projectEndDate"]')?.value || "";
  project.note = modal?.querySelector('[name="projectNote"]')?.value.trim() || "";
  const seenRigs = new Set();
  project.rigs = [...(modal?.querySelectorAll("[data-project-rig-row]") || [])].map((row) => {
    const rig = row.querySelector('[name="projectRigName"]')?.value.trim() || "";
    if (!rig || seenRigs.has(rig)) return null;
    seenRigs.add(rig);
    return {
      rig,
      start_date: row.querySelector('[name="projectRigStart"]')?.value || "",
      end_date: row.querySelector('[name="projectRigEnd"]')?.value || "",
      wells: parseWells(row.querySelector('[name="projectRigWells"]')?.value || ""),
      note: row.querySelector('[name="projectRigNote"]')?.value.trim() || "",
    };
  }).filter(Boolean);
  project.updated_at = new Date().toISOString().slice(0, 19);
  adminState.projectTeams.projects = projects;
  closeAdminModal();
  saveProjectTeamConfig("项目合同已保存");
}

function saveTeam() {
  const modal = document.querySelector(".admin-modal");
  const id = modal?.querySelector('[name="teamId"]')?.value || "";
  const originalName = modal?.querySelector('[name="teamOriginalName"]')?.value.trim() || "";
  const name = modal?.querySelector('[name="teamName"]')?.value.trim() || "";
  if (!name) return showToast("请填写队伍名称");
  const teams = [...(adminState.projectTeams.teams || [])];
  let team = teams.find((item) => item.id === id || item.name === name);
  if (!team) {
    team = { id: newClientId(), created_at: new Date().toISOString().slice(0, 19) };
    teams.push(team);
  }
  team.name = name;
  team.code = modal?.querySelector('[name="teamCode"]')?.value.trim() || "";
  team.contractor = modal?.querySelector('[name="teamContractor"]')?.value.trim() || "";
  const aliases = parseAliasList(modal?.querySelector('[name="teamAliases"]')?.value || "").filter((alias) => alias !== name);
  if (originalName && originalName !== name && !aliases.includes(originalName)) aliases.unshift(originalName);
  team.aliases = aliases;
  team.status = modal?.querySelector('[name="teamStatus"]')?.value || "active";
  adminState.projectTeams.teams = teams;
  if (originalName && originalName !== name) renameTeamReferences(originalName, name);
  closeAdminModal();
  saveProjectTeamConfig("队伍已保存");
}

function renameTeamReferences(originalName, newName) {
  (adminState.projectTeams.projects || []).forEach((project) => {
    (project.rigs || []).forEach((rig) => {
      if (rig.rig === originalName) rig.rig = newName;
    });
  });
  (adminState.projectTeams.pending_wells || []).forEach((item) => {
    if (item.rig === originalName) item.rig = newName;
  });
}

function parseWells(value) {
  return [...new Set(String(value || "").split(/[\s,，;；]+/).map((item) => item.trim()).filter(Boolean))].sort();
}

function fillProjectForm(id) {
  openProjectModal(id);
}

function fillTeamForm(id) {
  openTeamModal(id);
}

function assignPendingWell(index) {
  const host = document.querySelector('[data-admin-panel="projects"]');
  const projectId = host.querySelector(`[data-pending-project="${Number(index)}"]`)?.value || "";
  const pending = adminState.projectTeams.pending_wells?.[Number(index)];
  if (!projectId || !pending) return showToast("请先选择项目合同");
  const project = (adminState.projectTeams.projects || []).find((item) => item.id === projectId);
  if (!project) return showToast("项目不存在");
  project.rigs = project.rigs || [];
  let target = project.rigs.find((item) => item.rig === pending.rig);
  if (!target) {
    target = { rig: pending.rig, start_date: "", end_date: "", wells: [], note: "" };
    project.rigs.push(target);
  }
  if (!target.wells.includes(pending.wellbore)) target.wells.push(pending.wellbore);
  target.wells.sort();
  adminState.projectTeams.pending_wells.splice(Number(index), 1);
  saveProjectTeamConfig("待归集井号已归入项目");
}

function saveWellAssignment() {
  const modal = document.querySelector(".admin-modal");
  const originalProject = modal?.querySelector('[name="wellAssignmentOriginalProject"]')?.value || "";
  const originalRig = modal?.querySelector('[name="wellAssignmentOriginalRig"]')?.value || "";
  const originalWell = modal?.querySelector('[name="wellAssignmentOriginalWell"]')?.value || "";
  const kind = modal?.querySelector('[name="wellAssignmentKind"]')?.value || "";
  const pendingIndex = Number(modal?.querySelector('[name="wellAssignmentPendingIndex"]')?.value || -1);
  const projectId = modal?.querySelector('[name="wellAssignmentProject"]')?.value || "";
  const rig = modal?.querySelector('[name="wellAssignmentRig"]')?.value || "";
  const wellbore = modal?.querySelector('[name="wellAssignmentWell"]')?.value.trim() || "";
  if (!wellbore) return showToast("请填写井号");
  if (!rig) return showToast("请先选择队伍");

  removeWellAssignment(kind, originalProject, originalRig, originalWell, pendingIndex);
  if (projectId) {
    const project = (adminState.projectTeams.projects || []).find((item) => item.id === projectId);
    if (!project) return showToast("项目不存在");
    project.rigs = project.rigs || [];
    let target = project.rigs.find((item) => item.rig === rig);
    if (!target) {
      target = { rig, start_date: "", end_date: "", wells: [], note: "" };
      project.rigs.push(target);
    }
    target.wells = [...new Set([...(target.wells || []), wellbore])].sort();
    project.updated_at = new Date().toISOString().slice(0, 19);
  } else {
    adminState.projectTeams.pending_wells = adminState.projectTeams.pending_wells || [];
    if (!adminState.projectTeams.pending_wells.some((item) => item.rig === rig && item.wellbore === wellbore)) {
      adminState.projectTeams.pending_wells.push({ rig, wellbore, source: "manual", created_at: new Date().toISOString().slice(0, 19) });
    }
  }
  closeAdminModal();
  saveProjectTeamConfig("井号归属已保存");
}

function removeWellAssignment(kind, projectId, rig, wellbore, pendingIndex) {
  if (kind === "assigned") {
    const project = (adminState.projectTeams.projects || []).find((item) => item.id === projectId);
    const target = project?.rigs?.find((item) => item.rig === rig);
    if (target) target.wells = (target.wells || []).filter((well) => well !== wellbore);
  } else if (Number.isInteger(pendingIndex) && pendingIndex >= 0) {
    adminState.projectTeams.pending_wells?.splice(pendingIndex, 1);
  }
}

async function logoutAdmin() {
  await adminRequest("/api/admin/logout", { method: "POST", body: "{}" }).catch(() => {});
  window.location.href = "/login/?next=/admin/";
}

document.addEventListener("click", (event) => {
  const groupToggle = event.target.closest(".menu-group-toggle");
  if (groupToggle) {
    const group = groupToggle.closest(".menu-group");
    const expanded = !group.classList.contains("open");
    group.classList.toggle("open", expanded);
    groupToggle.setAttribute("aria-expanded", String(expanded));
    return;
  }
  const tab = event.target.closest("[data-admin-tab]");
  if (tab) {
    event.preventDefault();
    return switchAdminTab(tab.dataset.adminTab);
  }
  const logPageButton = event.target.closest("[data-admin-log-page]");
  if (logPageButton) {
    adminState.logsPage = Number(logPageButton.dataset.adminLogPage || 1);
    return renderAdminLogs();
  }
  const edit = event.target.closest("[data-admin-edit-user]");
  if (edit) return fillAdminUserForm(edit.dataset.adminEditUser);
  if (event.target.closest("[data-admin-modal-close]")) return closeAdminModal();
  if (event.target.closest("[data-admin-new-project]")) return openProjectModal();
  if (event.target.closest("[data-admin-new-team]")) return openTeamModal();
  if (event.target.closest("[data-admin-new-ai-model]")) return newAiModel();
  const editAiModel = event.target.closest("[data-admin-edit-ai-model]");
  if (editAiModel) {
    adminState.selectedAiModelId = editAiModel.dataset.adminEditAiModel;
    adminState.aiModelTestResult = null;
    return renderAdminAiModels();
  }
  if (event.target.closest("[data-admin-test-ai-model]")) return testAiModel();
  if (event.target.closest("[data-admin-save-ai-models]")) return saveAiModels();
  if (event.target.closest("[data-admin-delete-ai-model]")) return deleteSelectedAiModel();
  if (event.target.closest("[data-admin-new-extraction-rule]")) return newAiExtractionRule();
  const editExtraction = event.target.closest("[data-admin-edit-extraction-rule]");
  if (editExtraction) return editAiExtractionRule(editExtraction.dataset.adminEditExtractionRule);
  if (event.target.closest("[data-admin-save-extraction-rules]")) return saveAiExtractionRules();
  if (event.target.closest("[data-admin-delete-extraction-rule]")) return deleteAiExtractionRule();
  if (event.target.closest("[data-admin-test-extraction-rule]")) return runAiExtractionTest();
  const extractionView = event.target.closest("[data-ai-extraction-view]");
  if (extractionView) {
    adminState.aiExtractionView = extractionView.dataset.aiExtractionView || "rules";
    return renderAdminAiExtraction();
  }
  const queueExtraction = event.target.closest("[data-admin-queue-extractions]");
  if (queueExtraction) return queueAiExtractions(queueExtraction.dataset.adminQueueExtractions || "continue");
  if (event.target.closest("[data-admin-reset-translations]")) return resetTranslations();
  if (event.target.closest("[data-admin-queue-translations]")) return queueTranslations();
  if (event.target.closest("[data-admin-open-translation-queue]")) return openTranslationQueue();
  const queueSelected = event.target.closest("[data-admin-queue-selected]");
  if (queueSelected) return queueSelectedTranslations(queueSelected.dataset.adminQueueSelected);
  const tuningView = event.target.closest("[data-translation-tuning-view]");
  if (tuningView) return switchTranslationTuningView(tuningView.dataset.translationTuningView);
  if (event.target.closest("[data-admin-save-translation-tuning]")) return saveTranslationTuning();
  if (event.target.closest("[data-admin-add-translation-scope]")) return addTranslationScope();
  const removeScope = event.target.closest("[data-admin-remove-translation-scope]");
  if (removeScope) return removeTranslationScope(removeScope.dataset.adminRemoveTranslationScope);
  if (event.target.closest("[data-admin-run-translation-test]")) return runTranslationTuningTest();
  if (event.target.closest("[data-admin-import-translation-terms]")) return chooseTranslationTermWorkbook();
  if (event.target.closest("[data-admin-review-term-duplicates]")) return openTranslationTermDuplicateReview();
  if (event.target.closest("[data-admin-resolve-term-duplicates]")) return resolveTranslationTermDuplicates();
  if (event.target.closest("[data-admin-add-translation-term]")) return addTranslationTerm();
  if (event.target.closest("[data-admin-save-translation-term-modal]")) return saveTranslationTermModal();
  const termCategory = event.target.closest("[data-translation-term-category-value]");
  if (termCategory) {
    adminState.translationTermCategory = termCategory.dataset.translationTermCategoryValue || "all";
    adminState.translationTermPage = 1;
    return renderAdminTranslationTuning();
  }
  const termPage = event.target.closest("[data-translation-term-page]");
  if (termPage) {
    adminState.translationTermPage = Math.max(1, Number(termPage.dataset.translationTermPage || 1));
    return renderAdminTranslationTuning();
  }
  const editTranslationTerm = event.target.closest("[data-admin-edit-translation-term]");
  if (editTranslationTerm) {
    return openTranslationTermModal(editTranslationTerm.dataset.adminEditTranslationTerm);
  }
  const deleteTranslationTerm = event.target.closest("[data-admin-delete-translation-term]");
  if (deleteTranslationTerm) {
    if (!window.confirm("确认删除这条术语？")) return;
    const id = deleteTranslationTerm.dataset.adminDeleteTranslationTerm;
    adminState.translationTerms.terms = (adminState.translationTerms.terms || []).filter((term) => term.id !== id);
    return saveTranslationTerms();
  }
  const addProjectRig = event.target.closest("[data-admin-add-project-rig]");
  if (addProjectRig) {
    const list = document.querySelector("[data-project-rig-list]");
    if (list) list.insertAdjacentHTML("beforeend", projectRigRow({}, list.children.length));
    return;
  }
  const removeProjectRig = event.target.closest("[data-admin-remove-project-rig]");
  if (removeProjectRig) {
    const list = removeProjectRig.closest("[data-project-rig-list]");
    removeProjectRig.closest("[data-project-rig-row]")?.remove();
    if (list && !list.children.length) list.insertAdjacentHTML("beforeend", projectRigRow({}, 0));
    return;
  }
  const editProject = event.target.closest("[data-admin-edit-project]");
  if (editProject) return fillProjectForm(editProject.dataset.adminEditProject);
  const editTeam = event.target.closest("[data-admin-edit-team]");
  if (editTeam) return fillTeamForm(editTeam.dataset.adminEditTeam);
  const editWellAssignment = event.target.closest("[data-admin-edit-well-assignment]");
  if (editWellAssignment) return openWellAssignmentModal(editWellAssignment.dataset.adminEditWellAssignment);
  const assignPending = event.target.closest("[data-admin-assign-pending]");
  if (assignPending) return assignPendingWell(assignPending.dataset.adminAssignPending);
  if (event.target.closest("[data-admin-save-user]")) return saveAdminUser();
  if (event.target.closest("[data-admin-add-role]")) return addAdminRole();
  if (event.target.closest("[data-admin-save-roles]")) return saveAdminRoles();
  if (event.target.closest("[data-admin-save-project-modal]")) return saveProjectContract();
  if (event.target.closest("[data-admin-save-team-modal]")) return saveTeam();
  if (event.target.closest("[data-admin-save-well-assignment]")) return saveWellAssignment();
  if (event.target.closest("[data-admin-save-config]")) return saveAdminConfig();
  if (event.target.closest("[data-admin-save-translation-terms]")) return saveTranslationTerms();
  if (event.target.closest("[data-admin-logout]")) return logoutAdmin();
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-admin-log-page-size]")) {
    adminState.logsPageSize = Number(event.target.value || 20);
    adminState.logsPage = 1;
    renderAdminLogs();
  }
  if (event.target.matches('[name="translationPolicyEnabled"]')) {
    const label = event.target.closest("label")?.querySelector("span");
    if (label) label.textContent = event.target.checked ? "启用" : "停用";
  }
  if (event.target.matches('[name="translationScopeReportType"], [name="translationScopeSection"], [name="translationScopeField"]')) {
    return refreshTranslationScopeBuilder(event.target.name);
  }
  if (event.target.matches('[name="aiExtractionReportType"], [name="aiExtractionSourceSection"]')) {
    return refreshAiExtractionSource(event.target.name);
  }
  if (event.target.matches('[name="aiExtractionTestRecord"]')) {
    adminState.aiExtractionTestRecordId = event.target.value || "";
    adminState.aiExtractionTestResult = null;
  }
  if (event.target.matches("[data-ai-extraction-check-all]")) {
    document.querySelectorAll("[data-ai-extraction-record]:not(:disabled)").forEach((input) => { input.checked = event.target.checked; });
  }
  if (event.target.matches("[data-translation-term-file]")) {
    const file = event.target.files?.[0];
    event.target.value = "";
    return importTranslationTermWorkbook(file);
  }
  if (event.target.matches("[data-translation-queue-select-all]")) {
    document.querySelectorAll('[name="translationQueueRecord"]:not(:disabled)').forEach((input) => { input.checked = event.target.checked; });
  }
  if (event.target.matches("[data-translation-term-page-size]")) {
    adminState.translationTermPageSize = Number(event.target.value || 10);
    adminState.translationTermPage = 1;
    return renderAdminTranslationTuning();
  }
});

document.addEventListener("input", (event) => {
  if (event.target.matches("[data-translation-term-search]")) {
    adminState.translationTerms.protected_terms = captureProtectedTerms();
    adminState.translationTermSearch = event.target.value;
    adminState.translationTermPage = 1;
    renderAdminTranslationTuning();
    const search = document.querySelector("[data-translation-term-search]");
    search?.focus();
    if (search) search.setSelectionRange(search.value.length, search.value.length);
  }
});

document.addEventListener("keydown", (event) => {
  if (["Enter", " "].includes(event.key) && event.target.matches("[data-admin-open-translation-queue]")) {
    event.preventDefault();
    return openTranslationQueue();
  }
  if (event.key === "Escape") closeAdminModal();
});

loadAdminSession();
