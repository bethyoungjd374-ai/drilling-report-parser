const toast = document.querySelector("#toast");
const adminState = {
  authenticated: false,
  user: null,
  permissions: {},
  tab: "overview",
  users: [],
  roles: [],
  config: {},
  dataStatus: null,
  logs: []
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
    const [users, config, dataStatus, logs] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/data-status"),
      adminRequest("/api/admin/audit-logs"),
    ]);
    adminState.users = users.users || [];
    adminState.roles = users.roles || [];
    adminState.config = config.config || {};
    adminState.dataStatus = dataStatus;
    adminState.logs = logs.logs || [];
    renderAdminPanels();
  } catch (error) {
    showToast(error.message);
  }
}

function renderNoPermission() {
  document.querySelector(".admin-sidebar-nav")?.setAttribute("hidden", "");
  document.querySelector('[data-admin-panel="overview"]').hidden = false;
  document.querySelector('[data-admin-panel="overview"]').innerHTML = `<section class="panel admin-empty-panel"><div><h2>无后台权限</h2><p>当前账号可以登录前台，但没有系统后台管理权限。</p></div><a class="button secondary" href="/web_form/">返回前台</a></section>`;
  document.querySelectorAll('[data-admin-panel]:not([data-admin-panel="overview"])').forEach((panel) => panel.hidden = true);
}

function renderAdminPanels() {
  renderAdminOverview();
  renderAdminUsers();
  renderAdminRoles();
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
        <span><strong>系统参数</strong><small>维护记录分页、语言、Excel 路径和源文件策略</small></span>
        <span><strong>数据维护</strong><small>下载或备份当前 Excel 库</small></span>
        <span><strong>操作审计</strong><small>追踪后台登录、账号和配置变更</small></span>
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
  host.innerHTML = `<section class="panel"><div class="panel-heading"><h2>日志审计</h2><span class="panel-note">最近 120 条后台操作</span></div><div class="table-wrap"><table class="record-table admin-table"><thead><tr><th>时间</th><th>用户</th><th>动作</th><th>模块</th><th>对象</th><th>结果</th><th>备注</th></tr></thead><tbody>${(adminState.logs || []).map((log) => `<tr><td>${escapeHtml(log.time)}</td><td>${escapeHtml(log.user)}</td><td>${escapeHtml(log.action)}</td><td>${escapeHtml(log.module)}</td><td>${escapeHtml(log.target)}</td><td>${escapeHtml(log.result)}</td><td>${escapeHtml(log.note)}</td></tr>`).join("") || `<tr><td colspan="7">暂无日志</td></tr>`}</tbody></table></div></section>`;
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
  const edit = event.target.closest("[data-admin-edit-user]");
  if (edit) return fillAdminUserForm(edit.dataset.adminEditUser);
  if (event.target.closest("[data-admin-save-user]")) return saveAdminUser();
  if (event.target.closest("[data-admin-add-role]")) return addAdminRole();
  if (event.target.closest("[data-admin-save-roles]")) return saveAdminRoles();
  if (event.target.closest("[data-admin-save-config]")) return saveAdminConfig();
  if (event.target.closest("[data-admin-backup]")) return backupAdminDatabase();
  if (event.target.closest("[data-admin-logout]")) return logoutAdmin();
});

loadAdminSession();
