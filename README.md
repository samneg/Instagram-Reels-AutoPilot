# 📸 Instagram Reels AutoPilot AI (Cloud Edition)

[![GitHub Actions Workflow](https://img.shields.io/badge/GitHub_Actions-Cloud_Cron-blue?logo=githubactions)](https://github.com)
[![Python Version](https://img.shields.io/badge/python-3.11-brightgreen.svg?logo=python)](https://python.org)
[![Zero Cloud Cost](https://img.shields.io/badge/Hosting_Cost-$0_Free_Forever-success)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Instagram Automation](https://img.shields.io/badge/Instagram-Auto_Reels-E4405F?logo=instagram)](https://instagram.com)

An autonomous, **100% free ($0 recurring cost)** cloud automation pipeline for Instagram Reels. 

Pre-schedules hundreds of Reels across a 365-day calendar, stores high-resolution video files on **Google Drive**, and automatically publishes them twice daily using **GitHub Actions Cloud Cron**—with **zero requirement to keep your computer turned on**.

---

## ⚡ Why This Exists

Meta’s official Instagram Content Publishing API **does not allow pre-scheduling draft Reels to their servers months in advance** without an enterprise server setup. 

Typical social media scheduling tools (Buffer, Later, Hootsuite) charge \$20–\$100/month for bulk queuing. **Instagram Reels AutoPilot AI** solves this completely for **$0**:

* **Your PC Stays Off:** Runs on GitHub's free cloud runners.
* **Zero Storage Constraints:** Uses your Google Drive to host high-bitrate video files.
* **AI-Crafted Storytelling:** Every Reel has an attention-grabbing hook, engaging body caption, call-to-action, and strictly 5 high-relevance hashtags.
* **Auto-Syncing Schedule:** After each publication, the cloud runner marks the Reel as published, records the Instagram media ID/URL, and commits the updated schedule back to GitHub automatically.

---

## 🏗️ Architecture

```
                       [ Content Creator / Local AI Engine ]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
      [ Faster-Whisper CPU ]                           [ Gemini Flash AI ]
      Local Audio Transcription                        Hooks, Captions & Top 5 Hashtags
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                            [ Video Files (e.g. 1-249.mp4) ]
                                         │
                                         ▼ Upload Once
                             [ Google Drive Folder ]
                                         │
                                         ▼ (Referenced via File IDs)
                   ┌───────────────────────────────────────────┐
                   │    GitHub Actions Cloud Cron (24/7)       │
                   │                                           │
                   │  ⏰ Slot 1: 11:00 AM IST (05:30 UTC)       │
                   │  ⏰ Slot 2: 05:45 PM IST (12:15 UTC)       │
                   │                                           │
                   │  1. Check due Reel in cloud_schedule.json │
                   │  2. Download single video from GDrive     │
                   │  3. Upload directly via Instagrapi        │
                   │  4. Commit updated schedule back to git   │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                             📸 Published Live Reel
                           (e.g. @manhwamafia1)
```

---

## ✨ Features

- **🚀 100% Autonomous Cloud Publishing:** Scheduled via GitHub Actions (`cron: '30 5 * * *'` and `'15 12 * * *'`).
- **💾 Google Drive Integration:** Keeps your GitHub repository lightweight (< 500 KB) by streaming videos on-demand from Google Drive at runtime.
- **🔒 Encrypted Credential Security:** Authentication cookies (`IG_SESSIONID`) are stored strictly inside encrypted **GitHub Repository Secrets**—safe even on public repos.
- **🎯 Clean Hashtag Architecture:** Strictly uses the top 5 most relevant niche hashtags per Reel for optimal Instagram SEO and aesthetic feed hygiene.
- **🔄 Smart Failover & Catch-Up:** Automatically detects if a slot was missed and processes the next pending video in natural numerical sequence (`1.mp4`, `2.mp4` ... `249.mp4`).
- **📊 Step Summaries & Direct Links:** Every cloud run outputs a markdown report with the live Instagram Reel URL and publication metadata directly in your GitHub Actions dashboard.

---

## 🚀 How to Fork & Use This For Your Channel

### Step 1: Fork or Clone This Repository
Click the **Fork** button at the top right of this repository, or clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/Instagram-Reels-AutoPilot.git
cd Instagram-Reels-AutoPilot
```

### Step 2: Upload Your Videos to Google Drive
1. Create a folder in **Google Drive** (e.g., `My_Instagram_Reels`).
2. Upload your numbered video files (`1.mp4`, `2.mp4`, etc.).
3. Set General Access to **"Anyone with the link can view"**.

### Step 3: Populate `cloud_schedule.json`
Map each video to its Google Drive File ID and metadata:
```json
[
  {
    "slot_id": 1,
    "filename": "1.mp4",
    "gdrive_file_id": "1f3DWw2sc3zntZN8JGpWQfxufGQ27PD41",
    "scheduled_slot_utc": "2026-11-15T05:30:00Z",
    "scheduled_slot_local": "2026-11-15 11:00:00",
    "hook": "You've been completely wrong about this anime secret...",
    "caption": "Here is the full breakdown of what actually happened...",
    "call_to_action": "Follow @YourPage for more daily anime breakdowns.",
    "hashtags": ["#AnimeTheory", "#Anime", "#Manga", "#Shonen", "#Otaku"],
    "status": "Pending"
  }
]
```

### Step 4: Add Your Instagram Session Secret
1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret**:
   - **Name:** `IG_SESSIONID`
   - **Value:** Your browser Instagram `sessionid` cookie value.
3. Go to **Settings** → **Actions** → **General** → scroll to **Workflow permissions** → select **Read and write permissions** → click **Save**.

### Step 5: Test Trigger
Go to the **Actions** tab in GitHub → Select **AutoPilot Instagram Reels Publisher** → Click **Run workflow** → Select **Dry run** (or normal) → Click **Run workflow**.

---

## 📅 Schedule Timing (Customizable)

The default schedule publishes twice daily at peak engagement times for Indian Standard Time (IST):
- **Morning Slot:** `11:00 AM IST` (`05:30 UTC`)
- **Evening Slot:** `05:45 PM IST` (`12:15 UTC`)

To modify the times or frequency, adjust the cron expression in [`.github/workflows/scheduled_reels.yml`](.github/workflows/scheduled_reels.yml):
```yaml
on:
  schedule:
    - cron: '30 5 * * *'   # 11:00 AM IST
    - cron: '15 12 * * *'  # 05:45 PM IST
```

---

## 🛠️ Local Testing

You can also run the publisher locally on your desktop at any time:
```bash
pip install -r requirements.txt
python publish_next_reel.py --dry-run
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). Free for personal and commercial content automation.

