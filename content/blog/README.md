# Přidání článku

Blog je statický. Na hostingu nejsou potřeba Python, databáze ani CMS; publikují se vygenerované HTML stránky stejně jako zbytek webu.

1. Vlož nový soubor `.md` do `content/blog/`. Použij jeden hlavní nadpis `#`, poté samostatný perex a další obsah. Podporované značky: kapitoly `##`, odstavce, `**tučně**`, `*kurzíva*`, seznamy `-` a oddělovač `---`. HTML se bezpečně vypisuje jako text. Odkazy, obrázky a jiné rozšířené Markdown prvky zatím nejsou součástí této jednoduché šablony.
2. Přidej záznam do `articles.json`: unikátní `slug`, `source`, `category`, `author`, `published`, `seoTitle`, `description`. Pořadí záznamů určuje pořadí karet.
3. Pro náhled nech `published: null`. Datum se nevymýšlí: karta i článek zobrazují „Připraveno k publikaci“ a nové stránky mají `noindex, follow`. Při schváleném zveřejnění nastav skutečný den ve formátu `YYYY-MM-DD`. Generátor potom doplní datum do stránky a BlogPosting a odstraní náhledové noindex. Při prvním zveřejnění tohoto článku musí být datum nastavené před nasazením.
4. Z kořene projektu spusť `python3 scripts/build_site.py`. Skript bez externích balíčků vytvoří články, přehledové karty a aktualizuje pouze blogové položky v sitemap. Doba čtení se počítá z celého textu tempem 200 slov za minutu, zaokrouhlením nahoru. Názvy, obsah, perex a zvýraznění pocházejí ze zdrojového souboru.
5. Prohlédni výsledek přes `python3 serve.py` a zkontroluj změny. Při přejmenování nebo odstranění článku odstraň ručně také starý vygenerovaný adresář v `blog/`; skript existující soubory nemaže.
6. Teprve po schválení odešli zdrojové soubory, šablony a vygenerované HTML do publikační větve. Samotné spuštění generátoru nic nepublikuje.

Společný obal je v `templates/blog/base.html`, rozložení v `article.html` a `index.html`. Vzhled upravuje `assets/css/blog.css`. Při budoucí změně společné navigace aktualizuj i `base.html` a znovu vygeneruj blog.

Nový článek zatím nemá úvodní ani sdílecí obrázek. Po dodání autentického vhodného obrázku lze doplnit OG/Twitter metadata. Nevkládá se náhradní nebo vymyšlený vizuál.

Volitelný náhled obrázku v přehledu: k záznamu článku přidej `"thumbnail": {"src": "/assets/images/nazev.webp", "alt": "Popis obrázku", "width": 1200, "height": 675}`. Použij skutečné rozměry a nejdřív nahraj soubor do assets/images. Generátor ověřuje jeho existenci. U jediného článku je obrázek na desktopu napravo vedle textu a na menších obrazovkách nad textem. Bez dodaného obrázku se nevykresluje prázdná výplň ani nefunkční obrázek.

## Rozšířená šablona článku

Článek má samostatný styl `assets/css/blog-article.css` a lehký skript `assets/js/blog-article.js`; přehled blogu ani ostatní stránky tyto soubory nenačítají. Šablona nabízí dvousloupcový hero, postranní obsah na desktopu, rozbalovací obsah na mobilu, indikátor průběhu čtení, autorský blok, CTA a sdílení. Bez JavaScriptu zůstává celý text, nativní obsah a otázky přístupné. Tlačítko sdílení používá nativní nabídku zařízení, pokud je dostupná, jinak odkaz pro sdílení e-mailem. Kopírování má při zamítnutí schránky ruční alternativu. Checklist nic neodesílá a neukládá.

Volitelný `heroImage` má stejná pole jako `thumbnail`. Lze tak mít jinou ilustraci v úvodu než v přehledu; hodnota `null` vytvoří čistě typografický hero. Hero obrázek se načítá přednostně, autorská fotografie až podle potřeby. Metadata obrázku pro sdílení i `BlogPosting.image` se doplňují automaticky.

