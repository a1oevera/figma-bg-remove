# Background Remover — local Figma plugin

Removes image backgrounds on your own machine using an open-source model
(rembg / IS-Net). No paid API, no upload limits, no watermarks.

Two parts:

```
server/         Python — runs the AI model, exposes POST /remove
figma-plugin/   the Figma plugin — sends your selected layer to the server
```

## 1. Run the server

```bash
cd server
pip install -r requirements.txt
python server.py
```

First image you process triggers a one-time model download (~180 MB),
cached in `~/.u2net/` after that.

## 2. Load the plugin in Figma

Figma **desktop app** → Plugins → Development → **Import plugin from manifest…**
→ pick `figma-plugin/manifest.json`.

## 3. Use it

1. Select one layer with an image.
2. Run the plugin, keep the URL as `http://localhost:5001`.
3. Hit **Remove background**. The cut-out appears next to the original
   (original is never touched).
4. Check **Smooth edges** for hair / fuzzy subjects — slower but cleaner.

## ngrok (only if localhost is blocked)

Figma desktop usually allows `http://localhost` directly. If your setup
refuses (e.g. Figma in the browser), tunnel it:

```bash
grok http 5001
```

Paste the `https://…ngrok…` URL it prints into the plugin's Server URL
field. Note the free-tier URL changes every time you restart ngrok —
claim your one free **static domain** in the ngrok dashboard to stop
re-pasting it.

## Troubleshooting (a.k.a. the greatest hits)

- **CORS error in the console** — the plugin UI runs in an iframe with a
  `null` origin, so the server must send `Access-Control-Allow-Origin`.
  `server.py` already does this via flask-cors; if you fork the server,
  keep that line.
- **"Failed to fetch"** — server not running, or the URL in the plugin
  doesn't match. Check `http://localhost:5001/health` in a browser; you
  should see `{"ok": true, ...}`.
- **First request is slow** — that's the model loading/downloading. Every
  request after is fast.
- **Jagged edges** — turn on Smooth edges, or swap `MODEL_NAME` in
  `server.py` (options: `isnet-general-use`, `u2net`, `birefnet-general`).
