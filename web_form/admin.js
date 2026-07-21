const toast = document.querySelector("#toast");
const ADMIN_DEFAULT_PAGE_SIZE = 20;
const ADMIN_QUEUE_POLL_INTERVAL_MS = 3000;
let adminQueuePollTimer = null;
let adminQueuePollRunning = false;
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
  aiJobMonitor: { translation: [], extraction: [], updatedAt: { translation: "", extraction: "" } },
  aiExtractionView: "rules",
  aiExtractionQueuePage: 1,
  aiExtractionQueuePageSize: ADMIN_DEFAULT_PAGE_SIZE,
  aiExtractionQueueStatusTab: "pending",
  selectedAiExtractionRuleId: "",
  aiExtractionTestRecordId: "",
  aiExtractionTestSource: "",
  aiExtractionTestResult: null,
  aiExtractionTestRunning: false,
  selectedAiModelId: "",
  aiModelTestResult: null,
  governance: {
    regions: [], companies: [], fields: [], blocks: [], teams: [], drillingRigs: [], workoverRigs: [], rigs: [], wells: [],
    contracts: [], projects: [], aliases: [], appendixCategories: [], appendixValues: [],
    assignments: [], wellAssignments: [], issues: [], classifications: [], rules: [], snapshot: null,
    masterEntity: "regions", masterView: "entities", appendixCategoryId: "", standardizationView: "pending"
  },
  translationTerms: { terms: [], protected_terms: {} },
  translationTuning: { scope_rules: [], scope_catalog: { report_types: [] }, target_languages: ["zh-CN"], prompt: {}, protections: {} },
  translationTuningView: "fields",
  translationScopeDraft: { report_type: "drilling", section: "report_fields", field_name: "currentOps" },
  translationScopePage: 1,
  translationScopePageSize: ADMIN_DEFAULT_PAGE_SIZE,
  translationTermImport: { running: false, result: null, duplicates: [] },
  translationTermCategory: "all",
  translationTermPage: 1,
  translationTermPageSize: ADMIN_DEFAULT_PAGE_SIZE,
  translationQueue: { records: [], pending_count: 0, processing_count: 0, current_version: "" },
  translationQueuePage: 1,
  translationQueuePageSize: ADMIN_DEFAULT_PAGE_SIZE,
  translationQueueStatusTab: "pending",
  translationTestResult: null,
  translationTestRunning: false,
  translationTestSource: "05:30-07:30, BAJA BHA #5 DIRECCIONAL HASTA 4125 ft. PERFORA DE 4125 ft A 4140 ft CON ROP 90 ft/hr, WOB 18 klb Y SPP 12.5 MPa.",
  translationTestModelId: "",
  translationTestLanguage: "zh-CN",
  translationTestFieldCode: "",
  translationTermSearch: "",
  translationMemory: { entries: [], count: 0, loading: false },
  translationExperience: { suggestions: [], counts: {}, loading: false },
  translationReview: { record_id: "", rows: [], loading: false },
  dataStatus: null,
  records: [],
  logs: [],
  logsPage: 1,
  logsPageSize: ADMIN_DEFAULT_PAGE_SIZE
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
  return window.NexoHttp.requestJson(path, options, "后台请求失败");
}

async function optionalAdminRequest(path) {
  try { return await adminRequest(path); }
  catch (error) { console.warn(`可选后台能力未启用：${path}`, error); return { items: [] }; }
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
    const [users, config, aiModels, aiExtraction, aiExtractionQueue, translationTerms, translationTuning, translationExperience, translationQueue, dataStatus, records, logs,
      masterRegions, masterCompanies, masterFields, masterBlocks, masterTeams, masterDrillingRigs, masterWorkoverRigs, masterWells,
      masterContracts, masterProjects, masterAliases, appendixCategories, appendixValues,
      assignments, wellAssignments, qualityIssues, classifications, classificationRules] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/ai-models"),
      adminRequest("/api/admin/ai-extraction-rules"),
      adminRequest("/api/admin/ai-extractions"),
      adminRequest("/api/admin/translation-terms"),
      adminRequest("/api/admin/translation-tuning"),
      adminRequest("/api/admin/translation-experience?limit=200"),
      adminRequest("/api/admin/translations"),
      adminRequest("/api/admin/data-status"),
      adminRequest("/api/records"),
      adminRequest("/api/admin/audit-logs"),
      optionalAdminRequest("/api/admin/master-data/regions?limit=500"),
      optionalAdminRequest("/api/admin/master-data/companies?limit=500"),
      optionalAdminRequest("/api/admin/master-data/fields?limit=500"),
      optionalAdminRequest("/api/admin/master-data/blocks?limit=500"),
      optionalAdminRequest("/api/admin/master-data/teams?limit=500"),
      optionalAdminRequest("/api/admin/master-data/drilling-rigs?limit=500"),
      optionalAdminRequest("/api/admin/master-data/workover-rigs?limit=500"),
      optionalAdminRequest("/api/admin/master-data/wells?limit=1000"),
      optionalAdminRequest("/api/admin/master-data/contracts?limit=500"),
      optionalAdminRequest("/api/admin/master-data/projects?limit=500"),
      optionalAdminRequest("/api/admin/master-data/aliases?limit=1000"),
      optionalAdminRequest("/api/admin/master-data/appendix-categories?limit=500"),
      optionalAdminRequest("/api/admin/master-data/appendix-values?limit=2000"),
      optionalAdminRequest("/api/admin/assignments?kind=project-team"),
      optionalAdminRequest("/api/admin/assignments?kind=project-well"),
      optionalAdminRequest("/api/admin/data-quality/issues?status=OPEN&limit=500"),
      optionalAdminRequest("/api/admin/time-classification/queue?limit=500"),
      optionalAdminRequest("/api/admin/time-classification/rules"),
    ]);
    adminState.users = users.users || [];
    adminState.roles = users.roles || [];
    adminState.config = config.config || {};
    adminState.aiModels = { models: aiModels.models || [], default_model_id: aiModels.default_model_id || "" };
    adminState.aiExtraction = aiExtraction || adminState.aiExtraction;
    adminState.aiExtractionQueue = aiExtractionQueue || adminState.aiExtractionQueue;
    adminState.selectedAiExtractionRuleId = adminState.aiExtraction.rules?.[0]?.id || "";
    adminState.selectedAiModelId = adminState.aiModels.default_model_id || adminState.aiModels.models?.[0]?.id || "";
    adminState.translationTerms = { terms: translationTerms.terms || [], protected_terms: translationTerms.protected_terms || {} };
    adminState.translationTuning = translationTuning || adminState.translationTuning;
    adminState.translationExperience = { suggestions: translationExperience.suggestions || [], counts: translationExperience.counts || {}, loading: false };
    adminState.translationQueue = translationQueue || adminState.translationQueue;
    adminState.dataStatus = dataStatus;
    adminState.records = records.records || [];
    adminState.logs = logs.logs || [];
    adminState.governance = {
      ...adminState.governance,
      regions: masterRegions.items || [], companies: masterCompanies.items || [], organizations: masterCompanies.items || [], fields: masterFields.items || [],
      blocks: masterBlocks.items || [], teams: masterTeams.items || [], drillingRigs: masterDrillingRigs.items || [], workoverRigs: masterWorkoverRigs.items || [],
      rigs: [...(masterDrillingRigs.items || []), ...(masterWorkoverRigs.items || [])], wells: masterWells.items || [],
      contracts: masterContracts.items || [], projects: masterProjects.items || [], aliases: masterAliases.items || [],
      appendixCategories: appendixCategories.items || [], appendixValues: appendixValues.items || [],
      assignments: assignments.items || [], wellAssignments: wellAssignments.items || [], issues: qualityIssues.items || [],
      classifications: classifications.items || [], rules: classificationRules.items || [],
    };
    adminState.logsPage = 1;
    renderAdminPanels();
    scheduleAdminQueuePoll();
  } catch (error) {
    showToast(error.message);
  }
}

function scheduleAdminQueuePoll(delay = ADMIN_QUEUE_POLL_INTERVAL_MS) {
  if (adminQueuePollTimer) clearTimeout(adminQueuePollTimer);
  adminQueuePollTimer = null;
  if (!adminState.authenticated) return;
  adminQueuePollTimer = setTimeout(pollAdminQueueStatus, Math.max(0, delay));
}

async function pollAdminQueueStatus() {
  adminQueuePollTimer = null;
  if (adminQueuePollRunning || document.hidden || !adminState.authenticated) {
    scheduleAdminQueuePoll();
    return;
  }
  const pollTranslation = adminState.tab === "translationTuning";
  const pollExtraction = adminState.tab === "aiExtraction";
  if (!pollTranslation && !pollExtraction) {
    scheduleAdminQueuePoll();
    return;
  }
  adminQueuePollRunning = true;
  try {
    if (pollTranslation) {
      const previousExperienceStatuses = (adminState.translationExperience?.suggestions || [])
        .map((item) => `${item.id}:${item.status}`)
        .join("|");
      const [status, monitor, experience] = await Promise.all([
        adminRequest("/api/admin/translations/status"),
        adminRequest("/api/admin/ai-jobs/monitor?kind=translation&limit=5"),
        adminRequest("/api/admin/translation-experience?limit=200"),
      ]);
      updateTranslationQueueSnapshot(status);
      updateAiJobMonitor("translation", monitor);
      adminState.translationExperience = { suggestions: experience.suggestions || [], counts: experience.counts || {}, loading: false };
      const currentExperienceStatuses = (adminState.translationExperience.suggestions || [])
        .map((item) => `${item.id}:${item.status}`)
        .join("|");
      const experienceTab = document.querySelector('[data-translation-tuning-view="memory"] .tuning-tab-count');
      if (experienceTab) experienceTab.textContent = Number(experience.counts?.PENDING || 0);
      if (adminState.translationTuningView === "memory" && previousExperienceStatuses !== currentExperienceStatuses) {
        renderAdminTranslationTuning();
      }
    }
    if (pollExtraction) {
      const [status, monitor] = await Promise.all([
        adminRequest("/api/admin/ai-extractions/status"),
        adminRequest("/api/admin/ai-jobs/monitor?kind=extraction&limit=5"),
      ]);
      updateExtractionQueueSnapshot(status);
      updateAiJobMonitor("extraction", monitor);
    }
  } catch (error) {
    if (!/请先登录|unauthorized/i.test(String(error.message || ""))) console.error(error);
  } finally {
    adminQueuePollRunning = false;
    scheduleAdminQueuePoll();
  }
}

function updateTranslationQueueSnapshot(queue = {}) {
  const statusById = new Map((queue.records || []).map((row) => [String(row.record_id || ""), row]));
  adminState.records = (adminState.records || []).map((record) => {
    const status = statusById.get(String(record.record_id || ""));
    return status ? { ...record, translation_status: status.status, translation_progress: status.progress, translation_error: status.error, translation_updated_at: status.updated_at } : record;
  });
  const records = (adminState.translationQueue?.records || []).map((row) => {
    const status = statusById.get(String(row.record_id || ""));
    if (!status) return row;
    const merged = { ...row, ...status };
    merged.reason = translationJobReason(merged, adminState.translationQueue?.current_version || "");
    return merged;
  });
  const mergedQueue = { ...adminState.translationQueue, ...queue, records };
  adminState.translationQueue = mergedQueue;
  refreshTuningQueueCount("translation", mergedQueue.processing_count);
  const byId = new Map(records.map((row) => [String(row.record_id || ""), row]));
  document.querySelectorAll("[data-translation-job-status]").forEach((cell) => {
    const row = byId.get(String(cell.dataset.translationJobStatus || ""));
    if (row) cell.innerHTML = translationJobStatusMarkup(row);
  });
  document.querySelectorAll("[data-translation-job-reason]").forEach((cell) => {
    const row = byId.get(String(cell.dataset.translationJobReason || ""));
    if (row) cell.textContent = row.reason || "-";
  });
  const actions = document.querySelector("[data-translation-queue-actions]");
  if (actions) actions.innerHTML = translationQueueActionsMarkup(mergedQueue);
  refreshAiQueueStatusCounts("translation", records);
  refreshTranslationQueueTable(records);
}

function updateExtractionQueueSnapshot(queue = {}) {
  const statusById = new Map((queue.records || []).map((row) => [String(row.record_id || ""), row]));
  adminState.records = (adminState.records || []).map((record) => {
    const status = statusById.get(String(record.record_id || ""));
    return status ? { ...record, extraction_status: status.status, extraction_progress: status.progress, extraction_error: status.error, extraction_updated_at: status.updated_at } : record;
  });
  const records = (adminState.aiExtractionQueue?.records || []).map((row) => {
    const status = statusById.get(String(row.record_id || ""));
    return status ? { ...row, ...status } : row;
  });
  const mergedQueue = { ...adminState.aiExtractionQueue, ...queue, records };
  adminState.aiExtractionQueue = mergedQueue;
  const currentTab = adminState.aiExtractionQueueStatusTab || "pending";
  const nextTab = preferredExtractionQueueStatusTab(records, currentTab);
  if (nextTab !== currentTab) {
    adminState.aiExtractionQueueStatusTab = nextTab;
    adminState.aiExtractionQueuePage = 1;
    renderAdminAiExtraction();
    return;
  }
  refreshTuningQueueCount("extraction", mergedQueue.processing_count);
  const byId = new Map(records.map((row) => [String(row.record_id || ""), row]));
  document.querySelectorAll("[data-extraction-job-status]").forEach((cell) => {
    const row = byId.get(String(cell.dataset.extractionJobStatus || ""));
    if (row) cell.innerHTML = extractionJobStatusMarkup(row);
  });
  document.querySelectorAll("[data-extraction-job-progress]").forEach((cell) => {
    const row = byId.get(String(cell.dataset.extractionJobProgress || ""));
    if (row) cell.textContent = `${row.progress || "0"}%`;
  });
  document.querySelectorAll("[data-extraction-job-updated]").forEach((cell) => {
    const row = byId.get(String(cell.dataset.extractionJobUpdated || ""));
    if (row) cell.textContent = row.updated_at || "-";
  });
  const actions = document.querySelector("[data-extraction-queue-actions]");
  if (actions) actions.innerHTML = extractionQueueActionsMarkup(mergedQueue);
  refreshAiQueueStatusCounts("extraction", records);
  refreshExtractionQueueTable(records);
}

function refreshAiQueueStatusCounts(kind, records = []) {
  const counts = { all: records.length, pending: 0, processing: 0, failed: 0, completed: 0 };
  records.forEach((row) => {
    const group = aiQueueStatusGroup(row.status, row);
    if (counts[group] !== undefined) counts[group] += 1;
  });
  Object.entries(counts).forEach(([group, count]) => {
    const target = document.querySelector(`[data-ai-queue-status-count="${kind}:${group}"]`);
    if (target) target.textContent = String(count);
  });
}

function refreshTuningQueueCount(kind, count = 0) {
  const target = document.querySelector(`[data-tuning-queue-count="${kind}"]`);
  if (target) target.textContent = String(Number(count || 0));
}

