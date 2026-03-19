# AgriSmart PWA — Guide de déploiement

## Structure des fichiers
```
agrismart-pwa/
├── index.html        ← Application principale
├── manifest.json     ← Configuration PWA
├── sw.js             ← Service Worker (cache hors-ligne)
└── icons/            ← Icônes pour Android/iOS
    ├── icon-72.png
    ├── icon-96.png
    ├── icon-128.png
    ├── icon-144.png
    ├── icon-152.png
    ├── icon-192.png
    ├── icon-384.png
    └── icon-512.png
```

## Fonctionnalités
- 📷 Prise de photo avec la caméra
- 🖼️ Upload depuis la galerie
- 🔍 Diagnostic via API FastAPI ou mode local
- 📴 Mode hors-ligne (Service Worker + cache)
- 📋 Historique des diagnostics (localStorage)
- ⚙️ Paramètres configurables

---

## ÉTAPE 1 — Tester en local

```bash
# Installer un serveur HTTP simple
pip install flask

# OU avec Python
python -m http.server 8080

# Ouvrir dans le navigateur
# http://localhost:8080
```

---

## ÉTAPE 2 — Déployer sur GitHub Pages (gratuit)

1. Créez un dépôt GitHub : `agrismart-pwa`
2. Uploadez tous les fichiers du dossier
3. Allez dans **Settings → Pages → Source → main branch**
4. Votre URL : `https://votre-username.github.io/agrismart-pwa`

---

## ÉTAPE 3 — Publier sur le Play Store via PWABuilder

### Pré-requis
- Compte Google Play Developer (25$ une fois)
- PWA déployée sur HTTPS (GitHub Pages ou autre)

### Procédure
1. Allez sur **[pwabuilder.com](https://pwabuilder.com)**
2. Entrez l'URL de votre PWA (ex: `https://catherine-rina.github.io/agrismart-pwa`)
3. Cliquez **Start** → vérifiez le score PWA
4. Cliquez **Package for stores**
5. Choisissez **Android (Google Play)**
6. Téléchargez le package `.aab`
7. Uploadez sur **[play.google.com/console](https://play.google.com/console)**

### Score PWA requis
- ✅ HTTPS
- ✅ manifest.json valide
- ✅ Service Worker actif
- ✅ Icônes 192px et 512px

---

## ÉTAPE 4 — Connecter à l'API FastAPI

Dans l'app, allez dans **Paramètres** et mettez l'URL de votre API :
- En local : `http://localhost:8000`
- En production : `https://votre-api.render.com`

### Déployer l'API sur Render (gratuit)
1. Allez sur [render.com](https://render.com)
2. Nouveau service → Web Service
3. Connectez votre dépôt GitHub (avec `api_agrismart.py`)
4. Build command : `pip install -r requirements.txt`
5. Start command : `uvicorn api_agrismart:app --host 0.0.0.0 --port 10000`

---

## Notes importantes

- Le mode **local (démo)** génère des résultats aléatoires
- Pour le vrai diagnostic, connectez l'API FastAPI
- Pour intégrer TF.js (vraie inférence locale), ajoutez le modèle `.json` et importez TensorFlow.js
