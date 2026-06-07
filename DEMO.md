# JuteVerde Social Media Agent — Demo Guide

**For:** Marketing team running live demos
**Time needed:** 5 minutes
**Technical knowledge required:** None

---

## What is this?

An automated content agent that writes social media posts for a jute business — every day, on a schedule, with no human involved.

It picks a topic, writes a post, has a second AI check it for quality, then saves the approved post ready to publish anywhere — LinkedIn, Instagram, Facebook, X, wherever.

---

## Why Google Sheets and not posting directly to social media?

> "Every major social platform charges businesses to post through their API — some charge just to get access. Google Sheets is free, and for a demo it's actually better because you can watch the post appear on screen in real time. Wiring it up to post directly to any platform is straightforward once the client wants to go live."

---

## What are Guardrails?

The most common question you'll get: *"how do you make sure it doesn't post something embarrassing?"*

> "After the AI writes the post, a completely separate AI reads it and scores it out of 10. It checks whether the post is accurate, on-brand, and professional. Only posts scoring 6 or above get published. If a post fails, the system retries up to 3 times automatically. Every attempt — including rejections — is logged with the reason why."

---

## Before you demo — open these two tabs

- **Tab 1 — the Google Sheet:** shows the posts the agent has already written
- **Tab 2 — GitHub Actions:** where you trigger the live run

---

## The demo (5 minutes)

**1. Show the Sheet first**

Open Tab 1. Show the Feed tab (approved posts) and the Log tab (every attempt, including rejections with scores and reasons).

> "This is the output. Every approved post lands here, ready to publish. The Log tab shows everything — including posts the system rejected and why."

---

**2. Trigger a live run**

Switch to Tab 2. Click **Run workflow → Run workflow**.

> "Normally this runs automatically every morning. I'm triggering it manually so you can watch it happen."

---

**3. Watch the post appear**

Switch back to Tab 1. A new row appears within 30 seconds.

Point out: the topic, the format, the guardrail score, the status "published".

> "It picked a topic it hasn't covered recently, wrote the post, had a second AI score it — 9 out of 10 — and published it. Thirty seconds. Every morning, without anyone touching it."

---

**4. Run it again**

Trigger a second run. Show it picks a **different topic and a different format**.

> "It never repeats. It rotates between educational posts, pitch posts, and calls to action — so the feed stays varied automatically."

---

## Questions you'll probably get

**"Can it post directly to Instagram / LinkedIn / X?"**
> "Yes. That's the next step — it's straightforward to connect. We built the demo on Sheets so you can actually see the output live. Direct posting is ready to add when the client wants to go live."

**"What stops it posting something wrong?"**
> "The guardrail — a second AI scores every post before it's approved. Anything below a 6 is rejected and retried. Full log always visible."

**"How much does it cost to run?"**
> "This demo runs at zero cost. AI writing, quality check, scheduling, storage — all free. The only cost that comes in later is platform API access for direct posting, and that depends on which platforms."

**"Can we change the topics or the brand?"**
> "Yes — topics and brand voice are just a simple list. No coding. Change the list, push it, live on the next run."

**"What if it fails one day?"**
> "It skips that day and nothing goes out. The failure shows up immediately so someone can check. It doesn't retry bad content — it just waits for the next scheduled run."

---

## What this is not (be upfront)

- Does not post directly to social platforms yet
- Text only — no images or graphics
- Does not reply to comments or engage with followers
- One brand voice per setup
