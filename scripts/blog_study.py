"""Small, accessible study components shared by both static article locales."""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re

COMPONENTS = ('stats', 'results', 'evidence', 'comparison', 'quote', 'reference')
RESULT_KEYS = ('overall', 'accuracy', 'clarity', 'applicability')


def load(root, entry):
    filename = entry.get('studyData')
    if not filename:
        return None
    path = root / 'content/blog' / filename
    if not path.resolve().is_relative_to((root / 'content/blog/studies').resolve()) or path.suffix != '.json':
        raise ValueError('Study data must be a JSON file in content/blog/studies')
    data = json.loads(path.read_text())
    counts, results = data['counts'], data['results']
    if any(type(n) is not int or n < 1 for n in counts.values()):
        raise ValueError('Study counts must be positive integers')
    if counts['trainerRaters'] + counts['scientistRaters'] != counts['raters']:
        raise ValueError('Reviewer groups must add up to the total')
    if counts['weightLossQuestions'] > counts['questions']:
        raise ValueError('Question subgroup cannot exceed the question total')
    if set(results) != set(RESULT_KEYS) or any(type(n) is not int or not 0 <= n <= counts['questions'] for n in results.values()):
        raise ValueError('Study results must be question counts within the question total')
    for key in ('doi', 'fullText'):
        url = urlsplit(data['citation'][key])
        if url.scheme != 'https' or not url.netloc:
            raise ValueError('Study references must use absolute HTTPS URLs')
    return data


def source(text, data):
    if not data:
        return text
    def number(match):
        value = data
        for key in match[1].split('.'):
            value = value[key]
        if not isinstance(value, (str, int)):
            raise ValueError('Study placeholders must reference a scalar value')
        return str(value)
    return re.sub(r'\{\{study\.([a-zA-Z.]+)\}\}', number, text)


def render(kind, data, language):
    labels = data['locales'][language]
    total = data['counts']['questions']
    if kind == 'stats':
        values = [data['counts']['trainers'], data['counts']['raters'], total, f'{data["results"]["overall"]}/{total}']
        cards = ''.join(f'<li class="blog-study-stat{" is-highlighted" if i == 3 else ""}" data-study-reveal><strong>{escape(str(value))}</strong><span>{escape(label)}</span></li>' for i, (value, label) in enumerate(zip(values, labels['stats'])))
        return f'<aside class="blog-study-stats" aria-label="{escape(labels["statsLabel"])}"><ul>{cards}</ul></aside>'
    if kind == 'results':
        rows = ''
        for key in RESULT_KEYS:
            count = data['results'][key]
            value = labels['resultValue'].format(count=count, total=total)
            rows += f'<li data-result="{key}" data-count="{count}" data-total="{total}"><div class="blog-study-result-label"><span>{escape(labels["resultLabels"][key])}</span><strong>{escape(value)}</strong></div><div class="blog-study-track" aria-hidden="true"><span data-study-bar style="--study-fraction:{count/total:.9f}"></span></div></li>'
        return f'<figure class="blog-study-chart" aria-labelledby="study-chart-title" aria-describedby="study-chart-note"><h3 id="study-chart-title">{escape(labels["chartTitle"])}</h3><ul>{rows}</ul><div class="blog-study-axis" aria-hidden="true"><span>0</span><span>{escape(labels["axisEnd"].format(total=total))}</span></div><figcaption id="study-chart-note">{escape(labels["chartNote"])}</figcaption></figure>'
    if kind == 'evidence':
        cards = ''
        values = dict(data['counts'], **data['results'])
        paths = {'check':'<path d="m5 12 4 4L19 6"/>', 'info':'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/>'}
        for card in labels['evidence']:
            cards += f'<section class="blog-study-evidence-card" data-study-reveal><svg viewBox="0 0 24 24" aria-hidden="true">{paths[card["icon"]]}</svg><h4>{escape(card["title"])}</h4><ul>'+''.join('<li>'+escape(item.format(**values))+'</li>' for item in card['items'])+'</ul></section>'
        return f'<aside class="blog-study-evidence" aria-labelledby="study-evidence-title"><h3 id="study-evidence-title">{escape(labels["evidenceTitle"])}</h3><div class="blog-study-evidence-grid">{cards}</div></aside>'
    if kind == 'comparison':
        columns = labels['columns']
        rows = ''.join('<tr>'+''.join(f'<td data-label="{escape(label)}">{escape(cell)}</td>' for label, cell in zip(columns, row))+'</tr>' for row in labels['rows'])
        return f'<div class="blog-study-comparison"><table role="table" aria-describedby="study-comparison-note"><caption>{escape(labels["comparisonTitle"])}</caption><thead><tr>'+''.join('<th scope="col">'+escape(label)+'</th>' for label in columns)+f'</tr></thead><tbody>{rows}</tbody></table><p id="study-comparison-note" class="blog-study-note">{escape(labels["comparisonNote"])}</p></div>'
    if kind == 'quote':
        opening, closing = ('„', '“') if language == 'cs' else ('“', '”')
        return f'<figure class="blog-study-quote" data-study-reveal><blockquote><p>{opening}{escape(labels["quote"])}{closing}</p></blockquote><figcaption><strong>Radek Rosa</strong><span>{escape(labels["authorRole"])}</span></figcaption></figure>'
    if kind == 'reference':
        citation = data['citation']
        return f'<div class="blog-study-reference"><p>{escape(citation["authors"])} ({data["year"]}). <cite>{escape(citation["title"])}</cite> {escape(citation["journal"])}, {citation["volume"]}({citation["issue"]}), {escape(citation["pages"])}.</p><ul><li><a href="{escape(citation["doi"])}" target="_blank" rel="noopener">{escape(labels["doiLabel"])}: {escape(citation["doi"].removeprefix("https://doi.org/"))}</a></li><li><a href="{escape(citation["fullText"])}" target="_blank" rel="noopener">{escape(labels["fullTextLabel"])} <span aria-hidden="true">↗</span></a></li></ul></div>'
    raise ValueError('Unknown study component: '+kind)


