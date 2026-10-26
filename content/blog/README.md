# Přidání článku

Blog je statický. Na hostingu nejsou potřeba Python, databáze ani CMS; publikují se vygenerované HTML stránky stejně jako zbytek webu.

1. Vlož nový soubor `.md` do `content/blog/`. Použij jeden hlavní nadpis `#`, poté samostatný perex a další obsah. Podporované značky: kapitoly `##`, odstavce, `**tučně**`, `*kurzíva*`, seznamy `-` a oddělovač `---`. HTML se bezpečně vypisuje jako text. Odkazy, obrázky a jiné rozšířené Markdown prvky zatím nejsou součástí této jednoduché šablony.
2. Přidej záznam do `articles.json`: unikátní `slug`, `source`, `category`, `author`, `published`, `seoTitle`, `description`. Pořadí záznamů určuje pořadí karet.
3. Pro náhled nech `published: null`. Datum se nevymýšlí: karta i článek zobrazují „Připraveno k publikaci“ a nové stránky mají `noindex, follow`. Při schváleném zveřejnění nastav skutečný den ve formátu `YYYY-MM-DD`. Generátor potom doplní datum do stránky a BlogPosting a odstraní náhledové noindex. Při prvním zveřejnění tohoto článku musí být datum nastavené před nasazením.
4. Z kořene projektu spusť `python3 scripts/build_blog.py`. Skript bez externích balíčků vytvoří články, přehledové karty a aktualizuje pouze blogové položky v sitemap. Doba čtení se počítá z celého textu tempem 200 slov za minutu, zaokrouhlením nahoru. Názvy, obsah, perex a zvýraznění pocházejí ze zdrojového souboru.
5. Prohlédni výsledek přes `python3 serve.py` a zkontroluj změny. Při přejmenování nebo odstranění článku odstraň ručně také starý vygenerovaný adresář v `blog/`; skript existující soubory nemaže.
6. Teprve po schválení odešli zdrojové soubory, šablony a vygenerované HTML do publikační větve. Samotné spuštění generátoru nic nepublikuje.

Společný obal je v `templates/blog/base.html`, rozložení v `article.html` a `index.html`. Vzhled upravuje `assets/css/blog.css`. Při budoucí změně společné navigace aktualizuj i `base.html` a znovu vygeneruj blog.

Nový článek zatím nemá úvodní ani sdílecí obrázek. Po dodání autentického vhodného obrázku lze doplnit OG/Twitter metadata. Nevkládá se náhradní nebo vymyšlený vizuál.

Volitelný náhled obrázku v přehledu: k záznamu článku přidej `"thumbnail": {"src": "/assets/images/nazev.webp", "alt": "Popis obrázku", "width": 1200, "height": 675}`. Použij skutečné rozměry a nejdřív nahraj soubor do assets/images. Generátor ověřuje jeho existenci. U jediného článku je obrázek na desktopu napravo vedle textu a na menších obrazovkách nad textem. Bez dodaného obrázku se nevykresluje prázdná výplň ani nefunkční obrázek.
