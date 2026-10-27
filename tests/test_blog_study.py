"""Check scientific-data semantics, both locales and malformed-data protection."""
from copy import deepcopy
from pathlib import Path
import importlib
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
blog = importlib.import_module('build_blog')
study = importlib.import_module('blog_study')


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.entry = next(e for e in json.loads((ROOT/'content/blog/articles.json').read_text()) if e['id']=='chatgpt-personal-trainers-study')
        self.data = study.load(ROOT, self.entry)

    def test_counts_match_labels_and_plot_in_both_languages(self):
        self.assertEqual(self.data['results'], {'overall':6,'accuracy':5,'clarity':6,'applicability':5})
        for language in ('cs','en'):
            graph = study.render('results',self.data,language)
            self.assertEqual(graph.count('data-study-bar'),4)
            self.assertIn('aria-describedby="study-chart-note"',graph)
            self.assertNotIn('67%',graph)
            self.assertIn(self.data['locales'][language]['chartNote'],graph)
            # Editing a single data value changes both the exact label and plotted width.
            changed = deepcopy(self.data)
            changed['results']['overall']=7
            graph = study.render('results',changed,language)
            self.assertIn('data-result="overall" data-count="7" data-total="9"',graph)
            self.assertIn('--study-fraction:0.777777778',graph)
            self.assertIn(changed['locales'][language]['resultValue'].format(count=7,total=9),graph)
            self.assertIn('7/9',study.render('stats',changed,language))
            self.assertIn('7',study.render('evidence',changed,language))
            self.assertIn('7',study.source('{{study.results.overall}}',changed))

    def test_generated_article_components_sources_and_seo(self):
        for language, route in [('cs','blog/chatgpt-vs-osobni-trener'),('en','en/blog/chatgpt-vs-personal-trainers')]:
            html=(ROOT/route/'index.html').read_text()
            self.assertNotIn('[[study:',html)
            self.assertNotIn('{{study.',html)
            self.assertEqual(html.count('class="blog-study-stat'),5)  # The wrapper plus four cards.
            self.assertEqual(html.count('class="blog-study-evidence-card"'),2)
            self.assertEqual(html.count('<th scope="col">'),2)
            self.assertEqual(html.count('<td data-label='),8)
            self.assertIn('blog-study.css',html)
            self.assertIn(self.data['citation']['doi'],html)
            self.assertIn(self.data['citation']['fullText'],html)
            self.assertEqual(html.count('<h1>'),1)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)[1])
            self.assertEqual(schema['@type'],'BlogPosting')
            self.assertEqual(schema['inLanguage'],language)
            self.assertEqual(schema['datePublished'],self.entry['published'])
            self.assertEqual(schema['url'],'https://radekrosastrong.cz/'+route+'/')
            index=(ROOT/('en/blog' if language=='en' else 'blog')/'index.html').read_text()
            self.assertIn('/'+route+'/',index)
        # The old article gets discovery links, but no study components/styles.
        old=(ROOT/'blog/jak-poznat-kvalitniho-trenera/index.html').read_text()
        self.assertNotIn('blog-study.css',old)
        self.assertNotIn('class="blog-study-',old)

    def test_invalid_data_and_missing_component_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'content/blog/studies'):
            study.load(ROOT,dict(self.entry,studyData='../articles.json'))
        with self.assertRaisesRegex(ValueError,'exactly one stats'):
            study.enhance('<p>No components.</p>',self.data,'cs')


if __name__=='__main__':
    unittest.main()
