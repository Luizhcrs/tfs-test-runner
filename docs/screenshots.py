"""Generate README/USAGE screenshots from the sample HTML kit.

Usage:
    cd <repo root>
    python docs/screenshots.py

Outputs PNGs to docs/images/.
"""
from __future__ import annotations
import asyncio, base64, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tfs_test_runner.parse import parse_xlsx
from tfs_test_runner.translate import translate_cases
from tfs_test_runner.classify import load_yaml_phases, apply_yaml_phases
from tfs_test_runner.render import render

OUT_DIR = ROOT / "docs" / "images"
SAMPLE_XLSX = ROOT / "examples" / "sample.xlsx"
PHASES_YAML = ROOT / "examples" / "sample-phases.yaml"
HTML_OUT = ROOT / "docs" / "_screenshot-sample.html"


def make_demo_image(label: str, color: str = "#4a90e2") -> str:
    """Synthetic PNG: simple labeled rectangle. Returns data URL."""
    # 800x500 colored rect with white text — generated as SVG then rasterized via base64.
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
        <rect width="800" height="500" fill="{color}"/>
        <rect x="20" y="20" width="760" height="460" fill="white" stroke="#333" stroke-width="2"/>
        <text x="400" y="240" font-family="Arial,sans-serif" font-size="40" font-weight="bold"
              text-anchor="middle" fill="#333">{label}</text>
        <text x="400" y="290" font-family="Arial,sans-serif" font-size="20"
              text-anchor="middle" fill="#666">Synthetic screenshot for demo purposes</text>
    </svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


# Pre-populated state: 1 case fully done with images, 1 in progress, 1 pending.
DEMO_STATE_SCRIPT = r"""
async () => {
    // Open IndexedDB and put demo images
    const imgs = window.__demoImages;
    const db = await new Promise((res, rej) => {
        const req = indexedDB.open('e350-imgs', 1);
        req.onupgradeneeded = (e) => e.target.result.createObjectStore('imgs', {keyPath: 'id'});
        req.onsuccess = (e) => res(e.target.result);
        req.onerror = (e) => rej(e);
    });
    const tx = db.transaction('imgs', 'readwrite');
    const store = tx.objectStore('imgs');
    for (const [id, dataUrl] of Object.entries(imgs)) {
        store.put({id, dataUrl, ts: Date.now()});
    }
    await new Promise(r => tx.oncomplete = r);

    // Set localStorage state
    const state = {
        '101:0':  {checked:true, status:'pass', obs:'App opened on Chrome 122; no console errors.'},
        '101:1':  {checked:true, status:'pass', obs:'Used valid email user@example.com.'},
        '101:2':  {checked:true, status:'pass', obs:'Password masked as expected.'},
        '101:3':  {checked:true, status:'pass', obs:'Redirected to /dashboard within 350ms.'},
        'sum:101':{text:'Smoke test passed end-to-end. Run on staging build #4521.'},

        '102:0':  {checked:true, status:'pass'},
        '102:1':  {checked:true, status:'pass'},
        '102:2':  {checked:true, status:'fail', obs:'Error message displayed in English instead of selected pt-BR locale. Logged ticket #BUG-841.'},
        '102:3':  {checked:true, status:'pass'},
        'sum:102':{text:'Localization regression found in the error toast.'},
    };
    const captions = {
        'step:101:0:demo1': 'Login page initial render',
        'step:101:3:demo2': 'Dashboard after successful sign-in',
        'step:102:2:demo3': 'Error toast (note: wrong locale)',
        'case:101:demo0':   'Browser/network tab snapshot',
    };
    localStorage.setItem('e350-tests-v3', JSON.stringify(state));
    localStorage.setItem('e350-tests-v3-cap', JSON.stringify(captions));
    // open all phases & cases by default
    const open = {};
    document.querySelectorAll('.phase').forEach(p => open['p_' + p.dataset.pid] = true);
    document.querySelectorAll('.case').forEach(c => open['c_' + c.dataset.cid] = true);
    localStorage.setItem('e350-tests-v3-open', JSON.stringify(open));
}
"""


def build_sample_html():
    cases = parse_xlsx(SAMPLE_XLSX)
    translate_cases(cases, backend="none")
    cfg = load_yaml_phases(PHASES_YAML)
    phase_data = apply_yaml_phases(cases, cfg)
    render(phase_data, HTML_OUT, page_title="Web App QA — Sprint 42",
           force=True)
    return HTML_OUT


