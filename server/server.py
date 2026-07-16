"""
Local background remover server.
Runs the AI model on YOUR machine — nothing is uploaded to a paid service.

Run:
    pip install -r requirements.txt
    python server.py

Then either:
  - use http://localhost:5001 directly (works in Figma desktop), or
  - tunnel it:  ngrok http 5001   and use the https URL ngrok gives you.

First run downloads the model (~170 MB) automatically, then it's cached.
"""

import io

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from rembg import remove, new_session

app = Flask(__name__)

# The Figma plugin UI runs in an iframe with a "null" origin.
# This is what causes the CORS errors — the server must explicitly
# allow any origin or the browser blocks the response.
CORS(app, origins="*")

# "isnet-general-use" gives cleaner edges than the default "u2net".
# Swap back to "u2net" if you want the smaller/faster model.
MODEL_NAME = "isnet-general-use"
session = None  # loaded lazily on first request so startup is instant


def get_session():
    global session
    if session is None:
        print(f"Loading model '{MODEL_NAME}' (first time downloads it)...")
        session = new_session(MODEL_NAME)
    return session


@app.get("/health")
def health():
    """Lets the plugin check the server is up before sending an image."""
    return jsonify(ok=True, model=MODEL_NAME)


@app.post("/remove")
def remove_background():
    """
    Accepts raw image bytes (PNG/JPG) in the request body.
    Returns a PNG with transparent background.

    Query params:
      ?matting=1   -> alpha matting for smoother edges on hair/fuzzy
                      subjects (slower)
    """
    data = request.get_data()
    if not data:
        return jsonify(error="No image bytes in request body"), 400

    use_matting = request.args.get("matting") == "1"

    try:
        result = remove(
            data,
            session=get_session(),
            alpha_matting=use_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
        )
    except Exception as e:  # noqa: BLE001 - surface any model error to the plugin
        return jsonify(error=str(e)), 500

    return send_file(io.BytesIO(result), mimetype="image/png")


if __name__ == "__main__":
    print("Background remover running on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
