#!/usr/bin/env python3
"""Generate static blog HTML from the supported Markdown subset, without dependencies."""
from pathlib import Path
from datetime import date
from html import escape
import json
import math
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://radekrosastrong.cz'

def template(name, values):
    source = (ROOT / 'templates/blog' / name).read_text()
    return re.sub(r'\{\{([a-z_]+)\}\}', lambda m: str(values[m[1]]), source)

def inline(text):
    text = escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

def plain(text):
    return text.replace('**', '').replace('*', '').replace('\n', ' ').strip()

def render_markdown(source):
    """Headings, paragraphs, emphasis, unordered lists and thematic breaks only.

    HTML is escaped. Reject unsupported blocks instead of silently losing content.
    """
    blocks = re.split(r'\n\s*\n', source.strip())
    output, headings = [], []
    for block in blocks:
        if block.startswith('# '):
            raise ValueError('The H1 belongs in the page header, not the article body')
        if block.startswith('## '):
            title = block[3:]
            anchor = f'kapitola-{len(headings) + 1}'
            headings.append((anchor, title))
            output.append(f'<h2 id="{anchor}">{inline(title)}</h2>')
        elif block == '---':
            output.append('<hr>')
        elif block.startswith('- '):
            lines = block.splitlines()
            if any(not line.startswith('- ') for line in lines):
                raise ValueError('Unsupported list continuation')
            output.append('<ul>' + ''.join('<li>' + inline(line[2:]) + '</li>' for line in lines) + '</ul>')
        else:
            if re.match(r'^(?:#{3,}|>|```|\d+\.)', block):
                raise ValueError('Unsupported Markdown block; extend the renderer explicitly')
            output.append('<p>' + '<br>\n'.join(inline(line.rstrip()) for line in block.splitlines()) + '</p>')
    return '\n'.join(output), headings

def main():
    entries = json.loads((ROOT / 'content/blog/articles.json').read_text())
    slugs, cards, urls = set(), [], [BASE_URL + '/blog/']
    for entry in entries:
        slug = entry['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Invalid or duplicate slug: ' + slug)
        slugs.add(slug)
        source_path = ROOT / 'content/blog' / entry['source']
        if source_path.resolve().parent != (ROOT / 'content/blog').resolve():
            raise ValueError('Article source must be in content/blog')
        source = source_path.read_text()
        parts = re.split(r'\n\s*\n', source.strip(), maxsplit=2)
        if len(parts) < 3 or not parts[0].startswith('# '):
            raise ValueError('Article requires an H1, perex and body')
        heading, perex, body = parts[0][2:], parts[1], parts[2]
        rendered, headings = render_markdown(body)
        minutes = max(1, math.ceil(len(re.findall(r'\b[\w]+(?:[’–-][\w]+)*\b', plain(source))) / 200))
        published = entry.get('published')
        if published and date.fromisoformat(published) > date.today():
            raise ValueError('Publication date cannot be in the future')
        date_html = (f'<time datetime="{published}">{date.fromisoformat(published).strftime("%d. %m. %Y")}</time>'
                     if published else '<span>Připraveno k publikaci</span>')
        url = BASE_URL + '/blog/' + slug + '/'
        urls.append(url)
        schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': heading,
                  'description': entry['description'], 'author': {'@type': 'Person', 'name': entry['author'], 'url': BASE_URL + '/#about'},
                  'mainEntityOfPage': url, 'url': url, 'inLanguage': 'cs', 'articleSection': entry['category'],
                  'timeRequired': f'PT{minutes}M'}
        extra = ''
        if published:
            schema['datePublished'] = published
            extra = f'<meta property="article:published_time" content="{published}">'
        else:
            extra = '<meta name="robots" content="noindex, follow">'
        extra += '\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
        common = dict(title=escape(entry['seoTitle']), description=escape(entry['description']), canonical=url,
                      og_type='article', extra_meta=extra, blog_current='location')
        content = template('article.html', dict(category=escape(entry['category']), heading=escape(heading), author=escape(entry['author']),
                           date=date_html, reading_time=minutes, perex='<p>' + inline(perex) + '</p>', body=rendered,
                           toc=''.join(f'<li><a href="#{a}">{escape(t)}</a></li>' for a,t in headings)))
        output = ROOT / 'blog' / slug / 'index.html'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(template('base.html', dict(common, content=content)))
        cards.append(f'''<article class="blog-card"><p class="blog-category">{escape(entry['category'])}</p><h3><a href="/blog/{slug}/">{escape(heading)}</a></h3><p class="blog-card-perex">{escape(plain(perex))}</p><div class="blog-meta"><span>{escape(entry['author'])}</span>{date_html}<span>{minutes} min čtení</span></div><a class="blog-read" href="/blog/{slug}/">Přečíst článek <span aria-hidden="true">→</span></a></article>''')
    content = template('index.html', dict(cards='\n'.join(cards)))
    (ROOT / 'blog/index.html').write_text(template('base.html', dict(content=content, title='Blog – Myšlenky. Zkušenosti. Trénink. | Radek Rosa',
       description='Odborné poznatky a praktické zkušenosti Radka Rosy o trenérské profesi, silovém tréninku a sportovní přípravě.',
       canonical=BASE_URL+'/blog/', og_type='website', blog_current='page',
       extra_meta='' if any(e.get('published') for e in entries) else '<meta name="robots" content="noindex, follow">')))
    # Preserve the original sitemap formatting and non-blog entries verbatim.
    sitemap = ROOT / 'sitemap.xml'
    xml = sitemap.read_text()
    ET.fromstring(xml)  # Fail clearly rather than rewrite malformed XML.
    xml = re.sub(r'\s*<url>\s*<loc>https://radekrosastrong\.cz/blog/[^<]*</loc>.*?</url>', '', xml, flags=re.S)
    additions = ''.join('  <url><loc>' + escape(url) + '</loc></url>\n' for url in urls)
    sitemap.write_text(xml.replace('</urlset>', additions + '</urlset>'))
    print(f'Generated blog index and {len(entries)} article(s). Set published to the actual release date before deployment.')

if __name__ == '__main__':
    main()
