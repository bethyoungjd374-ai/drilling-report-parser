const toast = document.querySelector("#toast");
let loggedInUser = null;
let currentLanguage = localStorage.getItem("drillingReportLanguage") || "zh";

const loginI18n = {
  zh: {
    pageTitle: "登录 - NexoRig",
    systemName: "NexoRig 钻完井管理平台",
    systemSubtitle: "面向钻井、完井、修井业务的日报智能解析、生产统计与运营分析平台",
    featureParse: "日报智能解析",
    featureStats: "生产数据统计",
    featureNpt: "NPT分析与趋势跟踪",
    loginTitle: "账号登录",
    loginSubtitle: "请输入系统账号密码",
    username: "用户名",
    password: "密码",
    remember: "记住我",
    forgot: "忘记密码？",
    loginButton: "登录",
    passwordHint: "首次登录请及时修改初始密码",
    changeTitle: "修改初始密码",
    changeSubtitle: "默认密码不可长期使用",
    oldPassword: "原密码",
    newPassword: "新密码",
    saveEnter: "保存并进入",
    mustChange: "请先修改初始密码",
    passwordChanged: "密码已修改，欢迎 {name}",
  },
  en: {
    pageTitle: "Login - NexoRig",
    systemName: "NexoRig",
    systemSubtitle: "Drilling intelligence for daily report parsing, production statistics, and operations analysis.",
    featureParse: "Smart report parsing",
    featureStats: "Production statistics",
    featureNpt: "NPT trend analysis",
    loginTitle: "Account Login",
    loginSubtitle: "Enter your system username and password",
    username: "Username",
    password: "Password",
    remember: "Remember me",
    forgot: "Forgot password?",
    loginButton: "Log in",
    passwordHint: "Change the initial password after first login",
    changeTitle: "Change Initial Password",
    changeSubtitle: "The default password should not be used long term",
    oldPassword: "Current password",
    newPassword: "New password",
    saveEnter: "Save and enter",
    mustChange: "Please change the initial password first",
    passwordChanged: "Password changed. Welcome, {name}",
  },
  es: {
    pageTitle: "Inicio de sesión - NexoRig",
    systemName: "NexoRig",
    systemSubtitle: "Inteligencia de perforación para análisis de reportes diarios, estadísticas de producción y operación.",
    featureParse: "Análisis inteligente",
    featureStats: "Estadísticas de producción",
    featureNpt: "Tendencias NPT",
    loginTitle: "Inicio de sesión",
    loginSubtitle: "Ingrese su usuario y contraseña del sistema",
    username: "Usuario",
    password: "Contraseña",
    remember: "Recordarme",
    forgot: "¿Olvidó la contraseña?",
    loginButton: "Iniciar sesión",
    passwordHint: "Cambie la contraseña inicial después del primer acceso",
    changeTitle: "Cambiar contraseña inicial",
    changeSubtitle: "La contraseña predeterminada no debe usarse a largo plazo",
    oldPassword: "Contraseña actual",
    newPassword: "Nueva contraseña",
    saveEnter: "Guardar y entrar",
    mustChange: "Cambie primero la contraseña inicial",
    passwordChanged: "Contraseña modificada. Bienvenido, {name}",
  },
};

function authText(key, values = {}) {
  let text = loginI18n[currentLanguage]?.[key] || loginI18n.zh[key] || key;
  Object.entries(values).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, value);
  });
  return text;
}

function escapeHtml(value = "") {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" })[char]);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

function applyLoginLanguage(language) {
  currentLanguage = loginI18n[language] ? language : "zh";
  localStorage.setItem("drillingReportLanguage", currentLanguage);
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : currentLanguage;
  document.title = authText("pageTitle");
  document.querySelectorAll("[data-auth-i18n]").forEach((el) => {
    el.textContent = authText(el.dataset.authI18n);
  });
  document.querySelectorAll("[data-auth-lang]").forEach((button) => {
    button.classList.toggle("active", button.dataset.authLang === currentLanguage);
  });
  document.querySelector('[name="username"]')?.setAttribute("aria-label", authText("username"));
  document.querySelector('[name="password"]')?.setAttribute("aria-label", authText("password"));
  document.querySelector('[name="oldPassword"]')?.setAttribute("aria-label", authText("oldPassword"));
  document.querySelector('[name="newPassword"]')?.setAttribute("aria-label", authText("newPassword"));
}

function nextUrl() {
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next") || "";
  return next.startsWith("/") ? next : "/web_form/";
}

function defaultUrlFor(user, permissions = {}) {
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next") || "";
  const isAdmin = Boolean(permissions.admin || user?.role === "admin");
  if (next.startsWith("/admin/")) return isAdmin ? "/admin/" : "/web_form/";
  if (next.startsWith("/web_form/")) return "/web_form/";
  return "/web_form/";
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || "请求失败");
  return payload;
}

async function checkExistingSession() {
  try {
    const payload = await request("/api/admin/session");
    if (payload.authenticated && !payload.user?.must_change_password) window.location.href = defaultUrlFor(payload.user, payload.permissions || {});
  } catch (error) {
    console.error(error);
  }
}

async function login() {
  const username = document.querySelector('[name="username"]').value.trim();
  const password = document.querySelector('[name="password"]').value;
  try {
    const payload = await request("/api/admin/login", { method: "POST", body: JSON.stringify({ username, password }) });
    loggedInUser = payload.user;
    if (payload.user?.must_change_password) {
      document.querySelector("[data-password-panel]").hidden = false;
      document.querySelector('[name="oldPassword"]').value = password;
      showToast(authText("mustChange"));
      return;
    }
    window.location.href = defaultUrlFor(payload.user, payload.permissions || {});
  } catch (error) {
    showToast(error.message);
  }
}

async function changePassword() {
  const oldPassword = document.querySelector('[name="oldPassword"]').value;
  const newPassword = document.querySelector('[name="newPassword"]').value;
  try {
    await request("/api/admin/change-password", { method: "POST", body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }) });
    showToast(authText("passwordChanged", { name: escapeHtml(loggedInUser?.display_name || loggedInUser?.username || "") }));
    setTimeout(() => window.location.href = defaultUrlFor(loggedInUser, {}), 500);
  } catch (error) {
    showToast(error.message);
  }
}

document.addEventListener("click", (event) => {
  const languageButton = event.target.closest("[data-auth-lang]");
  if (languageButton) {
    applyLoginLanguage(languageButton.dataset.authLang);
    return;
  }
  if (event.target.closest("[data-login-submit]")) login();
  if (event.target.closest("[data-change-password]")) changePassword();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !document.querySelector("[data-password-panel]").hidden) changePassword();
  else if (event.key === "Enter") login();
});

applyLoginLanguage(currentLanguage);
checkExistingSession();
