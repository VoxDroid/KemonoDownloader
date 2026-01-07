// background.js

// Helper function to format bytes
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'download') {
    chrome.downloads.download({
      url: request.url,
      filename: request.filename,
      saveAs: false
    }, (downloadId) => {
      if (chrome.runtime.lastError) {
        console.error('Download failed:', chrome.runtime.lastError);
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ success: true, downloadId });
      }
    });
    return true; // Keep message channel open for async response
  } else if (request.action === 'fetch_api') {
    // Background fetch for API endpoints with custom headers/credentials (used for sites blocking JSON requests)
    (async () => {
      try {
        console.log('Background: Fetching API URL with headers:', request.url, request.headers || {});
        const response = await fetch(request.url, {
          method: 'GET',
          credentials: request.credentials || 'include',
          headers: request.headers || { 'Accept': request.accept || 'text/css' }
        });
        const status = response.status;
        const text = await response.text();
        sendResponse({ success: response.ok, status, data: text });
      } catch (error) {
        console.error('Background: Error fetching API URL:', error);
        sendResponse({ success: false, error: error.message });
      }
    })();
    return true; // Keep the message channel open
  } else if (request.action === 'cancel_downloads') {
    // Cancel active downloads by ID
    (async () => {
      try {
        const ids = request.downloadIds || [];
        console.log('Background: Cancelling downloads:', ids);
        for (const id of ids) {
          try {
            chrome.downloads.cancel(id, () => {
              if (chrome.runtime.lastError) {
                console.warn('Failed to cancel download', id, chrome.runtime.lastError);
              } else {
                console.log('Cancelled download', id);
              }
            });
          } catch (e) {
            console.error('Error cancelling download id', id, e);
          }
        }
        sendResponse({ success: true });
      } catch (error) {
        console.error('Background: Error cancelling downloads:', error);
        sendResponse({ success: false, error: error.message });
      }
    })();
    return true;
  } else if (request.action === 'fetch_file') {
    // Handle CORS fetch in background script
    (async () => {
      try {
        console.log('Background: Fetching file:', request.url);

        const fileLabel = (request.fileIndex && request.totalFiles) ? `${request.fileIndex}/${request.totalFiles}: ${request.filename || 'file'}` : (request.filename || 'file');

        // Send initial progress update with index/total when available
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'downloading',
          message: `Fetching: ${fileLabel}`,
          progress: 0
        });

        const response = await fetch(request.url, {
          method: 'GET',
          mode: 'cors',
          cache: 'no-cache',
          redirect: 'follow'
        });

        if (!response.ok) {
          console.error(`Background: Failed to fetch ${request.url}: ${response.status}`);
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'zip_progress',
            status: 'error',
            message: `Failed to fetch file: HTTP ${response.status}`
          });
          sendResponse({ success: false, error: `HTTP ${response.status}: ${response.statusText}` });
          return;
        }

        // Send progress update for response received
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'downloading',
          message: `Processing: ${fileLabel}`,
          progress: 25
        });

        const blob = await response.blob();
        console.log(`Background: Fetched file (${blob.size} bytes, type: ${blob.type})`);

        // Send progress update with file size
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'downloading',
          message: `Processing: ${fileLabel} (${formatBytes(blob.size)})`,
          progress: 50,
          fileSize: blob.size
        });

        // Validate that we got actual file data, not an error page
        if (blob.size === 0) {
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'zip_progress',
            status: 'error',
            message: 'Empty response received'
          });
          sendResponse({ success: false, error: 'Empty response received' });
          return;
        }

        // Check if the response looks like HTML (error page)
        if (blob.type === 'text/html' || blob.type === '') {
          const text = await blob.text();
          if (text.includes('<html') || text.includes('<HTML')) {
            chrome.tabs.sendMessage(sender.tab.id, {
              action: 'zip_progress',
              status: 'error',
              message: 'Server returned error page'
            });
            sendResponse({ success: false, error: 'Server returned HTML error page instead of file' });
            return;
          }
        }

        // Send progress update for validation complete
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'downloading',
          message: `Converting: ${fileLabel}`,
          progress: 75
        });

        // Convert blob to base64 string for reliable message passing
        console.log(`Converting blob to base64, blob size: ${blob.size}, type: ${blob.type}`);
        const arrayBuffer = await blob.arrayBuffer();
        console.log(`ArrayBuffer size: ${arrayBuffer.byteLength}`);

        if (arrayBuffer.byteLength === 0) {
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'zip_progress',
            status: 'error',
            message: `Empty file data: ${request.filename || 'file'}`
          });
          sendResponse({ success: false, error: 'Empty file data after conversion' });
          return;
        }

        // Check size limits based on file type
        const isVideo = request.filename && (request.filename.toLowerCase().endsWith('.mp4') || request.filename.toLowerCase().endsWith('.webm'));
        const maxSize = isVideo ? 4 * 1024 * 1024 * 1024 : 2 * 1024 * 1024 * 1024; // 4GB for videos, 2GB for others

        if (arrayBuffer.byteLength > maxSize) {
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'zip_progress',
            status: 'error',
            message: `File too large: ${request.filename || 'file'} (${formatBytes(arrayBuffer.byteLength)})`
          });
          sendResponse({ success: false, error: `File too large: ${formatBytes(arrayBuffer.byteLength)} (limit: ${formatBytes(maxSize)})` });
          return;
        }

        const uint8Array = new Uint8Array(arrayBuffer);
        console.log(`Uint8Array length: ${uint8Array.length}`);

        // Use more efficient conversion for large files
        let binaryString;
        if (uint8Array.length > 10 * 1024 * 1024) { // 10MB
          console.log('Using efficient string conversion for large file...');
          const chunks = [];
          const chunkSize = 100 * 1024; // 100KB chunks (reduced from 1MB)
          for (let i = 0; i < uint8Array.length; i += chunkSize) {
            const chunk = uint8Array.slice(i, i + chunkSize);
            chunks.push(String.fromCharCode.apply(null, chunk));
            // Allow processing to remain responsive
            if ((i / chunkSize) % 100 === 0) { // Every 10MB
              await new Promise(resolve => setTimeout(resolve, 0));
            }
          }
          binaryString = chunks.join('');
        } else {
          binaryString = Array.from(uint8Array, byte => String.fromCharCode(byte)).join('');
        }

        console.log(`Binary string length: ${binaryString.length}`);

        let base64Data;
        try {
          // Use chunked base64 encoding for very large binary strings
          if (binaryString.length > 50 * 1024 * 1024) { // 50MB binary string threshold
            console.log('Using chunked base64 encoding for very large file...');
            const base64Chunks = [];
            const chunkSize = 10 * 1024 * 1024; // 10MB binary chunks (reduced from 50MB)
            for (let i = 0; i < binaryString.length; i += chunkSize) {
              const chunk = binaryString.slice(i, i + chunkSize);
              base64Chunks.push(btoa(chunk));
              // Allow processing to remain responsive - more frequent breaks
              if ((i / chunkSize) % 5 === 0) { // Every 50MB processed
                await new Promise(resolve => setTimeout(resolve, 0));
              }
            }
            base64Data = base64Chunks.join('');
          } else {
            base64Data = btoa(binaryString);
          }
          console.log(`Base64 data length: ${base64Data.length}`);
        } catch (btoaError) {
          console.error('btoa encoding failed:', btoaError);
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'zip_progress',
            status: 'error',
            message: `Encoding failed: ${request.filename || 'file'}`
          });
          sendResponse({ success: false, error: 'Base64 encoding failed' });
          return;
        }

        // Send final progress update
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'downloading',
          message: `Ready: ${fileLabel}`,
          progress: 100
        });

        sendResponse({ success: true, data: base64Data, type: blob.type });
      } catch (error) {
        console.error('Background: Error fetching file:', error);
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'zip_progress',
          status: 'error',
          message: `Error: ${error.message}`
        });
        sendResponse({ success: false, error: error.message });
      }
    })();
    return true; // Keep message channel open for async response
  }
});