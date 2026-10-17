# Obrázky a video

Fotky, loga a video webu. Stažené z původního WordPressu (`/wp-content/uploads/`) a zmenšené pro web:

- fotky jsou ve formátu WebP, nejdelší strana nejvýš 1600 px (úvodní fotka a bannery 1920 px),
- video `Brno.mp4` je převedené na 720 × 1280 (H.264, cca 6 MB).

Nepoužité soubory z WordPress knihovny sem nebyly převzaty.

## Výměna nebo nová fotka

1. Nahrajte soubor sem (**Add file → Upload files**). Ideálně WebP nebo JPG, šířka do 1600 px.
2. V příslušném `index.html` přepište název souboru v `src="…/assets/images/…"` a upravte `width` a `height` na rozměry nové fotky.
