const toast = document.querySelector("#toast");
const adminState = {
  authenticated: false,
  user: null,
  permissions: {},
  tab: "overview",
  users: [],
  roles: [],
  config: {},
  projectTeams: { teams: [], projects: [], pending_wells: [] },
  dataStatus: null,
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
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
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
    const [users, config, projectTeams, dataStatus, logs] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/project-teams"),
      adminRequest("/api/admin/data-status"),
      adminRequest("/api/admin/audit-logs"),
    ]);
    adminState.users = users.users || [];
    adminState.roles = users.roles || [];
    adminState.config = config.config || {};
    adminState.projectTeams = { teams: projectTeams.teams || [], projects: projectTeams.projects || [], pending_wells: projectTeams.pending_wells || [] };
    adminState.dataStatus = dataStatus;
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
  renderAdminProjects();
  renderAdminTeams();
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
      ${adminKpi("日报记录", status.records || 0, "Excel库记录数", "database")}
      ${adminKpi("源PDF", status.source_pdf_count || 0, "本地保存数量", "logs")}
      ${adminKpi("库文件", fileSize(status.database_size || 0), status.database_updated_at || "未生成", "settings")}
    </section>
    <section class="panel admin-overview-panel">
      <div class="panel-heading"><h2>后台范围</h2><span class="panel-note">独立管理入口，轻量 JSON 配置</span></div>
      <div class="admin-note-grid">
        <span><strong>账号与角色</strong><small>新增、启停账号并分配固定角色</small></span>
        <span><strong>项目队伍</strong><small>维护合同、队伍和项目井号归属</small></span>
        <span><strong>系统参数</strong><small>维护记录分页、语言、Excel 路径和源文件策略</small></span>
        <span><strong>数据维护</strong><small>下载或备份当前 Excel 库</small></span>
      </div>
    </section>
  `;
}

function adminKpi(label, value, caption, icon) {
  return `<div class="admin-kpi-card"><span class="admin-kpi-icon icon-${escapeHtml(icon)}" aria-hidden="true"></span><div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(caption || "")}</small></div></div>`;
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

function renderAdminProjects() {
  const host = document.querySelector('[data-admin-panel="projects"]');
  const config = adminState.projectTeams || { teams: [], projects: [], pending_wells: [] };
  const teams = config.teams || [];
  const projects = config.projects || [];
  const activeProjects = projects.filter((project) => project.status === "active");
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("项目合同", projects.length, `${activeProjects.length} 个启用`, "database")}
      ${adminKpi("队伍", teams.length, "全局队伍库", "users")}
      ${adminKpi("项目井号", projectWellCount(projects), "已归属井号", "overview")}
      ${adminKpi("待归集", (config.pending_wells || []).length, "日报自动发现", "logs")}
    </section>
    <section class="panel">
      <div class="panel-heading">
        <div><h2>项目合同列表</h2><span class="panel-note">编辑项目时维护绑定队伍、日期和井号</span></div>
        <button class="button small" type="button" data-admin-new-project>新增项目合同</button>
      </div>
      <div class="table-wrap"><table class="record-table admin-table project-table">
        <thead><tr><th>合同号</th><th>项目名称</th><th>状态</th><th>队伍 / 井</th><th>日期</th><th>操作</th></tr></thead>
        <tbody>${projects.map((project) => `<tr><td><strong>${escapeHtml(project.contract_no || "-")}</strong></td><td>${escapeHtml(project.project_name || "-")}</td><td><span class="status-pill ${project.status === "active" ? "uploaded" : "failed"}">${project.status === "active" ? "启用" : "关闭"}</span></td><td>${projectTeamSummary(project)}</td><td>${escapeHtml(project.start_date || "-")} 至 ${escapeHtml(project.end_date || "-")}</td><td><button class="link-button" type="button" data-admin-edit-project="${escapeHtml(project.id)}">编辑</button></td></tr>`).join("") || `<tr><td colspan="6">暂无项目合同</td></tr>`}</tbody>
      </table></div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>项目井号明细</h2><span class="panel-note">按项目展开队伍和井号</span></div>
      <div class="admin-project-cards">${projects.map(projectCard).join("") || `<div class="empty-records">暂无项目配置</div>`}</div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>待归集井号</h2><span class="panel-note">多个启用项目时，日报自动发现的井号先进入这里</span></div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>队伍</th><th>井号</th><th>日报类型</th><th>来源时间</th><th>归属项目</th><th>操作</th></tr></thead>
        <tbody>${(config.pending_wells || []).map((item, index) => `<tr><td>${escapeHtml(item.rig)}</td><td><strong>${escapeHtml(item.wellbore)}</strong></td><td>${escapeHtml(item.report_type || "-")}</td><td>${escapeHtml(item.created_at || "-")}</td><td><select class="admin-inline-select" data-pending-project="${index}">${projectSelectOptions(projects)}</select></td><td><button class="link-button" type="button" data-admin-assign-pending="${index}">归入项目</button></td></tr>`).join("") || `<tr><td colspan="6">暂无待归集井号</td></tr>`}</tbody>
      </table></div>
    </section>
  `;
}

