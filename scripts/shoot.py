#!/usr/bin/env python3
"""G2/G8 的截图器：本 skill 自带，不依赖外部工具。

做法：在项目目录起 stdlib http.server → 用本机浏览器 headless 截图 → 用 Pillow 校验尺寸。
用法:
  python3 shoot.py --project <目录> [--pages pages/list.html,...] \
      [--sizes 1440x900,768x1024,375x812] [--out qa/screenshots] [--browser auto]
退出码: 0=成功 1=有页面失败 2=用法错误 3=没有可用浏览器（跳过）
"""
from __future__ import annotations
import argparse, http.server, socket, socketserver, subprocess, sys, tempfile, threading
from pathlib import Path

CANDIDATES = [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


def find_browser(explicit: str | None) -> str | None:
    if explicit and explicit != "auto":
        return explicit if Path(explicit).is_file() else None
    for p in CANDIDATES:
        if Path(p).is_file():
            return p
    return None


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):  # 静默
        pass


def serve(root: Path):
    handler = lambda *a, **k: Quiet(*a, directory=str(root), **k)
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def crop_fullpage(path: Path, w: int) -> None:
    """整页图：按内容裁掉底部空白（用页面背景色判定）。"""
    try:
        from PIL import Image
    except Exception:
        return
    im = Image.open(path).convert("RGB")
    px = im.load()
    bg = px[2, 2]
    last = im.height - 1
    while last > 10:
        row_same = all(px[x, last] == bg for x in range(0, w, 7))
        if not row_same:
            break
        last -= 1
    if last < im.height - 1:
        im.crop((0, 0, im.width, min(im.height, last + 24))).save(path)


def shoot(browser: str, url: str, w: int, h: int, out: Path) -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--no-first-run", "--no-default-browser-check",
           f"--window-size={w},{h}", f"--screenshot={out}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    return out.is_file() and out.stat().st_size > 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--pages", default=None, help="逗号分隔，相对项目根；默认读 pages-manifest.json")
    ap.add_argument("--sizes", default="1440x900,768x1024,375x812")
    ap.add_argument("--out", default="qa/screenshots")
    ap.add_argument("--browser", default="auto")
    ap.add_argument("--fullpage", action="store_true", help="用 --screenshot 默认即整页")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"[shoot] 项目不存在 {root}", file=sys.stderr)
        return 2
    browser = find_browser(args.browser)
    if not browser:
        print("[shoot] SKIP：没找到可用浏览器（Edge/Chrome/Chromium/Brave）")
        return 3
    pages = [p.strip() for p in args.pages.split(",")] if args.pages else []
    if not pages:
        man = root / "pages-manifest.json"
        if man.is_file():
            import json
            pages = [p["path"] for p in json.loads(man.read_text(encoding="utf-8")).get("pages", [])]
    if not pages:
        print("[shoot] 没有页面可截（给 --pages 或提供 pages-manifest.json）", file=sys.stderr)
        return 2
    sizes = []
    for s in args.sizes.split(","):
        w, _, h = s.partition("x")
        sizes.append((int(w), int(h)))

    srv, port = serve(root)
    outdir = root / args.out
    failed = []
    try:
        for page in pages:
            stem = Path(page).stem
            for w, h in sizes:
                name = f"{stem}-{w}.png"
                dst = outdir / name
                render_h = 6000 if args.fullpage else h
                if not shoot(browser, f"http://127.0.0.1:{port}/{page}", w, render_h if args.fullpage else h, dst):
                    failed.append(name)
                    continue
                if args.fullpage:
                    crop_fullpage(dst, w)
                try:
                    from PIL import Image
                    iw, ih = Image.open(dst).size
                    flag = "" if iw <= w + 2 else f"  ⚠ 横向溢出（实宽 {iw}）"
                    print(f"  {name}: {iw}×{ih}{flag}")
                except Exception:
                    print(f"  {name}: 已生成（未校验尺寸）")
    finally:
        srv.shutdown()
    if failed:
        print(f"[shoot] FAIL：{len(failed)} 张失败（{', '.join(failed[:5])}）")
        return 1
    print(f"[shoot] 完成：{len(pages) * len(sizes)} 张 → {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
