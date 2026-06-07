# 🌿 JuteVerde Social Media Agent

Fully automated LinkedIn content engine. Generates posts on a daily cadence,
validates them through an AI guardrail, and writes approved posts to Google Sheets.
No human review required.

---

## How it works

```
GitHub Actions (cron 9am UTC or manual button click)
  → Topic Selector   reads recent posts from Sheets, picks next topic + format
  → Generator        calls Gemini to write the LinkedIn post
  → Guardrail Judge  second Gemini call evaluates safety + quality
  → Sheets Writer    publishes approved posts to the Feed tab, logs everything
```

**Three post formats rotate in order:**
- **Educate** — fact/insight post, ends with a question
- **Pitch** — problem/solution framing, jute as the answer
- **CTA** — drives one specific action

---

## Setup — step by step

### Step 1: Get your Gemini API key (free, ~2 minutes)

1. Go to **https://aistudio.google.com**
2. Sign in with your Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy the key — you'll add it to GitHub in Step 4

> Free tier: 1,500 requests/day, 15 requests/minute. More than enough.

---

### Step 2: Set up Google Sheets access (~10 minutes)

You need a **Service Account** — a robot Google account that can write to your Sheet.

#### 2a. Create a Google Cloud project

1. Go to **https://console.cloud.google.com**
2. Click the project dropdown (top left) → **"New Project"**
3. Name it `jute-social-agent` → **Create**
4. Make sure this project is selected in the dropdown

#### 2b. Enable the Google Sheets API

1. In the left sidebar: **APIs & Services → Library**
2. Search for `Google Sheets API` → click it → **Enable**
3. Also search for `Google Drive API` → **Enable** (needed to access the spreadsheet)

#### 2c. Create a Service Account

1. In the left sidebar: **APIs & Services → Credentials**
2. Click **"+ Create Credentials" → "Service Account"**
3. Name it `sheets-writer` → click **Done** (skip optional fields)
4. Click on the service account you just created
5. Go to the **Keys** tab → **Add Key → Create new key → JSON**
6. A JSON file downloads to your computer — **keep this safe, treat it like a password**

#### 2d. Create your Google Sheet

1. Go to **https://sheets.google.com** and create a new blank spreadsheet
2. Name it `JuteVerde Social Feed`
3. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/ >>>THIS_PART<<< /edit
   ```
4. Open the JSON file you downloaded in Step 2c
5. Find the `"client_email"` field — it looks like:
   `sheets-writer@jute-social-agent.iam.gserviceaccount.com`
6. In Google Sheets: click **Share** (top right) → paste that email → set role to **Editor** → Send

> The agent will automatically create the `Feed` and `Log` tabs on first run.

---

### Step 3: Create your GitHub repository (~3 minutes)

1. Go to **https://github.com** and sign in (create a free account if needed)
2. Click **"+" → "New repository"**
3. Name it `jute-social-agent`
4. Set it to **Private** (recommended — keeps your config private)
5. Click **Create repository**
6. Upload the project files by dragging the entire folder into the GitHub web interface,
   or use these commands if you have Git installed:
   ```bash
   cd jute-social-agent
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/jute-social-agent.git
   git push -u origin main
   ```

---

### Step 4: Add secrets to GitHub (~3 minutes)

Your repo → **Settings** (top tab) → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | The key from Step 1 |
| `GOOGLE_CREDENTIALS_JSON` | The **entire contents** of the JSON file from Step 2c (open in a text editor, select all, paste) |
| `SPREADSHEET_ID` | The ID you copied from the Sheets URL in Step 2d |

---

### Step 5: Test it manually

1. In your repo, click the **Actions** tab (top navigation)
2. Click **"🌿 JuteVerde Social Agent"** in the left sidebar
3. Click the **"Run workflow"** button (right side) → **"Run workflow"**
4. Watch the run — it takes about 20–30 seconds
5. Open your Google Sheet — you should see the `Feed` and `Log` tabs created
   and the first post in the Feed tab

If the run turns **red** (failed): click on it → click the `post` job → read the logs.
The most common issue is a typo in a secret value.

---

### Step 6: Enable the daily schedule

GitHub Actions disables scheduled workflows on new repos after 60 days of inactivity,
but for fresh repos it should be active immediately.

To verify: **Actions** tab → your workflow → the schedule shows as active if you've
pushed at least once and the workflow file exists.

**To change the posting time:** edit `.github/workflows/post.yml`, find the cron line:
```yaml
- cron: "0 9 * * *"   # 9am UTC
```
Use https://crontab.guru to generate a different time.

---

## Customising the demo

All changes can be made without touching Python code:

### Change the company / brand voice
Edit `config/config.yaml` — the `company` section.

### Add or change topics
Edit `data/topics.yaml` — add/remove/edit topic entries.

### Change posting frequency
Edit the `cron` line in `.github/workflows/post.yml`.

### Change guardrail strictness
Edit `config/config.yaml` → `guardrail.min_pass_score` (default: 6 out of 10).

---

## What the Google Sheet looks like

### Feed tab (the "published" social media feed)

| Run ID | Timestamp (UTC) | Topic | Format | Post Content | Guardrail Score | Status |
|---|---|---|---|---|---|---|
| RUN_20241210_090012 | 2024-12-10 09:00:12 | Jute vs plastic bags… | educate | Did you know a single… | 9 | published |

### Log tab (every attempt, including rejected ones)

Shows all generation attempts — great for demo transparency.
Rejected posts appear here with the reason they failed guardrail.

---

## Live demo script

1. Open the Google Sheet in one browser tab
2. Open the GitHub Actions page in another tab
3. Click **"Run workflow"**
4. While it runs (30 seconds), explain what each step does
5. Switch to the Sheet — the post appears in real time
6. Click on the Log tab — show the guardrail score and reasoning
7. Run it again — show it picks a different topic and format

---

## Costs

| Service | Cost |
|---|---|
| Gemini API | Free (1,500 calls/day limit) |
| Google Sheets API | Free |
| GitHub Actions | Free (2,000 min/month on free tier) |
| **Total** | **$0** |