Volitelné pole `features` u článku:

- `eyebrow`: krátký popisek nad nadpisem.
- `pullQuotes`: přesná znění samostatných tučných odstavců ze zdrojového Markdownu, bez značek `**`. Generátor je zvýrazní na původním místě, neduplikuje je a nedovolí vložit neexistující citaci.
- `comparison`: `afterHeading` musí přesně odpovídat názvu kapitoly včetně čísla. `cards` obsahuje položky `title`, `icon` (`education` nebo `communication`) a seznam `items`; `message` je shrnutí pod kartami. Tento doplněk se vloží na konec zvolené kapitoly.
- `checklist`: `afterHeading` je přesný název kapitoly a `title` nadpis komponenty. Kapitola musí obsahovat právě jeden odrážkový seznam. Jeho původní položky se převedou na zaškrtávací otázky bez změn textu; počet i indikátor se odvozují automaticky.

Všechny tyto možnosti lze vynechat. Nepřebírej celý záznam prvního článku pro nový článek bez úpravy `features`, protože citace i názvy kapitol se ověřují. Číslování, kotvy a obsah se generují z nadpisů. Související články se zobrazí pouze tehdy, když existuje další záznam se skutečným datem publikace.

Ověření: `python3 -m unittest discover -s tests -p test_blog.py`. Testy porovnávají text před a po přidání komponent, ověřují existenci citací, generování dalších článků, datum, sitemap a obrázky. Zdrojový Markdown prvního článku zůstává beze změny.

Pro české a anglické verze vždy spouštěj kompletní `build_site.py`, který navazuje generováním EN stránek a jazykových vazeb. Samostatný `build_blog.py` je pouze dílčí generátor české šablony. Viz [I18N_GUIDE.md](../../I18N_GUIDE.md).

## Článek ChatGPT vs. osobní trenéři

Český zdroj je `chatgpt-vs-osobni-trener.md`, anglický `en/chatgpt-vs-personal-trainers.md`. V přehledu je nejnovější článek první. Sdílený datový soubor `studies/chatgpt-personal-trainers.json` obsahuje všechny počty, verzi modelu, bibliografické údaje a texty infografik v obou jazycích. Ve zdrojových odstavcích se hodnoty vkládají pomocí `{{study.counts.questions}}`, `{{study.results.overall}}` apod.; výsledný web žádné šablonové značky neobsahuje.

Pole `studyData` v `articles.json` aktivuje komponenty v `scripts/blog_study.py`. Značky `[[study:stats]]`, `[[study:results]]`, `[[study:evidence]]`, `[[study:comparison]]`, `[[study:quote]]` a `[[study:reference]]` označují jejich umístění v Markdownu. Každá se musí vyskytovat právě jednou. Generátor ověřuje součty hodnotitelů, rozsah počtů otázek, bezpečné cesty a HTTPS odkazy. Statistické karty, graf a mobilní porovnání jsou sémantické HTML/CSS; přístupné jsou i bez JavaScriptu. Jednorázové animace přidává společný skript článků, respektující reduced motion. Nové styly `assets/css/blog-study.css` se načítají pouze u tohoto článku.

Malý náhled `assets/images/blog-chatgpt-vs-osobni-trener.svg` se při sestavení vytváří ze stejných dat. Zobrazuje šest zvýrazněných bodů z devíti; alt text výslovně uvádí, že jde o hodnocení odpovědí. Není to fotografie ani obrázek nahrazující obsahové infografiky.

Původ čísel: dodané zadání s citací DOI `10.52082/jssm.2026.235`. Při přípravě dne 27. 10. 2026 vracely vydavatel, DOI i bibliografické databáze přes síťový proxy chybu 403, a proto nezávislá kontrola plného textu nebyla dokončena. Žádné další výsledky ani p-hodnoty nebyly doplněny. Majitel byl na nedokončené ověření upozorněn a dne 27. 10. 2026 následně výslovně schválil zveřejnění připraveného článku. Porovnání s původním PDF zůstává otevřené; tato poznámka je pouze pro správu projektu, nikoliv součást veřejného článku.
