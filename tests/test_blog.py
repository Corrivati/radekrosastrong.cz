"""Exercise static generation in an isolated copy, never the working site's content."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_blog', ROOT / 'scripts/build_blog.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class BlogGenerationTests(unittest.TestCase):
    def test_preview_publication_and_new_article(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('content/blog', 'templates/blog'):
                shutil.copytree(ROOT / folder, root / folder)
            (root / 'blog').mkdir()
            shutil.copyfile(ROOT / 'sitemap.xml', root / 'sitemap.xml')
            metadata = root / "content/blog/articles.json"
            preview = json.loads(metadata.read_text())
            for entry in preview:
                entry["published"] = None
                entry.pop("thumbnail", None)
            metadata.write_text(json.dumps(preview))
            previous = build.ROOT
            build.ROOT = root
            try:
                build.main()
                article = root / 'blog/jak-poznat-kvalitniho-trenera/index.html'
                self.assertIn('noindex, follow', article.read_text())
                self.assertNotIn('"datePublished"', article.read_text())
                snapshot = {p.relative_to(root): p.read_bytes() for p in (root/'blog').rglob('*.html')}
                sitemap = (root/'sitemap.xml').read_bytes()
                build.main()
                self.assertEqual(snapshot, {p.relative_to(root):p.read_bytes() for p in (root/'blog').rglob('*.html')})
                self.assertEqual(sitemap, (root/'sitemap.xml').read_bytes())
                data_path = root / 'content/blog/articles.json'
                entries = json.loads(data_path.read_text())
                entries[0]['published'] = '2026-01-01'
                # A synthetic fixture proves cards and routes are generated, not hardcoded.
                (root/'content/blog/test.md').write_text('# Test\n\n*Úvod.*\n\n## Kapitola\n\n**Obsah.**')
                entries.append(dict(entries[0], slug='test', source='test.md', seoTitle='Test'))
                data_path.write_text(json.dumps(entries))
                build.main()
                self.assertIn('"datePublished": "2026-01-01"', article.read_text())
                self.assertNotIn('noindex, follow', article.read_text())
                self.assertTrue((root/'blog/test/index.html').exists())
                image = root / 'assets/images/test.webp'
                image.parent.mkdir(parents=True)
                image.write_bytes(b'local asset validation fixture')
                entries[0]['thumbnail'] = {'src': '/assets/images/test.webp', 'alt': 'Náhled článku', 'width': 1200, 'height': 675}
                data_path.write_text(json.dumps(entries))
                build.main()
                self.assertIn('class="blog-card-media"', (root/'blog/index.html').read_text())
                self.assertIn('loading="lazy"', (root/'blog/index.html').read_text())
                entries[0]['thumbnail']['src'] = '/assets/images/missing.webp'
                data_path.write_text(json.dumps(entries))
                with self.assertRaisesRegex(ValueError, 'existing local image'):
                    build.main()
                self.assertEqual((root/'blog/index.html').read_text().count('class="blog-card"'), 2)
                self.assertEqual((root/'sitemap.xml').read_text().count('<loc>https://radekrosastrong.cz/blog/test/</loc>'), 1)
            finally:
                build.ROOT = previous

if __name__ == '__main__':
    unittest.main()
