# Deploy della Guida agli Agenti AI

Il sito è completamente statico. Si serve da qualsiasi CDN o file server. Tre opzioni in ordine di facilità:

## Opzione 1 — Netlify (drag & drop, 60 secondi)

1. Esegui il build:
   ```bash
   python3 build_site.py
   python3 build_pdf.py
   ```
2. Vai su [netlify.com/drop](https://app.netlify.com/drop).
3. Trascina la cartella `website/` nella pagina.
4. Netlify ti dà un URL del tipo `random-name-12345.netlify.app`.
5. (Opzionale) Settings → Domain → Add custom domain → punta i tuoi DNS.

**Pro**: gratis, HTTPS automatico, CDN globale, deploy in <1 minuto.
**Con**: nessun build automatico — devi rifare il drag & drop quando aggiorni.

### Build automatico via Git
Se vuoi build automatico ad ogni `git push`:
1. Push del repository su GitHub.
2. Netlify → "Add new site" → "Import from Git" → scegli il repo.
3. Build command: `python3 build_site.py`
4. Publish directory: `website`
5. Environment variable: `PYTHON_VERSION=3.11`

## Opzione 2 — Vercel

1. Push del repo su GitHub.
2. [vercel.com/new](https://vercel.com/new) → importa il repo.
3. Configurazione:
   - **Framework Preset**: Other
   - **Build Command**: `pip install markdown beautifulsoup4 pygments && python3 build_site.py`
   - **Output Directory**: `website`
   - **Install Command**: (vuoto)
4. Deploy.

## Opzione 3 — GitHub Pages

1. Push del repo su GitHub.
2. Crea `.github/workflows/deploy.yml`:

```yaml
name: Deploy site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install markdown beautifulsoup4 pygments reportlab
      - run: python3 build_site.py
      - run: python3 build_pdf.py
      - uses: actions/upload-pages-artifact@v3
        with:
          path: website
      - id: deployment
        uses: actions/deploy-pages@v4
```

3. GitHub repo → Settings → Pages → Source: "GitHub Actions".
4. Push → il workflow gira → il sito è live su `https://USERNAME.github.io/REPO/`.

## Prima di andare in produzione

Il default è `https://myfirstaiagent.netlify.app`. Se in futuro migri a un dominio custom, aggiorna in `build_site.py`:

```python
SITE_BASE_URL = "https://il-tuo-dominio.com"
```

Questo influenza:
- Open Graph tags (anteprime social su Twitter/LinkedIn/Slack/WhatsApp)
- Canonical URL (SEO)
- sitemap.xml
- JSON-LD schema

I contatti e i link social sono già configurati con i tuoi dati reali:
- Email: `gabriele.bottai2001@gmail.com`
- GitHub: `https://github.com/GabrieleBottai01`
- LinkedIn: `https://www.linkedin.com/in/gabriele-bottai-1825a9302/`
- X: `https://x.com/bottai_gabriele`
- Portfolio: `https://gabrielebottai.netlify.app/`

Se vuoi, dal tuo portfolio principale aggiungi un link a questa guida — è il modo più diretto di trasformarla in un asset visibile per i recruiter / clienti.

## Dominio personalizzato

Per tutte e tre le opzioni:
1. Acquista un dominio (es. Cloudflare Registrar, costo annuale).
2. Nelle DNS, aggiungi il record che il provider ti chiede:
   - **Netlify/Vercel**: CNAME su `cname.vercel-dns.com` o equivalente Netlify, o A record su loro IP.
   - **GitHub Pages**: A records su 4 IP di GitHub + crea un file `website/CNAME` con il dominio.
3. Aspetta propagazione DNS (5 minuti - 1 ora).
4. Il provider auto-emette certificato Let's Encrypt → HTTPS gratis.

## Verifica post-deploy

Una volta live, controlla:

- [ ] Open Graph: incolla la URL su [opengraph.xyz](https://www.opengraph.xyz/) o nel preview di Twitter/LinkedIn → vedi titolo + descrizione + immagine.
- [ ] sitemap.xml accessibile su `/sitemap.xml`.
- [ ] robots.txt accessibile su `/robots.txt`.
- [ ] Search funzionante (Cmd+K → digita "tool" → risultati).
- [ ] Tutor RAG: clicca un capitolo → tutor sidebar → fai una domanda. La risposta dovrebbe citare il capitolo specifico.
- [ ] Mobile: apri da telefono, verifica che il chapter selector dropdown appaia.
- [ ] Print: Cmd+P su un capitolo → l'anteprima dovrebbe essere pulita (no sidebar/topbar).
- [ ] PDF download: link "scarica PDF" funziona.

## Crawl da Google

Dopo che il sito è live e ha un dominio reale:

1. Vai su [Google Search Console](https://search.google.com/search-console).
2. Aggiungi proprietà (verifica con DNS TXT o file).
3. Submit sitemap: incolla `https://tuo-dominio.com/sitemap.xml`.
4. Aspetta 2-7 giorni per la prima indicizzazione.

Ripeti per Bing Webmaster Tools (importante per ChatGPT/Claude search).

## Aggiornamenti incrementali

Quando aggiorni capitoli markdown:

```bash
# 1. Modifica i .md (root o en/)
# 2. Rebuild
python3 build_site.py
python3 build_pdf.py

# 3. Deploy:
# - Netlify drag & drop: trascina website/ di nuovo
# - Git-based: commit + push, deploy automatico
```

## Backup

Il sito **statico è il backup**. La cartella `website/` è autoconsistente:
- Salvala su Dropbox/Drive periodicamente.
- I .md originali sono in `01-...md` (root) e `en/01-...md`.
- Il PDF generato ha il valore "edizione finale" — copia anche quello.

---

© 2026 Gabriele Bottai · Guida agli Agenti AI
