# 📌 Třídní Nástěnka s AI

Jednoduchá webová aplikace v Pythonu (Flask), která funguje jako digitální nástěnka. Umožňuje přidávat vzkazy, obrázky a komunikovat s umělou inteligencí (model Gemma 3) přes školní Kuřim API.

## ⚙️ Co je potřeba
* Nainstalovaný **Python 3.12+** (pro lokální spuštění) nebo **Docker**.
* Získaný **API klíč** ze školního Kuřim AI Dashboardu.

## 🔐 Nastavení prostředí (.env)
Aplikace potřebuje ke svému běhu tajný API klíč. Vytvoř si ve složce s projektem soubor s názvem `.env` a vlož do něj tyto údaje:

```text
OPENAI_API_KEY=sk-R_tvuj_tajny_klic_z_dashboardu
OPENAI_BASE_URL=[https://kurim.ithope.eu/v1](https://kurim.ithope.eu/v1)
PORT=5000
```
> **⚠️ DŮLEŽITÉ:** Soubor `.env` nikdy nenahrávej na GitHub! Ujisti se, že máš v repozitáři soubor `.gitignore` a v něm je napsáno `.env`.

## 🚀 Jak to spustit lokálně (Python)

1. **Naklonuj nebo stáhni** tento repozitář.
2. **Nainstaluj potřebné knihovny:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Spusť aplikaci:**
   ```bash
   python app.py
   ```
4. Otevři prohlížeč a jdi na adresu: `http://localhost:5000`

## 🐳 Jak to spustit přes Docker (nebo školní server)

Aplikace je připravena pro kontejnerizaci. Školní server si Dockerfile načte automaticky. Pro ruční spuštění v Dockeru použij:

1. **Sestavení obrazu:**
   ```bash
   docker build -t nastenka-app .
   ```
2. **Spuštění kontejneru** (s načtením `.env` souboru):
   ```bash
   docker run -p 5000:5000 --env-file .env nastenka-app
   ```

## ⚠️ Řešení problémů se školním serverem
Pokud ti školní dashboard hlásí chybu `fatal: could not read Username for 'https://github.com': No such device or address`, znamená to, že máš repozitář nastavený jako **Private** (soukromý). 

**Řešení:** Na GitHubu jdi do `Settings` -> sjeď dolů na `Danger Zone` -> `Change repository visibility` -> přepni na **Public**. (Předtím se ale na 100 % ujisti, že na GitHubu nemáš nahraný soubor `.env`!).