def enhance(rendered, data, language):
    if not data:
        return rendered
    for kind in COMPONENTS:
        marker = '<p>[[study:'+kind+']]</p>'
        if rendered.count(marker) != 1:
            raise ValueError('Study article requires exactly one '+kind+' component')
        rendered = rendered.replace(marker, render(kind, data, language))
    if '[[study:' in rendered:
        raise ValueError('Unknown study component marker')
    return rendered


def word_count(text, data, language):
    """Include the infographic copy in the displayed reading-time estimate."""
    text = re.sub(r'\[\[study:[a-z]+\]\]', '', text)
    if data:
        class Text(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []
            def handle_data(self, value):
                self.parts.append(value)
        parser = Text()
        parser.feed(''.join(render(kind, data, language) for kind in COMPONENTS))
        text += ' '+' '.join(parser.parts)
    return len(re.findall(r'\b[\w]+(?:[’–-][\w]+)*\b', text))


def artwork(root, entry, data):
    """A tiny, shared SVG thumbnail; every plotted value comes from the study data."""
    if not data:
        return
    asset = entry.get('thumbnail', {}).get('src')
    if not asset or not asset.endswith('.svg'):
        return
    path = root / asset.lstrip('/')
    if not path.resolve().is_relative_to((root/'assets/images').resolve()):
        raise ValueError('Study artwork must be in assets/images')
    total, count = data['counts']['questions'], data['results']['overall']
    step = 960/max(total-1, 1)
    dots = ''.join(f'<circle cx="{120+i*step:g}" cy="525" r="25" fill="{"#bf2932" if i<count else "#78838d"}"/>' for i in range(total))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
<rect width="1200" height="675" rx="16" fill="#18232d"/>
<text x="90" y="140" font-family="Ubuntu,Arial,sans-serif" font-size="42" fill="#e5e9ec">{escape(data['model'])} {escape(data['version'])}</text>
<text x="82" y="420" font-family="Teko,Arial,sans-serif" font-size="270" font-weight="700" fill="#fff">{count}<tspan fill="#aab3bb" font-size="190"> / {total}</tspan></text>
{dots}</svg>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg+'\n')
