# Merch — nezveřejněný návrh

Stránka je připravená pro `/merch/`. Uchovávat ve větvi `draft/merch`; neslučovat do nasazované větve, dokud Radek neschválí zveřejnění. GitHub Pages neposkytuje soukromí pouhým vynecháním odkazu z menu. `noindex` je pouze doplňková ochrana proti indexaci, nikoli řízení přístupu.

Stránka není přidaná do navigace, sitemap ani jazykového generátoru. Jde zatím o český koncept. Fotografie jsou optimalizované WebP kopie dodaných PNG; původní soubory zůstávají zachované.

Potvrzená cena: **899 Kč včetně DPH**, doprava se připočítává. Osobní převzetí v Praze je zdarma (0 Kč); cena zaslání zatím není určena.

## Před spuštěním

- Potvrdit materiál, gramáž, péči, velikosti, skutečné rozměry a skladovou dostupnost. Celá současná tabulka je ilustrační.
- Potvrdit dopravu, dodací lhůtu, vrácení a obchodní podmínky pro fyzické zboží.
- Nastavit Stripe Payment Link pro správný fyzický produkt, varianty/velikosti, cenu, doručovací adresu a dopravu; ověřit celý objednávkový proces v sandboxu. Před spuštěním napojit zpracování objednávek přes ověřené webhooky `checkout.session.completed` a `checkout.session.async_payment_succeeded`, vždy až po potvrzení zaplacení. Zajištění expedice musí vycházet z potvrzené úspěšné platby ve Stripe, nikoliv z pouhé návštěvy návratové stránky.
- Doplnit Payment Link v `assets/js/merch.js`. Nákup je nyní vypnutý; není připojený produkt, platební brána ani inkaso. Žádné API klíče nejsou potřeba pro obyčejné přesměrování na Payment Link.
- Před zveřejněním upravit texty o přípravě prodeje a FAQ, odstranit pracovní banner a rozhodnout o indexaci, menu, sitemap a EN překladu. Samotné doplnění odkazu nestačí ke spuštění prodeje.

Náhled lokálně: z kořene repozitáře `python3 serve.py`, potom `/merch/`. Tento soubor ani návrh automaticky nic nepublikují.