function refreshTranslationQueueTable(records = []) {
  const body = document.querySelector("[data-translation-queue-body]");
  if (!body) return;
  const inputs = [...body.querySelectorAll('[name="translationQueueRecord"]')];
  const checked = new Set(inputs.filter((input) => input.checked).map((input) => input.value));
  const filtered = filterAiQueueRecords(records, adminState.translationQueueStatusTab || "pending");
  const pageSize = Number(adminState.translationQueuePageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  adminState.translationQueuePage = clampPage(adminState.translationQueuePage, totalPages);
  const visible = filtered.slice((adminState.translationQueuePage - 1) * pageSize, adminState.translationQueuePage * pageSize);
  body.innerHTML = translationQueueRowsMarkup(visible);
  if (inputs.length) body.querySelectorAll('[name="translationQueueRecord"]').forEach((input) => { input.checked = checked.has(input.value); });
  const pagination = document.querySelector("[data-translation-queue-pagination]");
  if (pagination) pagination.innerHTML = adminPaginationMarkup("translationQueue", filtered.length, adminState.translationQueuePage, totalPages, pageSize);
}

function refreshExtractionQueueTable(records = []) {
  const body = document.querySelector("[data-extraction-queue-body]");
  if (!body) return;
  const inputs = [...body.querySelectorAll("[data-ai-extraction-record]")];
  const checked = new Set(inputs.filter((input) => input.checked).map((input) => input.value));
  const filtered = filterAiQueueRecords(records, adminState.aiExtractionQueueStatusTab || "pending");
  const pageSize = Number(adminState.aiExtractionQueuePageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  adminState.aiExtractionQueuePage = clampPage(adminState.aiExtractionQueuePage, totalPages);
  const visible = filtered.slice((adminState.aiExtractionQueuePage - 1) * pageSize, adminState.aiExtractionQueuePage * pageSize);
  body.innerHTML = extractionQueueRowsMarkup(visible, adminState.aiExtractionQueueStatusTab === "completed");
  if (inputs.length) body.querySelectorAll("[data-ai-extraction-record]").forEach((input) => { input.checked = checked.has(input.value); });
  const pagination = document.querySelector("[data-extraction-queue-pagination]");
  if (pagination) pagination.innerHTML = adminPaginationMarkup("aiExtractionQueue", filtered.length, adminState.aiExtractionQueuePage, totalPages, pageSize);
}

function translationJobReason(row = {}, currentVersion = "") {
  const status = String(row.status || "").toUpperCase();
  if (status === "FAILED") return row.error || "上次翻译失败";
  if (status === "STOPPED") return "已停止，可继续未完成翻译";
  if (status === "QUEUED") return "等待执行";
  if (status === "IN_PROGRESS") return "模型翻译中";
  if (row.translation_version && currentVersion && row.translation_version !== currentVersion) return "翻译策略已更新";
  if (status === "COMPLETED") return "已完成";
  return "尚未翻译";
}

function updateAiJobMonitor(kind, payload = {}) {
  adminState.aiJobMonitor[kind] = payload.events || [];
  adminState.aiJobMonitor.updatedAt[kind] = payload.updated_at || "";
  const body = document.querySelector(`[data-ai-job-monitor-body="${kind}"]`);
  if (body) body.innerHTML = aiJobMonitorRowsMarkup(kind, adminState.aiJobMonitor[kind]);
  const updated = document.querySelector(`[data-ai-job-monitor-updated="${kind}"]`);
  if (updated) updated.textContent = monitorUpdatedLabel(payload.updated_at);
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
  renderAdminGovernance();
  renderAdminDataGovernance();
  renderAdminTranslationTuning();
  renderAdminConfig();
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
        <span><strong>数据标准化</strong><small>处理名称识别、唯一归属和时效分类问题</small></span>
      </div>
    </section>
  `;
}

const PROJECT_NPT_DEFAULT_HOURS = { drilling: 5, completion: 5, workover: 12 };

function projectTypeLabel(value) {
  return ({ drilling: "钻井", completion: "完井", workover: "修井" })[value] || "未设置";
}

const MASTER_ENTITY_DEFINITIONS = {
  regions: { label: "国家/区域", state: "regions", code: "region_code", name: "region_name", fields: [
    ["region_code", "区域编码", "text"], ["region_name", "区域名称", "text"], ["region_type_code", "区域类型", "appendix:REGION_TYPE"],
    ["iso_alpha2", "ISO二字码", "text"], ["parent_id", "上级区域", "regions"]
  ] },
  companies: { label: "公司", state: "companies", code: "organization_code", name: "organization_name", fields: [
    ["organization_code", "公司编码", "text"], ["organization_name", "公司简称", "text"], ["legal_name", "法定名称", "text"],
    ["organization_type", "公司类型", "appendix:COMPANY_TYPE"], ["country_region_id", "所在国家/区域", "regions"], ["parent_id", "上级公司", "companies"]
  ] },
  fields: { label: "油田", state: "fields", code: "field_code", name: "field_name", fields: [
    ["field_code", "油田编码", "text"], ["field_name", "油田名称", "text"], ["region_id", "国家/区域", "regions"],
    ["operator_company_id", "作业者", "companies"], ["field_type_code", "油田类型", "appendix:FIELD_TYPE"],
    ["lifecycle_status_code", "生命周期", "appendix:FIELD_STATUS"]
  ] },
  blocks: { label: "区块", state: "blocks", code: "block_code", name: "block_name", fields: [
    ["block_code", "区块编码", "text"], ["block_name", "区块名称", "text"], ["field_id", "所属油田", "fields"],
    ["region_id", "国家/区域", "regions"], ["operator_company_id", "作业者", "companies"],
    ["block_type_code", "区块类型", "appendix:BLOCK_TYPE"], ["parent_id", "上级区块", "blocks"]
  ] },
  teams: { label: "队伍", state: "teams", code: "team_code", name: "team_name", fields: [
    ["team_code", "队伍编码", "text"], ["team_name", "队伍名称", "text"], ["team_type_code", "队伍类型", "appendix:TEAM_TYPE"],
    ["company_id", "所属公司", "companies"], ["model_code", "设备型号", "appendix:RIG_TYPE"]
  ] },
  "drilling-rigs": { hidden: true, label: "钻机", state: "drillingRigs", code: "rig_code", name: "rig_name", fields: [
    ["rig_code", "钻机编码", "text"], ["rig_name", "钻机名称", "text"], ["team_id", "所属队伍", "teams"],
    ["owner_organization_id", "资产公司", "companies"], ["manufacturer", "制造商", "text"], ["model_code", "设备型号", "appendix:RIG_TYPE"],
    ["drive_type_code", "驱动方式", "appendix:RIG_DRIVE_TYPE"], ["rated_depth_m", "额定钻深(m)", "number"],
    ["equipment_status_code", "设备状态", "appendix:EQUIPMENT_STATUS"]
  ] },
  "workover-rigs": { hidden: true, label: "修井机", state: "workoverRigs", code: "rig_code", name: "rig_name", fields: [
    ["rig_code", "修井机编码", "text"], ["rig_name", "修井机名称", "text"], ["team_id", "所属队伍", "teams"],
    ["owner_organization_id", "资产公司", "companies"], ["manufacturer", "制造商", "text"], ["model_code", "设备型号", "appendix:RIG_TYPE"],
    ["rated_power_hp", "额定功率(HP)", "number"], ["drive_type_code", "驱动方式", "appendix:RIG_DRIVE_TYPE"],
    ["equipment_status_code", "设备状态", "appendix:EQUIPMENT_STATUS"]
  ] },
  wells: { label: "井", state: "wells", code: "well_code", name: "well_name", fields: [
    ["well_code", "井编码", "text"], ["well_name", "井名称", "text"], ["field_id", "所属油田", "fields"], ["block_id", "所属区块", "blocks"],
    ["operator_company_id", "作业者", "companies"], ["well_type_code", "井用途", "appendix:WELL_TYPE"],
    ["surface_latitude", "井口纬度", "number"], ["surface_longitude", "井口经度", "number"], ["well_profile_code", "井轨迹类型", "appendix:WELL_PROFILE"],
    ["trajectory_status_code", "轨迹状态", "appendix:TRAJECTORY_STATUS"], ["kickoff_md_m", "造斜点MD(m)", "number"], ["planned_td_md_m", "设计井深MD(m)", "number"],
    ["lifecycle_status_code", "生命周期", "appendix:WELL_STATUS"]
  ] },
  contracts: { hidden: true, label: "合同", state: "contracts", code: "contract_no", name: "contract_name", fields: [
    ["contract_no", "合同号", "text"], ["contract_name", "合同名称", "text"], ["customer_organization_id", "客户公司", "companies"],
    ["valid_from", "开始日期", "date"], ["valid_to", "结束日期", "date"]
  ] },
  projects: { hidden: true, label: "项目", state: "projects", code: "project_code", name: "project_name", fields: [
    ["project_code", "项目编码", "text"], ["project_name", "项目名称", "text"], ["project_type", "项目类型", "project-type"],
    ["npt_allowance_hours", "允许 NPT（h）", "number"], ["contract_id", "所属合同", "contracts"], ["service_scope", "服务范围", "text"],
    ["valid_from", "开始日期", "date"], ["valid_to", "结束日期", "date"]
  ] },
  "appendix-categories": { hidden: true, label: "附录类别", state: "appendixCategories", code: "category_code", name: "category_name", fields: [
    ["category_code", "类别编码", "text"], ["category_name", "类别名称", "text"], ["parent_id", "上级类别", "appendix-categories"],
    ["level_no", "层级", "number"], ["description", "说明", "textarea"]
  ] },
  "appendix-values": { hidden: true, label: "附录值", state: "appendixValues", code: "value_code", name: "value_name", fields: [
    ["category_id", "所属类别", "appendix-categories"], ["value_code", "值编码", "text"], ["value_name", "值名称", "text"],
    ["parent_value_id", "上级值", "appendix-values"], ["level_no", "层级", "number"], ["sort_order", "排序", "number"],
    ["display_color", "显示颜色", "color"], ["description", "说明", "textarea"]
  ] },
};

function masterEntityItems(entity) {
  const definition = MASTER_ENTITY_DEFINITIONS[entity];
  return definition ? (adminState.governance?.[definition.state] || []) : [];
}

function masterOptionLabel(source, item = {}) {
  const entity = Object.entries(MASTER_ENTITY_DEFINITIONS).find(([, definition]) => definition.state === source)?.[0];
  const definition = entity ? MASTER_ENTITY_DEFINITIONS[entity] : null;
  return definition ? `${item[definition.code] || ""} ${item[definition.name] || ""}`.trim() : String(item.id || "");
}

function masterDataPanelMarkup(data) {
  const visibleDefinitions = Object.entries(MASTER_ENTITY_DEFINITIONS).filter(([, item]) => !item.hidden);
  const entity = data.masterEntity && MASTER_ENTITY_DEFINITIONS[data.masterEntity] && !MASTER_ENTITY_DEFINITIONS[data.masterEntity].hidden ? data.masterEntity : "regions";
  const definition = MASTER_ENTITY_DEFINITIONS[entity];
  const items = masterEntityItems(entity);
  return `<section class="panel">
    <div class="panel-heading"><div><h2>标准主数据</h2><span class="panel-note">未被引用的数据可以删除；已引用数据须先解除关系，或改为停用</span></div><button class="button small" type="button" data-new-master-entity="${escapeHtml(entity)}">新增${escapeHtml(definition.label)}</button></div>
    <nav class="tuning-tabs" aria-label="主数据类型">${visibleDefinitions.map(([key, item]) => `<button class="tuning-tab ${key === entity ? "active" : ""}" type="button" data-master-entity="${escapeHtml(key)}">${escapeHtml(item.label)} <span class="tuning-tab-count">${masterEntityItems(key).length}</span></button>`).join("")}</nav>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>稳定ID</th><th>编码</th><th>名称</th><th>状态</th><th>版本</th><th>最近修改</th><th>操作</th></tr></thead><tbody>${items.map((item) => `<tr>
      <td>${escapeHtml(item.id)}</td><td><strong>${escapeHtml(item[definition.code] || "-")}</strong></td><td>${escapeHtml(item[definition.name] || "-")}</td>
      <td><span class="status-pill ${item.status === "active" ? "uploaded" : "failed"}">${escapeHtml(item.status || "-")}</span></td><td>${escapeHtml(item.version || 1)}</td>
      <td>${escapeHtml(item.updated_at || "-")}</td><td><button class="link-button" type="button" data-edit-master-entity="${escapeHtml(entity)}" data-master-id="${escapeHtml(item.id)}">编辑</button><button class="link-button danger-link" type="button" data-delete-master-entity="${escapeHtml(entity)}" data-master-id="${escapeHtml(item.id)}">删除</button></td>
    </tr>`).join("") || `<tr><td colspan="7">当前没有${escapeHtml(definition.label)}主数据</td></tr>`}</tbody></table></div>
  </section>`;
}

function appendixPanelMarkup(data) {
  const categories = data.appendixCategories || [];
  const selectedId = String(data.appendixCategoryId || categories[0]?.id || "");
  data.appendixCategoryId = selectedId;
  const selected = categories.find((item) => String(item.id) === selectedId) || {};
  const values = (data.appendixValues || []).filter((item) => String(item.category_id) === selectedId);
  const valueById = new Map((data.appendixValues || []).map((item) => [String(item.id), item]));
  return `<section class="panel">
    <div class="panel-heading"><div><h2>附录</h2><span class="panel-note">统一维护各主数据下拉选项；类别和值均使用稳定编码，并支持父子层级</span></div><button class="button small" type="button" data-new-appendix-category>新增类别</button></div>
    <div class="master-appendix-layout">
      <aside class="master-appendix-categories"><div class="master-appendix-title">枚举类别</div>${categories.map((item) => `<button class="master-appendix-category ${String(item.id) === selectedId ? "active" : ""}" type="button" data-appendix-category="${escapeHtml(item.id)}"><span><strong>${escapeHtml(item.category_name)}</strong><small>${escapeHtml(item.category_code)}</small></span><em>${(data.appendixValues || []).filter((value) => String(value.category_id) === String(item.id)).length}</em></button>`).join("") || `<p class="panel-note">尚未配置附录类别</p>`}</aside>
      <div class="master-appendix-values">
        <div class="panel-heading compact-heading"><div><h3>${escapeHtml(selected.category_name || "枚举值")}</h3><span class="panel-note">${escapeHtml(selected.category_code || "请先创建类别")}${selected.description ? ` · ${escapeHtml(selected.description)}` : ""}</span></div><div class="admin-actions heading-actions">${selected.id ? `<button class="button secondary small" type="button" data-edit-master-entity="appendix-categories" data-master-id="${escapeHtml(selected.id)}">编辑类别</button><button class="button secondary small danger-button" type="button" data-delete-master-entity="appendix-categories" data-master-id="${escapeHtml(selected.id)}">删除类别</button><button class="button small" type="button" data-new-appendix-value="${escapeHtml(selected.id)}">新增枚举值</button>` : ""}</div></div>
        <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>编码</th><th>名称</th><th>显示颜色</th><th>上级值</th><th>层级</th><th>排序</th><th>状态</th><th>操作</th></tr></thead><tbody>${values.map((item) => `<tr><td><strong>${escapeHtml(item.value_code)}</strong></td><td>${escapeHtml(item.value_name)}</td><td><span class="appendix-color-swatch" style="--appendix-color:${escapeHtml(item.display_color || "#94a3b8")}"></span>${escapeHtml(item.display_color || "-")}</td><td>${escapeHtml(valueById.get(String(item.parent_value_id))?.value_name || "-")}</td><td>${escapeHtml(item.level_no ?? 1)}</td><td>${escapeHtml(item.sort_order ?? 0)}</td><td><span class="status-pill ${item.status === "active" ? "uploaded" : "failed"}">${item.status === "active" ? "启用" : "停用"}</span></td><td><button class="link-button" type="button" data-edit-master-entity="appendix-values" data-master-id="${escapeHtml(item.id)}">编辑</button><button class="link-button danger-link" type="button" data-delete-master-entity="appendix-values" data-master-id="${escapeHtml(item.id)}">删除</button></td></tr>`).join("") || `<tr><td colspan="8">当前类别暂无枚举值</td></tr>`}</tbody></table></div>
      </div>
    </div>
  </section>`;
}

function classificationRuleValue(rule = {}) {
  if (typeof rule.classification_json === "object" && rule.classification_json) return rule.classification_json;
  try { return JSON.parse(rule.classification_json || "{}"); } catch { return {}; }
}

function timeRulePanelMarkup(data) {
  return `<section class="panel"><div class="panel-heading"><div><h2>工作量分类规则</h2><span class="panel-note">OP CODE / OP SUB 精确规则优先，关键词规则次之；规则补充工作量等维度，不覆盖原日报 P / SC / NPT</span></div><div class="admin-actions heading-actions"><button class="button secondary small" type="button" data-reclassify-time-facts>重新应用规则</button><button class="button small" type="button" data-new-time-rule>新增规则</button></div></div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>优先级</th><th>规则</th><th>匹配条件</th><th>分类结果</th><th>版本</th><th>状态</th><th>操作</th></tr></thead><tbody>${(data.rules || []).map((rule) => {
      const classification = classificationRuleValue(rule);
      return `<tr><td>${escapeHtml(rule.priority)}</td><td><strong>${escapeHtml(rule.rule_name)}</strong><small>${escapeHtml(rule.rule_code)}</small></td>
        <td>${escapeHtml([rule.op_code_pattern && `CODE=${rule.op_code_pattern}`, rule.op_sub_pattern && `SUB=${rule.op_sub_pattern}`, rule.keyword_pattern && `关键词=${rule.keyword_pattern}`].filter(Boolean).join("；") || "-")}</td>
        <td>${escapeHtml([classification.confirmed_op_type, classification.work_bucket, classification.billing_status, classification.responsibility, classification.cause_code].filter(Boolean).join(" / ") || "-")}</td>
        <td>${escapeHtml(rule.rule_version || "-")}</td><td>${escapeHtml(rule.status || "-")}</td><td><button class="link-button" type="button" data-edit-time-rule="${escapeHtml(rule.id)}">编辑</button></td></tr>`;
    }).join("") || `<tr><td colspan="7">尚未配置规则；未命中数据会进入人工确认队列</td></tr>`}</tbody></table></div>
  </section>`;
}

function openTimeRuleModal(id = "") {
  const rule = (adminState.governance.rules || []).find((item) => String(item.id) === String(id)) || {};
  const classification = classificationRuleValue(rule);
  const select = (name, values, current) => `<select name="${name}"><option value="">未设置</option>${values.map(([value, label]) => `<option value="${value}" ${value === current ? "selected" : ""}>${label}</option>`).join("")}</select>`;
  openAdminModal(rule.id ? "编辑时间分类规则" : "新增时间分类规则", `
    <input type="hidden" name="timeRuleId" value="${escapeHtml(rule.id || "")}" /><input type="hidden" name="timeRuleVersion" value="${escapeHtml(rule.version || "")}" />
    <div class="admin-modal-form compact">
      <label>规则编码<input name="timeRuleCode" value="${escapeHtml(rule.rule_code || "")}" /></label><label>规则名称<input name="timeRuleName" value="${escapeHtml(rule.rule_name || "")}" /></label>
      <label>优先级<input name="timeRulePriority" type="number" value="${escapeHtml(rule.priority ?? 100)}" /></label>
      <label>OP CODE 正则<input name="timeRuleOpCode" value="${escapeHtml(rule.op_code_pattern || "")}" placeholder="如 ^DRILLING$" /></label>
      <label>OP SUB 正则<input name="timeRuleOpSub" value="${escapeHtml(rule.op_sub_pattern || "")}" /></label>
      <label class="wide">描述关键词正则<input name="timeRuleKeyword" value="${escapeHtml(rule.keyword_pattern || "")}" /></label>
      <label>生产属性${select("timeRuleProductive", [["PRODUCTION","生产"],["NON_PRODUCTION","非生产"]], classification.productive_flag)}</label>
      <label>缺失类型候选${select("timeRuleOpType", [["P","P"],["SC","SC"],["NPT","NPT"]], classification.confirmed_op_type)}</label>
      <label>工作量分类${select("timeRuleBucket", [["OPERATION","作业"],["MOVE","搬迁"],["STANDBY_STAFFED","有人待工"],["STANDBY_UNSTAFFED","无人待工"],["FORCE_MAJEURE","不可抗力"],["MAINTENANCE","维修"]], classification.work_bucket)}</label>
      <label>计费状态${select("timeRuleBilling", [["FULL_RATE","全日费"],["PARTIAL_RATE","部分日费"],["ZERO_RATE","零日费"]], classification.billing_status)}</label>
      <label>责任方${select("timeRuleResponsibility", [["OURS","我方"],["CLIENT","甲方"],["THIRD_PARTY","第三方"],["FORCE_MAJEURE","不可抗力"]], classification.responsibility)}</label>
      <label>原因编码<input name="timeRuleCause" value="${escapeHtml(classification.cause_code || "")}" /></label><label>服务线<input name="timeRuleServiceLine" value="${escapeHtml(classification.service_line || "")}" /></label>
      <label>状态<select name="timeRuleStatus"><option value="active" ${rule.status !== "inactive" ? "selected" : ""}>启用</option><option value="inactive" ${rule.status === "inactive" ? "selected" : ""}>停用</option></select></label>
      <label class="wide">变更原因<input name="timeRuleReason" placeholder="必填" /></label>
    </div>`, `<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button" type="button" data-save-time-rule>保存规则</button>`);
}

async function saveTimeRuleFromModal() {
  const value = (name) => document.querySelector(`[name="${name}"]`)?.value || "";
  if (!value("timeRuleReason").trim()) return showToast("请填写变更原因");
  const payload = {
    id: Number(value("timeRuleId")) || undefined, version: Number(value("timeRuleVersion")) || undefined,
    rule_code: value("timeRuleCode"), rule_name: value("timeRuleName"), priority: Number(value("timeRulePriority") || 100),
    op_code_pattern: value("timeRuleOpCode"), op_sub_pattern: value("timeRuleOpSub"), keyword_pattern: value("timeRuleKeyword"),
    classification: { productive_flag: value("timeRuleProductive"), confirmed_op_type: value("timeRuleOpType"), work_bucket: value("timeRuleBucket"),
      billing_status: value("timeRuleBilling"), responsibility: value("timeRuleResponsibility"), cause_code: value("timeRuleCause"), service_line: value("timeRuleServiceLine") },
    status: value("timeRuleStatus"), change_reason: value("timeRuleReason"),
  };
  try {
    await adminRequest("/api/admin/time-classification/rules", { method: payload.id ? "PATCH" : "POST", body: JSON.stringify(payload) });
    const response = await adminRequest("/api/admin/time-classification/rules");
    adminState.governance.rules = response.items || [];
    closeAdminModal(); renderAdminDataGovernance(); showToast("分类规则已保存");
  } catch (error) { showToast(error.message); }
}

async function reclassifyTimeFacts() {
  try {
    const response = await adminRequest("/api/admin/time-classification/reclassify", { method: "POST", body: "{}" });
    await refreshGovernanceQueues();
    showToast(`已重算 ${response.result?.processed || 0} 条，仍待确认 ${response.result?.pending || 0} 条`);
  } catch (error) { showToast(error.message); }
}

function openMasterEntityModal(entity, id = "", preset = {}) {
  const definition = MASTER_ENTITY_DEFINITIONS[entity];
  if (!definition) return;
  const item = { ...preset, ...(masterEntityItems(entity).find((row) => String(row.id) === String(id)) || {}) };
  if (entity === "projects") {
    item.project_type = item.project_type || "drilling";
    if (item.npt_allowance_hours === undefined || item.npt_allowance_hours === null || item.npt_allowance_hours === "") {
      item.npt_allowance_hours = PROJECT_NPT_DEFAULT_HOURS[item.project_type];
    }
  }
  const fields = definition.fields.map(([key, label, type]) => {
    const value = item[key] ?? "";
    if (type === "project-type") {
      return `<label>${escapeHtml(label)}<select data-master-field="${escapeHtml(key)}">${[["drilling", "钻井"], ["completion", "完井"], ["workover", "修井"]].map(([optionValue, optionLabel]) => `<option value="${optionValue}" ${optionValue === value ? "selected" : ""}>${optionLabel}</option>`).join("")}</select></label>`;
    }
    if (String(type).startsWith("appendix:")) {
      const categoryCode = String(type).slice("appendix:".length);
      const category = (adminState.governance.appendixCategories || []).find((row) => row.category_code === categoryCode);
      const options = (adminState.governance.appendixValues || []).filter((row) => String(row.category_id) === String(category?.id) && row.status === "active");
      return `<label>${escapeHtml(label)}<select data-master-field="${escapeHtml(key)}"><option value="">未设置</option>${options.map((option) => `<option value="${escapeHtml(option.value_code)}" ${String(option.value_code) === String(value) ? "selected" : ""}>${escapeHtml(`${option.value_name} (${option.value_code})`)}</option>`).join("")}</select></label>`;
    }
    if (MASTER_ENTITY_DEFINITIONS[type]) {
      const reference = MASTER_ENTITY_DEFINITIONS[type];
      let options = adminState.governance?.[reference.state] || [];
      if (entity === "appendix-values" && type === "appendix-values" && item.category_id) options = options.filter((option) => String(option.category_id) === String(item.category_id));
      return `<label>${escapeHtml(label)}<select data-master-field="${escapeHtml(key)}"><option value="">未设置</option>${options.filter((option) => String(option.id) !== String(id) || type !== entity).map((option) => `<option value="${escapeHtml(option.id)}" ${String(option.id) === String(value) ? "selected" : ""}>${escapeHtml(masterOptionLabel(reference.state, option))}</option>`).join("")}</select></label>`;
    }
    if (type === "textarea") return `<label class="wide">${escapeHtml(label)}<textarea data-master-field="${escapeHtml(key)}">${escapeHtml(typeof value === "object" ? JSON.stringify(value) : value)}</textarea></label>`;
    const numberAttributes = key === "npt_allowance_hours" ? ' min="0" max="999999.99" step="0.01" inputmode="decimal" data-project-npt-hours' : "";
    return `<label>${escapeHtml(label)}<input data-master-field="${escapeHtml(key)}" type="${type}" value="${escapeHtml(type === "date" ? String(value).slice(0, 10) : value)}"${numberAttributes} /></label>`;
  }).join("");
  openAdminModal(
    `${item.id ? "编辑" : "新增"}${definition.label}`,
    `<input type="hidden" data-master-record-id value="${escapeHtml(item.id || "")}" /><input type="hidden" data-master-version value="${escapeHtml(item.version || "")}" />
    <div class="admin-modal-form compact" data-master-entity-form="${escapeHtml(entity)}">${fields}
      <label>状态<select data-master-field="status"><option value="active" ${item.status !== "inactive" ? "selected" : ""}>启用</option><option value="inactive" ${item.status === "inactive" ? "selected" : ""}>停用</option></select></label>
      <label class="wide">变更原因<input data-master-field="change_reason" value="" placeholder="新增、修改或停用均必须填写" /></label>
    </div>`,
    `${item.id ? `<button class="button secondary danger-button" type="button" data-delete-master-entity="${escapeHtml(entity)}" data-master-id="${escapeHtml(item.id)}">删除</button>` : ""}<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button" type="button" data-save-master-entity="${escapeHtml(entity)}">保存</button>`
  );
}

function openDeleteMasterEntityModal(entity, id) {
  const definition = MASTER_ENTITY_DEFINITIONS[entity];
  const item = masterEntityItems(entity).find((row) => String(row.id) === String(id));
  if (!definition || !item) return showToast("未找到要删除的数据，请刷新后重试");
  const code = item[definition.code] || item.id;
  const name = item[definition.name] || code;
  openAdminModal(
    `删除${definition.label}`,
    `<div class="master-delete-warning"><strong>确认删除“${escapeHtml(name)}”吗？</strong><p>仅未被引用的数据可以彻底删除。若存在下级数据、项目关系、日报或别名引用，系统会拒绝并提示引用来源。</p></div>
    <div class="admin-modal-form compact" data-delete-master-form>
      <label>稳定ID<input value="${escapeHtml(item.id)}" disabled /></label>
      <label>编码<input value="${escapeHtml(code)}" disabled /></label>
      <label class="wide">删除原因<input data-delete-master-reason placeholder="请说明删除原因" /></label>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button danger-button" type="button" data-confirm-delete-master-entity="${escapeHtml(entity)}" data-master-id="${escapeHtml(item.id)}" data-master-version="${escapeHtml(item.version || 1)}">确认删除</button>`
  );
}

async function deleteMasterEntityFromModal(entity, id, version) {
  const reason = document.querySelector("[data-delete-master-reason]")?.value?.trim() || "";
  if (!reason) return showToast("请填写删除原因");
  try {
    await adminRequest(`/api/admin/master-data/${entity}`, { method: "DELETE", body: JSON.stringify({ id: Number(id), version: Number(version), change_reason: reason }) });
    const response = await adminRequest(`/api/admin/master-data/${entity}?limit=1000`);
    adminState.governance[MASTER_ENTITY_DEFINITIONS[entity].state] = response.items || [];
    if (entity === "appendix-categories") adminState.governance.appendixCategoryId = String(response.items?.[0]?.id || "");
    closeAdminModal(); renderAdminGovernance();
    if (entity === "projects" || entity === "contracts") renderAdminProjects();
    showToast("主数据已删除");
  } catch (error) { showToast(error.message); }
}

async function saveMasterEntityFromModal(entity) {
  const form = document.querySelector(`[data-master-entity-form="${entity}"]`);
  if (!form) return;
  const payload = {};
  form.querySelectorAll("[data-master-field]").forEach((input) => { payload[input.dataset.masterField] = input.value; });
  payload.id = Number(document.querySelector("[data-master-record-id]")?.value || 0) || undefined;
  payload.version = Number(document.querySelector("[data-master-version]")?.value || 0) || undefined;
  if (!String(payload.change_reason || "").trim()) return showToast("请填写变更原因");
  Object.keys(payload).filter((key) => key.endsWith("_id")).forEach((key) => { payload[key] = payload[key] ? Number(payload[key]) : null; });
  try {
    await adminRequest(`/api/admin/master-data/${entity}`, { method: payload.id ? "PATCH" : "POST", body: JSON.stringify(payload) });
    const response = await adminRequest(`/api/admin/master-data/${entity}?limit=1000`);
    adminState.governance[MASTER_ENTITY_DEFINITIONS[entity].state] = response.items || [];
    closeAdminModal(); renderAdminGovernance();
    if (entity === "projects" || entity === "contracts") renderAdminProjects();
    showToast("主数据已保存");
  } catch (error) { showToast(error.message); }
}

function renderAdminGovernance() {
  const host = document.querySelector('[data-admin-panel="governance"]');
  if (!host) return;
  const data = adminState.governance || {};
  const masterStates = Object.values(MASTER_ENTITY_DEFINITIONS).filter((item) => !item.hidden).map((item) => item.state);
  const masterCount = masterStates
    .reduce((total, key) => total + (data[key] || []).length, 0);
  const activeCount = masterStates
    .reduce((total, key) => total + (data[key] || []).filter((item) => item.status === "active").length, 0);
  host.innerHTML = `
    <section class="admin-kpi-grid">
      ${adminKpi("主数据类型", masterStates.length, "OSDU精简属性", "overview")}
      ${adminKpi("实体数据", masterCount, "全部使用稳定ID", "database")}
      ${adminKpi("启用实体", activeCount, "可用于业务关系", "users")}
      ${adminKpi("附录类别", (data.appendixCategories || []).length, `${(data.appendixValues || []).length} 个枚举值`, "logs")}
    </section>
    <nav class="tuning-tabs master-view-tabs" aria-label="主数据管理视图"><button class="tuning-tab ${data.masterView !== "appendix" ? "active" : ""}" type="button" data-master-view="entities">实体数据</button><button class="tuning-tab ${data.masterView === "appendix" ? "active" : ""}" type="button" data-master-view="appendix">附录</button></nav>
    ${data.masterView === "appendix" ? appendixPanelMarkup(data) : masterDataPanelMarkup(data)}`;
}

function qualityIssueDetails(item = {}) {
  if (typeof item.details_json === "object" && item.details_json) return item.details_json;
  try { return JSON.parse(item.details_json || "{}"); } catch { return {}; }
}

function qualityIssueTypeLabel(type = "") {
  return ({
    ALIAS_REVIEW: "名称待识别",
    CLASSIFICATION_PENDING: "来源时效异常",
    HOURS_NOT_24: "日报工时不平",
    UNASSIGNED: "项目归属缺失",
    AMBIGUOUS: "项目归属冲突",
    MASTER_NOT_FOUND: "主数据缺失",
    NORMALIZATION_FAILED: "标准化失败",
  })[String(type).toUpperCase()] || type || "数据待核对";
}

function qualityIssueGuidance(item = {}) {
  const type = String(item.issue_type || "").toUpperCase();
  const details = qualityIssueDetails(item);
  if (type === "CLASSIFICATION_PENDING") return `${Number(details.pending_count || 0)} 条作业活动的原日报类型缺失或存在规则冲突；正常 P / SC / NPT 不在此队列重复确认。`;
  if (type === "HOURS_NOT_24") {
    const role = details.boundary_role === "FIRST_AND_LAST" ? "首日且末日" : details.boundary_role === "FIRST" ? "首日" : "末日";
    return `该日报是同类型、同井的${role}，作业合计 ${Number(details.total_hours || 0).toFixed(2)} 小时，与 24 小时相差 ${Math.abs(Number(details.difference || 0)).toFixed(2)} 小时。`;
  }
  if (type === "ALIAS_REVIEW") {
    const candidates = [details.left, details.right].filter(Boolean);
    if (candidates.length > 1) return `“${candidates.join("”与“")}”可能是同一实体，需要人工判断是否建立名称映射。`;
    return `来源名称“${details.raw_value || details.alias_value || candidates[0] || "未识别名称"}”尚未映射到标准实体。`;
  }
  if (type === "UNASSIGNED") return "当前日报没有找到唯一有效的项目归属。";
  if (type === "AMBIGUOUS") return "当前日报同时命中多个项目关系，必须调整有效期或井范围。";
  return details.message || details.reason || details.raw_value || item.resolution_note || "需要人工核对后才能进入正式统计。";
}

function qualityIssueSubject(item = {}) {
  const details = qualityIssueDetails(item);
  const candidates = [details.left, details.right].filter(Boolean);
  if (candidates.length) return `${standardEntityTypeLabel(item.entity_type)}：${candidates.join(" / ")}`;
  return item.record_id || item.entity_id || "-";
}

function standardEntityTypeLabel(type = "") {
  return ({ block: "区块", rig: "队伍", well: "井", project: "项目" })[String(type).toLowerCase()] || type || "实体";
}

function qualityIssueAction(item = {}) {
  const type = String(item.issue_type || "").toUpperCase();
  if (type === "ALIAS_REVIEW" || type === "MASTER_NOT_FOUND") return { route: "aliases", label: "维护名称映射" };
  if (type === "CLASSIFICATION_PENDING") return { route: "classification", label: "核对来源类型" };
  if (type === "UNASSIGNED" || type === "AMBIGUOUS") return { route: "projects", label: "调整项目归属" };
  if (type === "HOURS_NOT_24" || type === "NORMALIZATION_FAILED") return { route: "daily-report", label: "检查原始日报" };
  return { route: "results", label: "查看标准化结果" };
}

function standardEntityLabel(items = [], id, nameField, codeField) {
  if (!id) return "未匹配";
  const item = items.find((row) => String(row.id) === String(id));
  if (!item) return `稳定ID ${id}`;
  return item[nameField] || item[codeField] || `稳定ID ${id}`;
}

function standardizationResultRows(data = {}) {
  const records = adminState.records || [];
  return records.slice(0, 200).map((record) => {
    const status = String(record.master_match_status || "").toUpperCase();
    const rig = standardEntityLabel(data.rigs || [], record.rig_id, "rig_name", "rig_code");
    const well = standardEntityLabel(data.wells || [], record.well_id, "well_name", "well_code");
    const project = standardEntityLabel(data.projects || [], record.project_id, "project_name", "project_code");
    const statusLabel = ({ MATCHED: "已建立唯一归属", UNASSIGNED: "待确定归属", AMBIGUOUS: "归属存在冲突", NORMALIZATION_FAILED: "标准化失败" })[status] || (status || "待处理");
    return `<tr>
      <td>${escapeHtml(record.report_date || record.reportDate || "-")}</td>
      <td><strong>${escapeHtml(record.rig || "-")}</strong><small>${escapeHtml(record.wellbore || "-")}</small></td>
      <td><strong>${escapeHtml(rig)}</strong><small>${escapeHtml(well)}</small></td>
      <td><strong>${escapeHtml(project)}</strong><small>${record.job_id ? `作业实例 #${escapeHtml(record.job_id)}` : "尚未建立作业实例"}</small></td>
      <td><span class="status-pill ${status === "MATCHED" ? "uploaded" : "failed"}">${escapeHtml(statusLabel)}</span>
        <details class="standardization-id-details"><summary>追溯ID</summary><small>设备 ${escapeHtml(record.rig_id || "-")} · 井 ${escapeHtml(record.well_id || "-")} · 项目 ${escapeHtml(record.project_id || "-")} · 作业 ${escapeHtml(record.job_id || "-")}</small></details>
      </td>
    </tr>`;
  }).join("");
}

function standardizationPendingMarkup(data, issues, classifications) {
  const issueRows = issues.slice(0, 100).map((item) => {
    const action = qualityIssueAction(item);
    return `<tr>
      <td><span class="status-pill failed">${escapeHtml(qualityIssueTypeLabel(item.issue_type))}</span><small>${escapeHtml(item.issue_type || "")}</small></td>
      <td>${escapeHtml(qualityIssueSubject(item))}</td>
      <td>${escapeHtml(qualityIssueGuidance(item))}</td>
      <td><strong>${escapeHtml(action.label)}</strong><small>处理完成后再关闭问题</small></td>
      <td><div class="admin-actions compact-actions"><button class="link-button" type="button" data-standardization-route="${escapeHtml(action.route)}">${escapeHtml(action.label)}</button><button class="link-button danger-link" type="button" data-resolve-quality-issue="${escapeHtml(item.id)}">完成后关闭</button></div></td>
    </tr>`;
  }).join("");
  const classificationRows = classifications.slice(0, 100).map((item) => `<tr>
    <td>${escapeHtml(item.report_date || "-")}</td><td>${escapeHtml(item.record_id || "-")}</td>
    <td><strong>${escapeHtml(item.op_code || "-")}</strong><small>${escapeHtml(item.op_sub || "-")}</small></td><td>${escapeHtml(item.hours || 0)} h</td>
    <td><span class="status-pill ${item.source_op_type ? "uploaded" : "failed"}">${escapeHtml(item.source_op_type || "未提取")}</span></td>
    <td>${escapeHtml(workBucketLabel(item.work_bucket))}</td>
    <td><button class="link-button" type="button" data-confirm-classification="${escapeHtml(item.activity_id)}">${item.source_op_type ? "补充分类" : "补录类型"}</button></td>
  </tr>`).join("");
  return `
    <section class="panel"><div class="panel-heading"><div><h2>待处理问题</h2><span class="panel-note">先按“建议去向”修正来源、主数据或关系，再关闭问题；关闭问题不会自动修改业务数据</span></div><span class="standardization-count-badge">${issues.length} 条</span></div>
      <div class="table-wrap"><table class="record-table admin-table standardization-issue-table"><thead><tr><th>问题类型</th><th>涉及对象</th><th>为什么不能直接统计</th><th>正确处理方式</th><th>操作</th></tr></thead><tbody>${issueRows || `<tr><td colspan="5">当前没有待处理的数据质量问题</td></tr>`}</tbody></table></div>
    </section>
    <section class="panel standardization-classification-panel"><div class="panel-heading"><div><h2>来源时效异常</h2><span class="panel-note">这里只处理原日报类型缺失或规则冲突；正常SC/NPT的复核、责任方和有/无人待工统一在NPT确认办理</span></div><div class="admin-actions"><span class="standardization-count-badge">${classifications.length} 条</span><button class="button secondary small" type="button" data-standardization-route="npt-confirmation">前往NPT确认</button></div></div>
      <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>日期</th><th>日报</th><th>作业编码</th><th>时长</th><th>原日报类型</th><th>工作量分类</th><th>处理</th></tr></thead><tbody>${classificationRows || `<tr><td colspan="7">当前没有需要补充的分类信息</td></tr>`}</tbody></table></div>
    </section>`;
}

function workBucketLabel(value = "") {
  return ({
    OPERATION: "作业", MOVE: "搬迁", STANDBY_STAFFED: "有人待工",
    STANDBY_UNSTAFFED: "无人待工", FORCE_MAJEURE: "不可抗力", MAINTENANCE: "维修",
  })[String(value || "").toUpperCase()] || "未分类";
}

function standardizationRulesMarkup(data) {
  return `<section class="standardization-rules-intro"><strong>规则的作用</strong><span>别名把来源名称识别为标准实体；分类规则只为原日报类型缺失或异常提供候选。P按原值直接生效，SC/NPT的复核、责任和待工归类只能在NPT确认中人工确定。</span></section>
    ${aliasGovernancePanelMarkup(data)}
    ${timeRulePanelMarkup(data)}`;
}

function standardizationResultsMarkup(data) {
  const rows = standardizationResultRows(data);
  return `<section class="panel"><div class="panel-heading"><div><h2>标准化结果</h2><span class="panel-note">这里用于核对加工结果，不在此修改主数据或项目关系；“已建立唯一归属”的日报才能进入项目统计</span></div><button class="button secondary small" type="button" data-standardization-route="pending">查看待处理问题</button></div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>日期</th><th>原始日报值</th><th>识别后的队伍 / 井</th><th>项目 / 作业实例</th><th>统计状态</th></tr></thead><tbody>${rows || `<tr><td colspan="5">当前没有日报记录</td></tr>`}</tbody></table></div>
  </section>`;
}

function renderAdminDataGovernance() {
  const host = document.querySelector('[data-admin-panel="dataGovernance"]');
  if (!host) return;
  const data = adminState.governance || {};
  const issues = data.issues || [];
  const classifications = data.classifications || [];
  const records = adminState.records || [];
  const matchedCount = records.filter((item) => String(item.master_match_status || "").toUpperCase() === "MATCHED").length;
  const view = data.standardizationView || "pending";
  host.innerHTML = `
    <section class="panel standardization-hero">
      <div class="standardization-hero-copy"><span class="standardization-kicker">DATA OPERATIONS</span><h2>数据标准化工作台</h2><p>把日报中的原始井号、队伍名称和作业描述，加工成可唯一归属、可分类、可追溯的统计事实。本模块负责发现问题和组织处理，不替代主数据、项目关系或原始日报维护。</p></div>
      <div class="standardization-scope">
        <div><strong>在这里处理</strong><span>名称识别、归属异常、原日报类型缺失和规则冲突</span></div>
        <div><strong>到关联模块维护</strong><span>标准实体、项目关系、原始日报；SC/NPT到NPT确认</span></div>
      </div>
    </section>
    <section class="standardization-flow" aria-label="日报标准化处理流程">
      <article><span>1</span><div><strong>原始日报</strong><small>保留 PDF 解析原值</small></div><a href="/web_form/">查看日报</a></article>
      <article><span>2</span><div><strong>名称识别</strong><small>依赖主数据与别名</small></div><button type="button" data-admin-tab="governance">主数据管理</button></article>
      <article><span>3</span><div><strong>唯一归属</strong><small>项目、队伍、井有效期</small></div><button type="button" data-admin-tab="projects">项目与队伍</button></article>
      <article><span>4</span><div><strong>时效生效</strong><small>P直接生效；SC/NPT人工确认</small></div><button type="button" data-standardization-route="npt-confirmation">NPT确认</button></article>
      <article><span>5</span><div><strong>标准事实</strong><small>供统计和报表使用</small></div><button type="button" data-standardization-route="results">核对结果</button></article>
    </section>
    <section class="admin-kpi-grid standardization-kpis">
      ${adminKpi("待处理问题", issues.length, "修正后才能正式统计", "logs")}
      ${adminKpi("来源时效异常", classifications.length, "不含正常SC/NPT待确认", "overview")}
      ${adminKpi("唯一归属日报", matchedCount, `共 ${records.length} 份日报`, "database")}
      ${adminKpi("识别与分类规则", (data.aliases || []).filter((item) => item.status === "active").length + (data.rules || []).filter((item) => item.status === "active").length, "启用规则与别名", "settings")}
    </section>
    <nav class="tuning-tabs standardization-tabs" aria-label="数据标准化工作台视图">
      <button class="tuning-tab ${view === "pending" ? "active" : ""}" type="button" data-standardization-view="pending">待处理与确认 <em>${issues.length + classifications.length}</em></button>
      <button class="tuning-tab ${view === "rules" ? "active" : ""}" type="button" data-standardization-view="rules">识别与分类规则</button>
      <button class="tuning-tab ${view === "results" ? "active" : ""}" type="button" data-standardization-view="results">标准化结果</button>
    </nav>
    ${view === "rules" ? standardizationRulesMarkup(data) : view === "results" ? standardizationResultsMarkup(data) : standardizationPendingMarkup(data, issues, classifications)}`;
}

function aliasGovernancePanelMarkup(data) {
  return `<section class="panel"><div class="panel-heading"><h2>名称别名与识别映射</h2><span class="panel-note">别名属于解析标准化规则，不属于实体基本属性</span></div>
    <input name="masterAliasId" type="hidden" /><input name="masterAliasVersion" type="hidden" />
    <div class="admin-config-grid"><label>原始名称<input name="masterAliasValue" placeholder="例如 W905" /></label>
    <label>标准实体<select name="masterAliasTarget">
      <optgroup label="井队">${(data.rigs || []).map((item) => `<option value="rig:${escapeHtml(item.id)}">${escapeHtml(item.rig_name || item.rig_code)}</option>`).join("")}</optgroup>
      <optgroup label="井">${(data.wells || []).map((item) => `<option value="well:${escapeHtml(item.id)}">${escapeHtml(item.well_name || item.well_code)}</option>`).join("")}</optgroup>
      <optgroup label="区块">${(data.blocks || []).map((item) => `<option value="block:${escapeHtml(item.id)}">${escapeHtml(item.block_name || item.block_code)}</option>`).join("")}</optgroup>
      <optgroup label="项目">${(data.projects || []).map((item) => `<option value="project:${escapeHtml(item.id)}">${escapeHtml(item.project_name || item.project_code)}</option>`).join("")}</optgroup>
    </select></label><label>状态<select name="masterAliasStatus"><option value="active">启用</option><option value="inactive">停用</option></select></label><label>确认原因<input name="masterAliasReason" placeholder="必填" /></label></div>
    <div class="admin-actions"><button class="button" type="button" data-save-master-alias>确认别名</button></div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>类型</th><th>原始名称</th><th>标准化名称</th><th>目标ID</th><th>确认状态</th><th>状态</th><th>操作</th></tr></thead><tbody>${(data.aliases || []).map((item) => `<tr><td>${escapeHtml(item.entity_type)}</td><td>${escapeHtml(item.alias_value)}</td><td>${escapeHtml(item.normalized_alias)}</td><td>${escapeHtml(item.entity_id)}</td><td>${escapeHtml(item.confirmation_status)}</td><td>${escapeHtml(item.status)}</td><td><button class="link-button" type="button" data-edit-master-alias="${escapeHtml(item.id)}">调整</button></td></tr>`).join("")}</tbody></table></div>
  </section>`;
}

function switchStandardizationView(view = "pending", focusSelector = "") {
  adminState.governance.standardizationView = ["pending", "rules", "results"].includes(view) ? view : "pending";
  renderAdminDataGovernance();
  if (focusSelector) window.requestAnimationFrame(() => document.querySelector(focusSelector)?.scrollIntoView({ behavior: "smooth", block: "start" }));
}

function followStandardizationRoute(route = "") {
  if (route === "aliases") return switchStandardizationView("rules", '[name="masterAliasValue"]');
  if (route === "classification") return switchStandardizationView("pending", ".standardization-classification-panel");
  if (route === "projects") return switchAdminTab("projects");
  if (route === "daily-report") {
    window.location.href = "/web_form/";
    return;
  }
  if (route === "npt-confirmation") {
    window.location.href = "/web_form/?page=rig-npt-ranking";
    return;
  }
  return switchStandardizationView(route === "results" ? "results" : "pending");
}

async function refreshGovernanceQueues() {
  const [issues, classifications] = await Promise.all([
    adminRequest("/api/admin/data-quality/issues?status=OPEN&limit=500"),
    adminRequest("/api/admin/time-classification/queue?limit=500"),
  ]);
  adminState.governance.issues = issues.items || [];
  adminState.governance.classifications = classifications.items || [];
  renderAdminDataGovernance();
}

async function resolveGovernanceIssue(id) {
  const item = (adminState.governance.issues || []).find((row) => String(row.id) === String(id));
  if (!item) return;
  const note = window.prompt("请输入处理说明（仅标记状态；如需更正主数据请先完成更正）：", "已人工核对");
  if (!note) return;
  try {
    await adminRequest(`/api/admin/data-quality/issues/${item.id}/resolve`, { method: "POST", body: JSON.stringify({ version: item.version, resolution_note: note }) });
    await refreshGovernanceQueues();
    showToast("质量问题已处理");
  } catch (error) { showToast(error.message); }
}

function confirmGovernanceClassification(id) {
  const item = (adminState.governance.classifications || []).find((row) => String(row.activity_id) === String(id));
  if (!item) return;
  const options = (values, current) => `<option value="" ${current ? "" : "selected"}>请选择</option>${values.map(([value, label]) => `<option value="${value}" ${value === current ? "selected" : ""}>${label}</option>`).join("")}`;
  const sourceType = String(item.source_op_type || "").toUpperCase();
  openAdminModal("补充分类信息", `
    <input type="hidden" name="classificationActivityId" value="${escapeHtml(item.activity_id)}" /><input type="hidden" name="classificationVersion" value="${escapeHtml(item.version)}" />
    <div class="admin-note-grid"><span><strong>${escapeHtml(item.op_code || "-")} / ${escapeHtml(item.op_sub || "-")}</strong><small>${escapeHtml(item.operation_details || "-")}</small></span><span><strong>原日报类型</strong><small>${escapeHtml(sourceType || "未提取，需要核对原表")}</small></span></div>
    <div class="admin-modal-form compact">
      <label>生产属性<select name="classificationProductive">${options([["PRODUCTION","生产"],["NON_PRODUCTION","非生产"]], item.productive_flag)}</select></label>
      <label>统计类型（仅用于纠错）<select name="classificationOpType">${options([["P","P"],["SC","SC"],["NPT","NPT"]], item.confirmed_op_type || sourceType)}</select></label>
      <label>工作量分类<select name="classificationBucket">${options([["OPERATION","作业"],["MOVE","搬迁"],["STANDBY_STAFFED","有人待工"],["STANDBY_UNSTAFFED","无人待工"],["FORCE_MAJEURE","不可抗力"],["MAINTENANCE","维修"]], item.work_bucket)}</select></label>
      <label>计费状态<select name="classificationBilling">${options([["FULL_RATE","全日费"],["PARTIAL_RATE","部分日费"],["ZERO_RATE","零日费"]], item.billing_status)}</select></label>
      <label>责任方<select name="classificationResponsibility">${options([["OURS","我方"],["CLIENT","甲方"],["THIRD_PARTY","第三方"],["FORCE_MAJEURE","不可抗力"]], item.responsibility)}</select></label>
      <label>原因编码<input name="classificationCause" value="${escapeHtml(item.cause_code || "")}" placeholder="设备、工具、人员、物资、社区、天气、事故" /></label>
      <label>服务线<input name="classificationServiceLine" value="${escapeHtml(item.service_line || "")}" /></label>
      <label class="wide">确认原因<input name="classificationReason" placeholder="必填" /></label>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button" type="button" data-save-classification-confirmation>保存分类</button>`
  );
}

async function saveGovernanceClassification() {
  const value = (name) => document.querySelector(`[name="${name}"]`)?.value || "";
  if (!value("classificationReason").trim()) return showToast("请填写确认原因");
  try {
    await adminRequest("/api/admin/time-classification/confirm", { method: "POST", body: JSON.stringify({
      activity_id: Number(value("classificationActivityId")), version: Number(value("classificationVersion")),
      productive_flag: value("classificationProductive"), confirmed_op_type: value("classificationOpType"),
      work_bucket: value("classificationBucket"), billing_status: value("classificationBilling"),
      responsibility: value("classificationResponsibility"), cause_code: value("classificationCause"),
      service_line: value("classificationServiceLine"), change_reason: value("classificationReason"),
    }) });
    closeAdminModal(); await refreshGovernanceQueues();
    showToast("分类信息已保存");
  } catch (error) { showToast(error.message); }
}

async function saveMasterAlias() {
  const host = document.querySelector('[data-admin-panel="dataGovernance"]');
  const aliasValue = host?.querySelector('[name="masterAliasValue"]')?.value.trim() || "";
  const reason = host?.querySelector('[name="masterAliasReason"]')?.value.trim() || "";
  const [entityType, entityId] = (host?.querySelector('[name="masterAliasTarget"]')?.value || "").split(":");
  if (!aliasValue || !entityType || !entityId || !reason) return showToast("请填写原始名称、标准实体和确认原因");
  try {
    await adminRequest("/api/admin/master-data/aliases", { method: "POST", body: JSON.stringify({
      entity_type: entityType, source_system: "manual", alias_value: aliasValue,
      id: Number(host?.querySelector('[name="masterAliasId"]')?.value || 0) || undefined,
      version: Number(host?.querySelector('[name="masterAliasVersion"]')?.value || 0) || undefined,
      entity_id: Number(entityId), confirmation_status: "confirmed",
      status: host?.querySelector('[name="masterAliasStatus"]')?.value || "active", change_reason: reason,
    }) });
    const response = await adminRequest("/api/admin/master-data/aliases?limit=1000");
    adminState.governance.aliases = response.items || [];
    showToast("别名已确认并立即生效");
    renderAdminDataGovernance();
  } catch (error) { showToast(error.message); }
}

function editMasterAlias(id) {
  const item = (adminState.governance.aliases || []).find((row) => String(row.id) === String(id));
  const host = document.querySelector('[data-admin-panel="dataGovernance"]');
  if (!item || !host) return;
  host.querySelector('[name="masterAliasId"]').value = item.id;
  host.querySelector('[name="masterAliasVersion"]').value = item.version;
  host.querySelector('[name="masterAliasValue"]').value = item.alias_value || "";
  host.querySelector('[name="masterAliasTarget"]').value = `${item.entity_type}:${item.entity_id}`;
  host.querySelector('[name="masterAliasStatus"]').value = item.status || "active";
  host.querySelector('[name="masterAliasReason"]').value = "";
  host.querySelector('[name="masterAliasReason"]').focus();
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
  const translationRunning = Number(adminState.translationQueue?.processing_count || 0) > 0;
  const extractionRunning = Number(adminState.aiExtractionQueue?.processing_count || 0) > 0;
  const jobsRunning = translationRunning || extractionRunning;
  const runningCount = Number(adminState.translationQueue?.processing_count || 0) + Number(adminState.aiExtractionQueue?.processing_count || 0);
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("模型配置", models.length, "公网 / 局域网 / 本地", "database")}
      ${adminKpi("已启用", enabledCount, "可被翻译任务调用", "overview")}
      ${adminKpi("默认模型", defaultAiModelName(), "日报翻译优先使用", "shield")}
      ${adminKpi("密钥存储", "本机JSON", "仅后端保存", "settings")}
    </section>
    <section class="panel">
      <div class="panel-heading">
        <div><h2>模型接入配置</h2><span class="panel-note">${jobsRunning ? `当前有 ${runningCount} 个运行任务；必须前往对应任务队列停止后，才能保存或切换默认模型` : "支持 OpenAI-Compatible 公网模型和局域网本地模型；保存后新任务使用默认启用模型"}</span></div>
        <div class="admin-actions">
          ${jobsRunning ? `<button class="button secondary small" type="button" data-admin-open-active-ai-jobs>查看运行任务 (${runningCount})</button>` : ""}
          <button class="button small" type="button" data-admin-new-ai-model ${jobsRunning ? "disabled" : ""}>新增模型</button>
        </div>
      </div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>配置名称</th><th>接口类型</th><th>API地址</th><th>模型名称</th><th>Think</th><th>超时</th><th>启用</th><th>默认</th><th>更新时间</th><th>操作</th></tr></thead>
        <tbody>${models.map(aiModelRow).join("") || `<tr><td colspan="10">暂无模型配置</td></tr>`}</tbody>
      </table></div>
    </section>
    <section class="admin-project-layout ai-model-layout">
      <section class="panel ai-model-config-panel">
        <div class="panel-heading"><h2>模型配置详情</h2><span class="panel-note">API Key 留空表示沿用已保存密钥；本地模型可不填 Key</span></div>
        ${aiModelForm(selected, jobsRunning)}
      </section>
      <section class="panel ai-model-test-panel">
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
    <td>${escapeHtml(thinkingModeLabel(model.thinking_mode))}</td>
    <td>${escapeHtml(model.timeout_seconds || 60)}s</td>
    <td><span class="status-pill ${model.enabled !== false ? "uploaded" : "failed"}">${model.enabled !== false ? "启用" : "停用"}</span></td>
    <td>${model.is_default ? "默认" : "-"}</td>
    <td>${escapeHtml(model.updated_at || "-")}</td>
    <td><button class="link-button" type="button" data-admin-edit-ai-model="${escapeHtml(model.id)}">编辑</button></td>
  </tr>`;
}

function aiModelForm(model = {}, jobsRunning = false) {
  const apiType = model.api_type || "openai-compatible";
  const isOllama = apiType === "ollama";
  const defaultOptions = model.is_default
    ? `<option value="true" selected>当前默认</option>`
    : `<option value="false" selected>非默认</option><option value="true">设为默认</option>`;
  return `<div class="ai-model-form">
    <input type="hidden" name="aiModelId" value="${escapeHtml(model.id || "")}" />
    <section class="ai-model-form-section">
      <div class="ai-model-form-heading"><strong>连接信息</strong><span>用于定位模型服务并完成身份验证</span></div>
      <div class="ai-model-form-grid connection-grid">
        <label class="ai-model-field">配置名称<input name="aiModelName" value="${escapeHtml(model.name || "")}" placeholder="例如：本地 Qwen" /></label>
        <label class="ai-model-field">接口类型<select name="aiModelApiType"><option value="openai-compatible" ${apiType !== "ollama" ? "selected" : ""}>OpenAI Compatible</option><option value="ollama" ${apiType === "ollama" ? "selected" : ""}>Ollama</option></select></label>
        <label class="ai-model-field full">API 地址<input name="aiModelBaseUrl" value="${escapeHtml(model.base_url || "")}" placeholder="${isOllama ? "http://127.0.0.1:11434" : "http://127.0.0.1:1234/v1"}" /><small data-ai-model-url-hint>${isOllama ? "填写 Ollama 服务根地址" : "OpenAI-Compatible 地址通常以 /v1 结尾"}</small></label>
        <label class="ai-model-field">模型名称<input name="aiModelModel" value="${escapeHtml(model.model || "")}" placeholder="qwen3.5-9b" /></label>
        <label class="ai-model-field ${isOllama ? "is-disabled" : ""}" data-ai-model-api-key-field>API Key<input name="aiModelApiKey" type="password" value="${model.api_key_set ? "********" : ""}" placeholder="${isOllama ? "Ollama 无需填写" : model.api_key_set ? "已保存，留空不改" : "本地服务可留空"}" ${isOllama ? "disabled" : ""} /><small>${isOllama ? "Ollama 调用不使用 API Key" : "仅发送给当前 OpenAI-Compatible 地址"}</small></label>
      </div>
    </section>
    <section class="ai-model-form-section">
      <div class="ai-model-form-heading"><strong>运行策略</strong><span>控制请求时限、翻译拆分和模型选择</span></div>
      <div class="ai-model-form-grid runtime-grid">
        <label class="ai-model-field">请求超时<input name="aiModelTimeout" type="number" min="5" max="600" value="${escapeHtml(model.timeout_seconds || 60)}" /><small>单次模型请求，5–600 秒</small></label>
        <label class="ai-model-field">翻译修复<input name="aiModelRetry" type="number" min="0" max="1" value="${escapeHtml(Math.min(1, model.retry_count ?? 1))}" /><small>最多一次定向修复或临时错误重试</small></label>
        <label class="ai-model-field">翻译分块上限<input name="aiModelChunkChars" type="number" min="0" max="8000" step="100" value="${escapeHtml(model.chunk_max_chars ?? 0)}" /><small>0=自动：兼容接口 2500，Ollama 6000</small></label>
        <label class="ai-model-field">Think 模式<select name="aiModelThinkingMode"><option value="disabled" ${model.thinking_mode === "disabled" ? "selected" : ""}>关闭（翻译推荐）</option><option value="enabled" ${model.thinking_mode === "enabled" ? "selected" : ""}>开启</option><option value="auto" ${!model.thinking_mode || model.thinking_mode === "auto" ? "selected" : ""}>跟随模型默认</option></select><small>关闭可减少延迟和推理 token</small></label>
        <label class="ai-model-field">启用状态<select name="aiModelEnabled"><option value="true" ${model.enabled !== false ? "selected" : ""}>启用</option><option value="false" ${model.enabled === false ? "selected" : ""}>停用</option></select><small>停用后不会被新任务调用</small></label>
        <label class="ai-model-field">默认模型<select name="aiModelDefault">${defaultOptions}</select><small>${model.is_default ? "切换默认模型时请编辑目标配置" : "设为默认后供新任务优先使用"}</small></label>
      </div>
    </section>
    <details class="ai-model-advanced">
      <summary>高级请求配置（JSON）</summary>
      <div class="ai-model-advanced-body">
        <div class="ai-model-config-path"><span>本机配置文件</span><code>outputs/ai_model_configs.json</code><small>页面不会回显原始 API Key；密钥仍只保存在后端文件中</small></div>
        <label class="ai-model-field">请求附加参数<textarea name="aiModelRequestOptions" rows="7" spellcheck="false" placeholder='{"thinking":{"type":"disabled"}}'>${escapeHtml(JSON.stringify(model.request_options || {}, null, 2))}</textarea><small>用于供应商专用参数；手动值优先于自动 Think 映射。model、messages、prompt、stream 和鉴权字段不可覆盖。</small></label>
      </div>
    </details>
    <div class="admin-actions ai-model-form-actions">
      <button class="button secondary" type="button" data-admin-test-ai-model>测试连接</button>
      <button class="button" type="button" data-admin-save-ai-models ${jobsRunning ? "disabled" : ""}>保存配置</button>
      <button class="button secondary" type="button" data-admin-delete-ai-model ${model.id && !jobsRunning ? "" : "disabled"}>删除</button>
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
  return { id: newClientId(), name: "新模型配置", api_type: "openai-compatible", base_url: "", model: "", timeout_seconds: 60, retry_count: 1, chunk_max_chars: 0, thinking_mode: "disabled", enabled: true, is_default: !(adminState.aiModels.models || []).length };
}

function thinkingModeLabel(value) {
  if (value === "disabled") return "关闭";
  if (value === "enabled") return "开启";
  return "默认";
}

function syncAiModelInterfaceFields(select) {
  const form = select?.closest(".ai-model-form");
  if (!form) return;
  const isOllama = select.value === "ollama";
  const keyField = form.querySelector("[data-ai-model-api-key-field]");
  const keyInput = keyField?.querySelector('input[name="aiModelApiKey"]');
  const keyHint = keyField?.querySelector("small");
  const urlInput = form.querySelector('input[name="aiModelBaseUrl"]');
  const urlHint = form.querySelector("[data-ai-model-url-hint]");
  keyField?.classList.toggle("is-disabled", isOllama);
  if (keyInput) {
    keyInput.disabled = isOllama;
    keyInput.placeholder = isOllama ? "Ollama 无需填写" : "本地服务可留空";
  }
  if (keyHint) keyHint.textContent = isOllama ? "Ollama 调用不使用 API Key" : "仅发送给当前 OpenAI-Compatible 地址";
  if (urlInput) urlInput.placeholder = isOllama ? "http://127.0.0.1:11434" : "http://127.0.0.1:1234/v1";
  if (urlHint) urlHint.textContent = isOllama ? "填写 Ollama 服务根地址" : "OpenAI-Compatible 地址通常以 /v1 结尾";
}

function apiTypeLabel(value) {
  return value === "ollama" ? "Ollama" : "OpenAI Compatible";
}

function defaultAiModelName() {
  const found = (adminState.aiModels.models || []).find((item) => item.id === adminState.aiModels.default_model_id);
  return found?.name || "-";
}

function openActiveAiJobsModal() {
  const translations = (adminState.translationQueue?.records || []).filter((item) => ["QUEUED", "IN_PROGRESS"].includes(String(item.status || "").toUpperCase()));
  const extractions = (adminState.aiExtractionQueue?.records || []).filter((item) => ["QUEUED", "IN_PROGRESS"].includes(String(item.status || "").toUpperCase()));
  const section = (title, rows, kind) => `<section class="active-ai-job-section">
    <div class="panel-heading"><div><h3>${title}</h3><span class="panel-note">${rows.length} 条运行中</span></div></div>
    <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>日期 / 报告号</th><th>井号</th><th>队伍</th><th>状态</th><th>进度</th></tr></thead>
      <tbody>${rows.map((row) => `<tr><td>${escapeHtml(row.report_date || "-")}<small class="table-subtext">${escapeHtml(row.report_no || "-")}</small></td><td>${escapeHtml(row.wellbore || "-")}</td><td>${escapeHtml(row.rig || "-")}</td><td><span class="status-pill processing">${kind === "translation" ? translationQueueStatusLabel(row.status) : aiQueueStatusLabel(row.status)}</span></td><td>${escapeHtml(row.progress || "0")}%</td></tr>`).join("") || `<tr><td colspan="5">当前没有运行任务</td></tr>`}</tbody>
    </table></div>
  </section>`;
  openAdminModal(
    `正在运行的 AI 任务（${translations.length + extractions.length}）`,
    `<div class="active-ai-job-list">${section("日报翻译", translations, "translation")}${section("数据提炼", extractions, "extraction")}</div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>关闭</button>
     ${translations.length ? `<button class="button secondary" type="button" data-admin-jump-ai-queue="translation">前往翻译任务</button>` : ""}
     ${extractions.length ? `<button class="button" type="button" data-admin-jump-ai-queue="extraction">前往提炼任务</button>` : ""}`
  );
}

function jumpToAiJobQueue(kind) {
  closeAdminModal();
  if (kind === "extraction") {
    adminState.aiExtractionView = "queue";
    switchAdminTab("aiExtraction");
    return renderAdminAiExtraction();
  }
  adminState.translationTuningView = "queue";
  switchAdminTab("translationTuning");
  renderAdminTranslationTuning();
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
        <h2>AI 数据提炼规则</h2>
        <div class="admin-actions heading-actions">
          <label class="auto-execute-toggle" title="首次上传、重新上传或人工修正提炼来源数据后自动更新；无相关变化时不会重复调用模型。关闭后需在任务队列手动执行。">
            <input type="checkbox" name="aiExtractionAutoExecute" ${config.auto_execute !== false ? "checked" : ""} />
            <span class="auto-execute-switch" aria-hidden="true"></span>
            <span>数据变更后自动提炼</span>
          </label>
          <button class="button small" type="button" data-admin-new-extraction-rule>新增规则</button>
        </div>
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
      ${aiExtractionTab("rules", "规则配置")}${aiExtractionTab("queue", "任务队列", queue.processing_count)}${aiExtractionTab("test", "测试工作台")}
    </nav>
    <div class="translation-tuning-content">${content}</div>`;
}

function aiExtractionTab(value, label, runningCount = null) {
  const count = runningCount === null ? "" : `<span class="tuning-tab-count" data-tuning-queue-count="extraction">${Number(runningCount || 0)}</span>`;
  return `<button type="button" class="${adminState.aiExtractionView === value ? "active" : ""}" data-ai-extraction-view="${value}">${label}${count}</button>`;
}

function aiQueueStatusGroup(status = "", row = {}) {
  const value = String(status || "PENDING").toUpperCase();
  if (value === "FAILED") return "failed";
  if (["QUEUED", "IN_PROGRESS"].includes(value)) return "processing";
  if (row.needs_translation || row.needs_extraction) return "pending";
  if (value === "COMPLETED") return "completed";
  if (["PENDING", "STOPPED", "STALE", ""].includes(value)) return "pending";
  return "other";
}

function filterAiQueueRecords(records = [], tab = "all") {
  return tab === "all" ? records : records.filter((row) => aiQueueStatusGroup(row.status, row) === tab);
}

function preferredExtractionQueueStatusTab(records = [], currentTab = "pending") {
  if (filterAiQueueRecords(records, currentTab).length) return currentTab;
  return ["pending", "processing", "failed", "completed"].find((tab) => filterAiQueueRecords(records, tab).length) || currentTab;
}

function aiQueueStatusTabsMarkup(kind, records = [], activeTab = "pending") {
  const counts = { all: records.length, pending: 0, processing: 0, failed: 0, completed: 0 };
  records.forEach((row) => {
    const group = aiQueueStatusGroup(row.status, row);
    if (counts[group] !== undefined) counts[group] += 1;
  });
  const labels = { all: "全部", pending: "未处理", processing: "进行中", failed: "失败", completed: "已完成" };
  return `<nav class="queue-status-tabs" aria-label="任务状态筛选">${Object.entries(labels).map(([value, label]) => `<button type="button" class="${activeTab === value ? "active" : ""}" data-ai-queue-status-tab="${kind}" data-ai-queue-status-value="${value}">${label}<span data-ai-queue-status-count="${kind}:${value}">${counts[value]}</span></button>`).join("")}</nav>`;
}

function aiExtractionQueueMarkup() {
  const queue = adminState.aiExtractionQueue || {};
  const rows = queue.records || [];
  const statusTab = adminState.aiExtractionQueueStatusTab || "pending";
  const filteredRows = filterAiQueueRecords(rows, statusTab);
  const pageSize = Number(adminState.aiExtractionQueuePageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const currentPage = clampPage(adminState.aiExtractionQueuePage, totalPages);
  adminState.aiExtractionQueuePage = currentPage;
  const visibleRows = filteredRows.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  return `<div class="ai-queue-stack"><section class="panel">
    <div class="panel-heading"><h2>数据提炼任务</h2>
      <div class="admin-actions heading-actions" data-extraction-queue-actions>${extractionQueueActionsMarkup(queue)}</div>
    </div>
    ${aiQueueStatusTabsMarkup("extraction", rows, statusTab)}
    <div class="table-wrap"><table class="record-table admin-table queue-select-table"><thead><tr><th><input type="checkbox" data-ai-extraction-check-all ${statusTab === "completed" && visibleRows.length ? "checked" : ""} /></th><th>日期 / 井号</th><th>井队</th><th>状态</th><th>进度</th><th>更新时间</th></tr></thead>
      <tbody data-extraction-queue-body>${extractionQueueRowsMarkup(visibleRows, statusTab === "completed")}</tbody>
    </table></div>
    <div data-extraction-queue-pagination>${adminPaginationMarkup("aiExtractionQueue", filteredRows.length, currentPage, totalPages, pageSize)}</div>
  </section>${aiJobMonitorPanelMarkup("extraction")}</div>`;
}

function extractionQueueRowsMarkup(rows = [], selectCompleted = false) {
  return rows.map((row) => {
    const checked = row.needs_extraction || (selectCompleted && aiQueueStatusGroup(row.status, row) === "completed");
    return `<tr><td><input type="checkbox" data-ai-extraction-record value="${escapeHtml(row.record_id)}" ${checked ? "checked" : ""} /></td><td><strong>${escapeHtml(row.report_date || "-")} / ${escapeHtml(row.wellbore || "-")}</strong><small>${escapeHtml(row.report_no || "")}</small></td><td>${escapeHtml(row.rig || "-")}</td><td data-extraction-job-status="${escapeHtml(row.record_id)}">${extractionJobStatusMarkup(row)}</td><td data-extraction-job-progress="${escapeHtml(row.record_id)}">${escapeHtml(row.progress || "0")}%</td><td data-extraction-job-updated="${escapeHtml(row.record_id)}">${escapeHtml(row.updated_at || "-")}</td></tr>`;
  }).join("") || `<tr><td colspan="6">当前状态下没有日报任务</td></tr>`;
}

function extractionQueueActionsMarkup(queue = {}) {
  const tab = adminState.aiExtractionQueueStatusTab || "pending";
  if (tab === "processing") return `<button class="button secondary small" type="button" data-admin-stop-extractions ${Number(queue.processing_count || 0) ? "" : "disabled"}>停止进行中任务</button>`;
  if (tab === "completed") return `<button class="button small" type="button" data-admin-queue-extractions="overwrite">重新提炼选中</button>`;
  if (tab === "failed") return `<button class="button small" type="button" data-admin-queue-extractions="continue">重新提炼选中</button>`;
  if (tab === "pending") return `<button class="button small" type="button" data-admin-queue-extractions="continue">开始提炼选中</button>`;
  return `<span class="panel-note">请选择具体任务状态后执行批量操作</span>`;
}

function extractionJobStatusMarkup(row = {}) {
  return `<span class="status-pill ${aiQueueStatusTone(row.status)}" title="${escapeHtml(row.error || "")}">${escapeHtml(aiQueueStatusLabel(row.status))}</span>`;
}

function aiQueueStatusLabel(status = "") {
  return ({ PENDING: "待提炼", STOPPED: "已停止", QUEUED: "排队中", IN_PROGRESS: "提炼中", COMPLETED: "已提炼", FAILED: "失败", STALE: "规则已更新", NOT_REQUIRED: "无需提炼" })[String(status).toUpperCase()] || "待提炼";
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
    <div class="admin-actions wide"><button class="button" type="button" data-admin-save-extraction-rules ${Number(adminState.aiExtractionQueue?.processing_count || 0) ? "disabled" : ""}>保存规则</button><button class="button secondary" type="button" data-admin-delete-extraction-rule>删除规则</button></div>
  </div>`;
}

function aiExtractionTestMarkup() {
  const selectedRule = (adminState.aiExtraction.rules || []).find((item) => item.id === adminState.selectedAiExtractionRuleId) || {};
  const matchingRecords = (adminState.records || []).filter((record) => !selectedRule.report_type || selectedRule.report_type === "all" || record.report_type === selectedRule.report_type);
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
  renderAdminProjectRelationships(host);
}

function renderAdminProjectRelationships(host) {
  if (!host) return;
  const data = adminState.governance || {};
  const projects = data.projects || [];
  const teams = data.teams || [];
  const contracts = data.contracts || [];
  const assignments = data.assignments || [];
  const wellAssignments = data.wellAssignments || [];
  const contractById = new Map(contracts.map((item) => [String(item.id), item]));
  const projectById = new Map(projects.map((item) => [String(item.id), item]));
  const teamById = new Map(teams.map((item) => [String(item.id), item]));
  const wellById = new Map((data.wells || []).map((item) => [String(item.id), item]));
  const activeTeams = assignments.filter((item) => item.status === "active");
  const activeWells = wellAssignments.filter((item) => item.status === "active");
  const conflictTeamIds = projectTeamConflictIds(activeTeams);
  const projectRows = projects.map((project) => {
    const contract = contractById.get(String(project.contract_id)) || {};
    const projectTeams = activeTeams.filter((item) => String(item.project_id) === String(project.id));
    const projectWells = activeWells.filter((item) => String(item.project_id) === String(project.id));
    return `<tr><td><strong>${escapeHtml(project.project_name || project.project_code)}</strong><small>${escapeHtml(project.project_code)}</small></td>
      <td>${escapeHtml(contract.contract_no || "-")}</td><td>${escapeHtml(projectTypeLabel(project.project_type))}</td>
      <td>${escapeHtml(project.npt_allowance_hours ?? "-")} h</td><td>${escapeHtml(projectPeriodText({ start_date: project.valid_from, end_date: project.valid_to }))}</td>
      <td><span class="status-pill ${project.status === "active" ? "uploaded" : "failed"}">${project.status === "active" ? "启用" : "停用"}</span></td>
      <td>${projectTeams.length} 队 / ${projectWells.length} 井</td><td><button class="link-button" type="button" data-admin-edit-project-master="${escapeHtml(project.id)}">编辑项目</button><button class="link-button" type="button" data-admin-edit-project="${escapeHtml(project.id)}">维护关系</button></td></tr>`;
  }).join("");
  const teamRows = teams.map((team) => {
    const rows = activeTeams.filter((item) => String(item.team_id) === String(team.id));
    const projectNames = rows.map((item) => projectById.get(String(item.project_id))?.project_name || item.project_id);
    const periods = rows.map((item) => `${String(item.valid_from || "").slice(0, 10)} 至 ${String(item.valid_to || "长期").slice(0, 10)}`);
    return `<tr><td><strong>${escapeHtml(team.team_name || team.team_code)}</strong><small>${escapeHtml(team.team_code)}</small></td>
      <td>${escapeHtml(projectNames.join("、") || "未派遣")}</td><td>${periods.map(escapeHtml).join("<br>") || "-"}</td>
      <td><span class="status-pill ${conflictTeamIds.has(String(team.id)) ? "failed" : "uploaded"}">${conflictTeamIds.has(String(team.id)) ? "有效期冲突" : "正常"}</span></td><td>${escapeHtml(team.status || "-")}</td></tr>`;
  }).join("");
  const wellRows = activeWells.map((item) => `<tr><td><strong>${escapeHtml(wellById.get(String(item.well_id))?.well_name || item.well_id)}</strong></td>
    <td>${escapeHtml(projectById.get(String(item.project_id))?.project_name || item.project_id)}</td><td>${escapeHtml(item.job_type || "全部作业")}</td>
    <td>${escapeHtml(String(item.valid_from || "").slice(0, 10))} 至 ${escapeHtml(item.valid_to ? String(item.valid_to).slice(0, 10) : "长期")}</td></tr>`).join("");
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("项目", projects.length, `${projects.filter((item) => item.status === "active").length} 个启用`, "database")}
      ${adminKpi("标准队伍", teams.length, "来自主数据", "users")}
      ${adminKpi("有效派遣", activeTeams.length, "项目 ↔ 队伍", "overview")}
      ${adminKpi("关系冲突", conflictTeamIds.size, `${activeWells.length} 个有效井范围`, "logs")}
    </section>
    <section class="panel">
      <div class="panel-heading"><div><h2>项目关系维护</h2><span class="panel-note">按项目集中维护队伍派遣和井范围；队伍和井属性请到“主数据管理”修改</span></div><button class="button small" type="button" data-admin-new-project>新增项目</button></div>
      <div class="table-wrap"><table class="record-table admin-table project-table"><thead><tr><th>项目</th><th>合同号</th><th>项目类型</th><th>允许 NPT</th><th>项目周期</th><th>状态</th><th>队伍 / 井</th><th>操作</th></tr></thead><tbody>${projectRows || `<tr><td colspan="8">暂无项目主数据</td></tr>`}</tbody></table></div>
    </section>
    <section class="panel"><div class="panel-heading"><h2>队伍派遣总览</h2><span class="panel-note">一个队伍在同一有效时段只能归属一个项目；采用 [开始, 结束) 有效期</span></div>
      <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>队伍</th><th>归属项目</th><th>有效期</th><th>关系状态</th><th>主数据状态</th></tr></thead><tbody>${teamRows || `<tr><td colspan="5">暂无队伍主数据</td></tr>`}</tbody></table></div>
    </section>
    <section class="panel"><div class="panel-heading"><h2>项目井范围总览</h2><span class="panel-note">井级范围优先于仅按井队匹配</span></div>
      <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>井</th><th>归属项目</th><th>作业类型</th><th>有效期</th></tr></thead><tbody>${wellRows || `<tr><td colspan="4">暂无项目井范围</td></tr>`}</tbody></table></div>
    </section>`;
}

function projectTeamConflictIds(assignments = []) {
  const conflicts = new Set();
  assignments.forEach((left, index) => {
    assignments.slice(index + 1).forEach((right) => {
      if (String(left.team_id) !== String(right.team_id)) return;
      const leftStart = new Date(left.valid_from).getTime();
      const rightStart = new Date(right.valid_from).getTime();
      const leftEnd = left.valid_to ? new Date(left.valid_to).getTime() : Number.POSITIVE_INFINITY;
      const rightEnd = right.valid_to ? new Date(right.valid_to).getTime() : Number.POSITIVE_INFINITY;
      if (leftStart < rightEnd && rightStart < leftEnd) conflicts.add(String(left.team_id));
    });
  });
  return conflicts;
}

function projectPeriodText(project = {}) {
  return `${project.start_date || "-"} 至 ${project.end_date || "-"}`;
}

function renderAdminTranslationTuning() {
  const host = document.querySelector('[data-admin-panel="translationTuning"]');
  if (!host) return;
  const tuning = adminState.translationTuning || {};
  const terms = adminState.translationTerms?.terms || [];
  const enabledFields = (tuning.scope_rules || []).filter((item) => item.enabled !== false).length;
  const pendingCount = Number(adminState.translationQueue?.pending_count || 0);
  const view = adminState.translationTuningView || "fields";
  const content = view === "terms" ? translationTermsMarkup() : view === "queue" ? translationQueuePanelMarkup() : view === "test" ? translationTestWorkbenchMarkup() : view === "memory" ? translationMemoryAndLogsMarkup() : translationFieldPoliciesMarkup();
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
      ${translationTuningTab("queue", "任务队列", adminState.translationQueue?.processing_count)}
      ${translationTuningTab("test", "测试工作台")}
      ${translationTuningTab("memory", "经验闭环", adminState.translationExperience?.counts?.PENDING)}
    </nav>
    <div class="translation-tuning-content">${content}</div>`;
}

function translationTuningTab(value, label, runningCount = null) {
  const count = runningCount === null ? "" : `<span class="tuning-tab-count" data-tuning-queue-count="translation">${Number(runningCount || 0)}</span>`;
  return `<button type="button" class="${adminState.translationTuningView === value ? "active" : ""}" data-translation-tuning-view="${value}">${label}${count}</button>`;
}

function translationLanguageNames(values = []) {
  const labels = { "zh-CN": "中文" };
  return values.map((value) => labels[value] || value).join(" / ") || "未配置";
}

function translationQueuePanelMarkup() {
  const queue = adminState.translationQueue || {};
  const records = queue.records || [];
  const statusTab = adminState.translationQueueStatusTab || "pending";
  const filteredRecords = filterAiQueueRecords(records, statusTab);
  const pageSize = Number(adminState.translationQueuePageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(filteredRecords.length / pageSize));
  const currentPage = clampPage(adminState.translationQueuePage, totalPages);
  adminState.translationQueuePage = currentPage;
  const visibleRecords = filteredRecords.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  return `<div class="ai-queue-stack"><section class="panel"><div class="panel-heading"><h2>日报翻译任务</h2><div class="admin-actions heading-actions" data-translation-queue-actions>${translationQueueActionsMarkup(queue)}</div></div>
    ${aiQueueStatusTabsMarkup("translation", records, statusTab)}
    <div class="table-wrap"><table class="record-table admin-table queue-select-table"><thead><tr><th><input type="checkbox" data-translation-queue-select-all /></th><th>类型</th><th>日期 / 报告号</th><th>井号</th><th>队伍</th><th>状态</th><th>原因</th></tr></thead><tbody data-translation-queue-body>${translationQueueRowsMarkup(visibleRecords)}</tbody></table></div>
    <div data-translation-queue-pagination>${adminPaginationMarkup("translationQueue", filteredRecords.length, currentPage, totalPages, pageSize)}</div>
  </section>${aiJobMonitorPanelMarkup("translation")}</div>`;
}

function translationQueueRowsMarkup(records = []) {
  return records.map(translationQueueRowMarkup).join("") || `<tr><td colspan="7">当前状态下没有日报任务</td></tr>`;
}

function translationQueueActionsMarkup(queue = {}) {
  const tab = adminState.translationQueueStatusTab || "pending";
  if (tab === "processing") return `<button class="button secondary small" type="button" data-admin-stop-translations ${Number(queue.processing_count || 0) ? "" : "disabled"}>停止进行中任务</button>`;
  if (tab === "completed") return `<button class="button small" type="button" data-admin-queue-selected="overwrite">重新翻译选中</button>`;
  if (tab === "failed") return `<button class="button small" type="button" data-admin-queue-selected="continue">重新翻译选中</button>`;
  if (tab === "pending") return `<button class="button small" type="button" data-admin-queue-selected="continue">开始翻译选中</button>`;
  return `<button class="button secondary small" type="button" data-admin-reset-translations>清空全部译文</button>`;
}

function aiJobMonitorPanelMarkup(kind) {
  const label = kind === "translation" ? "翻译模型运行监控" : "提炼模型运行监控";
  const events = adminState.aiJobMonitor?.[kind] || [];
  return `<section class="panel ai-job-monitor-panel">
    <div class="panel-heading"><h2><span class="monitor-live-dot" aria-hidden="true"></span>${label}</h2><span class="monitor-updated" data-ai-job-monitor-updated="${kind}">${monitorUpdatedLabel(adminState.aiJobMonitor?.updatedAt?.[kind])}</span></div>
    <div class="ai-job-monitor-stream" data-ai-job-monitor-body="${kind}">${aiJobMonitorRowsMarkup(kind, events)}</div>
  </section>`;
}

function aiJobMonitorRowsMarkup(kind, events = []) {
  const rows = [...events].reverse();
  if (!rows.length) return `<div class="admin-empty-panel"><p>等待模型调用事件。任务运行后会在这里显示输入和返回。</p></div>`;
  return rows.map((event) => {
    const eventName = String(event.event || "");
    const tone = eventName === "response" ? "success" : eventName === "error" ? "failed" : "running";
    const stage = eventName === "response" ? "已返回" : eventName === "error" ? "调用失败" : eventName === "retry" ? "自动重试" : "请求中";
    const model = event.model_name || event.model_config_id || event.engine || "默认模型";
    const elapsed = Number(event.elapsed_ms);
    const source = event.source_preview || (eventName === "request"
      ? "本次请求未记录文本预览"
      : "发送数据见下方对应的请求记录");
    const output = event.error || event.response_preview || (eventName === "request"
      ? "等待模型返回…"
      : eventName === "response" && kind === "extraction"
        ? "无充分证据，模型返回空值（未识别责任方）"
        : eventName === "response"
          ? "模型返回空内容"
          : "-");
    return `<article class="ai-job-monitor-row ${tone}">
      <div class="monitor-event-meta"><span class="monitor-stage ${tone}">${stage}</span><time>${monitorTimeLabel(event.time)}</time><strong>${escapeHtml(event.record_id || "-")}</strong><span>${escapeHtml(model)}</span>${Number.isFinite(elapsed) ? `<span>${(elapsed / 1000).toFixed(1)}s</span>` : ""}</div>
      <div class="monitor-event-content"><div><small>发送数据${event.source_chars ? ` · ${escapeHtml(event.source_chars)} 字符` : ""}</small><p>${escapeHtml(source)}</p></div><div><small>模型返回</small><p>${escapeHtml(output)}</p></div></div>
    </article>`;
  }).join("");
}

function monitorTimeLabel(value) {
  const parsed = new Date(value || "");
  return Number.isNaN(parsed.getTime()) ? "-" : parsed.toLocaleTimeString("zh-CN", { hour12: false });
}

function monitorUpdatedLabel(value) {
  if (!value) return "等待刷新";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? "刚刚刷新" : `更新于 ${parsed.toLocaleTimeString("zh-CN", { hour12: false })}`;
}

function translationFieldPoliciesMarkup() {
  const tuning = adminState.translationTuning || {};
  const prompt = tuning.prompt || {};
  const protections = tuning.protections || {};
  const rules = tuning.scope_rules || [];
  const pageSize = Number(adminState.translationScopePageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const pageCount = Math.max(1, Math.ceil(rules.length / pageSize));
  adminState.translationScopePage = clampPage(adminState.translationScopePage, pageCount);
  const start = (adminState.translationScopePage - 1) * pageSize;
  const visibleRules = rules.slice(start, start + pageSize);
  return `
    <section class="panel tuning-policy-panel">
      <div class="panel-heading">
        <h2>翻译策略</h2>
        <div class="admin-actions heading-actions">
          <label class="auto-execute-toggle" title="开启后，上传日报会自动加入翻译任务队列；同一日报重新上传时会清除该记录的旧译文并重新翻译。">
            <input type="checkbox" name="translationAutoOnUpload" ${tuning.auto_translate_on_upload ? "checked" : ""} />
            <span class="auto-execute-switch" aria-hidden="true"></span>
            <span>上传后自动翻译</span>
          </label>
          <button class="button small" type="button" data-admin-save-translation-tuning ${Number(adminState.translationQueue?.processing_count || 0) ? "disabled" : ""}>保存策略</button>
        </div>
      </div>
      <div class="tuning-policy-layout">
        <div class="tuning-prompt-form">
          <label>系统角色<textarea name="translationSystemPrompt" rows="3" maxlength="1200">${escapeHtml(prompt.system_prompt || "")}</textarea></label>
          <label>翻译要求<textarea name="translationInstruction" rows="4" maxlength="2400">${escapeHtml(prompt.translation_instruction || "")}</textarea></label>
          <details class="prompt-preview"><summary>按业务类型补充 Prompt</summary><div class="business-prompt-grid">${businessPromptTemplatesMarkup(tuning.prompt_templates || {})}</div></details>
        </div>
        <div class="tuning-option-panel">
          <fieldset><legend>目标语言</legend>${translationTargetOptions(tuning.target_languages || [])}</fieldset>
          <fieldset><legend>内容保护方式</legend>${translationProtectionModeOptions(protections)}</fieldset>
          <fieldset><legend>全局保护范围</legend>${translationProtectionOptions(protections)}</fieldset>
          <p>“上下文翻译”负责结合完整事项、作业关系和命中术语理解原文；“结果校验”负责核对数字、日期、单位和必保专名。两项可独立启用，建议同时开启。日期输出格式直接遵循上方翻译要求，不再维护重复设置。</p>
          <p>全局保护开关与术语词库中的对应类别关联：取消后不再加入对应必保项或校验；术语表中单独设为“严格保护词”的条目始终生效。</p>
        </div>
      </div>
      ${translationScopeBuilderMarkup()}
      <div class="table-wrap tuning-field-table-wrap">
        <table class="record-table admin-table tuning-field-table">
          <thead><tr><th>日报类型</th><th>模块 / 部分</th><th>字段</th><th>字段编码</th><th>处理方式</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>${visibleRules.map((rule) => `<tr data-translation-scope-rule="${escapeHtml(rule.id)}">
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
      ${adminPaginationMarkup("translationScope", rules.length, adminState.translationScopePage, pageCount, pageSize)}
    </section>`;
}

function businessPromptTemplatesMarkup(templates = {}) {
  return [["drilling", "钻井（含搬迁）"], ["completion", "完井"], ["workover", "修井"]]
    .map(([value, label]) => `<label>${label}<textarea name="translationBusinessPrompt" data-report-type="${value}" rows="3" maxlength="1200">${escapeHtml(templates[value] || "")}</textarea></label>`)
    .join("");
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

function translationProtectionModeOptions(protections = {}) {
  return [
    ["contextual_translation", "上下文翻译", protections.contextual_translation !== false],
    ["validate_results", "结果校验", protections.validate_results !== false],
  ].map(([value, label, checked]) => `<label><input type="checkbox" name="translationProtectionMode" value="${value}" ${checked ? "checked" : ""} />${label}</label>`).join("");
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
  const pageSize = Number(adminState.translationTermPageSize || ADMIN_DEFAULT_PAGE_SIZE);
  const pageCount = Math.max(1, Math.ceil(filteredTerms.length / pageSize));
  adminState.translationTermPage = Math.min(Math.max(1, adminState.translationTermPage || 1), pageCount);
  const start = (adminState.translationTermPage - 1) * pageSize;
  const visibleTerms = filteredTerms.slice(start, start + pageSize);
  return `
    <section class="panel">
      <div class="panel-heading tuning-term-heading">
        <h2>术语词库</h2>
        <div class="admin-actions tuning-term-actions"><input type="file" accept=".xlsx,.xls,.xlsm,.xltx,.xltm" data-translation-term-file hidden /><a class="button secondary small" href="/api/admin/translation-terms/template">下载模板</a><button class="button secondary small" type="button" data-admin-import-translation-terms ${adminState.translationTermImport.running ? "disabled" : ""}>${adminState.translationTermImport.running ? "分析中..." : "导入 Excel"}</button><a class="button secondary small" href="/api/admin/translation-terms/export">导出 Excel</a><button class="button small" type="button" data-admin-add-translation-term>新增术语</button></div>
      </div>
      ${translationTermImportSummaryMarkup()}
      <div class="translation-term-toolbar"><input class="tuning-term-search" type="search" value="${escapeHtml(adminState.translationTermSearch)}" placeholder="搜索中文、英文或西班牙语" aria-label="搜索术语" data-translation-term-search /><div class="translation-term-segments" role="group" aria-label="作业类型筛选">${translationTermCategorySegments(category)}</div></div>
      <div class="table-wrap tuning-term-table-wrap"><table class="record-table admin-table tuning-term-table">
        <thead><tr><th>作业类型</th><th>术语类型</th><th>中文</th><th>English</th><th>Español</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>${visibleTerms.map(translationTermListRow).join("") || `<tr><td colspan="7">没有匹配的术语</td></tr>`}</tbody>
      </table></div>
      ${adminPaginationMarkup("translationTerms", filteredTerms.length, adminState.translationTermPage, pageCount, pageSize, "translation-term-pagination")}
    </section>
    <section class="panel tuning-protection-panel">
      <div class="panel-heading"><div><h2>全局保护项</h2><span class="panel-note">缩写、单位和专名会随 Prompt 发送给模型并要求保持原样</span></div><button class="button small" type="button" data-admin-save-translation-terms>保存保护项</button></div>
      ${protectedTermsMarkup()}
    </section>`;
}

function translationTermCategoryLabel(value = "general") {
  return { general: "通用", drilling: "钻井（含搬迁）", completion: "完井", workover: "修井" }[value] || "通用";
}

function translationTermTypeLabel(value = "preferred") {
  return { protected: "严格保护", preferred: "标准术语", contextual: "上下文术语", phrase: "行业短语" }[value] || "标准术语";
}

function translationTermTypeOptions(selected = "preferred") {
  return [["protected", "严格保护词"], ["preferred", "固定标准术语"], ["contextual", "上下文术语"], ["phrase", "行业短语"]]
    .map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`).join("");
}

function translationTermCategoryOptions(selected = "general", includeAll = false) {
  const options = [["general", "通用"], ["drilling", "钻井（含搬迁）"], ["completion", "完井"], ["workover", "修井"]];
  return `${includeAll ? `<option value="all" ${selected === "all" ? "selected" : ""}>全部作业类型</option>` : ""}${options.map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`).join("")}`;
}

function translationTermCategorySegments(selected = "all") {
  const options = [["all", "全部"], ["general", "通用"], ["drilling", "钻井（含搬迁）"], ["completion", "完井"], ["workover", "修井"]];
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
    <td><span class="type-pill">${escapeHtml(translationTermCategoryLabel(term.category))}</span></td><td><span class="type-pill">${escapeHtml(translationTermTypeLabel(term.term_type))}</span></td><td><strong>${escapeHtml(term.zh || "-")}</strong></td><td>${escapeHtml(term.en || "-")}</td><td>${escapeHtml(term.es || "-")}</td>
    <td><span class="status-pill ${term.enabled !== false ? "uploaded" : "failed"}">${term.enabled !== false ? (term.strict_preserve ? "启用 / 严格" : "启用") : "停用"}</span></td>
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
      <div class="admin-actions"><button class="button" type="button" data-admin-run-translation-test ${adminState.translationTestRunning ? "disabled" : ""}>${adminState.translationTestRunning ? "测试中..." : "运行单条测试"}</button><button class="button secondary" type="button" data-admin-run-translation-batch-test ${adminState.translationTestRunning ? "disabled" : ""}>运行 6 条批量稳定性测试</button></div>
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
  const matchedTerms = Array.isArray(result.matched_terms) ? result.matched_terms : [];
  const protectedTerms = Array.isArray(result.protected_terms) ? result.protected_terms : [];
  return `<div class="translation-test-result ${result.ok ? "success" : "failed"}">
    <div class="translation-output-text"><span>译文</span><p>${escapeHtml(result.translated_text || result.error || "模型未返回译文")}</p></div>
    <div class="translation-test-meta"><span>上下文 <strong>${result.contextual_translation === false ? "关闭" : "开启"}</strong></span><span>结果校验 <strong>${result.validate_results === false ? "关闭" : "开启"}</strong></span><span>源语言 <strong>${escapeHtml(result.source_language || "-")}</strong></span><span>目标语言 <strong>${escapeHtml(result.target_language || "-")}</strong></span><span>Prompt版本 <strong>${escapeHtml(result.prompt_version || "-")}</strong></span><span>测试规模 <strong>${escapeHtml(result.batch_size || 1)} 条</strong></span><span>Prompt <strong>${escapeHtml(result.prompt_chars || 0)} 字符</strong></span><span>内部保护标记 <strong>${escapeHtml(result.placeholder_count || 0)}</strong></span></div>
    <details class="prompt-preview"><summary>实际送模原文</summary><pre>${escapeHtml(result.request_source_text || "-")}</pre></details>
    <div class="translation-test-diagnostics"><div><strong>命中术语</strong><p>${matchedTerms.length ? matchedTerms.map((term) => `${escapeHtml(term.source)} → ${escapeHtml(term.target)}（${escapeHtml(translationTermTypeLabel(term.type))}）`).join("<br>") : "无"}</p></div><div><strong>严格保护项</strong><p>${protectedTerms.length ? protectedTerms.map(escapeHtml).join("、") : "无"}</p></div></div>
    <div class="translation-checks">${(result.checks || []).map((check) => `<div class="${escapeHtml(check.status || "warning")}"><span aria-hidden="true"></span><div><strong>${escapeHtml(check.label)}</strong>${check.detail ? `<small>${escapeHtml(check.detail)}</small>` : ""}</div></div>`).join("")}</div>
  </div>`;
}

function translationMemoryAndLogsMarkup() {
  const memory = adminState.translationMemory || { entries: [], loading: false };
  const experience = adminState.translationExperience || { suggestions: [], counts: {}, loading: false };
  const suggestions = experience.suggestions || [];
  const actionable = suggestions.filter((item) => ["PENDING", "QUEUED", "APPLIED"].includes(String(item.status || "")));
  const verified = suggestions.filter((item) => item.status === "VERIFIED").slice(0, 12);
  return `<div class="translation-knowledge-layout">
    <section class="panel translation-experience-panel">
      <div class="panel-heading"><div><h2>翻译错误记录</h2><span class="panel-note">自动归因并合并同类问题；不会自动修改正式 Prompt</span></div><button class="button secondary small" type="button" data-admin-refresh-translation-knowledge>刷新</button></div>
      <div class="experience-flow" aria-label="经验处理流程"><span>1 自动归因</span><span>2 合并同类问题</span><span>3 人工决定</span><span>4 重跑确认</span></div>
      <div class="experience-summary"><strong>${Number(experience.counts?.PENDING || 0)}</strong><span>待处理建议</span><strong>${Number(experience.counts?.QUEUED || 0) + Number(experience.counts?.APPLIED || 0)}</strong><span>排队/验证中</span><strong>${Number(experience.counts?.VERIFIED || 0)}</strong><span>已验证经验</span></div>
      <div class="translation-experience-list">${experience.loading ? `<div class="admin-empty-panel"><p>正在分析错误经验…</p></div>` : actionable.map(translationExperienceCardMarkup).join("") || `<div class="admin-empty-panel success"><p>当前没有待处理建议。后续翻译失败时会自动在这里给出原因和可应用方案，不需要逐条查看日志。</p></div>`}</div>
      ${verified.length ? `<details class="verified-experience"><summary>查看最近已验证经验（${verified.length}）</summary><div class="translation-experience-list compact">${verified.map(translationExperienceCardMarkup).join("")}</div></details>` : ""}
    </section>
    <details class="panel translation-advanced-knowledge"><summary><strong>人工复核与逐句记忆（高级）</strong><span>日常不需要操作；只用于少量例外处理</span></summary>
      <div class="translation-advanced-content">
        ${translationReviewMarkup()}
        <section class="panel translation-memory-panel">
          <div class="panel-heading"><div><h2>人工确认翻译记忆</h2><span class="panel-note">只复用完全相同原文，保留作为少量例外兜底</span></div></div>
          <div class="translation-memory-form">
            <label>日报类型<select name="translationMemoryReportType"><option value="">通用</option><option value="drilling">钻井（含搬迁）</option><option value="completion">完井</option><option value="workover">修井</option></select></label>
            <label>字段编码<input name="translationMemoryFieldCode" placeholder="operations.operation_details" /></label>
            <label class="wide">西语 / 英语原文<textarea name="translationMemorySource" rows="4" maxlength="12000"></textarea></label>
            <label class="wide">人工确认中文<textarea name="translationMemoryTarget" rows="4" maxlength="12000"></textarea></label>
            <div class="admin-actions wide"><button class="button small" type="button" data-admin-save-translation-memory>保存确认译例</button></div>
          </div>
          <div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>范围</th><th>原文</th><th>标准中文</th><th>确认人 / 更新</th><th>操作</th></tr></thead><tbody>${memory.loading ? `<tr><td colspan="5">正在读取翻译记忆…</td></tr>` : (memory.entries || []).map(translationMemoryRowMarkup).join("") || `<tr><td colspan="5">暂无人工确认译例</td></tr>`}</tbody></table></div>
        </section>
      </div>
    </details>
  </div>`;
}

function translationExperienceCardMarkup(item = {}) {
  const status = String(item.status || "PENDING");
  const statusLabel = { PENDING: "待采纳", QUEUED: "已接收，等待重跑", APPLIED: "重跑验证中", VERIFIED: "已验证", DISMISSED: "已忽略" }[status] || status;
  const actionLabel = {
    add_protected_unit: "加入全局单位保护",
    add_protected_acronym: "加入全局缩写保护",
    add_protected_proper_noun: "加入全局专名保护",
    enable_placeholder: "按当前保护策略重跑",
    add_prompt_rule: "按当前规则重跑（不改Prompt）",
    retry_current_rules: "按当前规则重跑",
  }[item.action_type] || item.action_type || "应用建议";
  const evidence = (item.evidence || [])[0] || {};
  const scope = [item.report_type, item.field_code].filter(Boolean).join(" · ") || "全局";
  const changesStructuredPool = ["add_protected_unit", "add_protected_acronym", "add_protected_proper_noun"].includes(item.action_type);
  const applyLabel = changesStructuredPool ? "确认加入词库并重跑" : "按当前规则重跑";
  return `<article class="translation-experience-card ${status.toLowerCase()}">
    <div class="experience-card-heading"><div><span class="status-pill ${status === "VERIFIED" ? "uploaded" : ["QUEUED", "APPLIED"].includes(status) ? "processing" : "pending"}">${escapeHtml(statusLabel)}</span><strong>${escapeHtml(item.title || "翻译经验建议")}</strong></div><span class="experience-confidence">${item.confidence === "high" ? "高置信" : "需验证"} · ${escapeHtml(scope)}</span></div>
    <div class="experience-cause"><small>识别原因</small><p>${escapeHtml(item.cause || "-")}</p></div>
    <div class="experience-recommendation"><small>建议动作</small><p><strong>${escapeHtml(actionLabel)}</strong>：${escapeHtml(item.recommendation || "-")}</p></div>
    ${evidence.error_message ? `<details><summary>查看触发证据 · 累计 ${Number(item.occurrence_count || 1)} 次${Number(item.regression_count || 0) ? ` · 回归 ${Number(item.regression_count)} 次` : ""}</summary><p>${escapeHtml(evidence.error_message)}</p><small>${escapeHtml(evidence.record_id || "")} ${escapeHtml(evidence.field_code || "")}</small></details>` : ""}
    <div class="experience-card-actions">${status === "PENDING" ? `<button class="button small" type="button" data-admin-apply-translation-experience="${escapeHtml(item.id)}">${applyLabel}</button><button class="link-button" type="button" data-admin-dismiss-translation-experience="${escapeHtml(item.id)}">忽略</button>` : status === "QUEUED" ? `<span>建议已接收；当前翻译结束后会自动处理并重跑</span>` : status === "APPLIED" ? `<span>已记录处理结果，等待重跑验证</span>` : `<span>验证日报：${escapeHtml(item.verified_record_id || "-")} · ${escapeHtml(item.verified_at || "-")}</span>`}</div>
  </article>`;
}

function translationReviewMarkup() {
  const review = adminState.translationReview || { record_id: "", rows: [], loading: false };
  const records = adminState.translationQueue?.records || [];
  return `<section class="panel translation-review-panel"><div class="panel-heading"><div><h2>日报译文人工修订</h2><span class="panel-note">每次保存都会记录修改前后文本，可同时沉淀为已确认翻译记忆</span></div></div><div class="translation-review-toolbar"><label>日报<select name="translationReviewRecord"><option value="">请选择日报</option>${records.map((record) => `<option value="${escapeHtml(record.record_id)}" ${review.record_id === record.record_id ? "selected" : ""}>${escapeHtml(record.report_date || "-")} · ${escapeHtml(record.wellbore || "-")} · ${escapeHtml(record.report_type_label || record.report_type || "-")}</option>`).join("")}</select></label><button class="button secondary small" type="button" data-admin-load-translation-review>加载译文</button></div><div class="translation-review-list">${review.loading ? `<div class="admin-empty-panel"><p>正在读取日报译文…</p></div>` : (review.rows || []).map(translationReviewRowMarkup).join("") || `<div class="admin-empty-panel"><p>选择一份已翻译日报进行人工复核。</p></div>`}</div></section>`;
}

function translationReviewRowMarkup(row = {}, index = 0) {
  return `<article class="translation-review-row" data-translation-review-row="${index}" data-entity-id="${escapeHtml(row.entity_id || "")}" data-field-code="${escapeHtml(row.field_code || "")}" data-target-language="${escapeHtml(row.target_language || "zh-CN")}"><div><span class="type-pill">${escapeHtml(row.field_code || "-")}</span><small>${row.is_manual_modified ? "已人工修订" : "模型译文"}</small></div><div class="translation-review-columns"><label>原文<textarea rows="5" readonly>${escapeHtml(row.source_text || "")}</textarea></label><label>中文译文<textarea name="translationReviewText" rows="5">${escapeHtml(row.translated_text || "")}</textarea></label></div><div class="translation-review-actions"><label><input type="checkbox" name="translationReviewAddMemory" checked />加入翻译记忆</label><input name="translationReviewNote" placeholder="修订说明（可选）" maxlength="1000" /><button class="button small" type="button" data-admin-save-translation-review>保存本条修订</button></div></article>`;
}

function translationMemoryRowMarkup(entry = {}) {
  return `<tr><td><span class="type-pill">${escapeHtml(entry.report_type || "通用")}</span><small>${escapeHtml(entry.field_code || "全部字段")}</small></td><td><p class="memory-cell-text">${escapeHtml(entry.source_text || "-")}</p></td><td><p class="memory-cell-text">${escapeHtml(entry.translated_text || "-")}</p></td><td>${escapeHtml(entry.confirmed_by || "-")}<small>${escapeHtml(entry.updated_at || "-")}</small></td><td><button class="link-button danger-link" type="button" data-admin-delete-translation-memory="${escapeHtml(entry.id)}">删除</button></td></tr>`;
}

function aliasInputValue(value) {
  return Array.isArray(value) ? value.join("\n") : "";
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

function v2RelationshipOptions(items, selected, valueKey, labelKeys) {
  return (items || []).map((item) => {
    const label = [...new Set(labelKeys.map((key) => item[key]).filter(Boolean))].join(" / ") || item[valueKey];
    return `<option value="${escapeHtml(item[valueKey])}" ${String(item[valueKey]) === String(selected) ? "selected" : ""}>${escapeHtml(label)}</option>`;
  }).join("");
}

function v2ProjectRigRow(item = {}) {
  const conflict = item.status !== "inactive" && projectTeamConflictIds((adminState.governance.assignments || []).filter((row) => row.status === "active")).has(String(item.team_id));
  return `<div class="admin-project-rig-row ${conflict ? "relation-row-conflict" : ""}" data-v2-project-rig-row>
    <input type="hidden" name="v2RelationId" value="${escapeHtml(item.id || "")}" /><input type="hidden" name="v2RelationVersion" value="${escapeHtml(item.version || "")}" />
    <label>队伍 ${conflict ? `<span class="relation-conflict-note">有效期冲突</span>` : ""}<select name="v2RelationTeamId"><option value="">选择队伍</option>${v2RelationshipOptions(adminState.governance.teams, item.team_id, "id", ["team_name", "team_code"])}</select></label>
    <label>开始日期<input name="v2RelationStart" type="date" value="${escapeHtml(String(item.valid_from || "").slice(0, 10))}" /></label>
    <label>结束日期（不含）<input name="v2RelationEnd" type="date" value="${escapeHtml(String(item.valid_to || "").slice(0, 10))}" /></label>
    <label>服务专业<input name="v2RelationDiscipline" value="${escapeHtml(item.service_discipline || "")}" placeholder="钻井 / 修井 / 完井" /></label>
    <label>业务说明<input name="v2RelationNote" value="${escapeHtml(item.assignment_note || "")}" placeholder="关系范围说明" /></label>
    <label>状态<select name="v2RelationStatus"><option value="active" ${item.status !== "inactive" ? "selected" : ""}>启用</option><option value="inactive" ${item.status === "inactive" ? "selected" : ""}>停用</option></select></label>
    <button class="icon-button" type="button" data-v2-remove-relation-row aria-label="停用或移除队伍关系">×</button>
  </div>`;
}

function v2ProjectWellRow(item = {}) {
  return `<div class="admin-project-rig-row" data-v2-project-well-row>
    <input type="hidden" name="v2WellRelationId" value="${escapeHtml(item.id || "")}" /><input type="hidden" name="v2WellRelationVersion" value="${escapeHtml(item.version || "")}" />
    <label>井<select name="v2WellRelationWellId"><option value="">选择井</option>${v2RelationshipOptions(adminState.governance.wells, item.well_id, "id", ["well_name", "well_code"])}</select></label>
    <label>作业类型<select name="v2WellRelationJobType"><option value="" ${!item.job_type ? "selected" : ""}>全部作业</option><option value="drilling" ${item.job_type === "drilling" ? "selected" : ""}>钻井（含搬迁）</option><option value="completion" ${item.job_type === "completion" ? "selected" : ""}>完井</option><option value="workover" ${item.job_type === "workover" ? "selected" : ""}>修井</option></select></label>
    <label>开始日期<input name="v2WellRelationStart" type="date" value="${escapeHtml(String(item.valid_from || "").slice(0, 10))}" /></label>
    <label>结束日期（不含）<input name="v2WellRelationEnd" type="date" value="${escapeHtml(String(item.valid_to || "").slice(0, 10))}" /></label>
    <label>业务说明<input name="v2WellRelationNote" value="${escapeHtml(item.scope_note || "")}" placeholder="井范围说明" /></label>
    <label>状态<select name="v2WellRelationStatus"><option value="active" ${item.status !== "inactive" ? "selected" : ""}>启用</option><option value="inactive" ${item.status === "inactive" ? "selected" : ""}>停用</option></select></label>
    <button class="icon-button" type="button" data-v2-remove-relation-row aria-label="停用或移除井范围">×</button>
  </div>`;
}

function openProjectRelationshipModal(id) {
  const data = adminState.governance || {};
  const project = (data.projects || []).find((item) => String(item.id) === String(id));
  if (!project) return showToast("项目主数据不存在");
  const contract = (data.contracts || []).find((item) => String(item.id) === String(project.contract_id)) || {};
  const rigRows = (data.assignments || []).filter((item) => String(item.project_id) === String(project.id));
  const wellRows = (data.wellAssignments || []).filter((item) => String(item.project_id) === String(project.id));
  openAdminModal("维护项目关系", `
    <input type="hidden" name="v2RelationshipProjectId" value="${escapeHtml(project.id)}" />
    <div class="admin-note-grid"><span><strong>${escapeHtml(project.project_name || project.project_code)}</strong><small>${escapeHtml(project.project_code)} · 合同 ${escapeHtml(contract.contract_no || "未关联")} · ${escapeHtml(String(project.valid_from || "-").slice(0, 10))} 至 ${escapeHtml(project.valid_to ? String(project.valid_to).slice(0, 10) : "长期")}</small></span></div>
    <section class="admin-modal-subsection"><div class="panel-heading compact-heading"><div><h3>队伍派遣</h3><span class="panel-note">维护项目与队伍的有效期关系，采用 [开始, 结束)</span></div><button class="button secondary small" type="button" data-v2-add-project-rig>添加队伍</button></div>
      <div class="admin-project-rig-list" data-v2-project-rig-list>${rigRows.map(v2ProjectRigRow).join("") || v2ProjectRigRow({ valid_from: project.valid_from, valid_to: project.valid_to })}</div>
    </section>
    <section class="admin-modal-subsection"><div class="panel-heading compact-heading"><div><h3>项目井范围</h3><span class="panel-note">同一口井可按作业类型分别配置</span></div><button class="button secondary small" type="button" data-v2-add-project-well>添加井</button></div>
      <div class="admin-project-rig-list" data-v2-project-well-list>${wellRows.map(v2ProjectWellRow).join("") || v2ProjectWellRow({ valid_from: project.valid_from, valid_to: project.valid_to })}</div>
    </section>
    <div class="admin-modal-form compact"><label class="wide">变更原因<input name="v2RelationshipReason" placeholder="必填；将写入每条关系的审计记录" /></label></div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button><button class="button" type="button" data-v2-save-project-relationships>保存全部关系</button>`
  );
}

function openProjectModal(id = "") {
  openProjectRelationshipModal(id);
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

function renderAdminLogs() {
  const host = document.querySelector('[data-admin-panel="logs"]');
  const logs = adminState.logs || [];
  const pageSize = Number(adminState.logsPageSize || ADMIN_DEFAULT_PAGE_SIZE);
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
  return adminPaginationMarkup("logs", totalRows, currentPage, totalPages, pageSize, "admin-log-pagination");
}

function clampPage(value, totalPages) {
  const page = Number.parseInt(value, 10);
  return Math.min(Math.max(Number.isFinite(page) ? page : 1, 1), Math.max(1, totalPages));
}

function adminPaginationMarkup(kind, totalRows, currentPage, totalPages, pageSize, extraClass = "") {
  const start = totalRows ? (currentPage - 1) * pageSize + 1 : 0;
  const end = Math.min(totalRows, currentPage * pageSize);
  const sizes = [10, 20, 50];
  return `
    <div class="record-pagination standard-pagination admin-list-pagination ${extraClass}">
      <span class="pagination-summary">共 ${totalRows} 条，显示 ${start}-${end}</span>
      <div class="standard-pagination-controls admin-log-page-controls">
        <label class="standard-page-size">每页
          <select data-admin-page-size="${kind}">
            ${sizes.map((size) => `<option value="${size}" ${size === pageSize ? "selected" : ""}>${size} 条</option>`).join("")}
          </select>
        </label>
        <div class="record-page-buttons">
          <button class="icon-button" type="button" data-admin-page="${kind}" data-admin-page-value="${currentPage - 1}" ${currentPage <= 1 ? "disabled" : ""} aria-label="上一页">‹</button>
          <label class="page-jump">第 <input type="number" min="1" max="${totalPages}" value="${currentPage}" inputmode="numeric" data-admin-page-jump="${kind}" aria-label="跳转页码" /> / ${totalPages} 页</label>
          <button class="icon-button" type="button" data-admin-page="${kind}" data-admin-page-value="${currentPage + 1}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="下一页">›</button>
        </div>
      </div>
    </div>`;
}

function setAdminPage(kind, page) {
  if (kind === "logs") {
    adminState.logsPage = page;
    return renderAdminLogs();
  }
  if (kind === "translationTerms") {
    adminState.translationTermPage = page;
    return renderAdminTranslationTuning();
  }
  if (kind === "translationScope") {
    captureTranslationTuningForm();
    adminState.translationScopePage = page;
    return renderAdminTranslationTuning();
  }
  if (kind === "aiExtractionQueue") {
    adminState.aiExtractionQueuePage = page;
    return renderAdminAiExtraction();
  }
  if (kind === "translationQueue") {
    adminState.translationQueuePage = page;
    return renderAdminTranslationTuning();
  }
}

function setAdminPageSize(kind, pageSize) {
  if (kind === "logs") {
    adminState.logsPageSize = pageSize;
    adminState.logsPage = 1;
    return renderAdminLogs();
  }
  if (kind === "translationTerms") {
    adminState.translationTermPageSize = pageSize;
    adminState.translationTermPage = 1;
    return renderAdminTranslationTuning();
  }
  if (kind === "translationScope") {
    captureTranslationTuningForm();
    adminState.translationScopePageSize = pageSize;
    adminState.translationScopePage = 1;
    return renderAdminTranslationTuning();
  }
  if (kind === "aiExtractionQueue") {
    adminState.aiExtractionQueuePageSize = pageSize;
    adminState.aiExtractionQueuePage = 1;
    return renderAdminAiExtraction();
  }
  if (kind === "translationQueue") {
    adminState.translationQueuePageSize = pageSize;
    adminState.translationQueuePage = 1;
    return renderAdminTranslationTuning();
  }
}

function commitAdminPageJump(input) {
  if (!input) return;
  const kind = input.dataset.adminPageJump;
  const max = Number(input.max || 1);
  setAdminPage(kind, clampPage(input.value, max));
}

function switchAdminTab(tab) {
  if (tab === "teams") tab = "projects";
  adminState.tab = tab;
  document.querySelectorAll("[data-admin-tab]").forEach((button) => button.classList.toggle("active", button.dataset.adminTab === tab));
  document.querySelectorAll("[data-admin-panel]").forEach((panel) => panel.hidden = panel.dataset.adminPanel !== tab);
  scheduleAdminQueuePoll(0);
}

function roleLabel(value) {
  return (adminState.roles || []).find((role) => role.value === value)?.label || value || "-";
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
  const requestOptionsText = host?.querySelector('[name="aiModelRequestOptions"]')?.value.trim() || "{}";
  let requestOptions;
  try {
    requestOptions = JSON.parse(requestOptionsText);
  } catch (error) {
    throw new Error(`高级请求配置不是有效 JSON：${error.message}`);
  }
  if (!requestOptions || Array.isArray(requestOptions) || typeof requestOptions !== "object") {
    throw new Error("高级请求配置必须是 JSON 对象。");
  }
  const reservedOptionKeys = new Set(["authorization", "api_key", "apikey", "base_url", "messages", "model", "prompt", "stream"]);
  const blockedOption = Object.keys(requestOptions).find((key) => reservedOptionKeys.has(key.trim().toLowerCase()));
  if (blockedOption) throw new Error(`高级请求配置不允许覆盖 ${blockedOption}。`);
  if (new TextEncoder().encode(requestOptionsText).length > 12000) {
    throw new Error("高级请求配置不能超过 12 KB。");
  }
  return {
    id: host?.querySelector('[name="aiModelId"]')?.value || newClientId(),
    name: host?.querySelector('[name="aiModelName"]')?.value.trim() || "未命名模型",
    api_type: host?.querySelector('[name="aiModelApiType"]')?.value || "openai-compatible",
    base_url: host?.querySelector('[name="aiModelBaseUrl"]')?.value.trim() || "",
    api_key: host?.querySelector('[name="aiModelApiKey"]')?.value || "",
    model: host?.querySelector('[name="aiModelModel"]')?.value.trim() || "",
    timeout_seconds: Number(host?.querySelector('[name="aiModelTimeout"]')?.value || 60),
    thinking_mode: host?.querySelector('[name="aiModelThinkingMode"]')?.value || "auto",
    retry_count: Number(host?.querySelector('[name="aiModelRetry"]')?.value || 1),
    chunk_max_chars: Number(host?.querySelector('[name="aiModelChunkChars"]')?.value || 0),
    request_options: requestOptions,
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
  try {
    const models = aiModelsWithCurrentForm();
    const defaultModel = models.find((item) => item.is_default) || models.find((item) => item.enabled !== false) || models[0];
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
  let model;
  try {
    model = collectAiModelForm();
  } catch (error) {
    adminState.aiModelTestResult = { ok: false, error: error.message };
    renderAdminAiModels();
    return;
  }
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

async function stopTranslations(confirmAction = true) {
  if (confirmAction && !window.confirm("确认停止当前翻译队列？已完成译文会保留，未完成日报之后可以继续。")) return false;
  const result = await adminRequest("/api/admin/translations/stop", { method: "POST", body: "{}" });
  showToast(`已停止翻译：${result.stopped_records || 0} 条未完成日报`);
  return true;
}

async function stopAiExtractions(confirmAction = true) {
  if (confirmAction && !window.confirm("确认停止当前数据提炼队列？已完成结果会保留，未完成日报之后可以继续。")) return false;
  const result = await adminRequest("/api/admin/ai-extractions/stop", { method: "POST", body: "{}" });
  showToast(`已停止提炼：${result.stopped_records || 0} 条未完成日报`);
  return true;
}

async function stopTranslationsAndRefresh() {
  try {
    if (await stopTranslations()) await loadAdminData();
  } catch (error) {
    showToast(error.message);
  }
}

async function stopExtractionsAndRefresh() {
  try {
    if (await stopAiExtractions()) await loadAdminData();
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
    <td data-translation-job-status="${escapeHtml(record.record_id)}">${translationJobStatusMarkup(record)}</td>
    <td data-translation-job-reason="${escapeHtml(record.record_id)}">${escapeHtml(record.reason || "-")}</td>
  </tr>`;
}