function renderAdminTeams() {
  const host = document.querySelector('[data-admin-panel="teams"]');
  const config = adminState.projectTeams || { teams: [], projects: [], pending_wells: [] };
  const teams = config.teams || [];
  const usedTeams = new Set((config.projects || []).flatMap((project) => (project.rigs || []).map((rig) => rig.rig).filter(Boolean)));
  host.innerHTML = `
    <section class="admin-kpi-grid compact">
      ${adminKpi("队伍总数", teams.length, "全局队伍库", "users")}
      ${adminKpi("已绑定队伍", usedTeams.size, "已用于项目合同", "database")}
      ${adminKpi("启用队伍", teams.filter((team) => team.status !== "inactive").length, "可被项目选择", "overview")}
      ${adminKpi("待归集", (config.pending_wells || []).length, "日报自动发现", "logs")}
    </section>
    <section class="panel">
      <div class="panel-heading">
        <div><h2>队伍列表</h2><span class="panel-note">维护全局队伍库，项目配置中可选择绑定</span></div>
        <button class="button small" type="button" data-admin-new-team>新增队伍</button>
      </div>
      <div class="table-wrap"><table class="record-table admin-table">
        <thead><tr><th>队伍</th><th>编号</th><th>承包商</th><th>状态</th><th>项目绑定</th><th>操作</th></tr></thead>
        <tbody>${teams.map((team) => `<tr><td><strong>${escapeHtml(team.name)}</strong></td><td>${escapeHtml(team.code || "-")}</td><td>${escapeHtml(team.contractor || "-")}</td><td><span class="status-pill ${team.status === "active" ? "uploaded" : "failed"}">${team.status === "active" ? "启用" : "停用"}</span></td><td>${usedTeams.has(team.name) ? "已绑定" : "未绑定"}</td><td><button class="link-button" type="button" data-admin-edit-team="${escapeHtml(team.id)}">编辑</button></td></tr>`).join("") || `<tr><td colspan="6">暂无队伍</td></tr>`}</tbody>
      </table></div>
    </section>
  `;
}

function projectCard(project) {
  return `<article class="admin-project-card"><header><strong>${escapeHtml(project.contract_no || project.project_name)}</strong><span>${escapeHtml(project.project_name || "")}</span></header>${(project.rigs || []).map((rig) => `<div><b>${escapeHtml(rig.rig)}</b><small>${escapeHtml(projectRigDateText(rig))}</small><small>${(rig.wells || []).map(escapeHtml).join("、") || "暂无井号"}</small></div>`).join("") || `<p>暂无队伍</p>`}</article>`;
}

function projectWellCount(projects) {
  return (projects || []).reduce((sum, project) => sum + (project.rigs || []).reduce((inner, rig) => inner + (rig.wells || []).length, 0), 0);
}

function projectTeamSummary(project) {
  const rigs = project.rigs || [];
  return `${rigs.length} 队 / ${projectWellCount([project])} 井`;
}

function projectRigDateText(rig = {}) {
  const start = rig.start_date || "";
  const end = rig.end_date || "";
  if (!start && !end) return "未设置队伍周期";
  return `${start || "-"} 至 ${end || "-"}`;
}

