(() => {
  "use strict";

  async function requestJson(path, options = {}, defaultError = "请求失败") {
    const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
    const headers = {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    };
    const response = await fetch(path, {
      credentials: "same-origin",
      ...options,
      headers,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || defaultError);
    return payload;
  }

  Object.defineProperty(window, "NexoHttp", {
    value: Object.freeze({ requestJson }),
    configurable: false,
    writable: false,
  });
})();
