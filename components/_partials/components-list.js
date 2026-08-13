document.querySelectorAll(".component-list-card").forEach((card) => {
  const image = card.querySelector(".component-list-preview");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!image) return;

  const showAnimation = () => {
    if (reducedMotion.matches) return;
    image.src = image.dataset.animatedSrc;
    card.classList.add("is-previewing");
  };

  const showPoster = () => {
    image.src = image.dataset.staticSrc;
    card.classList.remove("is-previewing");
  };

  card.addEventListener("pointerenter", (event) => {
    if (event.pointerType !== "touch") showAnimation();
  });
  card.addEventListener("pointerleave", showPoster);
  card.addEventListener("focus", showAnimation);
  card.addEventListener("blur", showPoster);
  image.addEventListener("error", () => {
    if (image.src !== new URL(image.dataset.staticSrc, document.baseURI).href) {
      showPoster();
    }
  });
});
