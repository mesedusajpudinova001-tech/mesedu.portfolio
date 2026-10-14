"""Prepare old-address redirects only after verifying the separate cafe site."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def destination_base(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("Use the HTTPS root URL of the verified separate cafe site.")
    base = value.rstrip("/") + "/"
    if base == "https://mesedusajpudinova001-tech.github.io/mesedu.portfolio/zadu/":
        raise ValueError("The destination must differ from the printed QR address.")
    return base


def page_destination(base, relative):
    # /zadu/interior/menu/... becomes /interior/menu/... within the new site.
    # An index page keeps its directory URL, including the cafe's root entry.
    route = relative.as_posix()
    if route.endswith("index.html"):
        route = route[:-len("index.html")]
    return urljoin(base, route)


def redirect_document(target):
    encoded = json.dumps(target, ensure_ascii=False).replace("<", "\\u003c")
    attribute = escape(target, quote=True)
    return (
        '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="theme-color" content="#ffffff"><title>ZÁDU — меню</title>'
        '<link rel="canonical" href="' + attribute + '">'
        '<script>const target=new URL(' + encoded + ');'
        'target.search=window.location.search;target.hash=window.location.hash;'
        'window.location.replace(target.href);</script>'
        '<noscript><meta http-equiv="refresh" content="0;url=' + attribute + '"></noscript>'
        '</head><body style="margin:0;padding:40px;background:#fff;color:#4f523d;'
        'font-family:Arial,sans-serif"><a href="' + attribute + '" style="color:inherit">'
        'Открыть меню ZÁDU</a></body></html>\n'
    )


def verify_page(task):
    source, target = task
    request = Request(target, headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=25) as response:
        body = response.read()
        if response.status != 200 or urlsplit(response.url).scheme != "https":
            raise ValueError("The destination is not available over HTTPS: " + target)
    if sha256(body).digest() != sha256(source.read_bytes()).digest():
        raise ValueError("The separate site does not match the prepared source: " + target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists():
        parser.error("Choose a new output directory; existing files are never replaced.")
    base = destination_base(args.destination)
    pages = sorted(source_root.rglob("*.html"))
    tasks = [(page, page_destination(base, page.relative_to(source_root))) for page in pages]
    # Never switch the printed QR to an unverified site or an older menu.
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(verify_page, tasks))
    for page, target in tasks:
        relative = page.relative_to(source_root)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(redirect_document(target), encoding="utf-8")
    print("Verified", len(tasks), "pages. Prepared redirects in", output)
    print("The live portfolio and old cafe pages have not been modified.")


if __name__ == "__main__":
    main()
