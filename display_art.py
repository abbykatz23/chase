#!/usr/bin/env python3
"""
Daily art display for Inky Impression 4"
Pulls a random public-domain artwork from the Art Institute of Chicago API
"""

import requests
import random
import os
import sys
import time
import logging
from PIL import Image
from io import BytesIO

SEEN_IDS_FILE = os.path.expanduser("~/seen_ids.txt")
DISPLAY_WIDTH  = 600
DISPLAY_HEIGHT = 400
IIIF_BASE      = "https://www.artic.edu/iiif/2"
HEADERS        = {"User-Agent": "Mozilla/5.0 (compatible; InkyArtDisplay/1.0)"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.expanduser("~/display_art.log")),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

def load_seen_ids():
    if not os.path.exists(SEEN_IDS_FILE):
        return set()
    with open(SEEN_IDS_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_id(artwork_id):
    with open(SEEN_IDS_FILE, "a") as f:
        f.write(f"{artwork_id}\n")

def clear_seen_ids():
    open(SEEN_IDS_FILE, "w").close()
    log.info("Seen IDs file cleared - starting fresh rotation")

def fetch_random_artwork(seen_ids, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            page = random.randint(1, 500)
            url = (
                f"https://api.artic.edu/api/v1/artworks"
                f"?page={page}&limit=50"
                f"&fields=id,image_id,title,artist_display"
                f"&query[term][is_public_domain]=true"
            )
            resp = requests.get(url, timeout=15, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()

            candidates = [
                a for a in data.get("data", [])
                if a.get("image_id") and str(a["id"]) not in seen_ids
            ]

            if candidates:
                artwork = random.choice(candidates)
                log.info(f"Selected: '{artwork.get('title', 'Unknown')}' "
                         f"by {artwork.get('artist_display', 'Unknown')}")
                return artwork

            log.info(f"Attempt {attempt+1}: no unseen candidates on page {page}, retrying...")

        except Exception as e:
            log.warning(f"Attempt {attempt+1} failed: {e}")

        time.sleep(2)

    return None

def fetch_image(image_id):
    url = f"{IIIF_BASE}/{image_id}/full/843,/0/default.jpg"
    log.info(f"Fetching image: {url}")
    resp = requests.get(url, timeout=30, headers=HEADERS)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")

def fit_to_display(img):
    ratio = min(DISPLAY_WIDTH / img.width, DISPLAY_HEIGHT / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (255, 255, 255))
    x = (DISPLAY_WIDTH - new_w) // 2
    y = (DISPLAY_HEIGHT - new_h) // 2
    canvas.paste(img, (x, y))
    return canvas

def send_to_display(img):
    from inky.inky_e640 import Inky
    inky = Inky()
    inky.set_image(img)
    inky.show()
    log.info("Image sent to display")

def main():
    seen_ids = load_seen_ids()
    log.info(f"Loaded {len(seen_ids)} seen IDs")

    artwork = fetch_random_artwork(seen_ids)

    if artwork is None:
        log.warning("Couldn't find an unseen artwork - clearing history and retrying")
        clear_seen_ids()
        artwork = fetch_random_artwork(set())

    if artwork is None:
        log.error("API unavailable after all attempts - keeping current display")
        sys.exit(0)

    try:
        img = fetch_image(artwork["image_id"])
        img = fit_to_display(img)
        send_to_display(img)
        save_seen_id(str(artwork["id"]))
        log.info("Done!")
    except Exception as e:
        log.error(f"Failed to display image: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()


