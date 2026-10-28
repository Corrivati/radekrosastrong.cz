"""Render only the homepage gallery from reviewed photo/crop metadata."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.tif', '.tiff', '.heic', '.heif', '.bmp'}


def load_photos():
    photos = json.loads((ROOT/'content/gallery/photos.json').read_text())
    sources = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and 'novywebfoto' in p.name.lower() and p.suffix.lower() in FORMATS}
    declared = [photo['source'] for photo in photos]
    if not photos or len(set(declared)) != len(declared) or set(declared) != sources:
        raise ValueError('Gallery must contain each novywebfoto original exactly once')
    for photo in photos:
        if not photo.get('alt') or type(photo.get('wide')) is not bool:
            raise ValueError('Gallery needs descriptive alt text and a reviewed frame type')
        for key in ('position', 'mobilePosition'):
            if not re.fullmatch(r'(?:100|[0-9]{1,2})% (?:100|[0-9]{1,2})%', photo[key]):
                raise ValueError('Gallery focal positions must be percentages')
        for kind in ('thumbnail', 'full'):
            asset = photo[kind]
            path = ROOT/asset['src'].lstrip('/')
            if not asset['src'].startswith('/assets/images/gallery/') or not path.resolve().is_relative_to((ROOT/'assets/images/gallery').resolve()) or not path.is_file():
                raise ValueError('Gallery images must exist in assets/images/gallery')
            if any(type(asset.get(k)) is not int or asset[k] <= 0 for k in ('width', 'height')):
                raise ValueError('Gallery images need accurate dimensions')
    return photos


def main():
    photos = load_photos()
    links = []
    for photo in photos:
        thumbnail = photo['thumbnail']
        wide = ' gallery-photo-wide' if photo['wide'] else ''
        links.append(f'<a class="gallery-photo{wide}" href="{escape(photo["full"]["src"])}" style="--gallery-position:{photo["position"]};--gallery-mobile-position:{photo["mobilePosition"]}"><img src="{escape(thumbnail["src"])}" width="{thumbnail["width"]}" height="{thumbnail["height"]}" alt="{escape(photo["alt"])}" loading="lazy" decoding="async"></a>')
    path = ROOT/'index.html'
    html = path.read_text()
    start = html.index('<section class="gallery"')
    end = html.index('</section>', start)+len('</section>')
    section, count = re.subn(r'(<div class="carousel-track">).*?(</div>)', lambda m:m[1]+'\n        '+'\n        '.join(links)+'\n      '+m[2], html[start:end], flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one existing homepage gallery track')
    html = html[:start]+section+html[end:]
    if 'href="/assets/css/gallery.css?v=1"' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/css/gallery.css?v=1">\n</head>')
    path.write_text(html)
    print(f'Built gallery with all {len(photos)} novywebfoto originals; no other sections changed.')


if __name__ == '__main__':
    main()
