from pathlib import Path

from playwright.sync_api import Page, expect


DEFERRED_PREVIEWS_SCRIPT = (
    Path(__file__).parent / "_partials" / "deferred-component-previews.js"
)


def test_preview_loads_only_when_it_nears_the_viewport(page: Page) -> None:
    page.set_content(
        """
        <main>
          <iframe id="near" data-src="near.html" title="Near preview"></iframe>
          <div style="height: 3000px"></div>
          <iframe id="far" data-src="far.html" title="Far preview"></iframe>
        </main>
        """
    )

    if DEFERRED_PREVIEWS_SCRIPT.exists():
        page.add_script_tag(path=DEFERRED_PREVIEWS_SCRIPT)

    near = page.locator("#near")
    far = page.locator("#far")
    expect(near).to_have_attribute("src", "near.html")
    expect(far).not_to_have_attribute("src", "far.html")

    far.scroll_into_view_if_needed()
    expect(far).to_have_attribute("src", "far.html")


def test_shinylive_preview_starts_only_when_it_nears_the_viewport(page: Page) -> None:
    page.route(
        "**/run-python-blocks.js?component-preview=*",
        lambda route: route.fulfill(
            content_type="text/javascript",
            headers={"access-control-allow-origin": "*"},
            body="""
                document.querySelectorAll('.shinylive-python').forEach((source) => {
                  const iframe = document.createElement('iframe');
                  iframe.title = source.dataset.title;
                  source.replaceWith(iframe);
                });
            """,
        ),
    )
    page.set_content(
        """
        <script type="application/json"
          src="https://preview.test/run-python-blocks.js"></script>
        <main>
          <div class="component-list-card">
            <pre class="shinylive-python" data-title="Near live preview"></pre>
          </div>
          <div style="height: 3000px"></div>
          <div class="component-list-card">
            <pre class="shinylive-python" data-title="Far live preview"></pre>
          </div>
        </main>
        """
    )
    page.add_script_tag(path=DEFERRED_PREVIEWS_SCRIPT)

    expect(page.locator('iframe[title="Near live preview"]')).to_have_count(1)
    expect(page.locator('[data-title="Far live preview"]')).to_have_class(
        "deferred-shinylive-python"
    )

    page.locator(".component-list-card").last.scroll_into_view_if_needed()
    expect(page.locator('iframe[title="Far live preview"]')).to_have_count(1)
