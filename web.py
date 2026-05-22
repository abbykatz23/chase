#!/usr/bin/env python3
"""Tiny web UI to trigger a new artwork on the Inky display."""

import subprocess
from pathlib import Path
from flask import Flask

SCRIPT = Path(__file__).with_name("display_art.py")

app = Flask(__name__)
current = None  # last subprocess.Popen, or None

PAGE = """
<!doctype html>
<title>Chase's Art Display</title>
<style>
  body {{ font-family: system-ui, sans-serif; display: grid; place-items: center;
         height: 100vh; margin: 0; background: #f4f1ea; }}
  form {{ text-align: center; }}
  button {{ font-size: 2rem; padding: 1.5rem 3rem; border-radius: 1rem;
           border: none; background: #2b2b2b; color: white; cursor: pointer; }}
  p {{ color: #666; margin-top: 1rem; }}
</style>
<form method="post" action="/refresh">
  <button type="submit">New Artwork</button>
  {msg}
</form>
"""

@app.route("/")
def index():
    return PAGE.format(msg="")

@app.route("/refresh", methods=["POST"])
def refresh():
    global current
    if current is not None and current.poll() is None:
        return PAGE.format(msg="<p>Already refreshing… please wait.</p>")
    current = subprocess.Popen(["/usr/bin/python3", str(SCRIPT)])
    return PAGE.format(msg="<p>Refreshing… give it about a minute.</p>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
