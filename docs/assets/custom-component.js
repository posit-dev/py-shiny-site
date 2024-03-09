const cssPaths = [
  "assets/custom-styles.css",
  "/site_libs/bootstrap/bootstrap.min.css",
];

const styleSheetPromises = {};

// Load a CSS file and return a promise that resolves to a CSSStyleSheet. Multiple calls
// to this function with the same path will return the same promise, so this will not
// make multiple requests for the same file.
function loadStyleSheet(cssPath) {
  if (styleSheetPromises[cssPath] === undefined) {
    styleSheetPromises[cssPath] = (async () => {
      const response = await fetch(cssPath);
      const css = await response.text();
      const sheet = new CSSStyleSheet();
      sheet.replaceSync(css);
      return sheet;
    })();
  }
  return styleSheetPromises[cssPath];
}

class CustomComponent extends HTMLElement {
  constructor() {
    super(); // Always call super first in constructor
    this.attachShadow({ mode: "open" }); // Attach a shadow root to the element.
  }

  connectedCallback() {
    this.moveChildrenToShadowDOM();
    this.loadStyles();
  }

  moveChildrenToShadowDOM() {
    // Move existing children to the shadow DOM.
    while (this.childNodes.length > 0) {
      this.shadowRoot.appendChild(this.firstChild);
    }
  }

  async loadStyles() {
    // Load CSS from external files.
    const loadedStyleSheets = await Promise.all(cssPaths.map(loadStyleSheet));
    this.shadowRoot.adoptedStyleSheets = loadedStyleSheets;
  }
}

customElements.define("custom-component", CustomComponent);
