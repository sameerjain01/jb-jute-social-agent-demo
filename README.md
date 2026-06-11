# Social Media Agent

Fully automated social media content engine for small businesses. Generates posts and infographics on a daily cadence, validates them through an AI guardrail, and writes approved content to Google Sheets — ready to copy and post anywhere.

Runs entirely on free services. No servers to manage.

---

## How it works

```
GitHub Actions (daily schedule or manual trigger)
  → Topic Selector    reads recent post history, picks next topic + emotional hook
  → Generator         calls Groq to write the post and generate infographic data
  → Guardrail Judge   second AI call scores safety and quality (rejects < 6/10)
  → Infographic       Playwright renders a branded 1080x1080 PNG from an HTML template
  → Sheets Writer     publishes approved post + infographic link to Feed tab
```

**Three post formats rotate automatically:**
- **Educate** — insight or fact, ends with a question to spark replies
- **Pitch** — problem / solution framing, brand as the answer
- **CTA** — drives one specific action

**Topics are anchored to emotional dimensions** (configurable per business):
nostalgia, comfort, celebration, grief, love, wonder, community, and more.

---

## Setup

### 1. Get a Groq API key (free, 2 minutes)

1. Go to **https://console.groq.com**
2. Sign in or create a free account
3. Go to **Settings → API Keys → Create API key**
4. Copy the key — you will add it to GitHub in Step 4

> Groq is genuinely free with no credit card required.

---

### 2. Set up Google Sheets access (~10 minutes)

You need a **Service Account** — a robot Google account that can write to your Sheet.

#### 2a. Create a Google Cloud project

1. Go to **https://console.cloud.google.com**
2. Click the project dropdown → **New Project** → name it and create
3. Make sure your new project is selected

#### 2b. Enable APIs

1. **APIs & Services → Library**
2. Search for and enable: `Google Sheets API`
3. Search for and enable: `Google Drive API`

#### 2c. Create a Service Account

1. **APIs & Services → Credentials → + Create Credentials → Service Account**
2. Name it (e.g. `sheets-writer`) → Done
3. Click the service account → **Keys tab → Add Key → Create new key → JSON**
4. A JSON file downloads — keep it safe, treat it like a password

#### 2d. Create your Google Sheet

1. Go to **https://sheets.google.com** and create a new blank spreadsheet
2. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/>>>THIS_PART<<</edit
   ```
3. Open the JSON file from Step 2c, find `"client_email"`, copy it
4. In Google Sheets: **Share → paste that email → Editor → Send**

> The agent creates the `Feed` and `Log` tabs automatically on first run.

---

### 3. Fork or push to GitHub

1. Create a new repository at **https://github.com**
2. Push this project to it:
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

---

### 4. Add secrets to GitHub (~3 minutes)

**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `GROQ_API_KEY` | Key from Step 1 |
| `GOOGLE_CREDENTIALS_JSON` | Entire contents of the JSON file from Step 2c |
| `SPREADSHEET_ID` | ID from the Sheets URL in Step 2d |

---

### 5. Test it

1. **Actions tab → workflow name → Run workflow**
2. The run takes about 40–60 seconds (Playwright installs on first run)
3. Open your Google Sheet — `Feed` and `Log` tabs appear with the first post
4. Click **View Infographic** in the Feed tab to see the generated image

If the run is red: click it → click the `post` job → read the error in the logs.

---

### 6. Schedule

The workflow runs daily at 9am UTC by default. To change it, edit `.github/workflows/post.yml`:

```yaml
- cron: "0 9 * * *"   # 9am UTC
```

Use **https://crontab.guru** to build a different schedule.

---

## Customising for a different business

All customisation is in two files — no Python required.

### Brand and voice
Edit `config/config.yaml` → `company` section: name, tagline, description, website, voice.

### Topics and emotional hooks
Edit `data/topics.yaml`. Each topic has:
- `name` — the topic the post is about
- `category` — `educate`, `pitch`, or `cta`
- `emotion` — the emotional dimension to write to (`nostalgia`, `celebration`, `grief`, `love`, etc.)
- `hook` — one-line note on the angle to take

### Infographic design
Edit `src/infographic_template.html` — standard HTML and CSS. Change colors, fonts, layout without touching Python.

### Posting schedule
Edit the `cron` line in `.github/workflows/post.yml`.

### Guardrail strictness
Edit `config/config.yaml` → `guardrail.min_pass_score` (default: 6 out of 10).

---

## What the Google Sheet looks like

### Feed tab

| Run ID | Timestamp | Topic | Format | Post Content | Score | Status | Infographic |
|---|---|---|---|---|---|---|---|
| RUN_… | 2026-06-11 09:00 | The muffin that tastes like… | educate | The smell of vanilla at 4am… | 9 | published | View Infographic |

### Log tab

Every generation attempt — including guardrail rejections with scores and reasons. Useful for demos and auditing.

---

## Costs

| Service | Cost |
|---|---|
| Groq API (AI generation) | Free |
| Google Sheets API | Free |
| GitHub Actions | Free (2,000 min/month on free tier) |
| **Total** | **$0** |
