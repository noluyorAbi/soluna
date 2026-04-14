<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">SOLUNA</h1></p>
<p align="center">
    <em>Clash-of-Clans Aktivitäts-Dashboard mit Live-Daten, interaktiven Charts und automatischer Interpretation</em>
</p>
<p align="center">
    <img src="https://img.shields.io/github/license/noluyorAbi/soluna?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
    <img src="https://img.shields.io/github/last-commit/noluyorAbi/soluna?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
    <img src="https://img.shields.io/github/languages/top/noluyorAbi/soluna?style=default&color=0080ff" alt="repo-top-language">
    <img src="https://img.shields.io/github/languages/count/noluyorAbi/soluna?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
    <!-- default option, no dependency badges. -->
</p>
<br>

## 🔗 Table of Contents

- [� Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#️-prerequisites)
  - [⚙️ Installation](#️-installation)
  - [🤖 Usage](#-usage)
  - [🧪 Testing](#-testing)
- [📌 Project Roadmap](#-project-roadmap)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

SOLUNA ist ein Web-Dashboard, das Aktivität, Spenden, Angriffe, Kriegsstatistik und Rathaus-Zusammensetzung eines Clash-of-Clans-Clans in Echtzeit visualisiert. Das Backend holt Live-Daten über die [coc.py](https://github.com/mathsman5133/coc.py)-Bibliothek, berechnet einen gewichteten Aktivitäts-Score pro Mitglied und rendert ein interaktives Plotly-Dashboard. Der Clan-Tag kann frei gewählt werden — das Dashboard lässt sich für beliebige Clans generieren.

### Dashboard-Features

- **Clan-Tag-Suche** auf der Startseite — jeder Clan per Tag analysierbar
- **10 Metrik-Karten** mit Status-Ampel (schwach / solide / stark / exzellent)
- **Automatische Interpretation** der Daten (Spenden-Bilanz, Top-Spender, Konzentration der Top-10 %, Trophäenspitze, Kriegsstern-Leader, potenziell inaktive Mitglieder)
- **7 interaktive Charts** (Light-Theme, Plotly):
  - Aktivitäts-Scatter mit Quartil-Farben und Ø/Median-Linien
  - Horizontaler Spenden-Balken (gegeben vs. erhalten, sortiert nach Netto)
  - Histogramm + Boxplot des Aktivitäts-Scores
  - Kampf-Profil-Bubble (Trophäen × Angriffe, Größe = Spenden, Farbe = Rathaus)
  - Rathaus-Donut
  - Rollen-Donut
  - Beitrags-Treemap (Fläche = Spenden, Farbe = Aktivität)
- **Aktivitäts-Score v3** (ungedeckelt, lineare Rohwerte), gerendert als LaTeX via KaTeX — siehe [Scoring](#-aktivitäts-score-v3)
- **Zweischichtige Interpretation**: jede Kachel zeigt oben den Fakt, darunter die Bedeutung in einfacher Sprache (inkl. Erklärung von „rechts-schief", „Konzentration", „Netto-Spenden" u. a.)
- **Orientierungswerte-Tabelle** (was sind gute Werte pro Metrik)
- **Deep-Explanation** im Dashboard: Formel, Gewichtungsbegründung, Vergleich zur Legacy-Formel v1, Saison-Hinweise, Quartil-Legende
- **Mobile-responsive** (Breakpoints bei 960 / 640 / 420 px, scrollbare Tabellen, stackender Header)
- **DataTables** (Top 5 / Bottom 5 / vollständige sortierbare Rangliste)
- **HTML-Download** des vollständigen Dashboards pro Clan

### 📐 Aktivitäts-Score v3

Lineare, **ungedeckelte** Summe in natürlichen Einheiten. Wer 10× mehr leistet, hat 10× mehr Punkte — die reale Aktivitätsspanne bleibt sichtbar, statt in einer 0–100-Skala plattgedrückt zu werden.

```
Score = D_geg + 3 · A · m_T + 0.5 · W

D_geg = Spenden gegeben (Saison)        → 1 Pkt pro Spende
A     = Gewonnene Angriffe (Saison)     → 3 Pkt × Trophäen-Bonus
W     = Kriegs-Sterne (lifetime)        → 0.5 Pkt (halbiert, weil kumulativ)
m_T   = 0.8 + 0.5 · min(1, T/5000)      → bounded 0.8…1.3 (TH-Fairness, kein Cap)
```

Im Dashboard wird die Formel als echtes LaTeX gerendert (KaTeX), mit aufgeschlüsselten Teilformeln, Rechenbeispielen (aktiver TH13 ≈ 1.985 Pkt, Casual TH10 ≈ 290 Pkt, Leech ≈ 62 Pkt) und Orientierungs-Ampel (< 100 schwach, 100–500 solide, 500–1.500 stark, > 1.500 exzellent).

**Warum v3 statt v2 oder v1?**

| Version | Problem |
|---------|---------|
| **v1** (`0.3·D_geg + 0.1·D_erh + A·(1+T/500)`) | Trophäen-Bonus unbeschränkt (bis ≈11× bei TH17), Kriegs-Sterne ignoriert, erhaltene Spenden geben Punkte. |
| **v2** (`100 · [0.4·D̂ + 0.3·Â·m_T + 0.15·Ŵ + 0.15·Bal]`) | Sättigende 0–100-Skala versteckte Leistungsunterschiede — ein Whale mit 10.000 Spenden sah aus wie einer mit 2.000. |
| **v3** (aktuell, linear ungedeckelt) | Brutale Wahrheit: tatsächliche Aktivität wird direkt sichtbar. Trophäen-Bonus bleibt beschränkt (0.8–1.3) für TH-Fairness, aber nichts sonst ist gecappt. |

**Beispiel-Spread** (echter Clan, 44 Mitglieder): Top 6.136 Pkt, Median ≈ 350 Pkt, Bottom 3,5 Pkt — ein Faktor von ~1.750× zwischen stärkster und schwächster Aktivität.

Legacy-v1-Werte bleiben intern als `Aktivität_v1` erhalten (nicht angezeigt, für Vergleichszwecke verfügbar).

---

## 👾 Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Architecture**  | <ul><li>Next.js 15 (App Router) Frontend mit TypeScript und Tailwind CSS.</li><li>FastAPI-Backend mit asynchronem [coc.py](https://github.com/mathsman5133/coc.py)-Client für die CoC-API.</li><li>Plotly (Python) rendert Server-seitig ein vollständig interaktives HTML-Dashboard.</li></ul> |
| 📊 | **Analytics**     | <ul><li>Gewichteter Aktivitäts-Score pro Mitglied (Spenden, Angriffe, Trophäen-Multiplikator).</li><li>Quartil-basierte Visualisierung mit Durchschnitts- und Median-Referenzlinien.</li><li>Automatische datengetriebene Interpretation (Spenden-Konzentration, inaktive Mitglieder, Schiefe der Verteilung).</li></ul> |
| 🎨 | **UI/UX**         | <ul><li>Light-Theme mit inline SVG-Icons (Lucide-Style), keine Emojis.</li><li>Responsive Grid, Status-farbkodierte Metrik-Karten.</li><li>Klare Trennung Dashboard / Interpretation / Rangliste / Erklärung.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Offizielle Clash-of-Clans-API via `coc.py` (Auto-Login, Rate-Limiting).</li><li>Next.js API-Route als Proxy zwischen Frontend und Backend.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Frontend und Backend komplett entkoppelt.</li><li>Eine einzelne FastAPI-Route `/clan-activity` erzeugt das gesamte Dashboard; Clan-Tag als Query-Parameter überschreibbar.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Asynchrone Spieler-Daten-Abfrage (parallel via `asyncio.gather`).</li><li>Plotly-Charts laden per CDN, Fonts via Google Fonts.</li></ul> |
| 🛡️ | **Security**      | <ul><li>CoC-Credentials ausschließlich über Umgebungsvariablen.</li><li>CORS-Middleware konfiguriert.</li><li>HTML-Escaping für Spielernamen und Clan-Tag.</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Frontend: `next`, `react`, `axios`, `plotly.js`, `tailwindcss`.</li><li>Backend: `fastapi`, `uvicorn`, `coc.py>=3.7`, `pandas`, `plotly`, `python-dotenv`.</li></ul> |

---

## 📁 Project Structure

```sh
└── soluna/
    ├── README.md
    ├── app
    │   ├── backend
    │   │   ├── __pycache__
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── clan-activity
    │   │   ├── loading.tsx
    │   │   ├── page.tsx
    │   │   └── route.ts
    │   ├── favicon.ico
    │   ├── fonts
    │   │   ├── GeistMonoVF.woff
    │   │   └── GeistVF.woff
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── loading.tsx
    │   └── page.tsx
    ├── bun.lockb
    ├── chat.txt
    ├── next.config.ts
    ├── package.json
    ├── postcss.config.mjs
    ├── public
    │   ├── file.svg
    │   ├── globe.svg
    │   ├── next.svg
    │   ├── vercel.svg
    │   └── window.svg
    ├── tailwind.config.ts
    └── tsconfig.json
```


### 📂 Project Index
<details open>
    <summary><b><code>SOLUNA/</code></b></summary>
    <details> <!-- __root__ Submodule -->
        <summary><b>__root__</b></summary>
        <blockquote>
            <table>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/chat.txt'>chat.txt</a></b></td>
                <td>- Facilitates user interaction within the chat module of the project by managing message exchanges and ensuring seamless communication<br>- Integrates with other components to provide a cohesive user experience, supporting real-time data processing and message handling<br>- Plays a crucial role in maintaining the overall functionality and responsiveness of the chat feature, contributing to the project's goal of delivering efficient and reliable communication tools.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/tsconfig.json'>tsconfig.json</a></b></td>
                <td>- Defines TypeScript configuration settings to ensure consistent and efficient compilation across the project<br>- It specifies the target JavaScript version, module resolution strategy, and library inclusions, while enabling strict type-checking and JSX support<br>- The configuration facilitates seamless integration with JavaScript, supports incremental builds, and sets up path aliases for streamlined imports, enhancing the development workflow and maintaining code quality within the project's architecture.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/postcss.config.mjs'>postcss.config.mjs</a></b></td>
                <td>- Configures PostCSS to integrate Tailwind CSS into the project, enabling the use of Tailwind's utility-first CSS framework throughout the codebase<br>- This setup facilitates streamlined styling and responsive design by leveraging Tailwind's extensive set of pre-defined classes<br>- By incorporating Tailwind CSS, the project benefits from a more efficient and consistent approach to styling, enhancing both development speed and maintainability.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/package.json'>package.json</a></b></td>
                <td>- The package.json file defines the Soluna project's metadata, dependencies, and scripts, serving as a central configuration for managing the project's build and development processes<br>- It specifies essential libraries like React, Next.js, and Tailwind CSS, ensuring a robust framework for building a modern web application<br>- Additionally, it includes scripts for development, building, and linting, streamlining the project's workflow and maintenance.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/next.config.ts'>next.config.ts</a></b></td>
                <td>- Configures the Next.js application by defining settings and options that influence the behavior and performance of the entire project<br>- Serves as a central point for customizing the build process, server settings, and other framework-specific features, ensuring that the application aligns with project requirements and optimizes the development workflow<br>- Plays a crucial role in integrating various components and enhancing the overall architecture of the codebase.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/tailwind.config.ts'>tailwind.config.ts</a></b></td>
                <td>- Tailwind configuration file defines the styling framework for the project by specifying the directories to scan for class usage and extending the default theme with custom colors<br>- It ensures consistent design across pages, components, and the app by integrating with Tailwind CSS<br>- This setup facilitates streamlined styling and theming, enhancing the overall visual coherence and maintainability of the codebase.</td>
            </tr>
            </table>
        </blockquote>
    </details>
    <details> <!-- app Submodule -->
        <summary><b>app</b></summary>
        <blockquote>
            <table>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/loading.tsx'>loading.tsx</a></b></td>
                <td>- Loading component enhances user experience by displaying a visually engaging animation while clan activity data is being fetched<br>- It maintains user engagement during data retrieval processes, ensuring a seamless transition within the application<br>- By providing immediate feedback, it helps manage user expectations and reduces perceived wait times, contributing to a smoother and more interactive interface within the overall project architecture.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/page.tsx'>page.tsx</a></b></td>
                <td>- The "app/page.tsx" component serves as the main entry point for the SOLUNA Clan Activity Dashboard, providing a user interface that welcomes users and guides them to the clan activity plot<br>- It includes navigation links, a welcoming message, and a button to transition to the activity page<br>- The page also features a loading state to enhance user experience while data is being processed.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/layout.tsx'>layout.tsx</a></b></td>
                <td>- The app/layout.tsx file establishes the foundational layout for the SOLUNA Dashboard by defining global styles and fonts, ensuring a consistent visual experience across the application<br>- It imports custom fonts and applies them to the entire application, while also setting metadata for the dashboard<br>- This setup supports a cohesive user interface and enhances the overall aesthetic of the project.</td>
            </tr>
            <tr>
                <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/globals.css'>globals.css</a></b></td>
                <td>- Define the global styling framework for the project by integrating Tailwind CSS's base, components, and utilities<br>- Establishes a consistent design language across the application, ensuring a cohesive look and feel<br>- Acts as a foundational layer that influences the visual presentation of all components and pages, promoting design uniformity and simplifying the styling process throughout the codebase.</td>
            </tr>
            </table>
            <details>
                <summary><b>backend</b></summary>
                <blockquote>
                    <table>
                    <tr>
                        <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/backend/main.py'>main.py</a></b></td>
                        <td>- The file `app/backend/main.py` serves as a critical component of the project's backend architecture<br>- Its primary purpose is to facilitate data interaction and visualization for the application, leveraging external APIs and libraries<br>- It integrates with the Clash of Clans API to retrieve and process game-related data, which is then visualized using libraries like Matplotlib and Plotly<br>- The file also establishes a FastAPI server to handle HTTP requests and responses, enabling seamless communication between the frontend and backend<br>- Additionally, it incorporates environment variables for secure credential management and includes middleware to handle cross-origin resource sharing (CORS), ensuring the application can interact with resources from different origins<br>- Overall, this file is essential for data processing, visualization, and API interaction within the project's architecture.</td>
                    </tr>
                    <tr>
                        <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/backend/requirements.txt'>requirements.txt</a></b></td>
                        <td>- The `requirements.txt` file specifies the dependencies necessary for the backend of the project, ensuring that all required libraries and frameworks are installed for the application to function correctly<br>- It includes essential packages for building a FastAPI-based web application, handling data manipulation and visualization, and managing environment variables, thus supporting the overall architecture by facilitating backend development and deployment.</td>
                    </tr>
                    </table>
                </blockquote>
            </details>
            <details>
                <summary><b>clan-activity</b></summary>
                <blockquote>
                    <table>
                    <tr>
                        <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/clan-activity/loading.tsx'>loading.tsx</a></b></td>
                        <td>- Loading component enhances user experience by displaying a visually engaging animation while clan activity data is being fetched<br>- It maintains user engagement and provides feedback during data retrieval processes<br>- Positioned within the app's architecture, it serves as a placeholder to ensure smooth transitions and prevent abrupt content changes, contributing to a seamless and interactive interface for users navigating the clan activity section.</td>
                    </tr>
                    <tr>
                        <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/clan-activity/page.tsx'>page.tsx</a></b></td>
                        <td>- Render a dynamic page displaying clan activity by fetching HTML content from an API endpoint<br>- It manages loading states and error handling to ensure a smooth user experience<br>- This component is part of the client-side architecture, enhancing the interactivity and responsiveness of the application by directly integrating with the backend to present real-time data updates to users.</td>
                    </tr>
                    <tr>
                        <td><b><a href='https://github.com/noluyorAbi/soluna/blob/master/app/clan-activity/route.ts'>route.ts</a></b></td>
                        <td>- Facilitates the retrieval and display of clan activity data by handling HTTP GET requests<br>- It connects to a backend service to fetch the necessary information and returns it as HTML content<br>- This functionality is crucial for presenting dynamic clan activity updates within the application, ensuring users have access to the latest information<br>- Error handling is included to manage potential issues during data retrieval.</td>
                    </tr>
                    </table>
                </blockquote>
            </details>
        </blockquote>
    </details>
</details>

---
## 🚀 Getting Started

### ☑️ Prerequisites

- **Node.js ≥ 18** (Frontend, Next.js 15)
- **Python ≥ 3.11** (Backend, FastAPI + coc.py)
- **Clash-of-Clans-Entwickler-Account** — Email + Passwort von [developer.clashofclans.com](https://developer.clashofclans.com) für die coc.py-Auto-Login-Methode

### 🔐 Environment variables

Lege im Backend-Verzeichnis eine `.env` an (das Frontend sucht zusätzlich nach `NEXT_PUBLIC_BACKEND_URL`):

```env
# Backend (./backend/.env oder je nach Projektaufbau ./.env)
COC_EMAIL=deine-cocapi-email@example.com
COC_PASSWORD=dein-cocapi-passwort

# Frontend (./.env.local)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Der Default-Clan-Tag (`#2LUVL2QGL`, SOLUNA) ist in `backend/api/main.py` als `CLAN_TAG` hinterlegt. Über die Startseite oder den Query-Parameter `?clan_tag=…` kannst du jeden anderen Clan abfragen.

### ⚙️ Installation

1. Repository klonen:
```sh
❯ git clone https://github.com/noluyorAbi/soluna
❯ cd soluna
```

2. **Frontend** installieren (Next.js):
```sh
❯ npm install
```

3. **Backend** in eigenem Verzeichnis aufsetzen:
```sh
❯ cd backend
❯ python3 -m venv venv
❯ source venv/bin/activate
❯ pip install -r api/requirements.txt
```

### 🤖 Usage

In zwei Terminals parallel laufen lassen:

**Backend** (FastAPI + Uvicorn, Port 8000):
```sh
❯ cd backend
❯ source venv/bin/activate
❯ uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend** (Next.js Dev-Server, Port 3000):
```sh
❯ npm run dev
```

Danach im Browser öffnen: `http://localhost:3000` → Clan-Tag eingeben (oder leer lassen für Default) → „Zum Aktivitäts-Plot“.

Direkter Zugriff auf das Dashboard-HTML:

```sh
❯ curl "http://localhost:8000/clan-activity?clan_tag=%232LUVL2QGL" > dashboard.html
```

### 🧪 Testing
Aktuell keine automatisierten Tests eingerichtet. Vorhandene Frontend-Skripte:

```sh
❯ npm run lint       # ESLint
❯ npm run build      # Production-Build verifizieren
```


---
## 📌 Project Roadmap

- [X] **Interaktives Aktivitäts-Dashboard** mit Plotly-Charts
- [X] **Clan-Tag-Suche** — beliebige Clans analysierbar
- [X] **Light-Theme mit SVG-Icons** (Lucide), responsive Karten-Grid
- [X] **Automatische Interpretation** (Top-Spender, Konzentration, inaktive Mitglieder)
- [X] **Orientierungswerte** & Aktivitäts-Score-Dokumentation im Dashboard
- [X] **Aktivitäts-Score v3** (ungedeckelt, lineare Rohwerte, TH-fairer Trophäen-Bonus)
- [X] **Zweischichtige Interpretation** mit Begriffserklärung (rechts-schief, Konzentration, Netto-Spenden, …)
- [X] **LaTeX-Formel-Rendering** via KaTeX
- [X] **Mobile-responsive** Layout (Breakpoints 960 / 640 / 420 px)
- [ ] Historische Zeitreihen (Saisonvergleiche persistieren)
- [ ] Hero- und Truppen-Level in die Analyse einbeziehen
- [ ] Kriegs-Log-Auswertung (CWL-Performance pro Mitglied)
- [ ] Dark/Light-Mode-Toggle

---

## 🔰 Contributing

- **💬 [Join the Discussions](https://github.com/noluyorAbi/soluna/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/noluyorAbi/soluna/issues)**: Submit bugs found or log feature requests for the `soluna` project.
- **💡 [Submit Pull Requests](https://github.com/noluyorAbi/soluna/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/noluyorAbi/soluna
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/noluyorAbi/soluna/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=noluyorAbi/soluna">
   </a>
</p>
</details>

---

## 🎗 License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## 🙌 Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
