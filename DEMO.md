# Sarah's Bakery — Social Media Agent Operator Guide

**For:** Anyone running or showing the demo
**Time needed:** 5 minutes to demo, 2 minutes to set up
**Technical knowledge required:** None

---

## Your two links — bookmark both

| What | Link |
|------|------|
| Google Sheet (posts + log) | https://docs.google.com/spreadsheets/d/1ga93Oi5MvnpzGteWiCZ4GWUW1vegUyxoH6T68IYHusg |
| GitHub Actions (trigger run) | https://github.com/sameerjain01/jb-jute-social-agent-demo/actions/workflows/post.yml |

---

## Before the demo — 2-minute checklist

Open both links in separate browser tabs. Then:

1. **Google Sheet** — click the **Feed** tab. Confirm there are existing rows. If it's empty, run the workflow once now and wait 40 seconds.
2. **GitHub Actions** — confirm the last run shows a green tick. If it shows red, see **Troubleshooting** below.

That's it. You're ready.

---

## The demo — step by step

### Step 1 — Show the Sheet

Open the Google Sheet. Show the **Feed** tab.

Point out the columns:
- **Topic** — what the post is about
- **Format** — educate / pitch / call-to-action
- **Post Content** — the full post text, ready to copy and post anywhere
- **Guardrail Score** — out of 10, always 6 or above to get published
- **Infographic URL** — click "View Infographic" to open the image in a new tab

Say:
> "This is the output. Every approved post lands here, ready to publish. Click 'View Infographic' to see the image it generated alongside the post."

Click a **View Infographic** link to show an example image.

Show the **Log** tab next.

Say:
> "The Log tab shows every attempt — including ones the AI rejected and why. Nothing is hidden."

---

### Step 2 — Trigger a live run

Switch to GitHub Actions. Click **Run workflow**, then click the green **Run workflow** button.

Say:
> "Normally this runs every morning at 9am automatically. I'm triggering it manually so you can watch it happen live."

---

### Step 3 — Watch the post appear

Stay on GitHub Actions. The run appears immediately — a yellow circle means it's running.

Switch back to the Google Sheet. **Refresh the tab after about 40 seconds** — a new row appears at the top with today's timestamp.

Point out:
- The topic is different from the previous post
- The score is visible
- Click **View Infographic** to open the image — it reflects the topic (ocean, forests, earth, or water)

Say:
> "It picked a topic it hasn't covered recently, wrote the post, had a second AI score it, and generated a matching seasonal infographic — all in under a minute. Every morning, without anyone touching it."

---

### Step 4 — Run it again (optional, max impact)

Trigger a second run. Wait 40 seconds. Show the new row at the top.

Point out the topic and format have rotated.

Say:
> "It never repeats topics or formats. It rotates between educational posts, pitches, and calls to action so the feed stays varied on its own."

---

## Questions you'll get

**"Can it post directly to Instagram / LinkedIn / X?"**
> "Yes. That's the next step — the content is already written and the image is already generated, so connecting to any platform is straightforward. The demo uses Sheets because you can watch it happen live on screen."

**"What stops it posting something embarrassing?"**
> "After it writes the post, a completely separate AI reads it and scores it out of 10. Anything below 6 is rejected and it tries again — up to 3 times. Every rejection is logged with the reason. Only posts that pass go to the Feed."

**"How much does it cost to run?"**
> "This demo runs at zero cost. AI writing, quality check, image generation, scheduling, storage — all free. The only cost that comes in later is the platform API fee for direct posting, which depends on the platform."

**"Can we change the topics or the brand voice?"**
> "Yes — topics and brand voice are a simple text list. No coding. Swap the bakery name, the product list, the seasonal specials — change the list, save it, live on the next run."

**"What if it fails one day?"**
> "It skips that day. Nothing bad goes out. The failure shows as a red mark in GitHub so someone can check. It doesn't retry bad content — it waits for the next scheduled run."

**"Who owns the AI-generated content?"**
> "The business does. The AI writes a draft, the guardrail checks it, and the business publishes it. Same as hiring a copywriter."

---

## Troubleshooting

### Last GitHub run shows red (failed)

1. Click the failed run to open it
2. Click **post** to expand the job steps
3. Scroll to the red step — the error message is right there

Common causes:
- **"API key invalid"** — the Groq key has expired. Generate a new one at console.groq.com → Settings → API Keys, then update the secret in GitHub (Settings → Secrets → GROQ_API_KEY)
- **"Guardrail failed after 3 attempts"** — rare. Just trigger a new run. It picks a different topic each time.

### Sheet shows no new row after 60 seconds

- Check GitHub Actions — the run may still be in progress (yellow circle) or may have failed
- Wait for it to fully complete (green tick), then refresh the Sheet

### "View Infographic" shows 404

- The infographic file is committed to GitHub as part of the run
- If the run is still in progress, the file won't exist yet — wait for green, then click again

### Sheet Feed tab is completely empty

- Run the workflow once manually and wait 60 seconds
- If still empty, check GitHub Actions for errors (see above)

---

## What this is and what it isn't

**Is:**
- Automated post writing, quality scoring, and infographic generation
- Runs daily on a schedule, no human required
- Logs every decision — transparent and auditable
- Zero running cost

**Is not (yet):**
- Does not post directly to social platforms — output is in Google Sheets ready to copy
- Does not reply to comments or engage with followers
- One brand voice per setup (multiple brands = multiple deployments)
