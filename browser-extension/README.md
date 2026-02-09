# Kemono Downloader Browser Extension

A standalone browser extension for downloading content from Kemono and Coomer sites. This extension provides an alternative to the desktop application, allowing you to download posts directly from your browser.

## Core Features

- Download individual posts or multiple files from Kemono/Coomer pages
- Selective file downloads with checkbox selection
- ZIP compression for multiple files with progress tracking
- Individual downloads for large video files
- Automatic file organization and naming
- Compatible with both kemono.cr and coomer.st

The extension works independently from the desktop application and uses your browser's download manager.

## Installation

### Chrome/Edge/Firefox Installation

1. Download the extension package from the [GitHub Releases](https://github.com/VoxDroid/KemonoDownloader/releases)
2. Extract the ZIP file to a folder on your computer
3. Follow the browser-specific instructions below

#### For Chrome/Edge:
1. Open Chrome or Edge and type `chrome://extensions/` in the address bar
2. Enable 'Developer mode' in the top right corner
3. Click 'Load unpacked' and select the extracted extension folder
4. The extension should now appear in your extensions list

#### For Firefox:
1. Open Firefox and go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. **Select `manifest.json`** from the extracted folder — this project uses a single Manifest V2 file (`manifest.json`) for compatibility across browsers
4. If you see the error **"background.service_worker is currently disabled. Add background.scripts."**, make sure you explicitly selected `manifest.json` when loading; if the problem persists check the Browser Console (Ctrl+Shift+J) for messages and follow the Troubleshooting steps below
5. The extension will be temporarily installed (you'll need to reinstall after browser restart)

> 💡 Tip: This repository keeps a single `manifest.json` (Manifest V2) that works for Firefox and for local testing in Chrome/Edge. If you need a Manifest V3 build for Chrome Web Store, see the **Manifest & Browser compatibility** section below.

## How It Works

The extension automatically detects when you're on a Kemono or Coomer post page and provides a download interface. You can select which files to download and choose between ZIP compression or individual file downloads.

## Manifest & Browser compatibility 

- This repository now contains two manifest files for convenience:
  - `chrome_manifest.json` — Manifest V3 for Chrome/Edge (service worker background)
  - `firefox_manifest.json` — Manifest V2 for Firefox and local testing

- To load the extension in a browser, rename the appropriate file to `manifest.json` (or copy it as `manifest.json`) in the extracted folder before using the browser's developer add-on/extension UI.

PowerShell quick-copy examples:

```powershell
# For Chrome/Edge (Manifest V3)
Copy-Item browser-extension\chrome_manifest.json browser-extension\manifest.json

# For Firefox (Manifest V2)
Copy-Item browser-extension\firefox_manifest.json browser-extension\manifest.json
```

Notes:
- MV3 (`chrome_manifest.json`) moves host patterns into `host_permissions` and uses a `background.service_worker` entry.
- MV2 (`firefox_manifest.json`) retains `background.scripts` and the `applications.gecko` block required by some Firefox installs.

> Tip: After renaming, use your browser's developer extension page to load the unpacked folder. Remember to rename back or keep both manifests to switch browsers easily.

> 💡 Tip: Keep `manifest.json` as the canonical, developer-friendly (MV2) manifest while generating `manifest.chrome.json` only when you need MV3-specific testing or publishing.

**Download Options:**
- **Selective Downloads:** Choose specific files using checkboxes
- **ZIP Compression:** Download multiple files as a single compressed archive
- **Individual Files:** Download large files separately for better performance
- **Progress Tracking:** Monitor download progress in real-time

Files are downloaded directly to your browser's default download folder.

## Troubleshooting

- If you see an alert: **"Post data not loaded yet. Please try again."**, open the **Browser Console** (Ctrl+Shift+J) and look for messages that start with `Fetching:` or `Fetch error:` — copy any errors and share them for help.
- Common causes:
  - **URL parsing failed** due to a different page layout or URL structure; try reloading the post page and clicking the button again.
  - **HTTP 403 / Authentication required**: If you see `Fetch error: HTTP 403`, the post API may require that you are logged in or that cookies are sent. Ensure you are logged in on `kemono.cr`/`coomer.st`, then reload the page and try again.
  - **Site blocks JSON API requests**: Some sites (or CDNs) intentionally block JSON API requests from unknown clients; the extension will now attempt a background fetch with a special `Accept: text/css` header (which some sites accept) and try to parse the response from the page as a fallback.
  - **Servers returning JSON with non-JSON content-type**: Some servers return JSON data but set the `Content-Type` to a non-JSON value (e.g., `text/css`). The extension will now attempt to parse the response body as JSON even when the content-type is not `application/json`.
  - **CORS or network errors** may prevent the API fetch; the Browser Console will show HTTP status codes or CORS errors. The extension will retry the API fetch once including credentials when a 403 is detected, and then try a background fetch fallback if necessary.
  - **Site requires authentication**: ensure you're logged in if the post is gated.
- If the problem persists, run the extension in the Browser Console and paste the latest logs (look for `Fetching:`, `Retry response status:`, `Background fetch result:`, `Fetch error:`) so we can diagnose further.

User actions:
- When a download is in progress, the progress modal shows a **Cancel** button. Clicking it will stop further processing, attempt to cancel active downloads, and then reload the page to refresh the post state.

## Technical Details

- Uses JSZip for client-side ZIP creation
- Implements CORS handling through background script permissions
- Real-time progress tracking with message passing
- Automatic filename sanitization
- Memory-efficient blob URL management
- Background script handles all file fetching
- Uses a single Manifest V2 file (`manifest.json`) for cross-browser compatibility; see **Manifest & Browser compatibility** for generating an MV3 manifest when needed

## Permissions Required

- `downloads`: To save files to your computer
- `activeTab`: To access the current tab
- `storage`: For extension settings
- Host permissions for kemono.cr and coomer.st