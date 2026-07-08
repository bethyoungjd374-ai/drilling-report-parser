// Minimal static server for the drilling-report-parser web_form.
// Serves /app/web_form static files. Proxies /api/* to backend on port 8001.
const path = require("path");
const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || "0.0.0.0";
const WEB_ROOT = path.resolve(__dirname, "..", "web_form");
const BACKEND = process.env.BACKEND_URL || "http://127.0.0.1:8001";

const app = express();

// Proxy API and other dynamic backend paths.
const backendProxy = createProxyMiddleware({
  target: BACKEND,
  changeOrigin: true,
  xfwd: true,
  ws: false,
  logLevel: "warn",
});
app.use((req, res, next) => {
  const p = req.path;
  if (
    p.startsWith("/api") ||
    p === "/login" ||
    p.startsWith("/login/") ||
    p === "/admin" ||
    p.startsWith("/admin/")
  ) {
    return backendProxy(req, res, next);
  }
  next();
});

// Root redirects to /login/
app.get("/", (req, res) => res.redirect("/login/"));

// Static files under /web_form/
app.use("/web_form", express.static(WEB_ROOT, { fallthrough: true }));

// Fallback: serve static assets from web_form for anything else.
app.use(express.static(WEB_ROOT));

app.listen(PORT, HOST, () => {
  console.log(`[frontend] listening on http://${HOST}:${PORT}`);
  console.log(`[frontend] proxy /api,/login,/admin -> ${BACKEND}`);
  console.log(`[frontend] static root ${WEB_ROOT}`);
});
