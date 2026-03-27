# PurrFectMD (A README generator)

> **Born out of frustration.** Managing multiple GitHub repos meant writing READMEs over and over again — each one tedious, time-consuming, and honestly kind of soul-crushing. So I built **PurrFectMD**: a Chrome Extension + Python backend that reads your GitHub repo's file structure and generates a polished, badge-heavy README in a single click.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=flat)
![CSS](https://img.shields.io/badge/CSS-3-blue?style=flat)
![HTML](https://img.shields.io/badge/HTML-5-orange?style=flat)

---

## Features

- **One-Click README Generation** — Trigger generation directly from your browser on any GitHub repo page
- **Structure-Aware** — Analyses your actual file/folder tree to produce accurate, context-rich documentation
- **Badge-Heavy & Modern** — Outputs visually polished READMEs with auto-detected tech stack badges
- **Zero Config** — No setup per repo; works across all your GitHub projects instantly

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-blue?style=flat)
![JavaScript](https://img.shields.io/badge/JavaScript-yellow?style=flat)
![HTML5](https://img.shields.io/badge/HTML5-orange?style=flat)
![CSS3](https://img.shields.io/badge/CSS3-blue?style=flat)
![Docker](https://img.shields.io/badge/Docker-blue?style=flat)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=flat)

---

## How to Use

### Step 1 — Install the Chrome Extension

1. Download or clone this repository
2. Open Google Chrome and go to `chrome://extensions/`
3. Enable **Developer Mode** (toggle in the top-right corner)
4. Click **"Load unpacked"** and select the `GoogleExtension/` folder from this repo
5. The PurrFectMD icon will appear in your Chrome toolbar — you're ready to go!

   <img width="400" height="131" padding:3px  alt="image" src="https://github.com/user-attachments/assets/4720bae1-1c2c-4979-94b9-7de7aa60a8eb" />


### Step 2 — Generate a README

1. Navigate to **any GitHub repository page** in your browser
2. Click the **PurrFectMD** extension icon in your toolbar
3. Hit **"Generate README"**
4. Your `README.md` is generated instantly based on the repo's structure.

   <img width="417" height="581" alt="image" src="https://github.com/user-attachments/assets/29b064e0-5007-4fc8-9ad6-4c537c05bad7" />
   

---

## A Cold Start Delay

The Python backend is currently hosted on **Render's free tier**, which spins down after periods of inactivity.

> **First request may take 2–3 minutes** while the server cold-starts. Subsequent requests within the same session will be fast.

Just be patient on the first click — grab a coffee ☕ and it'll be ready shortly.

---

## Architecture
```
User clicks "Generate" in Chrome Extension
        ↓
popup.js (Chrome Extension)
        ↓ API Request
app.py (Python Backend on Render)
        ↓ Parses repo structure + generates Markdown
README.md delivered to user
```

---

## Project Structure
```
.
├── app.py                  # Core Python backend — handles generation logic
├── requirements.txt        # Python dependencies
├── docker.yaml             # Docker config for local/containerized deployment
├── .dockerignore
├── .gitignore
└── GoogleExtension/
    ├── manifest.json       # Chrome extension config
    ├── popup.html          # Extension popup UI
    ├── popup.js            # Extension interaction logic
    ├── popup.css           # Extension styles
    └── bg_updated.png      # Extension icon/background
```

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: describe your change"`
4. Push and open a Pull Request

All contributions are welcome!

---

Made with PurrFectMD, my own README generator
