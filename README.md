# radekrosastrong.cz

Web Radka Rosy (silový a kondiční trenér). Je to kopie původního WordPressu (šablona Astra + Elementor) přepsaná do čistého HTML a CSS, bez WordPressu, pluginů a databáze. Žádný build ani `npm install`.

## Struktura

```
index.html                          /                       (úvod: o mně, certifikace, galerie, klienti, videa, reference, kontakt)
edukace/index.html                  /edukace/               (Přehled kurzů)
onlinecoaching/index.html           /onlinecoaching/        (Online Coaching)
strangetraining/index.html          /strangetraining/       (landing page Svalové kontrakce Brno)
strangetraining-old/index.html      /strangetraining-old/   (původní stránka Brno, odkaz v menu)
svalove-kontrakce/index.html        /svalove-kontrakce/     (Kontrakce level 1)
kontrakce2/index.html               /kontrakce2/            (Kontrakce level 2)
workshop-slachy/index.html          /workshop-slachy/       (Šlachy)
webinar-zdarma/index.html           /webinar-zdarma/        (webinář + registrační formulář)
gdpr/index.html                     /gdpr/
obchodni-podminky/index.html        /obchodni-podminky/
404.html                            chybová stránka
assets/css/style.css                vzhled celého webu
assets/css/strangetraining.css      vzhled landing page /strangetraining/
assets/js/main.js                   menu na mobilu, galerie, videa, formulář
assets/fonts/                       písma Teko a Ubuntu (bez Google Fonts)
assets/images/                      fotky (WebP), logo, favicon a video
serve.py                            lokální náhled
```

Adresy stránek jsou stejné jako na WordPressu (včetně lomítka na konci), takže odkazy z Googlu a sociálních sítí fungují dál.

## Formulář (webinář)

Registrační formulář na `/webinar-zdarma/` posílá `assets/js/main.js` přes službu [FormSubmit](https://formsubmit.co) na `treninkzen@email.cz` (stejná adresa jako ve WPForms).

**Po prvním odeslání** přijde na tento e-mail žádost o aktivaci od FormSubmit. Je potřeba ji jednou potvrdit, jinak zprávy nedorazí.

## Náhled na počítači

```
python3 serve.py
```

Pak otevřete http://localhost:8000.

## Úpravy

- **Text:** najděte ho v příslušném `index.html` a přepište. Jde to i přímo na GitHubu (ikona tužky).
- **Nová akce / termín:** stránka `edukace/index.html`, odstavec „AKCE SEŘAZENÉ PODLE TERMÍNŮ“.
- **Navigace a patička** jsou v každém souboru zvlášť. Při změně je upravte všude (nebo o to požádejte Claude).
- **Rok v patičce** je napsaný natvrdo (`Copyright © 2026`).

## Co bylo z WordPressu vynecháno

- Skryté prvky: tlačítko „Klikni pro strong blog“ (bylo skryté na všech zařízeních), prázdný nadpis v sekci O mně, neviditelný bílý nápis „Video“ na bílém pozadí.
- Prázdný článek `/strong-blog/` („Nic tu zatím není :)“) a nepoužívané stránky WooCommerce (`/obchod/`, `/kosik/`, `/pokladna/`, `/muj-ucet/`). Nyní vrací 404.
- Koncepty (Privacy Policy, Reklamace) a nepoužité šablony Elementoru.
- Instagram feed pod kontaktem (plugin vyžadoval napojení na Instagram API), cookie lišta (web už nepoužívá cookies; YouTube se načítá z `youtube-nocookie.com` až po kliknutí).
- Všechny pluginy, jQuery, Font Awesome, Elementor CSS/JS. Ikony jsou vložené přímo jako SVG.

## Co bylo upraveno

- Na mobilu se zobrazí celý seznam certifikací (dřív polovina skrytá s poznámkou „Více certifikací se zobrazí na PC“).
- Text podstránek měl na mobilu velikost 7 px. Nyní 16 px.
- Každá stránka má vlastní titulek a popis pro Google (dřív měly skoro všechny stejný), sitemap.xml a robots.txt.
- Souhlas s GDPR a odběr novinek ve formuláři nejsou předem zaškrtnuté (předzaškrtnutý souhlas GDPR neuznává).
- V patičce jsou odkazy na GDPR a obchodní podmínky.

## Nasazení na doménu

Na GitHub Pages: **Settings → Pages → Deploy from branch**, pak přidat soubor `CNAME` s textem `radekrosastrong.cz` a u registrátora domény nasměrovat DNS na GitHub Pages. Dokud se DNS nepřepne, běží dál WordPress.
