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
  projectTeams: { teams: [], projects: [], pending_wells: [] },
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
    const [users, config, aiModels, aiExtraction, aiExtractionQueue, projectTeams, translationTerms, translationTuning, translationExperience, translationQueue, dataStatus, records, logs] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/ai-models"),
      adminRequest("/api/admin/ai-extraction-rules"),
      adminRequest("/api/admin/ai-extractions"),
      adminRequest("/api/admin/project-teams"),
      adminRequest("/api/admin/translation-terms"),
      adminRequest("/api/admin/translation-tuning"),
      adminRequest("/api/admin/translation-experience?limit=200"),
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
    adminState.translationExperience = { suggestions: translationExperience.suggestions || [], counts: translationExperience.counts || {}, loading: false };
    adminState.translationQueue = translationQueue || adminState.translationQueue;
    adminState.dataStatus = dataStatus;
    adminState.records = records.records || [];
    adminState.logs = logs.logs || [];
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
  const counts = { all: records.length, pending: 0, processing: 0, completed: 0 };
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
  if (["QUEUED", "IN_PROGRESS"].includes(value)) return "processing";
  if (row.needs_translation) return "pending";
  if (value === "COMPLETED") return "completed";
  if (["PENDING", "STOPPED", "FAILED", "STALE", ""].includes(value)) return "pending";
  return "other";
}

function filterAiQueueRecords(records = [], tab = "all") {
  return tab === "all" ? records : records.filter((row) => aiQueueStatusGroup(row.status, row) === tab);
}

function preferredExtractionQueueStatusTab(records = [], currentTab = "pending") {
  if (filterAiQueueRecords(records, currentTab).length) return currentTab;
  return ["pending", "processing", "completed"].find((tab) => filterAiQueueRecords(records, tab).length) || currentTab;
}

function aiQueueStatusTabsMarkup(kind, records = [], activeTab = "pending") {
  const counts = { all: records.length, pending: 0, processing: 0, completed: 0 };
  records.forEach((row) => {
    const group = aiQueueStatusGroup(row.status, row);
    if (counts[group] !== undefined) counts[group] += 1;
  });
  const labels = { all: "全部", pending: "未处理", processing: "进行中", completed: "已完成" };
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
  if (tab === "pending") return `<button class="button small" type="button" data-admin-queue-extractions="continue">开始提炼选中</button>`;
  return `<span class="panel-note">请选择“未处理”“进行中”或“已完成”后执行批量操作</span>`;
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
  return [["drilling", "钻井"], ["completion", "完井"], ["workover", "修井"], ["move", "搬迁"]]
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
  return { general: "通用", drilling: "钻井", completion: "完井", workover: "修井", move: "搬迁" }[value] || "通用";
}

function translationTermTypeLabel(value = "preferred") {
  return { protected: "严格保护", preferred: "标准术语", contextual: "上下文术语", phrase: "行业短语" }[value] || "标准术语";
}

function translationTermTypeOptions(selected = "preferred") {
  return [["protected", "严格保护词"], ["preferred", "固定标准术语"], ["contextual", "上下文术语"], ["phrase", "行业短语"]]
    .map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`).join("");
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
            <label>日报类型<select name="translationMemoryReportType"><option value="">通用</option><option value="drilling">钻井</option><option value="completion">完井</option><option value="workover">修井</option><option value="move">搬迁</option></select></label>
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
  if (!['all', 'pending', 'processing', 'completed'].includes(value)) return;
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
  const adminPageButton = event.target.closest("[data-admin-page]");
  if (adminPageButton) return setAdminPage(adminPageButton.dataset.adminPage, Number(adminPageButton.dataset.adminPageValue || 1));
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
  if (event.target.matches('[name="aiModelApiType"]')) return syncAiModelInterfaceFields(event.target);
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
