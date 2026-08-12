(() => {
  const shinylivePreviews = document.querySelectorAll(".shinylive-python");
  const shinylivePreviewCards = new Map();
  const shinyliveRunner = document.querySelector(
    'script[src*="run-python-blocks.js"]',
  );
  let shinyliveImportId = 0;

  // The Quarto Shinylive module runs after parsing. Rename its source blocks now
  // so its eager page-wide scan has nothing to start.
  shinylivePreviews.forEach((preview) => {
    preview.classList.replace(
      "shinylive-python",
      "deferred-shinylive-python",
    );
    shinylivePreviewCards.set(
      preview.closest(".component-list-card") || preview,
      preview,
    );
  });

  const iframePreviewCards = new Map();
  document.querySelectorAll("iframe[data-src]").forEach((preview) => {
    iframePreviewCards.set(
      preview.closest(".component-list-card") || preview,
      preview,
    );
  });

  function loadIframePreview(preview) {
    preview.addEventListener(
      "load",
      () => preview.classList.remove("is-loading"),
      { once: true },
    );
    preview.src = preview.dataset.src;
    preview.removeAttribute("data-src");
  }

  function startShinylivePreviews(previews) {
    if (!previews.length || !shinyliveRunner) return;
    shinyliveImportId += 1;
    import(`${shinyliveRunner.src}?component-preview=${shinyliveImportId}`).catch(
      (error) => {
        previews.forEach((preview) =>
          preview.classList.replace(
            "shinylive-python",
            "deferred-shinylive-python",
          ),
        );
        console.error("Unable to load component preview", error);
      },
    );
  }

  if (!("IntersectionObserver" in window)) {
    iframePreviewCards.forEach(loadIframePreview);
    shinylivePreviews.forEach((preview) =>
      preview.classList.replace(
        "deferred-shinylive-python",
        "shinylive-python",
      ),
    );
    return;
  }

  // Observe the card rather than the preview inside it: cards are
  // `content-visibility: auto`, and descendants of a skipped subtree can report
  // an empty intersection rect.
  function observeCards(cards, rootMargin, onVisible) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = [];
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          observer.unobserve(entry.target);
          visible.push(cards.get(entry.target));
        });
        onVisible(visible);
      },
      { rootMargin },
    );
    cards.forEach((_preview, card) => observer.observe(card));
  }

  // A static preview is a few KB of HTML on top of libraries the first one
  // warms for the rest, so it can be fetched several screens ahead and be
  // there the moment it scrolls in. Shinylive previews each boot a Python
  // runtime, so they stay close to the viewport.
  observeCards(iframePreviewCards, "1500px 0px", (previews) =>
    previews.forEach(loadIframePreview),
  );
  observeCards(shinylivePreviewCards, "400px 0px", (previews) => {
    previews.forEach((preview) =>
      preview.classList.replace(
        "deferred-shinylive-python",
        "shinylive-python",
      ),
    );
    startShinylivePreviews(previews);
  });
})();
