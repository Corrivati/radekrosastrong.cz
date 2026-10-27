# Čeština a angličtina na Radek Rosa Strong

## Stav a místní kontrola

CZ/EN verze byla schválena ke zveřejnění dne 27. 10. 2026. Generování místního sestavení a jeho publikování jsou samostatné kroky; samotný build do produkce nic neodesílá.

Web zůstává statickým HTML/CSS/JS projektem bez databáze, CMS, npm nebo externí překladové služby. Anglické HTML se vytváří při sestavení, nikoliv při návštěvě. V obou jazycích se používají stejné styly, média a funkční skripty. Soubory v `en/` jsou výstup generátoru, ne druhá samostatně udržovaná instalace.

Z kořene projektu:

```sh
python3 scripts/build_site.py
python3 -m unittest discover -s tests
python3 serve.py
```

Náhled: `http://localhost:8000/` a `http://localhost:8000/en/`. Samotný build nic nepublikuje.

## Přeložené stránky

- Úvodní stránka, individuální trénink, online coaching.
- Přehled vzdělávání, workshop Svalové kontrakce, Level 2, workshop Šlachy, původní Strange Training landing page a webinář zdarma.
- Blog a celý článek „How to Choose a Good Personal Trainer: What Really Matters?“.
- GDPR a obchodní podmínky včetně anglického TXT ke stažení.
- Chybová stránka 404.
- Původní přesměrování `/obchod/` a `/svalove-kontrakce/` mají odpovídající anglická přesměrování a zůstávají mimo index a sitemap. Skrytý archiv uvnitř neaktivní HTML šablony se nezveřejňuje jako nový obsah.

## Zdroje a sdílené komponenty

- České stránky zůstávají na původních URL a slouží zároveň jako společná šablona rozložení. `build_i18n.py` převezme jejich markup a nahradí pouze revidované texty a jazykové odkazy. České texty ani recenze nepřepisuje.
- `i18n/config.json` definuje podporované jazyky a dvojice běžných stránek.
- `i18n/route-map.json` je vygenerovaná úplná mapa skutečně dostupných protějšků, včetně článků.
- `i18n/en/*.json` obsahuje překlady seskupené podle stránek; `common.json` obsahuje sdílené texty. Klíčem je normalizované české znění, hodnotou revidovaná britská angličtina. Jména, značky a původní anglické názvy certifikací jsou ponechány.
- `i18n/ui.json` obsahuje malé množství stavových hlášek pro formulář, historii akcí a blog. Na stránku se vloží jen příslušný jazyk. Žádný celý překladový katalog se nestahuje v prohlížeči.
- `assets/css/i18n.css` upravuje pouze přepínač a nutné rozestupy navigace. Logo zůstává na středu; na šířkách, kde by se navigace nevešla, se použije stávající mobilní menu.
- `assets/js/i18n.js` zpřístupňuje stavové hlášky a při ručním přepnutí zachovává query string i kotvu.
- `i18n/generated-pages.json` eviduje generované EN stránky, aby bylo možné odstranit zastaralý výstup při změně překladu na koncept.

## Jak upravit existující překlad

Najdi příslušný český text v `i18n/en/*.json`, uprav anglickou hodnotu a spusť celý build. Pokud se změní český text, aktualizuj také klíč a reviduj jeho překlad. Build běžných stránek při chybějícím překladu skončí chybou; nevytváří potichu stránku s českými odstavci pod anglickým menu. Drobné číselné datumy a částky se formátují jazykově, bez změny hodnoty nebo převodu měny.

Celý anglický článek se upravuje v jeho vlastním Markdown souboru, nikoli v katalogu vět z českého článku. Needituj přímo generované soubory v `en/`.

## Nový článek v CZ a EN

1. Vlož český Markdown do `content/blog/` a přidej položku do `content/blog/articles.json`. Zachovej stávající pole `slug`, `source`, `category`, `author`, `published`, SEO metadata a volitelné komponenty. Přidej unikátní stabilní `id`, například `training-load-basics`.
2. Anglický Markdown vlož do `content/blog/en/`. Dodrž stejnou strukturu, úplný obsah a přirozenou odbornou angličtinu. Nepoužívej automatický placeholder překladu.
3. Přidej anglické nastavení do `locales.en`, například:

```json
{
  "status": "draft",
  "slug": "understanding-training-load",
  "source": "en/understanding-training-load.md",
  "category": "Training",
  "seoTitle": "Understanding Training Load | Radek Rosa",
  "description": "A reviewed description of this article.",
  "features": {}
}
```