function translationJobStatusMarkup(record = {}) {
  const status = String(record.status || "").toUpperCase();
  const tone = status === "FAILED" ? "failed" : status === "COMPLETED" ? "uploaded" : ["QUEUED", "IN_PROGRESS"].includes(status) ? "processing" : "pending";
  const progress = ["QUEUED", "IN_PROGRESS"].includes(status) ? ` ${escapeHtml(record.progress || "0")}%` : "";
  return `<span class="status-pill ${tone}">${escapeHtml(translationQueueStatusLabel(status))}${progress}</span>`;
}

function translationQueueStatusLabel(status = "") {
  return { PENDING: "待处理", STOPPED: "已停止", FAILED: "失败", QUEUED: "已排队", IN_PROGRESS: "翻译中", COMPLETED: "已完成", NOT_REQUIRED: "无需翻译" }[status] || status || "待处理";
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
  const protections = {
    ...(current.protections || {}),
    ...Object.fromEntries(protectionInputs.map((input) => [input.value, input.checked])),
    contextual_translation: Boolean(host.querySelector('[name="translationProtectionMode"][value="contextual_translation"]')?.checked),
    validate_results: Boolean(host.querySelector('[name="translationProtectionMode"][value="validate_results"]')?.checked),
  };
  delete protections.mode;
  delete protections.date_format;
  const promptTemplates = Object.fromEntries(
    [...host.querySelectorAll('[name="translationBusinessPrompt"]')]
      .map((input) => [input.dataset.reportType || "", input.value.trim()])
      .filter(([reportType]) => reportType)
  );
  adminState.translationTuning = {
    ...current,
    auto_translate_on_upload: Boolean(host.querySelector('[name="translationAutoOnUpload"]')?.checked),
    scope_rules: scopeRules,
    target_languages: targetLanguages.length ? targetLanguages : ["zh-CN"],
    prompt: {
      system_prompt: host.querySelector('[name="translationSystemPrompt"]')?.value.trim() || "",
      translation_instruction: host.querySelector('[name="translationInstruction"]')?.value.trim() || "",
    },
    prompt_templates: promptTemplates,
    protections,
  };
  delete adminState.translationTuning.pipeline_mode;
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
  adminState.translationScopePage = Math.max(1, Math.ceil(rules.length / (adminState.translationScopePageSize || ADMIN_DEFAULT_PAGE_SIZE)));
  renderAdminTranslationTuning();
}

