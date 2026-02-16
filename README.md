# COLA – Simple Calculator

**Version: v1.0 (Stable)**

**Live Demo:** `https://<your-username>.github.io/<repo-name>/` (e.g. `https://yourname.github.io/COLA/` — replace with your actual GitHub Pages URL)

**Status:** Complete (v1.0 stable). Main branch is protected; changes must go through PR + CI. No further development unless a bug or v1.1 scope is approved.

A lightweight web-based calculator.

## Features

- Addition, subtraction, multiplication, division
- Decimal input
- Keyboard support
- Responsive layout
- Error handling (divide by zero)
- Number formatting (e.g. 1,000)

## How to Run

1. Download the project
2. Open `index.html` in a web browser

No installation required.

## Keyboard Controls

| Key | Action |
|-----|--------|
| 0–9 | Numbers |
| + - * / | Operators |
| . | Decimal |
| Enter or = | Calculate |
| Backspace | Delete last digit |
| Escape | Clear all |

## Project Files

- `index.html` – Calculator UI and button wiring
- `style.css` – Layout and responsive styles
- `app.js` – Calculator engine and keyboard handling
- `README.md` – This file

## Branch Strategy

| Branch   | Purpose |
|----------|---------|
| `main`   | Stable production (v1.0) |
| `develop`| Future improvements and bug fixes |

## Deploy with GitHub Pages

1. Ensure the project is in a GitHub repository (e.g. `COLA` or `cola-calculator`).
2. On GitHub: **Settings → Pages**.
3. Under **Source**: Branch **main**, Folder **/ (root)** → Save.
4. After a short wait, the calculator is available at:
   - `https://<your-username>.github.io/<repo-name>/`  
   (e.g. `https://yourname.github.io/COLA/` if the repo is named `COLA`).

To use a dedicated repo only for the calculator:

- Create a new public repo (e.g. `cola-calculator`), then push only `index.html`, `style.css`, `app.js`, and `README.md` to the `main` branch and enable Pages as above.
