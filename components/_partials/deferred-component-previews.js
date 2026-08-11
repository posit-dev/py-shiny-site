(() => {
  const iframePreviews = document.querySelectorAll("iframe[data-src]");
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

  function loadIframePreview(preview) {
    preview.addEventListener(
      "load",
      () => preview.classList.remove("is-loading"),
      { once: true },
    );
    preview.src = preview.dataset.src;
    preview.removeAttribute("data-src");
  }

  if (!("IntersectionObserver" in window)) {
    iframePreviews.forEach(loadIframePreview);
    shinylivePreviews.forEach((preview) =>
      preview.classList.replace(
        "deferred-shinylive-python",
        "shinylive-python",
      ),
    );
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const visibleShinylivePreviews = [];

      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);

        if (entry.target.matches("iframe[data-src]")) {
          loadIframePreview(entry.target);
          return;
        }

        const shinylivePreview = shinylivePreviewCards.get(entry.target);
        shinylivePreview.classList.replace(
          "deferred-shinylive-python",
          "shinylive-python",
        );
        visibleShinylivePreviews.push(shinylivePreview);
      });

      if (visibleShinylivePreviews.length && shinyliveRunner) {
        shinyliveImportId += 1;
        import(
          `${shinyliveRunner.src}?component-preview=${shinyliveImportId}`
        ).catch((error) => {
          visibleShinylivePreviews.forEach((preview) =>
            preview.classList.replace(
              "shinylive-python",
              "deferred-shinylive-python",
            ),
          );
          console.error("Unable to load component preview", error);
        });
      }
    },
    { rootMargin: "400px 0px" },
  );

  iframePreviews.forEach((preview) => observer.observe(preview));
  shinylivePreviewCards.forEach((_preview, card) => observer.observe(card));
})();