function removeTranslationScope(id) {
  captureTranslationTuningForm();
  adminState.translationTuning.scope_rules = (adminState.translationTuning.scope_rules || []).filter((rule) => rule.id !== id);
  adminState.translationScopePage = clampPage(adminState.translationScopePage, Math.ceil(adminState.translationTuning.scope_rules.length / (adminState.translationScopePageSize || ADMIN_DEFAULT_PAGE_SIZE)));
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
  const term = existing || { id: "", category: "general", term_type: "preferred", priority: 50, strict_preserve: false, zh: "", en: "", es: "", aliases: { zh: [], en: [], es: [] }, protected: false, enabled: true };
  const aliases = term.aliases || {};
  openAdminModal(
    existing ? "编辑术语" : "新增术语",
    `<div class="translation-term-modal-form">
      <input type="hidden" name="termModalId" value="${escapeHtml(term.id)}" />
      <label>作业类型<select name="termModalCategory">${translationTermCategoryOptions(term.category || "general")}</select></label>
      <label>术语类型<select name="termModalType">${translationTermTypeOptions(term.term_type || "preferred")}</select></label>
      <label>优先级<input type="number" name="termModalPriority" min="0" max="1000" value="${escapeHtml(term.priority ?? 50)}" /></label>
      <label>中文<input name="termModalZh" value="${escapeHtml(term.zh || "")}" /></label>
      <label>English<input name="termModalEn" value="${escapeHtml(term.en || "")}" /></label>
      <label>Español<input name="termModalEs" value="${escapeHtml(term.es || "")}" /></label>
      <label>中文别名<textarea name="termModalAliasesZh" rows="3">${escapeHtml(aliasInputValue(aliases.zh))}</textarea></label>
      <label>英文别名<textarea name="termModalAliasesEn" rows="3">${escapeHtml(aliasInputValue(aliases.en))}</textarea></label>
      <label>西语别名<textarea name="termModalAliasesEs" rows="3">${escapeHtml(aliasInputValue(aliases.es))}</textarea></label>
      <div class="tuning-term-switches"><label><input type="checkbox" name="termModalEnabled" ${term.enabled !== false ? "checked" : ""} />启用</label><label><input type="checkbox" name="termModalStrictPreserve" ${term.strict_preserve ? "checked" : ""} />必须原样保留</label></div>
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
  term.term_type = modal.querySelector('[name="termModalType"]')?.value || "preferred";
  term.priority = Math.max(0, Math.min(1000, Number(modal.querySelector('[name="termModalPriority"]')?.value || 50)));
  term.zh = zh;
  term.en = en;
  term.es = es;
  term.aliases = {
    zh: parseAliasList(modal.querySelector('[name="termModalAliasesZh"]')?.value || ""),
    en: parseAliasList(modal.querySelector('[name="termModalAliasesEn"]')?.value || ""),
    es: parseAliasList(modal.querySelector('[name="termModalAliasesEs"]')?.value || ""),
  };
  term.enabled = modal.querySelector('[name="termModalEnabled"]')?.checked ?? true;
  term.strict_preserve = modal.querySelector('[name="termModalStrictPreserve"]')?.checked ?? false;
  term.protected = term.term_type === "protected";
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
  if (!recordIds.length) return showToast("请勾选要提炼的日报；已完成列表默认全选");
  const action = mode === "overwrite" ? "按当前规则覆盖提炼" : "执行待处理提炼";
  if (!window.confirm(`确认对 ${recordIds.length} 条日报${action}？`)) return;
  try {
    const result = await adminRequest("/api/admin/ai-extractions/queue", { method: "POST", body: JSON.stringify({ mode, record_ids: recordIds }) });
    showToast(`已加入提炼队列：${result.queued_records || 0} 条`);
    adminState.aiExtractionQueue = await adminRequest("/api/admin/ai-extractions");
    adminState.aiExtractionQueueStatusTab = preferredExtractionQueueStatusTab(adminState.aiExtractionQueue.records || [], "processing");
    adminState.aiExtractionQueuePage = 1;
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

async function switchTranslationTuningView(view) {
  if (adminState.translationTuningView === "fields") captureTranslationTuningForm();
  if (adminState.translationTuningView === "terms") {
    adminState.translationTerms.protected_terms = captureProtectedTerms();
  }
  adminState.translationTuningView = view;
  renderAdminTranslationTuning();
  if (view === "memory") await loadTranslationKnowledge();
}

async function loadTranslationKnowledge() {
  adminState.translationMemory.loading = true;
  adminState.translationExperience.loading = true;
  renderAdminTranslationTuning();
  try {
    const [experience, memory] = await Promise.all([
      adminRequest("/api/admin/translation-experience?limit=200"),
      adminRequest("/api/admin/translation-memory?limit=200"),
    ]);
    adminState.translationExperience = { suggestions: experience.suggestions || [], counts: experience.counts || {}, loading: false };
    adminState.translationMemory = { entries: memory.entries || [], count: Number(memory.count || 0), loading: false };
  } catch (error) {
    adminState.translationExperience.loading = false;
    adminState.translationMemory.loading = false;
    showToast(error.message);
  }
  renderAdminTranslationTuning();
}

async function loadTranslationReview() {
  const recordId = document.querySelector('[name="translationReviewRecord"]')?.value || adminState.translationReview.record_id || "";
  if (!recordId) return showToast("请选择需要复核的日报");
  adminState.translationReview = { record_id: recordId, rows: [], loading: true };
  renderAdminTranslationTuning();
  try {
    const result = await adminRequest(`/api/admin/translation-content?record_id=${encodeURIComponent(recordId)}`);
    adminState.translationReview = { record_id: recordId, rows: result.rows || [], loading: false };
  } catch (error) {
    adminState.translationReview.loading = false;
    showToast(error.message);
  }
  renderAdminTranslationTuning();
}

async function saveTranslationReview(button) {
  const rowHost = button.closest("[data-translation-review-row]");
  const revisedText = rowHost?.querySelector('[name="translationReviewText"]')?.value.trim() || "";
  if (!rowHost || !revisedText) return showToast("修订译文不能为空");
  const record = (adminState.translationQueue?.records || []).find((item) => item.record_id === adminState.translationReview.record_id) || {};
  const payload = {
    record_id: adminState.translationReview.record_id,
    entity_id: rowHost.dataset.entityId || "",
    field_code: rowHost.dataset.fieldCode || "",
    target_language: rowHost.dataset.targetLanguage || "zh-CN",
    revised_text: revisedText,
    note: rowHost.querySelector('[name="translationReviewNote"]')?.value.trim() || "",
    add_to_memory: rowHost.querySelector('[name="translationReviewAddMemory"]')?.checked !== false,
    report_type: record.report_type || "",
  };
  try {
    await adminRequest("/api/admin/translation-content/revise", { method: "POST", body: JSON.stringify(payload) });
    showToast("译文修订及版本记录已保存");
    await Promise.all([loadTranslationReview(), loadTranslationKnowledge()]);
  } catch (error) {
    showToast(error.message);
  }
}

async function saveTranslationMemory() {
  const source = document.querySelector('[name="translationMemorySource"]')?.value?.trim() || "";
  const translated = document.querySelector('[name="translationMemoryTarget"]')?.value?.trim() || "";
  if (!source || !translated) return showToast("请填写完整原文和人工确认中文");
  const entry = {
    source_text: source,
    translated_text: translated,
    source_language: "es",
    target_language: "zh-CN",
    report_type: document.querySelector('[name="translationMemoryReportType"]')?.value || "",
    field_code: document.querySelector('[name="translationMemoryFieldCode"]')?.value?.trim() || "",
  };
  try {
    await adminRequest("/api/admin/translation-memory", { method: "POST", body: JSON.stringify({ entry }) });
    showToast("人工确认译例已保存");
    await loadTranslationKnowledge();
  } catch (error) {
    showToast(error.message);
  }
}

async function deleteTranslationMemory(id) {
  if (!window.confirm("确认删除这条翻译记忆？")) return;
  try {
    await adminRequest("/api/admin/translation-memory", { method: "POST", body: JSON.stringify({ action: "delete", id: Number(id) }) });
    showToast("翻译记忆已删除");
    await loadTranslationKnowledge();
  } catch (error) {
    showToast(error.message);
  }
}

async function applyTranslationExperience(id) {
  if (!window.confirm("确认处理这条建议并重跑受影响日报？经验记录不会修改正式 Prompt。")) return;
  const button = document.querySelector(`[data-admin-apply-translation-experience="${CSS.escape(id)}"]`);
  if (button) {
    button.disabled = true;
    button.textContent = "正在接收…";
  }
  try {
    const result = await adminRequest("/api/admin/translation-experience/apply", {
      method: "POST",
      body: JSON.stringify({ id, action: "apply_and_rerun" }),
    });
    showToast(result.deferred
      ? `建议已接收，当前翻译结束后自动重跑 ${result.pending_records || 0} 份日报`
      : `经验已应用，自动重跑 ${result.queued_records || 0} 份日报`);
    await Promise.all([loadTranslationKnowledge(), loadAdminData()]);
  } catch (error) {
    showToast(error.message);
    if (button?.isConnected) {
      button.disabled = false;
      button.textContent = "采纳建议并重跑";
    }
  }
}

async function dismissTranslationExperience(id) {
  if (!window.confirm("确认忽略这条经验建议？相同错误再次出现时会重新提示。")) return;
  try {
    await adminRequest("/api/admin/translation-experience/apply", {
      method: "POST",
      body: JSON.stringify({ id, action: "dismiss" }),
    });
    showToast("经验建议已忽略");
    await loadTranslationKnowledge();
  } catch (error) {
    showToast(error.message);
  }
}

function switchAiQueueStatusTab(kind, value) {
  if (!['all', 'pending', 'processing', 'failed', 'completed'].includes(value)) return;
  if (kind === "extraction") {
    adminState.aiExtractionQueueStatusTab = value;
    adminState.aiExtractionQueuePage = 1;
    return renderAdminAiExtraction();
  }
  adminState.translationQueueStatusTab = value;
  adminState.translationQueuePage = 1;
  renderAdminTranslationTuning();
}

async function runTranslationTuningTest(batchMode = false) {
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
    batch_mode: Boolean(batchMode),
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

async function saveV2ProjectRelationships() {
  const modal = document.querySelector(".admin-modal");
  if (!modal) return;
  const projectId = Number(modal.querySelector('[name="v2RelationshipProjectId"]')?.value || 0);
  const changeReason = modal.querySelector('[name="v2RelationshipReason"]')?.value.trim() || "";
  if (!changeReason) return showToast("请填写变更原因");
  const teamAssignments = [...modal.querySelectorAll("[data-v2-project-rig-row]")].map((row) => ({
    id: Number(row.querySelector('[name="v2RelationId"]')?.value || 0) || undefined,
    version: Number(row.querySelector('[name="v2RelationVersion"]')?.value || 0) || undefined,
    team_id: Number(row.querySelector('[name="v2RelationTeamId"]')?.value || 0),
    valid_from: row.querySelector('[name="v2RelationStart"]')?.value || "",
    valid_to: row.querySelector('[name="v2RelationEnd"]')?.value || "",
    service_discipline: row.querySelector('[name="v2RelationDiscipline"]')?.value.trim() || "",
    assignment_note: row.querySelector('[name="v2RelationNote"]')?.value.trim() || "",
    priority: 100, status: row.querySelector('[name="v2RelationStatus"]')?.value || "active",
  })).filter((item) => item.id || item.team_id);
  const wellScopes = [...modal.querySelectorAll("[data-v2-project-well-row]")].map((row) => ({
    id: Number(row.querySelector('[name="v2WellRelationId"]')?.value || 0) || undefined,
    version: Number(row.querySelector('[name="v2WellRelationVersion"]')?.value || 0) || undefined,
    well_id: Number(row.querySelector('[name="v2WellRelationWellId"]')?.value || 0),
    job_type: row.querySelector('[name="v2WellRelationJobType"]')?.value || "",
    scope_note: row.querySelector('[name="v2WellRelationNote"]')?.value.trim() || "",
    valid_from: row.querySelector('[name="v2WellRelationStart"]')?.value || "",
    valid_to: row.querySelector('[name="v2WellRelationEnd"]')?.value || "",
    status: row.querySelector('[name="v2WellRelationStatus"]')?.value || "active",
  })).filter((item) => item.id || item.well_id);
  const invalidTeam = teamAssignments.find((item) => item.status === "active" && (!item.team_id || !item.valid_from));
  const invalidWell = wellScopes.find((item) => item.status === "active" && (!item.well_id || !item.valid_from));
  if (invalidTeam || invalidWell) return showToast("启用的关系必须选择实体并填写开始日期");
  try {
    await adminRequest("/api/admin/project-relationships", { method: "POST", body: JSON.stringify({
      project_id: projectId, team_assignments: teamAssignments, well_scopes: wellScopes, change_reason: changeReason,
    }) });
    const [teamResponse, wellResponse] = await Promise.all([
      adminRequest("/api/admin/assignments?kind=project-team"),
      adminRequest("/api/admin/assignments?kind=project-well"),
    ]);
    adminState.governance.assignments = teamResponse.items || [];
    adminState.governance.wellAssignments = wellResponse.items || [];
    closeAdminModal(); renderAdminProjects(); showToast("项目关系已保存并刷新日报归属");
  } catch (error) { showToast(error.message); }
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
  const standardizationView = event.target.closest("[data-standardization-view]");
  if (standardizationView) return switchStandardizationView(standardizationView.dataset.standardizationView);
  const standardizationRoute = event.target.closest("[data-standardization-route]");
  if (standardizationRoute) return followStandardizationRoute(standardizationRoute.dataset.standardizationRoute);
  if (event.target.closest("[data-save-master-alias]")) return saveMasterAlias();
  const editAlias = event.target.closest("[data-edit-master-alias]");
  if (editAlias) return editMasterAlias(editAlias.dataset.editMasterAlias);
  const masterView = event.target.closest("[data-master-view]");
  if (masterView) { adminState.governance.masterView = masterView.dataset.masterView || "entities"; return renderAdminGovernance(); }
  const masterTab = event.target.closest("[data-master-entity]");
  if (masterTab) { adminState.governance.masterEntity = masterTab.dataset.masterEntity || "regions"; adminState.governance.masterView = "entities"; return renderAdminGovernance(); }
  const appendixCategory = event.target.closest("[data-appendix-category]");
  if (appendixCategory) { adminState.governance.appendixCategoryId = appendixCategory.dataset.appendixCategory || ""; return renderAdminGovernance(); }
  if (event.target.closest("[data-new-appendix-category]")) return openMasterEntityModal("appendix-categories");
  const newAppendixValue = event.target.closest("[data-new-appendix-value]");
  if (newAppendixValue) return openMasterEntityModal("appendix-values", "", { category_id: Number(newAppendixValue.dataset.newAppendixValue) || null, level_no: 1, sort_order: 0 });
  const newMaster = event.target.closest("[data-new-master-entity]");
  if (newMaster) return openMasterEntityModal(newMaster.dataset.newMasterEntity);
  const editMaster = event.target.closest("[data-edit-master-entity]");
  if (editMaster) return openMasterEntityModal(editMaster.dataset.editMasterEntity, editMaster.dataset.masterId);
  const deleteMaster = event.target.closest("[data-delete-master-entity]");
  if (deleteMaster) return openDeleteMasterEntityModal(deleteMaster.dataset.deleteMasterEntity, deleteMaster.dataset.masterId);
  const confirmDeleteMaster = event.target.closest("[data-confirm-delete-master-entity]");
  if (confirmDeleteMaster) return deleteMasterEntityFromModal(confirmDeleteMaster.dataset.confirmDeleteMasterEntity, confirmDeleteMaster.dataset.masterId, confirmDeleteMaster.dataset.masterVersion);
  const saveMaster = event.target.closest("[data-save-master-entity]");
  if (saveMaster) return saveMasterEntityFromModal(saveMaster.dataset.saveMasterEntity);
  if (event.target.closest("[data-admin-new-project]")) return openMasterEntityModal("projects");
  const editProjectMaster = event.target.closest("[data-admin-edit-project-master]");
  if (editProjectMaster) return openMasterEntityModal("projects", editProjectMaster.dataset.adminEditProjectMaster);
  if (event.target.closest("[data-new-time-rule]")) return openTimeRuleModal();
  const editTimeRule = event.target.closest("[data-edit-time-rule]");
  if (editTimeRule) return openTimeRuleModal(editTimeRule.dataset.editTimeRule);
  if (event.target.closest("[data-save-time-rule]")) return saveTimeRuleFromModal();
  if (event.target.closest("[data-reclassify-time-facts]")) return reclassifyTimeFacts();
  const qualityIssue = event.target.closest("[data-resolve-quality-issue]");
  if (qualityIssue) return resolveGovernanceIssue(qualityIssue.dataset.resolveQualityIssue);
  const classification = event.target.closest("[data-confirm-classification]");
  if (classification) return confirmGovernanceClassification(classification.dataset.confirmClassification);
  if (event.target.closest("[data-save-classification-confirmation]")) return saveGovernanceClassification();
  const adminPageButton = event.target.closest("[data-admin-page]");
  if (adminPageButton) return setAdminPage(adminPageButton.dataset.adminPage, Number(adminPageButton.dataset.adminPageValue || 1));
  const edit = event.target.closest("[data-admin-edit-user]");
  if (edit) return fillAdminUserForm(edit.dataset.adminEditUser);
  if (event.target.closest("[data-admin-modal-close]")) return closeAdminModal();
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
  if (event.target.closest("[data-admin-open-active-ai-jobs]")) return openActiveAiJobsModal();
  const jumpAiQueue = event.target.closest("[data-admin-jump-ai-queue]");
  if (jumpAiQueue) return jumpToAiJobQueue(jumpAiQueue.dataset.adminJumpAiQueue);
  if (event.target.closest("[data-admin-new-extraction-rule]")) return newAiExtractionRule();
  const editExtraction = event.target.closest("[data-admin-edit-extraction-rule]");
  if (editExtraction) return editAiExtractionRule(editExtraction.dataset.adminEditExtractionRule);
  if (event.target.closest("[data-admin-save-extraction-rules]")) return saveAiExtractionRules();
  if (event.target.closest("[data-admin-delete-extraction-rule]")) return deleteAiExtractionRule();
  if (event.target.closest("[data-admin-test-extraction-rule]")) return runAiExtractionTest();
  const extractionView = event.target.closest("[data-ai-extraction-view]");
  if (extractionView) {
    adminState.aiExtractionView = extractionView.dataset.aiExtractionView || "rules";
    if (adminState.aiExtractionView === "queue") {
      adminState.aiExtractionQueueStatusTab = preferredExtractionQueueStatusTab(
        adminState.aiExtractionQueue?.records || [],
        adminState.aiExtractionQueueStatusTab || "pending",
      );
      adminState.aiExtractionQueuePage = 1;
    }
    return renderAdminAiExtraction();
  }
  const queueExtraction = event.target.closest("[data-admin-queue-extractions]");
  if (queueExtraction) return queueAiExtractions(queueExtraction.dataset.adminQueueExtractions || "continue");
  const queueStatusTab = event.target.closest("[data-ai-queue-status-tab]");
  if (queueStatusTab) return switchAiQueueStatusTab(queueStatusTab.dataset.aiQueueStatusTab, queueStatusTab.dataset.aiQueueStatusValue);
  if (event.target.closest("[data-admin-stop-extractions]")) return stopExtractionsAndRefresh();
  if (event.target.closest("[data-admin-stop-translations]")) return stopTranslationsAndRefresh();
  if (event.target.closest("[data-admin-reset-translations]")) return resetTranslations();
  if (event.target.closest("[data-admin-queue-translations]")) return queueTranslations();
  if (event.target.closest("[data-admin-open-translation-queue]")) return openTranslationQueue();
  const queueSelected = event.target.closest("[data-admin-queue-selected]");
  if (queueSelected) return queueSelectedTranslations(queueSelected.dataset.adminQueueSelected);
  const tuningView = event.target.closest("[data-translation-tuning-view]");
  if (tuningView) return switchTranslationTuningView(tuningView.dataset.translationTuningView);
  if (event.target.closest("[data-admin-refresh-translation-knowledge]")) return loadTranslationKnowledge();
  const applyExperience = event.target.closest("[data-admin-apply-translation-experience]");
  if (applyExperience) return applyTranslationExperience(applyExperience.dataset.adminApplyTranslationExperience);
  const dismissExperience = event.target.closest("[data-admin-dismiss-translation-experience]");
  if (dismissExperience) return dismissTranslationExperience(dismissExperience.dataset.adminDismissTranslationExperience);
  if (event.target.closest("[data-admin-load-translation-review]")) return loadTranslationReview();
  const saveReview = event.target.closest("[data-admin-save-translation-review]");
  if (saveReview) return saveTranslationReview(saveReview);
  if (event.target.closest("[data-admin-save-translation-memory]")) return saveTranslationMemory();
  const deleteMemory = event.target.closest("[data-admin-delete-translation-memory]");
  if (deleteMemory) return deleteTranslationMemory(deleteMemory.dataset.adminDeleteTranslationMemory);
  if (event.target.closest("[data-admin-save-translation-tuning]")) return saveTranslationTuning();
  if (event.target.closest("[data-admin-add-translation-scope]")) return addTranslationScope();
  const removeScope = event.target.closest("[data-admin-remove-translation-scope]");
  if (removeScope) return removeTranslationScope(removeScope.dataset.adminRemoveTranslationScope);
  if (event.target.closest("[data-admin-run-translation-test]")) return runTranslationTuningTest();
  if (event.target.closest("[data-admin-run-translation-batch-test]")) return runTranslationTuningTest(true);
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
  if (event.target.closest("[data-open-master-projects]")) {
    adminState.governance.masterEntity = "teams";
    adminState.governance.masterView = "entities";
    renderAdminGovernance();
    return switchAdminTab("governance");
  }
  if (event.target.closest("[data-v2-add-project-rig]")) {
    document.querySelector("[data-v2-project-rig-list]")?.insertAdjacentHTML("beforeend", v2ProjectRigRow({}));
    return;
  }
  if (event.target.closest("[data-v2-add-project-well]")) {
    document.querySelector("[data-v2-project-well-list]")?.insertAdjacentHTML("beforeend", v2ProjectWellRow({}));
    return;
  }
  const removeV2Relation = event.target.closest("[data-v2-remove-relation-row]");
  if (removeV2Relation) {
    const row = removeV2Relation.closest("[data-v2-project-rig-row], [data-v2-project-well-row]");
    const id = row?.querySelector('[name="v2RelationId"], [name="v2WellRelationId"]')?.value || "";
    if (!id) row?.remove();
    else {
      const status = row.querySelector('[name="v2RelationStatus"], [name="v2WellRelationStatus"]');
      if (status) status.value = "inactive";
      row.classList.add("relation-row-inactive");
      showToast("该关系将在保存后停用");
    }
    return;
  }
  if (event.target.closest("[data-v2-save-project-relationships]")) return saveV2ProjectRelationships();
  const editProject = event.target.closest("[data-admin-edit-project]");
  if (editProject) return openProjectModal(editProject.dataset.adminEditProject);
  if (event.target.closest("[data-admin-save-user]")) return saveAdminUser();
  if (event.target.closest("[data-admin-add-role]")) return addAdminRole();
  if (event.target.closest("[data-admin-save-roles]")) return saveAdminRoles();
  if (event.target.closest("[data-admin-save-config]")) return saveAdminConfig();
  if (event.target.closest("[data-admin-save-translation-terms]")) return saveTranslationTerms();
  if (event.target.closest("[data-admin-logout]")) return logoutAdmin();
});

document.addEventListener("change", (event) => {
  if (event.target.matches('[name="aiModelApiType"]')) return syncAiModelInterfaceFields(event.target);
  if (event.target.matches('[data-master-entity-form="projects"] [data-master-field="project_type"]')) {
    const allowance = event.target.closest('[data-master-entity-form="projects"]')?.querySelector('[data-master-field="npt_allowance_hours"]');
    if (allowance) allowance.value = String(PROJECT_NPT_DEFAULT_HOURS[event.target.value] ?? 5);
    return;
  }
  if (event.target.matches("[data-admin-page-size]")) return setAdminPageSize(event.target.dataset.adminPageSize, Number(event.target.value || ADMIN_DEFAULT_PAGE_SIZE));
  if (event.target.matches("[data-admin-page-jump]")) return commitAdminPageJump(event.target);
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
  if (event.key === "Enter" && event.target.matches("[data-admin-page-jump]")) {
    event.preventDefault();
    return commitAdminPageJump(event.target);
  }
  if (["Enter", " "].includes(event.key) && event.target.matches("[data-admin-open-translation-queue]")) {
    event.preventDefault();
    return openTranslationQueue();
  }
  if (event.key === "Escape") closeAdminModal();
});

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) scheduleAdminQueuePoll(0);
});

loadAdminSession();
