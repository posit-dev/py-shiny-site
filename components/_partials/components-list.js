// Total play time of a GIF in ms: the sum of its frame delays, clamped the way
// browsers clamp them (a delay of 0 or 10 ms plays at 100 ms).
const gifDuration = (buffer) => {
  const bytes = new Uint8Array(buffer);
  const colorTable = (packed) => (packed & 0x80 ? 3 << ((packed & 7) + 1) : 0);
  const skipSubBlocks = (i) => {
    while (bytes[i]) i += bytes[i] + 1;
    return i + 1;
  };
  let total = 0;
  let i = 13 + colorTable(bytes[10]);
  while (i < bytes.length) {
    if (bytes[i] === 0x21) {
      if (bytes[i + 1] === 0xf9) {
        const delay = bytes[i + 4] | (bytes[i + 5] << 8);
        total += (delay <= 1 ? 10 : delay) * 10;
      }
      i = skipSubBlocks(i + 2);
    } else if (bytes[i] === 0x2c) {
      i = skipSubBlocks(i + 11 + colorTable(bytes[i + 9]));
    } else {
      break;
    }
  }
  return total;
};

// Touch screens can't hover, so there every card plays while it's on screen.
// Skipped with reduced motion or data saver.
const autoplay =
  window.matchMedia("(hover: none)").matches &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
  !navigator.connection?.saveData;
const onScreen = new Map();
const observer =
  autoplay &&
  new IntersectionObserver(
    (entries) => {
      for (const { target, isIntersecting } of entries) {
        const { show, hide } = onScreen.get(target);
        isIntersecting ? show() : hide();
      }
    },
    { threshold: 0.6 },
  );

document.querySelectorAll(".component-list-card").forEach((card) => {
  const image = card.querySelector(".component-list-preview");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!image) return;

  // Fetch the GIF once, then give it a fresh blob URL on every hover: a new URL
  // always plays from frame 0 (re-setting a cached GIF's src does not restart
  // it in every browser), which keeps the progress bar in step with it.
  let gif;
  let blobUrl;
  let previewing = false;
  // Read the download in chunks so the grey loading bar can show real progress
  // (it fills only at the end if the server sends no Content-Length).
  const download = async (response) => {
    const size = Number(response.headers.get("Content-Length")) || 0;
    const reader = response.body.getReader();
    const chunks = [];
    let received = 0;
    for (let chunk; !(chunk = await reader.read()).done; ) {
      chunks.push(chunk.value);
      received += chunk.value.length;
      if (size) card.style.setProperty("--preview-loaded", received / size);
    }
    card.style.setProperty("--preview-loaded", 1);
    return new Blob(chunks, { type: "image/gif" });
  };

  const loadGif = () =>
    (gif ??= fetch(image.dataset.animatedSrc)
      .then((response) => (response.ok ? download(response) : Promise.reject()))
      .then(async (blob) => {
        const duration = gifDuration(await blob.arrayBuffer());
        card.style.setProperty("--preview-duration", `${duration}ms`);
        return blob;
      }));

  const showPoster = () => {
    previewing = false;
    image.src = image.dataset.staticSrc;
    card.classList.remove("is-previewing", "is-playing");
    if (blobUrl) URL.revokeObjectURL(blobUrl);
    blobUrl = undefined;
  };

  const showAnimation = async () => {
    if (reducedMotion.matches || previewing) return;
    previewing = true;
    card.classList.add("is-previewing");
    try {
      const blob = await loadGif();
      if (!previewing) return;
      blobUrl = URL.createObjectURL(blob);
      image.src = blobUrl;
    } catch {
      showPoster();
    }
  };

  card.addEventListener("pointerenter", (event) => {
    if (event.pointerType !== "touch") showAnimation();
  });
  // A finger lifting off (or scrolling past) a card is not the end of a hover.
  card.addEventListener("pointerleave", (event) => {
    if (event.pointerType !== "touch") showPoster();
  });
  // Keyboard focus only: Android Chrome also focuses a tapped link, which
  // would start downloading the GIF just as the page navigates away.
  card.addEventListener("focus", () => {
    if (card.matches(":focus-visible")) showAnimation();
  });
  card.addEventListener("blur", showPoster);
  image.addEventListener("load", () => {
    if (blobUrl && image.src === blobUrl) card.classList.add("is-playing");
  });
  image.addEventListener("error", () => {
    if (image.src !== new URL(image.dataset.staticSrc, document.baseURI).href) {
      showPoster();
    }
  });
  if (observer) {
    onScreen.set(card, { show: showAnimation, hide: showPoster });
    observer.observe(card);
  }
});