function projectSelectOptions(projects) {
  const active = (projects || []).filter((project) => project.status !== "closed");
  return active.map((project) => `<option value="${escapeHtml(project.id)}">${escapeHtml(project.contract_no || project.project_name || "-")} / ${escapeHtml(project.project_name || "-")}</option>`).join("") || `<option value="">请先新增项目</option>`;
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
    <div class="admin-modal-form compact">
      <label>队伍名称<input name="teamName" value="${escapeHtml(team.name || "")}" placeholder="例如：00 SINOPEC 248" /></label>
      <label>队伍编号<input name="teamCode" value="${escapeHtml(team.code || "")}" placeholder="可选" /></label>
      <label>承包商<input name="teamContractor" value="${escapeHtml(team.contractor || "")}" placeholder="例如：SINOPEC" /></label>
      <label>状态
        <select name="teamStatus">
          <option value="active" ${team.status !== "inactive" ? "selected" : ""}>启用</option>
          <option value="inactive" ${team.status === "inactive" ? "selected" : ""}>停用</option>
        </select>
      </label>
    </div>`,
    `<button class="button secondary" type="button" data-admin-modal-close>取消</button>
    <button class="button" type="button" data-admin-save-team-modal>${isEdit ? "保存队伍" : "新增队伍"}</button>`
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
        <label>默认语言<select name="default_language"><option value="zh">中文</option><option value="en">EN</option><option value="es">ES</option></select></label>
        <label>每页记录数<input name="records_per_page" type="number" min="5" max="100" value="${escapeHtml(config.records_per_page)}" /></label>
        <label>Excel路径<input name="excel_path" value="${escapeHtml(config.excel_path)}" /></label>
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
    <section class="panel"><div class="panel-heading"><h2>数据维护</h2><span class="panel-note">备份当前 Excel 库，查看最近备份</span></div><div class="admin-actions"><a class="button secondary" href="/api/download-database">下载Excel库</a><button class="button" type="button" data-admin-backup>立即备份</button></div><div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>备份文件</th><th>大小</th><th>时间</th></tr></thead><tbody>${(status.backups || []).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong></td><td>${fileSize(item.size)}</td><td>${escapeHtml(item.created_at)}</td></tr>`).join("") || `<tr><td colspan="3">暂无备份</td></tr>`}</tbody></table></div></section>`;
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

async function saveProjectTeamConfig(message = "业务配置已保存") {
  const response = await adminRequest("/api/admin/project-teams", { method: "POST", body: JSON.stringify(adminState.projectTeams || {}) });
  adminState.projectTeams = { teams: response.teams || [], projects: response.projects || [], pending_wells: response.pending_wells || [] };
  showToast(message);
  renderAdminProjects();
  renderAdminTeams();
  renderAdminOverview();
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
  team.status = modal?.querySelector('[name="teamStatus"]')?.value || "active";
  adminState.projectTeams.teams = teams;
  closeAdminModal();
  saveProjectTeamConfig("队伍已保存");
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

async function backupAdminDatabase() {
  try {
    await adminRequest("/api/admin/backup", { method: "POST", body: "{}" });
    showToast("Excel库已备份");
    adminState.dataStatus = await adminRequest("/api/admin/data-status");
    renderAdminData();
    renderAdminOverview();
  } catch (error) {
    showToast(error.message);
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
  const assignPending = event.target.closest("[data-admin-assign-pending]");
  if (assignPending) return assignPendingWell(assignPending.dataset.adminAssignPending);
  if (event.target.closest("[data-admin-save-user]")) return saveAdminUser();
  if (event.target.closest("[data-admin-add-role]")) return addAdminRole();
  if (event.target.closest("[data-admin-save-roles]")) return saveAdminRoles();
  if (event.target.closest("[data-admin-save-project-modal]")) return saveProjectContract();
  if (event.target.closest("[data-admin-save-team-modal]")) return saveTeam();
  if (event.target.closest("[data-admin-save-config]")) return saveAdminConfig();
  if (event.target.closest("[data-admin-backup]")) return backupAdminDatabase();
  if (event.target.closest("[data-admin-logout]")) return logoutAdmin();
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-admin-log-page-size]")) {
    adminState.logsPageSize = Number(event.target.value || 20);
    adminState.logsPage = 1;
    renderAdminLogs();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeAdminModal();
});

loadAdminSession();
