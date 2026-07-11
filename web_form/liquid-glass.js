(function () {
  const FILTER_ID = "liquid-glass-filter";
  const MAP_ID = "liquid-glass-map";
  const MAP_WIDTH = 260;
  const MAP_HEIGHT = 180;
  const DISPLACEMENT_SCALE = 68;
  const SURFACE_SELECTOR = [
    ".auth-card",
    ".auth-feature-strip",
    ".pdf-modal-panel",
    ".toast",
  ].join(",");

  function smoothStep(a, b, value) {
    const t = Math.max(0, Math.min(1, (value - a) / (b - a)));
    return t * t * (3 - 2 * t);
  }

  function length(x, y) {
    return Math.sqrt(x * x + y * y);
  }

  function roundedRectSdf(x, y, width, height, radius) {
    const qx = Math.abs(x) - width + radius;
    const qy = Math.abs(y) - height + radius;
    return Math.min(Math.max(qx, qy), 0) + length(Math.max(qx, 0), Math.max(qy, 0)) - radius;
  }

  function liquidFragment(uv) {
    const ix = uv.x - 0.5;
    const iy = uv.y - 0.5;
    const distance = roundedRectSdf(ix, iy, 0.5, 0.5, 0.18);
    const edge = smoothStep(0, 0.12, distance);
    const inner = smoothStep(0.18, 0, Math.abs(distance));
    const bulge = Math.pow(Math.max(0, 1 - length(ix * 1.3, iy * 1.9)), 1.7);
    const chroma = edge * 0.58 + inner * 0.22 + bulge * 0.14;
    const waveX = Math.sin((uv.y * 3.2 + uv.x * 0.9) * Math.PI) * 0.025;
    const waveY = Math.cos((uv.x * 3.6 - uv.y * 0.8) * Math.PI) * 0.025;
    return {
      x: 0.5 + ix * chroma + waveX * edge,
      y: 0.5 + iy * chroma + waveY * edge,
    };
  }

  function displacementMapDataUrl(width, height) {
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d", { willReadFrequently: false });
    const image = context.createImageData(width, height);
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const uv = { x: x / (width - 1), y: y / (height - 1) };
        const map = liquidFragment(uv);
        const offset = (y * width + x) * 4;
        image.data[offset] = Math.max(0, Math.min(255, Math.round(map.x * 255)));
        image.data[offset + 1] = Math.max(0, Math.min(255, Math.round(map.y * 255)));
        image.data[offset + 2] = 128;
        image.data[offset + 3] = 255;
      }
    }
    context.putImageData(image, 0, 0);
    return canvas.toDataURL();
  }

  function ensureFilter() {
    let svg = document.querySelector(".liquid-glass-svg");
    if (!svg) {
      svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("aria-hidden", "true");
      svg.classList.add("liquid-glass-svg");
      document.body.prepend(svg);
    }
    svg.innerHTML = `
      <defs>
        <filter id="${FILTER_ID}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
          <feImage id="${MAP_ID}" href="${displacementMapDataUrl(MAP_WIDTH, MAP_HEIGHT)}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="none" result="map" />
          <feDisplacementMap in="SourceGraphic" in2="map" scale="${DISPLACEMENT_SCALE}" xChannelSelector="R" yChannelSelector="G" result="displaced" />
          <feGaussianBlur in="displaced" stdDeviation="0.18" result="soft" />
          <feColorMatrix in="soft" type="matrix" values="1.08 0 0 0 0  0 1.08 0 0 0  0 0 1.12 0 0  0 0 0 1 0" />
        </filter>
      </defs>`;
  }

  function enhanceSurface(element) {
    element.classList.add("liquid-glass");
    if (!element.querySelector(":scope > .liquid-glass-shine")) {
      const shine = document.createElement("span");
      shine.className = "liquid-glass-shine";
      shine.setAttribute("aria-hidden", "true");
      element.prepend(shine);
    }
  }

  function enhanceAll(root = document) {
    root.querySelectorAll(SURFACE_SELECTOR).forEach(enhanceSurface);
  }

  function bindPointerLight() {
    window.addEventListener("pointermove", (event) => {
      document.documentElement.style.setProperty("--glass-x", `${event.clientX}px`);
      document.documentElement.style.setProperty("--glass-y", `${event.clientY}px`);
    }, { passive: true });
  }

  function observeDynamicSurfaces() {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof Element)) return;
          if (node.matches(SURFACE_SELECTOR)) enhanceSurface(node);
          enhanceAll(node);
        });
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function init() {
    ensureFilter();
    enhanceAll();
    bindPointerLight();
    observeDynamicSurfaces();
    document.documentElement.classList.add("liquid-glass-ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
