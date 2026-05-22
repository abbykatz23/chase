#!/usr/bin/env python3
"""Tiny web UI to trigger a new artwork on the Inky display."""

import subprocess
from pathlib import Path
from flask import Flask, render_template_string

SCRIPT = Path(__file__).with_name("display_art.py")

WORDS = [
    "Awesome", "Amazing", "Brilliant", "Bold", "Brave",
    "Bright", "Caring", "Cheerful", "Clever", "Confident",
    "Creative", "Curious", "Daring", "Dazzling", "Delightful",
    "Dynamic", "Energetic", "Excellent", "Fantastic", "Fearless",
    "Friendly", "Funny", "Generous", "Genius", "Gentle",
    "Glowing", "Happy", "Helpful", "Honest", "Incredible",
    "Inspiring", "Jolly", "Joyful", "Kind", "Legendary",
    "Lovely", "Loyal", "Magnificent", "Marvelous", "Mighty",
    "Outstanding", "Patient", "Peaceful", "Playful", "Powerful",
    "Proud", "Radiant", "Remarkable", "Resilient", "Wonderful",
]

app = Flask(__name__)
current = None  # last subprocess.Popen, or None

PAGE = """
<!doctype html>
<title>Chase's Art Display</title>
<style>
  body { font-family: system-ui, sans-serif; display: grid; place-items: center;
         height: 100vh; margin: 0; background: #f4f1ea; }
  form { text-align: center; }
  button { font-size: 2rem; padding: 1.5rem 3rem; border-radius: 1rem;
           border: none; background: #2b2b2b; color: white; cursor: pointer;
           min-width: 20rem; }
  p { color: #666; margin-top: 1rem; }
</style>
<form method="post" action="/refresh">
  <button type="submit" id="btn">Chase Awesome!</button>
  {% if msg %}<p>{{ msg }}</p>{% endif %}
</form>
<script>
  const words = {{ words|tojson }};
  const btn = document.getElementById("btn");
  function pick() {
    const w = words[Math.floor(Math.random() * words.length)];
    btn.textContent = "Chase " + w + "!";
  }
  pick();
  setInterval(pick, 2500);
</script>
"""

@app.route("/")
def index():
    return render_template_string(PAGE, words=WORDS, msg=None)

@app.route("/refresh", methods=["POST"])
def refresh():
    global current
    if current is not None and current.poll() is None:
        return render_template_string(PAGE, words=WORDS,
                                      msg="Already refreshing… please wait.")
    current = subprocess.Popen(["/usr/bin/python3", str(SCRIPT)])
    return render_template_string(PAGE, words=WORDS,
                                  msg="Refreshing… give it about a minute.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
