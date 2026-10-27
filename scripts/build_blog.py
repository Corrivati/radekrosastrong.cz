#!/usr/bin/env python3
"""Generate static blog HTML from the supported Markdown subset, without dependencies."""
from pathlib import Path
from datetime import date
from html import escape
import json
import math
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote

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

def image_markup(image, *, eager=False):
    if not image:
        return ''
    path = ROOT / image['src'].lstrip('/')
    if not image['src'].startswith('/assets/images/') or not path.resolve().is_relative_to((ROOT/'assets/images').resolve()) or not path.is_file():
        raise ValueError('Article image must reference an existing local image in assets/images')
    if not image.get('alt') or any(not isinstance(image.get(k), int) or image[k] <= 0 for k in ('width', 'height')):
        raise ValueError('Article image needs alt text and positive width/height')
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{escape(image["src"])}" alt="{escape(image["alt"])}" width="{image["width"]}" height="{image["height"]}" {loading} decoding="async">'

def comparison_markup(config):
    icons = {
        'education': '<path d="m3 9 9-5 9 5-9 5-9-5Zm4 3v5c3 3 7 3 10 0v-5M21 10v7"/>',
        'communication': '<path d="M21 11a8 8 0 0 1-8 8H5l-4 3 2-6a8 8 0 1 1 18-5Z"/><path d="M7 9h8M7 13h5"/>'
    }
    cards = ''
    for card in config['cards']:
        icon = icons.get(card.get('icon'), '')
        cards += '<section class="blog-comparison-card"><svg viewBox="0 0 24 24" aria-hidden="true">' + icon + '</svg><h3>' + escape(card['title']) + '</h3><ul>'
        cards += ''.join('<li>' + escape(item) + '</li>' for item in card['items']) + '</ul></section>'
    return '<aside class="blog-comparison" data-editorial aria-label="' + escape(config.get('label', 'Odbornost a osobní kompatibilita')) + '"><div class="blog-comparison-grid">' + cards + '</div><p>' + escape(config['message']) + '</p></aside>'

def checklist_markup(items, config, identifier):
    labels = config.get('labels', {})
    questions = ''.join(f'<li><label><input type="checkbox" aria-labelledby="{identifier}-{i}"><span id="{identifier}-{i}">{item}</span></label></li>' for i,item in enumerate(items, 1))
    return f'''<div class="blog-checklist" data-checklist>
<h3 data-editorial>{escape(config['title'])}</h3>
<div class="blog-checklist-progress" data-editorial hidden><p id="{identifier}-count" aria-live="polite" aria-atomic="true"><span data-checklist-count>0</span> / {len(items)} {escape(labels.get('selected', 'označeno'))}</p><progress value="0" max="{len(items)}" aria-labelledby="{identifier}-count"></progress></div>
<ul>{questions}</ul><button class="blog-tool" type="button" data-checklist-reset data-editorial hidden>{escape(labels.get('reset', 'Vymazat výběr'))}</button>
<p class="blog-checklist-note" data-editorial>{escape(labels.get('note', 'Otázky slouží k zamyšlení, nikoli jako odborně ověřený hodnoticí nástroj. Výběr se nikam neodesílá ani neukládá.'))}</p></div>'''

