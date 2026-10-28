# Galerie hlavní stránky

`photos.json` obsahuje všech 16 originálů s označením `novywebfoto`, pořadí, popisy, individuální pozice ořezu a cesty k optimalizovaným variantám. Originály ve `strangetraining-old/` se neupravují. Původní fotky galerie zůstávají v repozitáři; nové položky na ně neodkazují.

`python3 scripts/build_site.py` nejprve zavolá `build_gallery.py`, který přegeneruje pouze obsah existujícího `.carousel-track` na hlavní stránce. Potom proběhne běžný blogový a CZ/EN build. Skript ověřuje, že žádný originál s označením nechybí ani není zařazen dvakrát. Samotné sestavení nevyžaduje Pillow, databázi ani npm. Překlady alt textů jsou v `i18n/en/gallery.json`.

WebP náhledy v `assets/images/gallery/` mají nejdelší stranu 1000 px u portrétů a 1200 px u širokých snímků (kvalita 84). Pro lightbox jsou samostatné, neoříznuté varianty do 1800 px (kvalita 88). Optimalizace proběhla z originálů s korektní EXIF orientací; build další kompresi neprovádí. Součet náhledů je přibližně 1,18 MB oproti 4,60 MB originálů. Velké varianty se načítají až v lightboxu, s přednačtením následujícího snímku.

`wide: true` rozšíří snímek na dva původní portrétní sloupce; výška řádku, tmavé pozadí, mezery 11 px a stávající rozložení 4/3/2 sloupců zůstávají. `position` a `mobilePosition` jsou individuální hodnoty `object-position`. Skupinové fotky díky širšímu rámci zachovávají celou skupinu; v lightboxu je vždy celý snímek bez ořezu.

Galerie dál používá plynulý automatický posun po 5000 ms, ruční šipky, dotykové posouvání a původní dialog. Posun počítá skutečné pozice snímků různých šířek. Před přechodem dekóduje potřebné náhledy; při přetočení přednačte i mezilehlé snímky, aby se neukázala prázdná plocha. Automatika se pozastaví při skrytí galerie, na pozadí karty, během prohlížení lightboxu, při najetí myší a při ovládání galerie klávesnicí. `prefers-reduced-motion` vypne automatiku i po změně za běhu; ruční ovládání zůstává dostupné.

Ořezy byly jednotlivě prohlédnuty na desktopu i mobilu. Bez JavaScriptu zůstává nativní posouvání a odkazy na větší fotografie. Žádná jiná sekce nepoužívá nové galerie styly; v hlavním skriptu se měnil pouze blok galerie.