4. `status: draft` nevytvoří EN stránku ani odkaz v EN přehledu, sitemap či hreflang. Český přepínač ukáže EN jako nedostupné; neposílá čtenáře na nesouvisející homepage. Existující veřejný EN výstup se při návratu na koncept odstraní. Český článek může dál zůstat publikovaný.
5. Po dokončení a kontrole překladu nastav `status: published`. Jde o povolení sestavit soubor, nikoli o automatické nasazení. České pole `published` nadále určuje skutečné původní datum článku. Samostatné číslování doby čtení se počítá z každého jazykového zdroje.
6. U volitelných `features` použij přesné anglické nadpisy kapitol a citace z anglického Markdownu. Checklist přebírá anglické otázky. Jeho `labels` obsahují `selected`, `reset`, `note`; srovnávací karty mají anglické názvy a shrnutí. Nevkládej české `features` do anglického záznamu bez překladu.
7. Anglické karty přehledu vznikají pouze z publikovaných EN metadat a anglického Markdownu. Pro český článek bez hotového EN překladu se nevytváří anglická karta ani není nutné překládat jeho perex do obecného katalogu.
8. Spusť celý build a kontroly. Zkontroluj obě URL, vzájemný přepínač a layout, teprve potom schvaluj zveřejnění.

Přesný příklad kompletního záznamu včetně obrázků a interaktivních komponent je v `content/blog/articles.json`. Podrobnosti Markdown šablony jsou v `content/blog/README.md`.

## Přepínač a interní odkazy

Přepínač `🇨🇿 CZ | 🇬🇧 EN` je vpravo v desktopové navigaci a ve stávajícím mobilním menu. Má přístupné popisky a označení aktuálního jazyka. Používá skutečné odkazy, takže funguje i bez JavaScriptu. S JavaScriptem zachovává také aktuální kotvu a query string.

Zvolený jazyk určuje URL, nikoli cookie nebo automatický redirect podle prohlížeče. EN interní odkazy míří na EN protějšky. Přímá česká i anglická URL zůstává vždy dostupná, uživatelovu volbu nic nepřebíjí. Pokud překlad budoucího článku není publikovaný, nevzniká falešný EN protějšek; případný běžný interní odkaz vede na existující český originál.

## SEO a chybové stránky

Indexovatelné dvojice mají vlastní canonical, reciproční `cs-CZ`, `en` a `x-default` (český originál), příslušný `html lang`, lokalizované titulky, popisy, Open Graph a strukturovaná data. Sitemap obsahuje jen reálné indexovatelné stránky a stejné jazykové vazby. `robots.txt` obě varianty povoluje. Nenastavuje se automatická konverze měn.

Neznámá URL vrací 404, ne fallback s HTTP 200 ani neomezené prefixy `/en/en/...`. Místní server umí přímo vrátit `/en/404.html`. GitHub Pages má jediný globální `404.html`, proto v něm je lokální předgenerovaný EN obal, který se pro neexistující `/en/` URL vybere bez síťového požadavku a bez přesměrování. U této chyby při zcela vypnutém JavaScriptu na GitHub Pages zůstává český fallback s přímým EN přepínačem. Všechny existující EN stránky jsou plně statické a čitelné bez JavaScriptu. Hosting s vlastními error pravidly může pro EN cesty používat přímo `/en/404.html`.

## Ověření a ruční kontrola před nasazením

Automatické testy kontrolují zachování českého textu, odkazy, obrázky, identické Stripe URL, canonical/hreflang, nezveřejnění konceptu překladu a stabilní generování. Prohlížečové kontroly navíc pokrývají desktop, tablet, mobil, přepínač, menu, galerii, FAQ, formulář a blogové interakce. Formulář se testuje s náhradou transportu, bez skutečného odesílání e-mailu nebo platby.

**Anglické znění GDPR a obchodních podmínek musí před zveřejněním zkontrolovat právník.** Překlad zachovává otevřené body a stejný význam českých dokumentů; neověřuje ani neopravuje právní nastavení cookies a služeb. Cookie lišta nebyla přidána, protože to není součást této jazykové změny.

Před publikací je vhodná také závěrečná jazyková kontrola majitelem, zejména citací klientů a odborných názvů školení. Reference v EN mají popisek „Translated from Czech“. Originální fotografie, grafika s vloženým textem a zvuková stopa videí zůstávají zachovány; nevytváří se dabing. Jazyk externích služeb, samotného Stripe checkoutu, TrueCoach nebo HeroHero závisí na jejich nastavení. Platební odkazy, adresy příjemců, ceny a podmínky nebyly změněny.