def editorial_body(rendered, features):
    """Enhance existing paragraphs/lists in place; do not duplicate or rewrite them."""
    for quote in features.get('pullQuotes', []):
        original = '<p>' + inline('**' + quote + '**') + '</p>'
        if rendered.count(original) != 1:
            raise ValueError('Pull quote must match one existing bold paragraph exactly')
        rendered = rendered.replace(original, '<blockquote class="blog-pullquote">' + original + '</blockquote>')
    comparison = features.get('comparison')
    checklist = features.get('checklist')
    matched = set()
    def chapter(match):
        number, title, content = match.group(1), match.group(2), match.group(3)
        if checklist and title == escape(checklist['afterHeading']):
            lists = list(re.finditer(r'<ul>(.*?)</ul>', content, re.S))
            if len(lists) != 1:
                raise ValueError('Checklist needs exactly one existing question list')
            item_list = lists[0]
            items = re.findall(r'<li>(.*?)</li>', item_list.group(1), re.S)
            content = content[:item_list.start()] + checklist_markup(items, checklist, 'checklist-'+number) + content[item_list.end():]
            matched.add('checklist')
        if comparison and title == escape(comparison['afterHeading']):
            content += comparison_markup(comparison)
            matched.add('comparison')
        decoration = f' data-number="{int(number):02d}"' if re.match(r'^\d+\.', title) else ''
        return f'<section class="blog-chapter"{decoration} aria-labelledby="kapitola-{number}"><h2 id="kapitola-{number}" tabindex="-1">{title}</h2>{content}</section>'
    rendered = re.sub(r'<h2 id="kapitola-(\d+)">(.*?)</h2>(.*?)(?=<h2 id="kapitola-|\Z)', chapter, rendered, flags=re.S)
    for name in ('comparison', 'checklist'):
        if features.get(name) and name not in matched:
            raise ValueError(f'{name} heading does not match an existing chapter')
    return rendered

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
        features = entry.get('features', {})
        rendered = editorial_body(rendered, features)
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
        hero_image = entry.get('heroImage', entry.get('thumbnail'))
        hero = '<figure class="blog-hero-illustration">' + image_markup(hero_image, eager=True) + '</figure>' if hero_image else ''
        if hero_image:
            schema['image'] = BASE_URL + hero_image['src']
        extra = ''
        if published:
            schema['datePublished'] = published
            extra = f'<meta property="article:published_time" content="{published}">'
        else:
            extra = '<meta name="robots" content="noindex, follow">'
        if hero_image:
            extra += f'\n<meta property="og:image" content="{escape(BASE_URL+hero_image["src"])}">\n<meta property="og:image:alt" content="{escape(hero_image["alt"])}">\n<meta name="twitter:image" content="{escape(BASE_URL+hero_image["src"])}">'
        extra += '\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
        common = dict(title=escape(entry['seoTitle']), description=escape(entry['description']), canonical=url,
                      og_type='article', extra_meta=extra, blog_current='location', page_assets='<link rel="stylesheet" href="/assets/css/blog-article.css?v=1">\n<script src="/assets/js/blog-article.js?v=1" defer></script>')
        related = ''
        others = [other for other in entries if other['slug'] != slug and other.get('published')]
        if others:
            related = '<section class="blog-related"><h2>Související články</h2><ul>'
            for other in others:
                other_title = (ROOT/'content/blog'/other['source']).read_text().splitlines()[0].removeprefix('# ')
                related += f'<li><a href="/blog/{escape(other["slug"])}/">{escape(other_title)}</a></li>'
            related += '</ul></section>'
        content = template('article.html', dict(category=escape(entry['category']), heading=escape(heading), author=escape(entry['author']),
                           date=date_html, reading_time=minutes, perex='<p>' + inline(perex) + '</p>', body=rendered,
                           hero_image=hero, eyebrow=escape(features.get('eyebrow', entry['category'])),
                           share_email=escape('mailto:?' + urlencode({'subject': heading, 'body': url}, quote_via=quote)),
                           canonical=url, related=related,
                           toc=''.join(f'<li><a href="#{a}">{escape(t)}</a></li>' for a,t in headings)))
        output = ROOT / 'blog' / slug / 'index.html'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(template('base.html', dict(common, content=content)))
        media = ''
        thumbnail = entry.get('thumbnail')
        if thumbnail:
            image_path = ROOT / thumbnail['src'].lstrip('/')
            if not thumbnail['src'].startswith('/assets/images/') or not image_path.resolve().is_relative_to((ROOT/'assets/images').resolve()) or not image_path.is_file():
                raise ValueError('Thumbnail must reference an existing local image in assets/images')
            if not thumbnail.get('alt') or any(not isinstance(thumbnail.get(k), int) or thumbnail[k] <= 0 for k in ('width', 'height')):
                raise ValueError('Thumbnail needs descriptive alt text and positive width/height')
            media = f'<a class="blog-card-media" href="/blog/{slug}/" aria-label="{escape(heading)}"><img src="{escape(thumbnail["src"])}" alt="{escape(thumbnail["alt"])}" width="{thumbnail["width"]}" height="{thumbnail["height"]}" loading="lazy" decoding="async"></a>'
        cards.append(f'''<article class="blog-card"><div class="blog-card-copy"><p class="blog-category">{escape(entry['category'])}</p><h3><a href="/blog/{slug}/">{escape(heading)}</a></h3><p class="blog-card-perex">{escape(plain(perex))}</p><div class="blog-meta"><span>{escape(entry['author'])}</span>{date_html}<span>{minutes} min čtení</span></div><a class="blog-read" href="/blog/{slug}/">Přečíst článek <span aria-hidden="true">→</span></a></div>{media}</article>''')
    content = template('index.html', dict(cards='\n'.join(cards)))
    (ROOT / 'blog/index.html').write_text(template('base.html', dict(content=content, title='Blog – Myšlenky. Zkušenosti. Trénink. | Radek Rosa',
       description='Odborné poznatky a praktické zkušenosti Radka Rosy o trenérské profesi, silovém tréninku a sportovní přípravě.',
       canonical=BASE_URL+'/blog/', og_type='website', blog_current='page',
       page_assets='',
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
