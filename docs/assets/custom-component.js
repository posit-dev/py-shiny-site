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
    // Load CSS from an external file.
    const cssPaths = [
      "assets/custom-styles.css",
      "/site_libs/bootstrap/bootstrap.min.css",
    ];
    cssPaths.forEach((cssPath) => this.loadStyle(cssPath));
  }

  async loadStyle(cssPath) {
    const response = await fetch(cssPath);
    const css = await response.text();
    const style = document.createElement("style");
    style.textContent = css;
    this.shadowRoot.appendChild(style);
  }
}

customElements.define("custom-component", CustomComponent);
