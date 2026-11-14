"""
Standalone Cloud Instagram Reels AutoPilot Publisher.
Designed to run inside GitHub Actions on a cron schedule twice a day
(11:00 AM & 05:45 PM IST). Downloads the due video from Google Drive,
publishes it as an Instagram Reel, and updates cloud_schedule.json.
"""

import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("CloudPublisher")

SCHEDULE_FILE = Path(__file__).resolve().parent / "cloud_schedule.json"
SESSION_DUMP_PATH = Path(__file__).resolve().parent / "instagram_session.json"


def get_instagram_client():
    from instagrapi import Client

    cl = Client()
    cl.delay_range = [2, 5]

    session_json_str = os.getenv("IG_SESSION_JSON", "").strip()
    sessionid = os.getenv("IG_SESSIONID", "").strip()

    if session_json_str and session_json_str.startswith("{"):
        logger.info("Logging into Instagram using IG_SESSION_JSON secret...")
        SESSION_DUMP_PATH.write_text(session_json_str, encoding="utf-8")
        cl.load_settings(SESSION_DUMP_PATH)
        # Login without password to validate loaded settings
        cl.login_by_sessionid(cl.sessionid)
    elif sessionid:
        logger.info("Logging into Instagram using IG_SESSIONID secret...")
        clean_sid = sessionid.strip('"').strip("'")
        cl.login_by_sessionid(clean_sid)
    elif SESSION_DUMP_PATH.exists():
        logger.info("Logging into Instagram using local instagram_session.json...")
        cl.load_settings(SESSION_DUMP_PATH)
        cl.login_by_sessionid(cl.sessionid)
    else:
        raise RuntimeError(
            "No Instagram credentials found! Set IG_SESSION_JSON or IG_SESSIONID in repository secrets."
        )

    info = cl.account_info()
    logger.info(f"Successfully authenticated as @{info.username} (PK: {info.pk})")
    return cl


def build_caption(hook: str, caption: str, call_to_action: str, hashtags: list) -> str:
    parts = []
    if hook.strip():
        parts.append(hook.strip())
    if caption.strip():
        parts.append(caption.strip())
    if call_to_action.strip():
        parts.append(call_to_action.strip())

    body = "\n\n".join(parts)

    clean_tags = []
    for t in hashtags:
        t = t.strip()
        if not t:
            continue
        if not t.startswith("#"):
            t = f"#{t}"
        if t not in clean_tags:
            clean_tags.append(t)
    clean_tags = clean_tags[:5]

    if clean_tags:
        body = f"{body}\n\n.\n.\n{' '.join(clean_tags)}"
    return body.strip()


def download_video(gdrive_file_id: str, filename: str) -> Path:
    out_dir = Path(__file__).resolve().parent / "temp_videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    logger.info(f"Downloading {filename} from Google Drive (ID: {gdrive_file_id})...")
    
    # Try direct download URL
    url = f"https://drive.google.com/uc?id={gdrive_file_id}&export=download"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req) as resp, open(out_path, "wb") as f:
            f.write(resp.read())
        size_mb = out_path.stat().st_size / (1024 * 1024)
        logger.info(f"Downloaded {filename} ({size_mb:.2f} MB)")
        return out_path
    except Exception as exc:
        logger.warning(f"Direct download failed: {exc}. Falling back to gdown...")
        import gdown
        gdown.download(id=gdrive_file_id, output=str(out_path), quiet=False)
        return out_path


def main():
    parser = argparse.ArgumentParser(description="Instagram Reels Cloud AutoPilot Publisher")
    parser.add_argument("--force", action="store_true", help="Publish the next pending reel even if scheduled time is in the future")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without uploading")
    args = parser.parse_args()

    if not SCHEDULE_FILE.exists():
        logger.error(f"Schedule file not found: {SCHEDULE_FILE}")
        sys.exit(1)

    schedule = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.info(f"Current UTC time: {now_utc}")

    # Find candidate
    candidate = None
    for item in schedule:
        if item.get("status") == "Pending":
            if args.force or item.get("scheduled_slot_utc", "") <= now_utc:
                candidate = item
                break

    if not candidate:
        logger.info("No Reels are due right now. Schedule is up to date!")
        return

    fname = candidate["filename"]
    slot_local = candidate.get("scheduled_slot_local", "")
    logger.info(f"Selected Reel to publish: {fname} (Scheduled Slot: {slot_local})")

    if args.dry_run:
        logger.info(f"[DRY-RUN] Would download and publish: {fname}")
        return

    # Download from Google Drive
    video_path = download_video(candidate["gdrive_file_id"], fname)
    if not video_path.exists() or video_path.stat().st_size < 1000:
        logger.error(f"Downloaded video file is missing or invalid: {video_path}")
        sys.exit(1)

    # Build caption
    caption_text = build_caption(
        hook=candidate.get("hook", ""),
        caption=candidate.get("caption", ""),
        call_to_action=candidate.get("call_to_action", ""),
        hashtags=candidate.get("hashtags", []),
    )

    # Upload to Instagram
    cl = get_instagram_client()
    logger.info(f"Uploading '{fname}' as an Instagram Reel...")

    media = cl.clip_upload(
        path=str(video_path),
        caption=caption_text,
    )

    media_id = str(getattr(media, "id", "") or getattr(media, "pk", ""))
    media_code = str(getattr(media, "code", ""))
    reel_url = f"https://www.instagram.com/reel/{media_code}/" if media_code else ""

    logger.info(f"Successfully published Reel '{fname}'!")
    logger.info(f"  Media ID: {media_id}")
    logger.info(f"  Code: {media_code}")
    logger.info(f"  URL: {reel_url}")

    # Update schedule
    candidate["status"] = "Published"
    candidate["instagram_media_id"] = media_id
    candidate["instagram_code"] = media_code
    candidate["published_at_utc"] = datetime.now(timezone.utc).isoformat()
    candidate["reel_url"] = reel_url

    SCHEDULE_FILE.write_text(json.dumps(schedule, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Updated cloud_schedule.json successfully!")

    # Write GitHub Actions Step Summary if in CI
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"### 🎉 Successfully Published Reel `{fname}`!\n\n")
            f.write(f"- **Scheduled Slot:** {slot_local}\n")
            f.write(f"- **Instagram Code:** `{media_code}`\n")
            if reel_url:
                f.write(f"- **View Live on Instagram:** [{reel_url}]({reel_url})\n\n")
            f.write(f"**Hook:** {candidate.get('hook', '')}\n")

    # Cleanup temp video to save space
    try:
        video_path.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
