import base64
import csv
import glob
import os
import re
import time
import json
import hashlib
import smtplib
import ssl
from typing import Iterable, Optional, Tuple, List
from dotenv import load_dotenv

import certifi
import requests
from bs4 import BeautifulSoup

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from urllib3.util.util import to_str

# ----------------------------
# Config
load_dotenv()

PROFILE = os.environ.get("LM_PROFILE")
LINKS_FILE = os.path.join("links", f"links_{PROFILE}.txt")


def load_links_from_file(path: str):
    links = []
    if not os.path.exists(path):
        print(f"[WARN] Links file not found: {path}")
        return links
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                links.append((row[0].strip(), row[1].strip()))
    return links


LINKS = load_links_from_file(LINKS_FILE)
# ----------------------------

CA_BUNDLE = certifi.where()
DATA_DIR = os.environ.get("LM_DATA_DIR", "data")
TIMEOUT = int(os.environ.get("LM_HTTP_TIMEOUT", "25"))

# Email settings
SHOT_DIR = os.path.join(DATA_DIR, "shots")
SMTP_HOST = os.environ.get("LM_SMTP_HOST")
SMTP_PORT = int(os.environ.get("LM_SMTP_PORT"))
SMTP_EMAIL = os.environ.get("LM_SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("LM_SMTP_PASSWORD")
base64_bytes = SMTP_PASSWORD.encode("ascii")
sample_string_bytes = base64.b64decode(base64_bytes)
SMTP_PASSWORD = sample_string_bytes.decode("ascii")

TO_ADDRESSES = os.environ.get("LM_TO", SMTP_EMAIL).split(",")


# ----------------------------
# Utilities
# ----------------------------
def sanitize_filename(name: str) -> str:
    """Safe filename derived from title."""
    name = re.sub(r"[\/:*?\"<>|]+", "_", name).strip()
    # keep it reasonable length
    return name[:180] or "untitled"


def ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def file_paths_for_title(title: str) -> Tuple[str, str]:
    """Return (content_path, meta_path) under DATA_DIR for this title."""
    base = os.path.join(DATA_DIR, sanitize_filename(title))
    return base + ".txt", base + ".json"


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


# ----------------------------
# Content fetching & normalization
# ----------------------------
def get_content(url: str) -> str:
    """Fetch a URL and return normalized textual content suitable for diffing."""
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, verify=os.environ.get("LM_REQUESTS_CA_BUNDLE"), timeout=15)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"[WARN] Timeout la {url}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ERROR la {url}")

    # Try to parse HTML and strip script/style/nav etc.
    text = resp.text
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    # Optional: collapse whitespace
    content = " ".join(soup.get_text(separator=" ").split())
    # Fallback to raw text if parsing failed terribly
    return content if content else text


def get_previous_content(title: str) -> Optional[str]:
    content_path, _ = file_paths_for_title(title)
    if os.path.exists(content_path):
        with open(content_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return None


# ----------------------------
# Screenshot (best-effort)
# ----------------------------
def shot_path(title: str, ts: int) -> str:
    ensure_dirs(SHOT_DIR)
    return os.path.join(SHOT_DIR, f"{sanitize_filename(title)}-{ts}.png")


def latest_shot_path(title: str) -> Optional[str]:
    base = os.path.join(SHOT_DIR, f"{sanitize_filename(title)}-*.png")
    files = glob.glob(base)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def take_screenshot_to(url: str, dest_path: str) -> bool:
    from playwright.sync_api import sync_playwright  # type: ignore

    ensure_dirs(os.path.dirname(dest_path))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.screenshot(path=dest_path, full_page=True)
        context.close()
        browser.close()
    return True


# ----------------------------
# Email
# ----------------------------
def send_email(subject: str, html_body: str, attachments: Optional[List[Tuple[str, bytes]]] = None) -> None:
    """
    Send a multipart email with optional attachments.
    attachments: list of (filename, bytes)
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = ", ".join(TO_ADDRESSES)
    msg["Subject"] = subject

    # prefer HTML, but include plaintext fallback
    plain = re.sub(r"<[^>]+>", "", html_body)
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(plain, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    # attachments
    for (fname, blob) in (attachments or []):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(blob)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{fname}"')
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, TO_ADDRESSES, msg.as_string())


# ----------------------------
# Persist
# ----------------------------
def save_current(title: str, content: str, url: str) -> None:
    content_path, meta_path = file_paths_for_title(title)
    ensure_dirs(os.path.dirname(content_path))
    with open(content_path, "w", encoding="utf-8") as f:
        f.write(content)
    meta = {"title": title, "url": url, "hash": hash_text(content), "saved_at": int(time.time())}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ----------------------------
# Diff/notify pipeline
# ----------------------------
def notify(title: str, url: str, old_shot: Optional[str], new_shot: Optional[str]) -> None:
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <h3>{title} — content changed</h3>
    <p><b>When:</b> {now_str}</p>
    <p><b>Link:</b> <a href="{url}">{url}</a></p>
    <p>Attachments: <i>old</i> and <i>new</i> screenshots.</p>
    """
    attachments = []
    if old_shot and os.path.exists(old_shot):
        with open(old_shot, "rb") as f:
            attachments.append((f"{sanitize_filename(title)}-old.png", f.read()))
    if new_shot and os.path.exists(new_shot):
        with open(new_shot, "rb") as f:
            attachments.append((f"{sanitize_filename(title)}-new.png", f.read()))

    send_email(subject=f"[LinkMonitor] {title} changed",
               html_body=html,
               attachments=attachments)
    print(f"{title} changed at {now_str}!!")


def process_link(link_title: Tuple[str, str]) -> None:
    url, title = link_title
    try:
        new_content = get_content(url)
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return

    old_content = get_previous_content(title)
    if old_content is None:
        # First run: save but don't notify (or choose to notify if you want)
        save_current(title, new_content, url)
        ts = int(time.time())
        take_screenshot_to(url, shot_path(title, ts))
        print(f"[INIT] Saved baseline for '{title}'")
        return

    if hash_text(new_content) != hash_text(old_content):
        prev_shot = latest_shot_path(title)
        ts = int(time.time())
        new_shot = shot_path(title, ts)
        take_screenshot_to(url, new_shot)

        notify(title, url, prev_shot, new_shot)
        save_current(title, new_content, url)
    else:
        print(f"[OK] No change for '{title}'")


def monitor(links_and_titles: Iterable[Tuple[str, str]]) -> None:
    for link in links_and_titles:
        process_link(link)


if __name__ == "__main__":
    monitor(LINKS)
