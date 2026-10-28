"""Validate locale coverage, SEO, source preservation and publication gating."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import collections
import importlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
build=importlib.import_module('build_i18n')

class Page(HTMLParser):
    def __init__(self,html):
        super().__init__();self.tags=[];self.text=[];self.stack=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if not self.stack or not self.stack[-1][1]:self.tags.append((tag,attrs))
        skip=(self.stack and self.stack[-1][1]) or tag in ('script','style','template')
        if tag not in build.VOID:self.stack.append((tag,skip))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break
    def handle_data(self,text):
        if not self.stack or not self.stack[-1][1]:self.text.append(text)
    def attrs(self,tag):return [a for t,a in self.tags if t==tag]
    def canonical(self):return next(a['href'] for a in self.attrs('link') if a.get('rel')=='canonical')

def local_file(route):return ROOT/(route.lstrip('/')+('index.html' if route.endswith('/') else ''))

class I18nTests(unittest.TestCase):
    def test_routes_seo_and_all_links(self):
        routes=json.loads((ROOT/'i18n/route-map.json').read_text())
        seen=set()
        for route in routes.values():
            cs,en=route['cs'],route.get('en')
            if not en:continue
            self.assertNotIn(en,seen);seen.add(en)
            self.assertNotIn('/en/en/',en)
            english=Page(local_file(en).read_text());czech=Page(local_file(cs).read_text())
            self.assertEqual(english.attrs('html')[0]['lang'],'en')
            if route['indexable']:
                self.assertEqual(english.canonical(),build.BASE+en)
                self.assertEqual(czech.canonical(),build.BASE+cs)
                for page in (english,czech):
                    alternatives={a['hreflang']:a['href'] for a in page.attrs('link') if a.get('rel')=='alternate'}
                    self.assertEqual(alternatives,{'cs-CZ':build.BASE+cs,'en':build.BASE+en,'x-default':build.BASE+cs})
            for tag,attrs in english.tags:
                for key in ('href','src','poster'):
                    value=attrs.get(key)
                    if not value:continue
                    url=urlsplit(urljoin(build.BASE+en,value))
                    if url.netloc!='radekrosastrong.cz' or url.scheme not in ('http','https'):continue
                    self.assertTrue(local_file(url.path).exists(),(en,value))
            payments=lambda page:collections.Counter(a['href'] for a in page.attrs('a') if a.get('href','').startswith('https://buy.stripe.com/'))
            self.assertEqual(payments(czech),payments(english))
            external=lambda page:collections.Counter(a['href'] for a in page.attrs('a') if a.get('href','').startswith(('http://','https://')) and not a['href'].startswith(build.BASE))
            self.assertEqual(external(czech),external(english))
            mail=lambda page:collections.Counter(a['href'].split('?',1)[0] for a in page.attrs('a') if a.get('href','').startswith('mailto:'))
            self.assertEqual(mail(czech),mail(english))
            assets=lambda page,base:collections.Counter(urlsplit(urljoin(build.BASE+base,a.get('src',''))).path for t,a in page.tags if t in ('img','video','source') and a.get('src'))
            self.assertEqual(assets(czech,cs),assets(english,en))

    def test_no_untranslated_visible_catalogue_entries(self):
        catalogue=build.load_catalogue()
        for path in (ROOT/'en').rglob('*.html'):
            for text in Page(path.read_text()).text:
                key=build.normal(text)
                if key in catalogue:self.assertEqual(key,catalogue[key],(str(path),key))

    def test_date_price_and_reading_time_formatting(self):
        for source,target in [('14.–15. 11. 2026','14–15 November 2026'),('1.1.2026','1 January 2026'),('14 000 Kč','CZK 14,000'),('7 000 Kč','CZK 7,000'),('7 min čtení','7 min read')]:
            self.assertEqual(build.english_format(source),target)

    def test_czech_text_preserved(self):
        config=json.loads((ROOT/'i18n/config.json').read_text())
        # Blog discovery changes when an article is added; unrelated page copy must not.
        sources=[p['source'] for p in config['pages'] if p['source'] != 'blog/index.html']
        for source in sources:
            original=subprocess.check_output(['git','show','HEAD:'+source],cwd=ROOT,text=True)
            current=build.clean((ROOT/source).read_text())
            if source=='index.html':
                # Only these approved qualification corrections may change home copy.
                for old,new in [('Daru Phil','Phil Daru'),('Alex Natura','Alex Natera'),('Fast twich fibers','Fast twitch fibers')]:
                    original=original.replace(old,new)
            self.assertEqual(build.normal(' '.join(Page(build.clean(original)).text)),build.normal(' '.join(Page(current).text)),source)
        source='content/blog/jak-poznat-kvalitniho-trenera.md'
        self.assertEqual(subprocess.check_output(['git','show','HEAD:'+source],cwd=ROOT),(ROOT/source).read_bytes())
        source='blog/jak-poznat-kvalitniho-trenera/index.html'
        original=subprocess.check_output(['git','show','HEAD:'+source],cwd=ROOT,text=True)
        current=(ROOT/source).read_text()
        prose=lambda html:re.search(r'<div class="blog-prose" data-article-body>(.*?)</div>\s*<section class="blog-author"',html,re.S)[1]
        self.assertEqual(prose(original),prose(current))

    def test_draft_translation_creates_no_public_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for folder in ('i18n','content','templates'):shutil.copytree(ROOT/folder,root/folder)
            routes=json.loads((ROOT/'i18n/route-map.json').read_text())
            for route in routes.values():
                target=root/route['source'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/route['source'],target)
            (root/'assets').mkdir();(root/'assets/images').symlink_to(ROOT/'assets/images',target_is_directory=True)
            old_root,old_blog_root=build.ROOT,build.blog.ROOT
            build.ROOT=build.blog.ROOT=root
            try:
                build.main()
                article=root/'en/blog/how-to-choose-a-good-personal-trainer/index.html'
                self.assertTrue(article.exists())
                metadata=root/'content/blog/articles.json';entries=json.loads(metadata.read_text())
                for entry in entries:
                    entry['locales']['en']['status']='draft';entry['locales']['en']['source']='does-not-exist.md'
                metadata.write_text(json.dumps(entries))
                index=root/'blog/index.html'
                index.write_text(index.read_text().replace('Jak poznat kvalitního trenéra? Podle čeho si vybrat toho správného?', 'Nový český titulek bez anglického překladu'))
                build.main()
                self.assertFalse(article.exists())
                self.assertNotIn('how-to-choose-a-good-personal-trainer', (root/'sitemap.xml').read_text())
                self.assertIn('language-unavailable',(root/'blog/jak-poznat-kvalitniho-trenera/index.html').read_text())
                self.assertNotIn('class="blog-card"',(root/'en/blog/index.html').read_text())
            finally:build.ROOT,build.blog.ROOT=old_root,old_blog_root

if __name__=='__main__':unittest.main()
