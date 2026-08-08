"""Regression tests for the lightweight component gallery previews."""

import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from bs4 import BeautifulSoup
from PIL import Image, ImageChops

COMPONENTS_DIR = Path(__file__).parent
SECTIONS = ("inputs", "outputs", "display-messages", "layout")
PREVIEW_SIZE = (450, 253)


def _changed_pixel_ratio(first: Image.Image, current: Image.Image) -> float:
    difference = ImageChops.difference(first.convert("RGB"), current.convert("RGB"))
    changed = difference.convert("L").point(lambda value: 255 if value > 12 else 0)
    histogram = changed.histogram()
    return histogram[255] / (first.width * first.height)


def _subject_extent(image: Image.Image) -> float:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    difference = ImageChops.difference(rgb, background)
    subject = difference.convert("L").point(lambda value: 255 if value > 12 else 0)
    bounds = subject.getbbox()
    if bounds is None:
        return 0
    left, top, right, bottom = bounds
    return max((right - left) / image.width, (bottom - top) / image.height)


def _component_pages() -> list[Path]:
    return sorted(
        page.parent
        for section in SECTIONS
        for page in (COMPONENTS_DIR / section).glob("*/index.qmd")
    )


@pytest.mark.parametrize(
    "page_dir",
    _component_pages(),
    ids=lambda page: str(page.relative_to(COMPONENTS_DIR)),
)
def test_component_page_has_gallery_preview_assets(page_dir: Path) -> None:
    """A gallery card must never fall back to a loading runtime or empty frame."""
    poster = page_dir / "thumbnail.png"
    assert poster.is_file()
    animation = page_dir / "preview.gif"
    assert animation.is_file()
    with Image.open(poster) as poster_image, Image.open(animation) as animation_image:
        assert poster_image.size == PREVIEW_SIZE
        assert animation_image.size == PREVIEW_SIZE
        assert animation_image.n_frames > 1
        assert poster_image.size == animation_image.size
        assert animation_image.info.get("loop") == 0

        durations = []
        changes = []
        first_frame = animation_image.convert("RGB")
        for frame_index in range(animation_image.n_frames):
            animation_image.seek(frame_index)
            durations.append(animation_image.info.get("duration", 0))
            changes.append(_changed_pixel_ratio(first_frame, animation_image))

        assert 1_800 <= sum(durations) <= 4_000
        assert all(duration > 0 for duration in durations)
        assert max(changes) >= 0.005
        subject_extent = _subject_extent(poster_image)
        assert subject_extent >= 0.28
        if page_dir.parent.name == "inputs":
            assert subject_extent <= 0.62

        animation_image.seek(0)
        difference = ImageChops.difference(
            poster_image.convert("RGB"), animation_image.convert("RGB")
        )
        assert difference.getbbox() is None


def test_rendered_gallery_uses_linked_lazy_animated_images(tmp_path: Path) -> None:
    """Cards link through and load their GIF only while they are being explored."""
    partials = tmp_path / "_partials"
    component = tmp_path / "components" / "example"
    partials.mkdir()
    component.mkdir(parents=True)
    shutil.copy(COMPONENTS_DIR / "_partials" / "components-list.ejs", partials)
    (tmp_path / "_quarto.yml").write_text(
        "project:\n  type: website\nwebsite:\n  title: Test\nformat: html\n"
    )
    (tmp_path / "index.qmd").write_text(
        """---
listing:
  - id: components
    type: grid
    template: _partials/components-list.ejs
    contents:
      - components/example/index.qmd
---

:::{#components}
:::
"""
    )
    (component / "index.qmd").write_text(
        """---
title: Example
appPreview:
  file: components/example/app.py
---
"""
    )
    (component / "thumbnail.png").write_bytes(b"poster")
    (component / "preview.gif").write_bytes(b"animation")

    subprocess.run(
        ["quarto", "render", "index.qmd"],
        cwd=tmp_path,
        check=True,
    )

    output = tmp_path / "_site" / "index.html"
    soup = BeautifulSoup(output.read_text(), "html.parser")
    cards = soup.select(".component-list-card")

    assert len(cards) == 1
    assert not soup.select(".quarto-listing iframe, .quarto-listing .shinylive-wrapper")

    for card in cards:
        column = card.find_parent("div", class_="component-list-column")
        assert column is not None
        assert "g-col-lg-4" in column.get("class", [])
        assert "g-col-lg-6" not in column.get("class", [])
        assert "g-col-md-4" not in column.get("class", [])
        assert card.name == "a"
        assert card.get("href")
        image = card.select_one("img.component-list-preview")
        assert image is not None
        for attribute, filename in (
            ("src", "thumbnail.png"),
            ("data-static-src", "thumbnail.png"),
            ("data-animated-src", "preview.gif"),
        ):
            asset_url = urlparse(image.get(attribute, ""))
            assert asset_url.path.endswith(f"/{filename}")
            version = parse_qs(asset_url.query).get("v")
            assert version and version[0].isdigit()
        assert image.get("alt")
