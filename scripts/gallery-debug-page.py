"""Write gallery-debug.html: every component thumbnail + GIF at card size.

Open the output directly in a browser to review recorded previews side by side.

    uv run python scripts/gallery-debug-page.py [OUT]  # default: gallery-debug.html
"""
import glob
import os
import sys
import time
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1] if len(sys.argv) > 1 else root / "gallery-debug.html").resolve()
v = int(time.time())
cards = []
for gif in sorted(glob.glob(str(root / "components/*/*/preview.gif"))):
    d = Path(gif).parent
    rel = Path(os.path.relpath(d, out.parent)).as_posix()
    with Image.open(gif) as im:
        ms = sum((im.seek(i), im.info.get("duration", 0))[1] for i in range(im.n_frames))
        n = im.n_frames
    kb = Path(gif).stat().st_size // 1024
    cards.append(f"""
<figure><figcaption><b>{d.parent.name}/{d.name}</b> <span>{n} frames · {ms/1000:.1f}s · {kb} KB</span></figcaption>
<div class="pair"><img src="{rel}/thumbnail.png?v={v}" title="thumbnail.png"><img src="{rel}/preview.gif?v={v}" title="preview.gif"></div></figure>""")
out.write_text(f"""<!doctype html><meta charset=utf-8><title>Gallery debug</title>
<style>
body {{ font: 13px system-ui; margin: 16px; background: #eef0f3; }}
header {{ position: sticky; top: 0; background: #eef0f3; padding: 6px 0; z-index: 1; }}
main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(920px, 1fr)); gap: 18px; }}
figure {{ margin: 0; }} figcaption span {{ color: #666; margin-left: 6px; }}
.pair {{ display: flex; gap: 10px; }}
img {{ width: 450px; height: 253px; background: #fff; border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0,0,0,.1), 0 3px 8px rgba(0,0,0,.1); }}
body.half img {{ width: 225px; height: 126px; }}
body.half main {{ grid-template-columns: repeat(auto-fill, minmax(470px, 1fr)); }}
body.nogif .pair img:last-child, body.nopng .pair img:first-child {{ display: none; }}
body.nogif main, body.nopng main {{ grid-template-columns: repeat(auto-fill, minmax(460px, 1fr)); }}
</style>
<header>{len(cards)} components · left: thumbnail.png, right: preview.gif ·
<label><input type=checkbox onchange="document.body.classList.toggle('half',this.checked)"> half size</label>
<label><input type=checkbox onchange="document.body.classList.toggle('nogif',this.checked)"> hide GIFs</label>
<label><input type=checkbox onchange="document.body.classList.toggle('nopng',this.checked)"> hide thumbnails</label>
<button onclick="document.querySelectorAll('img[src*=gif]').forEach(i=>{{i.src=i.src.replace(/v=[0-9]+/,'v='+Date.now())}})">restart GIFs</button>
</header><main>{''.join(cards)}</main>""")
print(out)
