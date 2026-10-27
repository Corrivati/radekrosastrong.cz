#!/usr/bin/env python3
"""Build static EN counterparts from shared CZ markup and reviewed translation data."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, urljoin, parse_qsl, urlencode, quote
import json
import math
import re
import xml.etree.ElementTree as ET
import build_blog as blog

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://radekrosastrong.cz'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
ATTR_TEXT = {'alt','aria-label','title','placeholder','data-success'}
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']


def clean(html):
    return re.sub(r'<!-- i18n:([\w-]+) -->.*?<!-- /i18n:\1 -->\s*', '', html, flags=re.S)


def normal(text):
    return ' '.join(text.split())


def load_catalogue():
    output = {}
    for path in sorted((ROOT/'i18n/en').glob('*.json')):
        for source, target in json.loads(path.read_text()).items():
            if source in output and output[source] != target:
                raise ValueError('Conflicting translation: '+source)
            output[source] = target
    return output


def english_format(text):
    text = re.sub(r'\b(\d+) min čtení\b',r'\1 min read',text)
    def date_range(m):
        return f'{int(m[1])}–{int(m[2])} {MONTHS[int(m[3])-1]} {m[4]}'
    text = re.sub(r'\b(\d{1,2})\.\s*[–−-]\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b', date_range, text)
    text = re.sub(r'\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b', lambda m:f'{int(m[1])} {MONTHS[int(m[2])-1]} {m[3]}', text)
    return re.sub(r'\b(\d[\d .]*),?-?\s*Kč', lambda m:'CZK '+format(int(re.sub(r'\D','',m[1])),','), text)


class Localiser(HTMLParser):
    def __init__(self, cs_route, routes, catalogue, strict=True):
        super().__init__(convert_charrefs=True)
        self.cs_route, self.routes, self.catalogue, self.strict = cs_route, routes, catalogue, strict
        self.stack, self.output, self.missing = [], [], set()

    def text(self, text):
        key = normal(text)
        if key in self.catalogue:
            left = text[:len(text)-len(text.lstrip())]
            right = text[len(text.rstrip()):]
            return left + self.catalogue[key] + right
        if text in self.catalogue:
            return self.catalogue[text]
        if self.strict and re.search(r'[A-Za-zÀ-ž]', key):
            self.missing.add(key)
        return english_format(text)

    def url(self, value):
        if value.startswith('#'):
            return value
        if value.startswith('mailto:'):
            parts = urlsplit(value)
            values = [(k,self.url(v) if v.startswith(BASE) else self.catalogue.get(v,self.catalogue.get(normal(v),v))) for k,v in parse_qsl(parts.query,keep_blank_values=True)]
            return urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(values,quote_via=quote),parts.fragment))
        parts = urlsplit(urljoin(BASE+self.cs_route, value))
        if parts.netloc != 'radekrosastrong.cz' or parts.scheme not in ('http','https'):
            return value
        path = parts.path
        docs = {'/assets/docs/ochrana-osobnich-udaju.txt':'/assets/docs/en/privacy-policy.txt','/assets/docs/obchodni-podminky.txt':'/assets/docs/en/terms-and-conditions.txt'}
        path = docs.get(path,path)
        target = self.routes.get(path,{}).get('en')
        if target:
            path = target
        # Assets remain shared at the root. Untranslated future articles link explicitly to their real CZ version.
        result = urlunsplit(('', '', path, parts.query, parts.fragment))
        return BASE+result if value.startswith(BASE) else result

    def handle_decl(self, decl): self.output.append('<!'+decl+'>')
    def handle_comment(self, data): self.output.append('<!--'+data+'-->')
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        inert = (self.stack[-1][2] if self.stack else False) or tag=='template'
        raw = tag in ('script','style')
        new = []
        for key,value in attrs:
            if value is None:
                new.append(key);continue
            if tag=='html' and key=='lang':value='en'
            elif key in ('href','src','poster','action'):value=self.url(value)
            elif tag=='meta' and key=='content' and d.get('property')=='og:locale':value='en_GB'
            elif tag=='meta' and key=='content' and d.get('property')=='og:url':value=self.url(value)
            elif tag=='meta' and key=='content' and d.get('http-equiv','').lower()=='refresh':
                value=re.sub(r'url=(.*)',lambda m:'url='+self.url(m[1]),value)
            elif not inert and (key in ATTR_TEXT or (tag=='meta' and key=='content' and (d.get('name') in ('description','twitter:title','twitter:description') or d.get('property') in ('og:title','og:description','og:site_name','og:image:alt'))) or (tag=='input' and key=='value' and d.get('name') in ('_subject','Chci novinky'))):
                value=self.text(value)
            elif key=='name' and tag=='input' and value in ('Jméno','Příjmení','Město','Chci novinky'):value=self.catalogue[value]
            elif key=='value' and value.startswith(BASE):value=self.url(value)
            new.append(key+'="'+escape(value,quote=True)+'"')
        self.output.append('<'+tag+(' '+' '.join(new) if new else '')+'>')
        if tag not in VOID:self.stack.append((tag,d, inert))

    def handle_endtag(self,tag):
        review = tag=='blockquote' and any(set(attrs.get('class','').split()) & {'quote','sk-review'} for _,attrs,_ in self.stack)
        if tag not in VOID:self.output.append('</'+tag+'>')
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break
        if review:
            # Review translations are labelled without changing their attribution or quoted wording.
            self.output.append('<span class="translation-note">Translated from Czech</span>')

    def handle_data(self,data):
        tag,attrs,inert=self.stack[-1] if self.stack else ('',{},False)
        if tag=='script' and attrs.get('type')=='application/ld+json':
            def local(value):
                if isinstance(value,dict):return {k:('en' if k=='inLanguage' else local(v)) for k,v in value.items()}
                if isinstance(value,list):return [local(v) for v in value]
                if isinstance(value,str):return self.url(value) if value.startswith(BASE) else self.catalogue.get(normal(value),value)
                return value
            self.output.append(json.dumps(local(json.loads(data)),ensure_ascii=False).replace('<','\\u003c'));return
        if tag in ('script','style'):
            if tag=='script':data=re.sub(r'window\.location\.replace\("([^\"]+)"\)', lambda m:'window.location.replace('+json.dumps(self.url(m[1]))+')',data)
            self.output.append(data);return
        self.output.append(escape(data if inert else self.text(data),quote=False))


def localise(source, cs, routes, catalogue, strict=True):
    parser=Localiser(cs,routes,catalogue,strict)
    parser.feed(source)
    if parser.missing:raise ValueError('Missing reviewed translations on '+cs+':\n'+'\n'.join(sorted(parser.missing)))
    return ''.join(parser.output)


def switch(cs, en, language):
    label='Jazyk stránky' if language=='cs' else 'Page language'
    links=[]
    for code,href,flag,name in [('cs',cs,'🇨🇿','CZ'),('en',en,'🇬🇧','EN')]:
        if href:
            current=' aria-current="true"' if code==language else ''
            desc='Česky' if code=='cs' else 'English'
            links.append(f'<a href="{escape(href)}" lang="{code}" hreflang="{code}" aria-label="{desc}"{current} data-language-link><span aria-hidden="true">{flag}</span> {name}</a>')
        else:links.append('<span class="language-unavailable" lang="en" title="Anglický překlad zatím není k dispozici">🇬🇧 EN</span>')
    return '<!-- i18n:switch --><nav class="language-switch" aria-label="'+label+'">'+'<span class="language-divider" aria-hidden="true">|</span>'.join(links)+'</nav><!-- /i18n:switch -->'


def decorate(source, route, language):
    source=clean(source)
    cs,en=route['cs'],route.get('en')
    seo=''
    if route.get('indexable') and en:
        seo=f'<link rel="alternate" hreflang="cs-CZ" href="{BASE+cs}">\n<link rel="alternate" hreflang="en" href="{BASE+en}">\n<link rel="alternate" hreflang="x-default" href="{BASE+cs}">\n'
    ui=json.loads((ROOT/'i18n/ui.json').read_text())[language]
    extras='<!-- i18n:head -->'+seo+'<link rel="stylesheet" href="/assets/css/i18n.css?v=1">\n<script id="i18n-runtime" type="application/json">'+json.dumps(ui,ensure_ascii=False).replace('<','\\u003c')+'</script>\n<script src="/assets/js/i18n.js?v=1" defer></script>\n<!-- /i18n:head -->\n'
    source=source.replace('</head>',extras+'</head>')
    control=switch(cs,en,language)
    if '<button class="menu-toggle"' in source:
        source=source.replace('<button class="menu-toggle"',control+'<button class="menu-toggle"',1)
        start=source.index('<nav class="offcanvas-panel"');end=source.index('</nav>',start)
        source=source[:end]+control+source[end:]
    else:source=source.replace('</main>',control+'</main>',1)
    for script,version in [('main.js',8),('edukace.js',2),('blog-article.js',2)]:
        source=re.sub(re.escape(script)+r'\?v=\d+',script+'?v='+str(version),source)
    return source


def english_article(entry, locale):
    source_path=ROOT/'content/blog'/locale['source']
    if not source_path.resolve().is_relative_to((ROOT/'content/blog/en').resolve()):
        raise ValueError('English article sources must be in content/blog/en')
    source=source_path.read_text()
    heading,perex,body=re.split(r'\n\s*\n',source.strip(),maxsplit=2)
    heading=heading.removeprefix('# ')
    rendered,headings=blog.render_markdown(body)
    rendered=blog.editorial_body(rendered,locale.get('features',{}))
    minutes=max(1,math.ceil(len(re.findall(r'\b[\w]+(?:[’–-][\w]+)*\b',blog.plain(source)))/200))
    url=BASE+'/en/blog/'+locale['slug']+'/'
    image=entry.get('heroImage',entry.get('thumbnail'))
    hero='<figure class="blog-hero-illustration">'+blog.image_markup(image,eager=True)+'</figure>' if image else ''
    date=english_format(entry['published'][8:10]+'.'+entry['published'][5:7]+'.'+entry['published'][:4])
    others=[other['locales']['en'] for other in json.loads((ROOT/'content/blog/articles.json').read_text()) if other.get('published') and other.get('id')!=entry['id'] and other.get('locales',{}).get('en',{}).get('status')=='published']
    related=''
    if others:
        related='<section class="blog-related"><h2>Related articles</h2><ul>'+''.join('<li><a href="/en/blog/'+escape(other['slug'])+'/">'+escape((ROOT/'content/blog'/other['source']).read_text().splitlines()[0].removeprefix('# '))+'</a></li>' for other in others)+'</ul></section>'
    content=blog.template('article.html',dict(category=escape(locale['category']),heading=escape(heading),author=escape(entry['author']),date=f'<time datetime="{entry["published"]}">{date}</time>',reading_time=minutes,perex='<p>'+blog.inline(perex)+'</p>',body=rendered,hero_image=hero,eyebrow=escape(locale.get('features',{}).get('eyebrow',locale['category'])),share_email=escape('mailto:?'+urlencode({'subject':heading,'body':url},quote_via=quote)),canonical=url,related=related,toc=''.join(f'<li><a href="#{a}">{escape(t)}</a></li>' for a,t in headings)))
    schema={'@context':'https://schema.org','@type':'BlogPosting','headline':heading,'description':locale['description'],'author':{'@type':'Person','name':entry['author'],'url':BASE+'/en/#about'},'mainEntityOfPage':url,'url':url,'inLanguage':'en','articleSection':locale['category'],'timeRequired':f'PT{minutes}M','datePublished':entry['published']}
    meta=f'<meta property="article:published_time" content="{entry["published"]}">'
    if image:
        schema['image']=BASE+image['src'];meta+=f'<meta property="og:image" content="{escape(BASE+image["src"])}"><meta property="og:image:alt" content="{escape(image["alt"])}"><meta name="twitter:image" content="{escape(BASE+image["src"])}">'
    output=blog.template('base.html',dict(content=content,title=escape(locale['seoTitle']),description=escape(locale['description']),canonical=url,og_type='article',blog_current='location',page_assets='<link rel="stylesheet" href="/assets/css/blog-article.css?v=1"><script src="/assets/js/blog-article.js?v=2" defer></script>',extra_meta=meta+'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'))
    return output,heading,blog.plain(perex),minutes


class LegalText(HTMLParser):
    def __init__(self):
        super().__init__();self.in_main=False;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='main':self.in_main=True
        if self.in_main and tag in ('p','h1','h2','li','tr','br'):self.parts.append('\n')
        if self.in_main and tag in ('td','th'):self.parts.append(' | ')
    def handle_endtag(self,tag):
        if tag=='main':self.in_main=False
        if self.in_main and tag in ('p','h1','h2','li','tr'):self.parts.append('\n')
    def handle_data(self,data):
        if self.in_main:self.parts.append(data)


def main():
    catalogue=load_catalogue()
    config=json.loads((ROOT/'i18n/config.json').read_text())
    routes={r['cs']:r for r in config['pages']}
    entries=json.loads((ROOT/'content/blog/articles.json').read_text())
    ids=set()
    for entry in entries:
        identifier=entry.get('id')
        if not identifier or identifier in ids:raise ValueError('Blog articles require unique stable IDs')
        ids.add(identifier)
        cs='/blog/'+entry['slug']+'/'
        locale=entry.get('locales',{}).get('en',{})
        if locale.get('status')=='published' and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',locale.get('slug','')):
            raise ValueError('Invalid English article slug')
        en='/en/blog/'+locale['slug']+'/' if entry.get('published') and locale.get('status')=='published' else None
        routes[cs]={'cs':cs,'en':en,'source':'blog/'+entry['slug']+'/index.html','indexable':bool(entry.get('published')),'articleId':identifier}
    english_routes=[r['en'] for r in routes.values() if r.get('en')]
    if len(english_routes)!=len(set(english_routes)) or any(not re.fullmatch(r'/en/(?:[a-z0-9-]+/)*(?:404\.html)?',path) or path.startswith('/en/en/') for path in english_routes):
        raise ValueError('Duplicate or invalid English route')
    outputs,english_cards={},[]
    for cs,route in routes.items():
        source=clean((ROOT/route['source']).read_text())
        if not route.get('en'):
            (ROOT/route['source']).write_text(decorate(source,route,'cs'));continue
        if 'articleId' in route:
            entry=next(e for e in entries if e['id']==route['articleId']);locale=entry['locales']['en']
            raw,title,perex,minutes=english_article(entry,locale)
            translated=localise(raw,cs,routes,catalogue,strict=False)
            image=entry.get('thumbnail');media=''
            if image:
                image=dict(image,alt=catalogue.get(image['alt'],image['alt']))
                media=f'<a class="blog-card-media" href="{route["en"]}" aria-label="{escape(title)}">'+blog.image_markup(image)+'</a>'
            date=english_format(entry['published'][8:10]+'.'+entry['published'][5:7]+'.'+entry['published'][:4])
            english_cards.append(f'<article class="blog-card"><div class="blog-card-copy"><p class="blog-category">{escape(locale["category"])}</p><h3><a href="{route["en"]}">{escape(title)}</a></h3><p class="blog-card-perex">{escape(perex)}</p><div class="blog-meta"><span>{escape(entry["author"])}</span><time datetime="{entry["published"]}">{date}</time><span>{minutes} min read</span></div><a class="blog-read" href="{route["en"]}">Read article <span aria-hidden="true">→</span></a></div>{media}</article>')
        else:
            shared_source=source
            if cs=='/blog/':
                # Do not require any translation for unpublished article cards.
                start=shared_source.index('<div class="blog-grid">')+len('<div class="blog-grid">')
                end=shared_source.index('</div></div></section>',start)
                shared_source=shared_source[:start]+shared_source[end:]
            translated=localise(shared_source,cs,routes,catalogue)
        outputs[route['en']]=decorate(translated,route,'en')
        (ROOT/route['source']).write_text(decorate(source,route,'cs'))
    # Only translated, explicitly published articles appear in the EN index.
    index=outputs['/en/blog/']
    start=index.index('<div class="blog-grid">')+len('<div class="blog-grid">')
    end=index.index('</div></div></section>',start)
    index=index[:start]+(''.join(english_cards) or '<p>English articles are being prepared.</p>')+index[end:]
    outputs['/en/blog/']=index
    previous_path=ROOT/'i18n/generated-pages.json'
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else []
    generated=[]
    for route,html in outputs.items():
        path=route.lstrip('/')+('index.html' if route.endswith('/') else '')
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html);generated.append(path)
    for route,filename in [('/en/gdpr/','privacy-policy.txt'),('/en/obchodni-podminky/','terms-and-conditions.txt')]:
        text=LegalText();text.feed(outputs[route])
        path=ROOT/'assets/docs/en'/filename;path.parent.mkdir(parents=True,exist_ok=True)
        lines=[normal(line) for line in ''.join(text.parts).splitlines() if normal(line)]
        path.write_text('\n'.join(line for line in lines if line not in ('Download the Privacy Policy (TXT)','Download the Terms and Conditions (TXT)'))+'\n')
    # GitHub Pages has a single 404 entry point. Embed its generated English shell
    # and select it only for unknown /en/ URLs, without a redirect or a network request.
    english_body=re.search(r'<body[^>]*>(.*?)</body>',outputs['/en/404.html'],re.S)[1]
    english_body=re.sub(r'<script\b[^>]*>.*?</script>','',english_body,flags=re.S)
    fallback='<!-- i18n:error --><template id="english-error-shell">'+english_body+'''</template><script>
if (window.location.pathname.indexOf('/en/') === 0) {
  var englishError = document.getElementById('english-error-shell').content.cloneNode(true);
  document.documentElement.lang = 'en';
  document.title = 'Page Not Found | Radek Rosa';
  document.body.replaceChildren(englishError);
}
</script><!-- /i18n:error -->'''
    error=ROOT/'404.html';html=error.read_text();match=re.search(r'<script src="[^"]*main\.js',html)
    html=html[:match.start()]+fallback+html[match.start():] if match else html.replace('</body>',fallback+'</body>')
    error.write_text(html)
    for stale in set(previous)-set(generated):
        path=ROOT/stale
        if path.is_relative_to(ROOT/'en') and path.is_file():
            path.unlink();parent=path.parent
            while parent!=ROOT/'en' and parent.exists() and not any(parent.iterdir()):parent.rmdir();parent=parent.parent
    previous_path.write_text(json.dumps(generated,indent=2)+'\n')
    (ROOT/'i18n/route-map.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2)+'\n')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';xh='http://www.w3.org/1999/xhtml'
    ET.register_namespace('',ns);ET.register_namespace('xhtml',xh)
    urlset=ET.Element('{'+ns+'}urlset')
    for route in routes.values():
        if not route.get('indexable'):continue
        for path in [route['cs'],route.get('en')]:
            if not path:continue
            node=ET.SubElement(urlset,'{'+ns+'}url');ET.SubElement(node,'{'+ns+'}loc').text=BASE+path
            if route.get('en'):
                for lang,target in [('cs-CZ',route['cs']),('en',route['en']),('x-default',route['cs'])]:ET.SubElement(node,'{'+xh+'}link',{'rel':'alternate','hreflang':lang,'href':BASE+target})
    ET.indent(urlset,space='  ');(ROOT/'sitemap.xml').write_text(ET.tostring(urlset,encoding='unicode')+'\n')
    print(f'Built {len(outputs)} EN pages and matching CZ language controls. No deployment performed.')

if __name__=='__main__':main()
