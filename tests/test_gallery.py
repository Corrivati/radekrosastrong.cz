"""Protect gallery source coverage and the rest of the homepage during regeneration."""
from pathlib import Path
from html.parser import HTMLParser
import importlib
import json
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
gallery = importlib.import_module('build_gallery')


def section(html):
    return re.search(r'<section class="gallery".*?</section>', html, re.S)[0]


class Images(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.images, self.links = [], []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'a':
            self.links.append(attrs)


class GalleryTests(unittest.TestCase):
    def test_all_originals_are_displayed_once_in_both_locales(self):
        photos = gallery.load_photos()
        for page in ('index.html', 'en/index.html'):
            content = Images(section((ROOT/page).read_text()))
            self.assertEqual([a['href'] for a in content.links], [p['full']['src'] for p in photos])
            self.assertEqual([i['src'] for i in content.images], [p['thumbnail']['src'] for p in photos])
            self.assertTrue(all(i.get('alt') and i.get('loading') == 'lazy' for i in content.images))
            self.assertEqual(sum('gallery-photo-wide' in a['class'] for a in content.links), sum(p['wide'] for p in photos))

    def test_regeneration_is_repeatable_and_only_changes_gallery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(ROOT/'index.html', root/'index.html')
            shutil.copytree(ROOT/'content/gallery', root/'content/gallery')
            shutil.copytree(ROOT/'assets/images/gallery', root/'assets/images/gallery')
            photos = gallery.load_photos()
            for photo in photos:
                target = root/photo['source']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/photo['source'], target)
            previous = gallery.ROOT
            gallery.ROOT = root
            try:
                original = (root/'index.html').read_text()
                metadata = root/'content/gallery/photos.json'
                photos[0]['position'] = '42% 38%'
                metadata.write_text(json.dumps(photos))
                gallery.main()
                changed = (root/'index.html').read_text()
                self.assertEqual(original.replace(section(original), ''), changed.replace(section(changed), ''))
                self.assertIn('--gallery-position:42% 38%', changed)
                gallery.main()
                self.assertEqual(changed, (root/'index.html').read_text())
                # A newly uploaded image must not silently disappear from the gallery.
                (root/'strangetraining-old/unmapped-novywebfoto.webp').write_bytes(b'fixture')
                with self.assertRaisesRegex(ValueError, 'each novywebfoto original'):
                    gallery.main()
            finally:
                gallery.ROOT = previous


if __name__ == '__main__':
    unittest.main()
