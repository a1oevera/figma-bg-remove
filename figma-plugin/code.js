// Main plugin thread. Talks to the canvas; the UI iframe (ui.html) talks to the server.
// Flow: selection -> exportAsync PNG bytes -> UI -> fetch server -> bytes back -> new image on canvas.

figma.showUI(__html__, { width: 300, height: 260 });

// Send the saved server URL to the UI on startup (clientStorage only works here).
figma.clientStorage.getAsync("serverUrl").then(function (saved) {
  figma.ui.postMessage({ type: "init", serverUrl: saved || "http://localhost:5001" });
});

figma.ui.onmessage = function (msg) {
  if (msg.type === "save-url") {
    figma.clientStorage.setAsync("serverUrl", msg.serverUrl);
    return;
  }

  if (msg.type === "export-selection") {
    var sel = figma.currentPage.selection;
    if (sel.length !== 1) {
      figma.ui.postMessage({ type: "error", message: "Select exactly one layer first." });
      return;
    }
    var node = sel[0];
    node
      .exportAsync({ format: "PNG", constraint: { type: "SCALE", value: 2 } })
      .then(function (bytes) {
        figma.ui.postMessage({
          type: "image-bytes",
          bytes: bytes,
          width: node.width,
          height: node.height,
          x: node.x,
          y: node.y,
          name: node.name
        });
      })
      .catch(function (err) {
        figma.ui.postMessage({ type: "error", message: "Export failed: " + err });
      });
    return;
  }

  if (msg.type === "processed-bytes") {
    // Place the cut-out next to the original instead of replacing it,
    // so a bad result never destroys the source layer.
    var image = figma.createImage(new Uint8Array(msg.bytes));
    var rect = figma.createRectangle();
    rect.resize(msg.width, msg.height);
    rect.x = msg.x + msg.width + 40;
    rect.y = msg.y;
    rect.name = msg.name + " (no bg)";
    rect.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: image.hash }];
    figma.currentPage.selection = [rect];
    figma.viewport.scrollAndZoomIntoView([rect]);
    figma.notify("Background removed ✂️");
    figma.ui.postMessage({ type: "done" });
    return;
  }
};
