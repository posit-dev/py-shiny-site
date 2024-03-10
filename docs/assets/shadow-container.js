const cssPaths = [
  // "assets/custom-styles.css",
  // "assets/shiny/bootstrap/bootstrap.min.css",
];

const styleSheetPromises = {};

/**
 * Loads a CSS file and returns a promise that resolves to a CSSStyleSheet. Multiple
 * calls to this function with the same path will return the same promise, so this will
 * not make multiple requests for the same file.
 *
 * @param {string} path - The path to the CSS file.
 * @returns {Promise<CSSStyleSheet>} A promise that resolves to a CSSStyleSheet.
 */
function loadCSS(path) {
  // function implementation goes here
}
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

/**
 * `ShadowContainer` is a custom HTML element that encapsulates its content in a Shadow
 * DOM. This provides style and markup encapsulation, isolating the styling from the
 * containing document and vice versa.
 *
 * @extends {HTMLElement}
 */
class ShadowContainer extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
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

customElements.define("shadow-container", ShadowContainer);