async def capture_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = build_sample_html()

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900},
                                         device_scale_factor=2)
        page = await ctx.new_page()

        # 1) Empty state hero
        await page.goto(html_path.as_uri())
        await page.wait_for_selector(".phase")
        await page.screenshot(path=str(OUT_DIR / "01-empty-overview.png"), full_page=False)

        # 2) Pre-populate state and reload
        demo = {
            "step:101:0:demo1": make_demo_image("Login page", "#5b8cff"),
            "step:101:3:demo2": make_demo_image("Dashboard", "#3fb950"),
            "step:102:2:demo3": make_demo_image("Error toast (wrong locale)", "#f85149"),
            "case:101:demo0":   make_demo_image("DevTools / Network", "#888"),
        }
        await page.evaluate(f"window.__demoImages = {repr(demo)};".replace("'", '"'))
        await page.evaluate(DEMO_STATE_SCRIPT)
        await page.reload()
        await page.wait_for_selector(".case.open")
        await page.wait_for_timeout(500)

        # 3) Hero with progress
        await page.screenshot(path=str(OUT_DIR / "02-hero-progress.png"), full_page=False)

        # 4) Full page (long screenshot of all cases expanded)
        await page.screenshot(path=str(OUT_DIR / "03-full-plan.png"), full_page=True)

        # 5) Single case zoom — focus first case
        first_case = page.locator(".case").first
        await first_case.scroll_into_view_if_needed()
        await page.wait_for_timeout(300)
        bbox = await first_case.bounding_box()
        if bbox:
            clip = {"x": max(0, bbox["x"] - 8), "y": max(0, bbox["y"] - 8),
                    "width": min(1400 - bbox["x"], bbox["width"] + 16),
                    "height": bbox["height"] + 16}
            await page.screenshot(path=str(OUT_DIR / "04-case-detail.png"), clip=clip)

        # 6) Filter chip "Failure" → only failure case
        await page.locator('.chip[data-f="fail"]').click()
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT_DIR / "05-filter-failures.png"), full_page=False)

        # Reset filter
        await page.locator('.chip[data-f="all"]').click()
        await page.wait_for_timeout(300)

        # 7) Print preview emulation (evidence layout — status hidden, default)
        await page.evaluate("document.body.classList.add('print-evidence')")
        await page.emulate_media(media="print")
        await page.screenshot(path=str(OUT_DIR / "06-pdf-evidence.png"), full_page=True)

        # 7b) Same print preview WITH status badges (toggle ON)
        await page.evaluate("document.body.classList.add('show-status-pdf')")
        await page.screenshot(path=str(OUT_DIR / "06b-pdf-evidence-status.png"), full_page=True)

        await page.emulate_media(media="screen")
        await page.evaluate("document.body.classList.remove('print-evidence','show-status-pdf')")

        # 8) Light theme
        await page.evaluate("document.documentElement.dataset.theme = 'light'")
        await page.wait_for_timeout(200)
        await page.screenshot(path=str(OUT_DIR / "08-light-theme.png"), full_page=False)

        # 9) Settings panel open (on light theme — looks cleaner)
        await page.evaluate("document.getElementById('settings-overlay').hidden = false")
        await page.wait_for_timeout(250)
        await page.screenshot(path=str(OUT_DIR / "09-settings-panel.png"), full_page=False)
        await page.evaluate("document.getElementById('settings-overlay').hidden = true")

        # back to dark
        await page.evaluate("document.documentElement.dataset.theme = 'dark'")
        await page.wait_for_timeout(200)

        # 10) Mobile-ish narrow view (dark)
        await page.set_viewport_size({"width": 480, "height": 900})
        await page.reload()
        await page.wait_for_selector(".case.open")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT_DIR / "07-narrow-view.png"), full_page=False)

        await browser.close()

    # Cleanup intermediate HTML
    HTML_OUT.unlink(missing_ok=True)
    for f in sorted(OUT_DIR.glob("*.png")):
        size = f.stat().st_size // 1024
        print(f"  {f.relative_to(ROOT)} ({size} KB)")


if __name__ == "__main__":
    asyncio.run(capture_all())
