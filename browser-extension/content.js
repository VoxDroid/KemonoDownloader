// content.js
(function() {
  'use strict';

  // Add JetBrains Mono font from Google Fonts
  const fontLink = document.createElement('link');
  fontLink.href = 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap';
  fontLink.rel = 'stylesheet';
  document.head.appendChild(fontLink);

  console.log('Kemono Downloader extension loaded');

  // Check page type
  const url = window.location.href;
  console.log('Current URL:', url);
  let isPostPage = url.includes('/post/');
  let isKemonoDomain = url.includes('kemono.cr') || url.includes('coomer.st');

  console.log('Page type:', isPostPage ? 'Post page' : 'Other page');
  console.log('Kemono domain:', isKemonoDomain);

  let postData = null;
  let files = [];
  let service, creator_id, post_id, domain, api_base;
  let currentButton = null;

  // Utility function to truncate long filenames for display
  function truncateFilename(filename, maxLength = 30) {
    if (filename.length <= maxLength) {
      return filename;
    }
    
    const extension = filename.split('.').pop();
    const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
    
    if (nameWithoutExt.length <= maxLength - 3 - extension.length - 1) {
      return filename;
    }
    
    const truncatedName = nameWithoutExt.substring(0, maxLength - 3 - extension.length - 1);
    return truncatedName + '...' + extension;
  }

  // Parse URL for post pages
  if (isPostPage) {
    const parts = url.split('/').filter(p => p);
    console.log('URL parts:', parts);
    if (parts.length < 7) {
      console.log('Not enough parts for post parsing');
    } else {
      service = parts[parts.length - 5];
      creator_id = parts[parts.length - 3];
      post_id = parts[parts.length - 1];

      console.log('Parsed:', { service, creator_id, post_id });

      domain = url.includes('coomer.st') ? 'coomer.st' : 'kemono.cr';
      api_base = `https://${domain}/api/v1`;
    }
  }

  // Create modal for non-post pages
  function createInfoModal() {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(10, 14, 23, 0.8)';
    modal.style.zIndex = '10001';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';

    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = '#1a1f2e';
    modalContent.style.padding = '24px';
    modalContent.style.borderRadius = '12px';
    modalContent.style.maxWidth = '400px';
    modalContent.style.width = '90%';
    modalContent.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
    modalContent.style.border = '1px solid #374151';
    modalContent.style.color = '#e2e8f0';
    modalContent.style.textAlign = 'center';

    const title = document.createElement('h2');
    title.textContent = 'Kemono Downloader';
    title.style.marginTop = '0';
    title.style.marginBottom = '16px';
    title.style.color = '#ffffff';
    title.style.fontSize = '24px';
    title.style.fontWeight = '600';
    modalContent.appendChild(title);

    const icon = document.createElement('div');
    const iconUrl = 'https://raw.githubusercontent.com/VoxDroid/KemonoDownloader/refs/heads/main/assets/icons/KemonoDownloader-48.png';
    icon.innerHTML = '<img src="' + iconUrl + '" alt="Kemono Downloader" style="width: 64px; height: 64px;" onerror="console.error(\'Icon failed to load from CDN:\', \'' + iconUrl + '\')">';
    icon.style.marginBottom = '16px';
    modalContent.appendChild(icon);

    const message = document.createElement('p');
    if (isKemonoDomain) {
      message.textContent = 'Navigate to a post page to start downloading! Look for posts with files or attachments.';
    } else {
      message.textContent = 'This extension works on Kemono and Coomer sites. Visit kemono.cr or coomer.st to use the downloader.';
    }
    message.style.marginBottom = '24px';
    message.style.color = '#94a3b8';
    message.style.fontSize = '16px';
    message.style.lineHeight = '1.5';
    modalContent.appendChild(message);

    const closeButton = document.createElement('button');
    closeButton.textContent = 'Got it!';
    closeButton.style.padding = '8px 16px';
    closeButton.style.backgroundColor = '#6d28d9';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '6px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontSize = '14px';
    closeButton.style.fontWeight = '500';
    closeButton.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    closeButton.style.transition = 'all 0.3s ease';
    closeButton.onclick = () => modal.remove();
    closeButton.onmouseover = () => closeButton.style.backgroundColor = '#7c3aed';
    closeButton.onmouseout = () => closeButton.style.backgroundColor = '#6d28d9';
    modalContent.appendChild(closeButton);

    modal.appendChild(modalContent);

    // Close modal when clicking outside
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };

    return modal;
  }

  // Fetch post data on load (only for post pages)
  async function fetchPostData() {
    if (!isPostPage) return false;

    // Ensure we have parsed URL pieces; if not, attempt fallbacks
    if (!service || !creator_id || !post_id || !domain || !api_base) {
      console.warn('Missing parsed URL parts, attempting fallback parsing');
      const parts = window.location.href.split('/').filter(p => p);
      // Attempt to find 'post' segment and extract surrounding pieces
      const postIndex = parts.findIndex(p => p === 'post');
      if (postIndex !== -1 && parts.length > postIndex + 1) {
        post_id = parts[postIndex + 1];
        // Try to get creator id and service relative to 'post' position
        if (postIndex >= 2) {
          creator_id = parts[postIndex - 1];
        }
        if (postIndex >= 4) {
          service = parts[postIndex - 3];
        }
        domain = window.location.href.includes('coomer.st') ? 'coomer.st' : 'kemono.cr';
        api_base = `https://${domain}/api/v1`;
        console.log('Fallback parsed:', { service, creator_id, post_id, domain });
      }

      // DOM-based fallback: try to find canonical URL or meta tags
      if (!post_id) {
        const canonical = document.querySelector('link[rel="canonical"]');
        if (canonical && canonical.href) {
          const m = canonical.href.match(/\/post\/([^\/\?#]+)/);
          if (m) post_id = m[1];
        }
      }

      if (!creator_id) {
        // Some pages may include creator id in a data attribute or in the page markup
        const creatorElem = document.querySelector('[data-creator-id], .creator-id, .user-id');
        if (creatorElem) {
          creator_id = creatorElem.getAttribute('data-creator-id') || creatorElem.textContent.trim();
          console.log('Found creator id from DOM:', creator_id);
        }
      }

      if (!service) {
        // Guess service from URL path segments
        service = (window.location.href.includes('/fanbox/')) ? 'fanbox' : service;
      }

      if (!post_id || !creator_id || !service) {
        console.error('Unable to determine post identifiers:', { service, creator_id, post_id });
        return false;
      }
    }

    try {
      const api_url = `${api_base}/${service}/user/${creator_id}/post/${post_id}`;
      console.log('Fetching:', api_url);

      // Initial fetch
      let response = await fetch(api_url);

      // If we get a 403, retry including credentials (cookies) which may be required for gated/private posts
      if (!response.ok) {
        if (response.status === 403) {
          console.warn('Fetch returned 403 — retrying with credentials included');
          try {
            response = await fetch(api_url, { credentials: 'include' });
            console.log('Retry response status:', response.status);
          } catch (credErr) {
            console.error('Retry with credentials failed:', credErr);
          }
        }
      }

      if (!response.ok) {
        // If 403, attempt a background fetch with special header (site suggests using `Accept: text/css`)
        if (response.status === 403) {
          console.warn('Fetch returned 403 — attempting background fetch with Accept: text/css');
          try {
            const bgResp = await new Promise(resolve => chrome.runtime.sendMessage({ action: 'fetch_api', url: api_url, accept: 'text/css' }, resolve));
            console.log('Background fetch result:', bgResp);
            if (bgResp && bgResp.success && bgResp.status === 200 && bgResp.data) {
              // Try parse JSON first
              let parsed;
              try {
                parsed = JSON.parse(bgResp.data);
              } catch (err) {
                // Try common in-page JSON containers
                const scriptMatch = bgResp.data.match(/<script[^>]*id=["']__NEXT_DATA__|__INITIAL_STATE__[^>]*>([\s\S]*?)<\/script>/i);
                if (scriptMatch && scriptMatch[1]) {
                  try {
                    parsed = JSON.parse(scriptMatch[1]);
                  } catch (e) {
                    // fallthrough
                  }
                }

                if (!parsed) {
                  // Try to find a JSON object that contains "post"
                  const postMatch = bgResp.data.match(/"post"\s*:\s*(\{[\s\S]*?\})/);
                  if (postMatch && postMatch[1]) {
                    try {
                      parsed = { post: JSON.parse(postMatch[1]) };
                    } catch (e) {
                      // last resort: try extracting a larger JSON block
                      const braceMatch = bgResp.data.match(/(\{[\s\S]*\})/);
                      if (braceMatch && braceMatch[1]) {
                        try { parsed = JSON.parse(braceMatch[1]); } catch (e) { parsed = null; }
                      }
                    }
                  }
                }
              }

              if (parsed) {
                console.log('Parsed data from background fetch:', parsed);
                postData = parsed.post || parsed;
              } else {
                throw new Error('Background fetch returned non-JSON content that could not be parsed');
              }
            } else {
              throw new Error(`Background fetch failed: ${bgResp && (bgResp.status || bgResp.error) ? (bgResp.status || bgResp.error) : 'no response'}`);
            }
          } catch (bgError) {
            console.error('Background fetch error:', bgError);
            let bodyText = '';
            try { bodyText = await response.text(); } catch (e) {}
            throw new Error(`Failed to fetch post data: HTTP ${response.status}${bodyText ? ' - ' + bodyText.substring(0,200) : ''} (background fetch also failed)`);
          }
        } else {
          // Try to capture a helpful response body for debugging
          let bodyText = '';
          try {
            bodyText = await response.text();
          } catch (e) {
            // ignore
          }
          throw new Error(`Failed to fetch post data: HTTP ${response.status}${bodyText ? ' - ' + bodyText.substring(0, 200) : ''}`);
        }
      }

      // If postData was set by the background-fetch branch, skip JSON parsing; otherwise parse normally
      let data;
      if (!postData) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
          data = await response.json();
        } else {
          // Some CDNs or sites return JSON payloads with incorrect content-type (e.g., text/css).
          // Try reading the body as text and parse it as JSON as a best-effort fallback.
          const text = await response.text();
          try {
            data = JSON.parse(text);
            console.warn('Parsed JSON from non-JSON content-type:', contentType);
          } catch (err) {
            console.warn('Unexpected content-type from API and JSON parse failed:', contentType);
            throw new Error('Unexpected response from API: ' + (text ? text.substring(0, 200) : '(no body)'));
          }
        }

        console.log('API response:', data);
        postData = data.post || data;
      } else {
        console.log('Using postData retrieved from background fetch');
      }

      // Build files list
      files = [];

      // Main file
      if (postData.file && postData.file.path) {
        const file_url = `https://${domain}${postData.file.path}`;
        const file_name = postData.file.name || 'file';
        files.push({ url: file_url, filename: file_name, type: 'file', checked: true });
      }

      // Attachments
      if (postData.attachments) {
        postData.attachments.forEach((att, index) => {
          if (att.path) {
            const att_url = `https://${domain}${att.path}`;
            const att_name = att.name || `attachment_${index}`;
            files.push({ url: att_url, filename: att_name, type: 'attachment', checked: true });
          }
        });
      }

      console.log('Files available:', files);
      return true;
    } catch (error) {
      console.error('Fetch error:', error);
      return false;
    }
  }

  // Create modal with professional design
  function createModal() {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(10, 14, 23, 0.8)';
    modal.style.zIndex = '10001';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';

    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = '#1a1f2e';
    modalContent.style.padding = '24px';
    modalContent.style.borderRadius = '12px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '90%';
    modalContent.style.maxHeight = '80vh';
    modalContent.style.overflowY = 'auto';
    modalContent.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
    modalContent.style.border = '1px solid #374151';
    modalContent.style.color = '#e2e8f0';

    const title = document.createElement('h2');
    title.textContent = 'Download Post';
    title.style.marginTop = '0';
    title.style.marginBottom = '8px';
    title.style.color = '#ffffff';
    title.style.fontSize = '24px';
    title.style.fontWeight = '600';
    modalContent.appendChild(title);

    const subtitle = document.createElement('p');
    subtitle.textContent = postData.title || 'Untitled Post';
    subtitle.style.marginBottom = '24px';
    subtitle.style.color = '#94a3b8';
    subtitle.style.fontSize = '14px';
    modalContent.appendChild(subtitle);

    // Files section
    const filesSection = document.createElement('div');
    filesSection.style.marginBottom = '24px';

    const filesHeader = document.createElement('div');
    filesHeader.style.display = 'flex';
    filesHeader.style.justifyContent = 'space-between';
    filesHeader.style.alignItems = 'center';
    filesHeader.style.marginBottom = '12px';

    const filesTitle = document.createElement('h3');
    filesTitle.textContent = 'Files to Download';
    filesTitle.style.margin = '0';
    filesTitle.style.color = '#ffffff';
    filesTitle.style.fontSize = '16px';
    filesTitle.style.fontWeight = '600';

    const selectButtons = document.createElement('div');
    const selectAllBtn = document.createElement('button');
    selectAllBtn.textContent = 'Select All';
    selectAllBtn.style.padding = '6px 12px';
    selectAllBtn.style.marginRight = '8px';
    selectAllBtn.style.backgroundColor = '#6d28d9';
    selectAllBtn.style.color = 'white';
    selectAllBtn.style.border = 'none';
    selectAllBtn.style.borderRadius = '6px';
    selectAllBtn.style.cursor = 'pointer';
    selectAllBtn.style.fontSize = '12px';
    selectAllBtn.style.fontWeight = '500';
    selectAllBtn.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    selectAllBtn.style.transition = 'all 0.3s ease';
    selectAllBtn.onmouseover = () => selectAllBtn.style.backgroundColor = '#7c3aed';
    selectAllBtn.onmouseout = () => selectAllBtn.style.backgroundColor = '#6d28d9';
    selectAllBtn.onclick = () => {
      files.forEach((file, index) => {
        file.checked = true;
        document.getElementById(`file_${index}`).checked = true;
      });
    };

    const selectNoneBtn = document.createElement('button');
    selectNoneBtn.textContent = 'Select None';
    selectNoneBtn.style.padding = '6px 12px';
    selectNoneBtn.style.backgroundColor = '#ef4444';
    selectNoneBtn.style.color = 'white';
    selectNoneBtn.style.border = 'none';
    selectNoneBtn.style.borderRadius = '6px';
    selectNoneBtn.style.cursor = 'pointer';
    selectNoneBtn.style.fontSize = '12px';
    selectNoneBtn.style.fontWeight = '500';
    selectNoneBtn.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    selectNoneBtn.style.transition = 'all 0.3s ease';
    selectNoneBtn.onmouseover = () => selectNoneBtn.style.backgroundColor = '#dc2626';
    selectNoneBtn.onmouseout = () => selectNoneBtn.style.backgroundColor = '#ef4444';
    selectNoneBtn.onclick = () => {
      files.forEach((file, index) => {
        file.checked = false;
        document.getElementById(`file_${index}`).checked = false;
      });
    };

    selectButtons.appendChild(selectAllBtn);
    selectButtons.appendChild(selectNoneBtn);
    filesHeader.appendChild(filesTitle);
    filesHeader.appendChild(selectButtons);
    filesSection.appendChild(filesHeader);

    const filesDiv = document.createElement('div');
    filesDiv.style.maxHeight = '200px';
    filesDiv.style.overflowY = 'auto';
    filesDiv.style.border = '1px solid #374151';
    filesDiv.style.borderRadius = '8px';
    filesDiv.style.padding = '12px';
    filesDiv.style.backgroundColor = '#111827';

    if (files.length === 0) {
      const noFiles = document.createElement('p');
      noFiles.textContent = 'No files available for this post.';
      noFiles.style.color = '#94a3b8';
      noFiles.style.textAlign = 'center';
      noFiles.style.margin = '0';
      noFiles.style.fontSize = '14px';
      filesDiv.appendChild(noFiles);
    } else {
      files.forEach((file, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.style.display = 'flex';
        fileDiv.style.alignItems = 'center';
        fileDiv.style.marginBottom = '8px';
        fileDiv.style.padding = '8px';
        fileDiv.style.borderRadius = '6px';
        fileDiv.style.backgroundColor = index % 2 === 0 ? '#1f2937' : '#111827';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = file.checked;
        checkbox.id = `file_${index}`;
        checkbox.onchange = () => file.checked = checkbox.checked;
        checkbox.style.marginRight = '12px';
        checkbox.style.accentColor = '#6d28d9';

        const label = document.createElement('label');
        label.htmlFor = `file_${index}`;
        label.textContent = truncateFilename(file.filename);
        label.title = file.filename; // Show full filename on hover
        label.style.cursor = 'pointer';
        label.style.flexGrow = '1';
        label.style.fontSize = '14px';
        label.style.color = '#e2e8f0';

        const fileType = document.createElement('span');
        fileType.textContent = file.type === 'file' ? 'File' : 'Attachment';
        fileType.style.marginLeft = '8px';
        fileType.style.fontSize = '12px';
        fileType.style.color = '#94a3b8';
        fileType.style.backgroundColor = file.type === 'file' ? '#dbeafe' : '#fef3c7';
        fileType.style.padding = '2px 6px';
        fileType.style.borderRadius = '4px';

        fileDiv.appendChild(checkbox);
        fileDiv.appendChild(label);
        fileDiv.appendChild(fileType);
        filesDiv.appendChild(fileDiv);
      });
    }

    filesSection.appendChild(filesDiv);
    modalContent.appendChild(filesSection);

    // Options section
    const optionsSection = document.createElement('div');
    optionsSection.style.marginBottom = '24px';

    const optionsTitle = document.createElement('h3');
    optionsTitle.textContent = 'Options';
    optionsTitle.style.marginBottom = '16px';
    optionsTitle.style.color = '#ffffff';
    optionsTitle.style.fontSize = '16px';
    optionsTitle.style.fontWeight = '600';
    optionsSection.appendChild(optionsTitle);

    const optionsGrid = document.createElement('div');
    optionsGrid.style.display = 'grid';
    optionsGrid.style.gridTemplateColumns = '1fr 1fr';
    optionsGrid.style.gap = '12px';

    // Text content option
    const textDiv = document.createElement('div');
    textDiv.style.display = 'flex';
    textDiv.style.alignItems = 'center';

    const textCheckbox = document.createElement('input');
    textCheckbox.type = 'checkbox';
    textCheckbox.id = 'download_text';
    textCheckbox.checked = !!postData.content;
    textCheckbox.disabled = !postData.content;
    textCheckbox.style.marginRight = '8px';
    textCheckbox.style.accentColor = '#6d28d9';

    const textLabel = document.createElement('label');
    textLabel.htmlFor = 'download_text';
    textLabel.textContent = 'Include text content';
    textLabel.style.cursor = 'pointer';
    textLabel.style.fontSize = '14px';
    textLabel.style.color = '#e2e8f0';

    textDiv.appendChild(textCheckbox);
    textDiv.appendChild(textLabel);
    optionsGrid.appendChild(textDiv);

    // ZIP option
    const zipDiv = document.createElement('div');
    zipDiv.style.display = 'flex';
    zipDiv.style.alignItems = 'center';

    const zipCheckbox = document.createElement('input');
    zipCheckbox.type = 'checkbox';
    zipCheckbox.id = 'download_zip';
    zipCheckbox.checked = true;
    zipCheckbox.style.marginRight = '8px';
    zipCheckbox.style.accentColor = '#6d28d9';

    const zipLabel = document.createElement('label');
    zipLabel.htmlFor = 'download_zip';
    zipLabel.textContent = 'Download as ZIP (non video files)';
    zipLabel.style.cursor = 'pointer';
    zipLabel.style.fontSize = '14px';
    zipLabel.style.color = '#e2e8f0';

    zipDiv.appendChild(zipCheckbox);
    zipDiv.appendChild(zipLabel);
    optionsGrid.appendChild(zipDiv);

    // Auto-rename option
    const renameDiv = document.createElement('div');
    renameDiv.style.display = 'flex';
    renameDiv.style.alignItems = 'center';

    const renameCheckbox = document.createElement('input');
    renameCheckbox.type = 'checkbox';
    renameCheckbox.id = 'auto_rename';
    renameCheckbox.checked = true;
    renameCheckbox.style.marginRight = '8px';
    renameCheckbox.style.accentColor = '#6d28d9';

    const renameLabel = document.createElement('label');
    renameLabel.htmlFor = 'auto_rename';
    renameLabel.textContent = 'Auto-rename files';
    renameLabel.style.cursor = 'pointer';
    renameLabel.style.fontSize = '14px';
    renameLabel.style.color = '#e2e8f0';

    renameDiv.appendChild(renameCheckbox);
    renameDiv.appendChild(renameLabel);
    optionsGrid.appendChild(renameDiv);

    optionsSection.appendChild(optionsGrid);
    modalContent.appendChild(optionsSection);

    // Buttons
    const buttonsDiv = document.createElement('div');
    buttonsDiv.style.display = 'flex';
    buttonsDiv.style.justifyContent = 'flex-end';
    buttonsDiv.style.gap = '12px';
    buttonsDiv.style.marginTop = '24px';

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.style.padding = '8px 16px';
    cancelBtn.style.backgroundColor = '#374151';
    cancelBtn.style.color = '#e2e8f0';
    cancelBtn.style.border = '1px solid #4b5563';
    cancelBtn.style.borderRadius = '6px';
    cancelBtn.style.cursor = 'pointer';
    cancelBtn.style.fontSize = '14px';
    cancelBtn.style.fontWeight = '500';
    cancelBtn.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    cancelBtn.style.transition = 'all 0.3s ease';
    cancelBtn.onmouseover = () => {
      cancelBtn.style.backgroundColor = '#4b5563';
    };
    cancelBtn.onmouseout = () => {
      cancelBtn.style.backgroundColor = '#374151';
    };
    cancelBtn.onclick = () => modal.remove();

    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = 'Download';
    downloadBtn.style.padding = '8px 16px';
    downloadBtn.style.backgroundColor = '#6d28d9';
    downloadBtn.style.color = 'white';
    downloadBtn.style.border = 'none';
    downloadBtn.style.borderRadius = '6px';
    downloadBtn.style.cursor = 'pointer';
    downloadBtn.style.fontSize = '14px';
    downloadBtn.style.fontWeight = '500';
    downloadBtn.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    downloadBtn.style.transition = 'all 0.3s ease';
    downloadBtn.onmouseover = () => downloadBtn.style.backgroundColor = '#7c3aed';
    downloadBtn.onmouseout = () => downloadBtn.style.backgroundColor = '#6d28d9';
    downloadBtn.onclick = async () => {
      const selectedFiles = files.filter(f => f.checked);
      const downloadText = textCheckbox.checked && postData.content;
      const useZip = zipCheckbox.checked;
      const autoRename = renameCheckbox.checked;

      if (selectedFiles.length === 0 && !downloadText) {
        alert('Please select at least one file or text to download');
        return;
      }

      downloadBtn.disabled = true;
      downloadBtn.textContent = 'Processing...';

      try {
        if (useZip) {
          // Show progress modal for ZIP creation
          createProgressModal();
          updateProgress({ status: 'initializing', message: 'Starting ZIP creation...', progress: 0 });

          await downloadAsZip(selectedFiles, downloadText, autoRename);
        } else {
          // Start individual downloads and show progress modal with cancel option
          downloadIndividual(selectedFiles, downloadText, autoRename);
          createProgressModal();
          updateProgress({ status: 'processing', message: 'Individual downloads started... Use Cancel to stop and refresh.', progress: 5 });
        }
        // Close the selection modal (progress modal will remain)
        modal.remove();
      } catch (error) {
        console.error('Download error:', error);
        alert('Download failed: ' + error.message);
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
      }
    };

    buttonsDiv.appendChild(cancelBtn);
    buttonsDiv.appendChild(downloadBtn);
    modalContent.appendChild(buttonsDiv);

    // Branding footer
    const footer = document.createElement('div');
    footer.style.marginTop = '20px';
    footer.style.paddingTop = '16px';
    footer.style.borderTop = '1px solid #e5e7eb';
    footer.style.textAlign = 'center';
    footer.style.fontSize = '12px';
    footer.style.color = '#9ca3af';

    const brandingText = document.createElement('div');
    brandingText.innerHTML = 'Kemono Downloader v1.0 | <a href="https://github.com/VoxDroid" target="_blank" style="color: #3b82f6; text-decoration: none;">@VoxDroid</a>';
    brandingText.style.marginBottom = '4px';
    footer.appendChild(brandingText);

    const poweredBy = document.createElement('div');
    poweredBy.textContent = 'Kemono Downloader Extension powered by VoxDroid';
    poweredBy.style.fontSize = '11px';
    poweredBy.style.color = '#d1d5db';
    footer.appendChild(poweredBy);

    modalContent.appendChild(footer);

    modal.appendChild(modalContent);

    // Close on click outside
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };

    return modal;
  }

  // Download as ZIP
  async function downloadAsZip(selectedFiles, downloadText, autoRename) {
    console.log('Creating ZIP with', selectedFiles.length, 'files');

    // Show progress
    updateProgress({ status: 'preparing', message: `Preparing to download ${selectedFiles.length} files...`, progress: 5 });

    try {
      const zip = new JSZip();



      // Add files to ZIP
      let processedFiles = 0;
      let totalBytesDownloaded = 0;
      let videoDownloads = [];
      let videoDownloadPromises = [];
      const totalFiles = selectedFiles.length;
      const baseProgress = downloadText ? 15 : 10;
      const progressRange = 80 - baseProgress; // Leave room for final ZIP processing

      for (const file of selectedFiles) {
        if (downloadCancelled) {
          console.log('Download cancelled by user, aborting ZIP creation');
          updateProgress({ status: 'error', message: 'Download cancelled by user' });
          return false;
        }
        try {
          console.log('Processing file:', file.url);

          // For very large files (MP4 and other video formats), download individually without processing
          const isVideoFile = file.filename.toLowerCase().endsWith('.mp4') ||
                             file.filename.toLowerCase().endsWith('.webm') ||
                             file.filename.toLowerCase().endsWith('.avi') ||
                             file.filename.toLowerCase().endsWith('.mkv') ||
                             file.filename.toLowerCase().endsWith('.mov');

          if (isVideoFile) {
            console.log(`Video file detected: ${file.filename}, downloading individually...`);

            // Update video status
            if (window.videoStatusElement) {
              window.videoStatusElement.textContent = `Downloading: ${file.filename}`;
              window.videoStatusElement.style.color = '#0369a1';
            }

            const fileName = autoRename ? `${sanitizeFilename(postData.title || 'post')}_${file.filename}` : file.filename;

            // Track video download
            const videoDownloadPromise = new Promise((resolve, reject) => {
              chrome.runtime.sendMessage({
                action: 'download',
                url: file.url,
                filename: fileName
              }, (downloadResponse) => {
                if (chrome.runtime.lastError) {
                  console.error('Individual download failed:', chrome.runtime.lastError);
                  if (window.videoStatusElement) {
                    window.videoStatusElement.textContent = `Failed: ${file.filename}`;
                    window.videoStatusElement.style.color = '#dc2626';
                  }
                  reject(new Error(`Failed to download ${file.filename}: ${chrome.runtime.lastError.message}`));
                } else {
                  console.log(`Individual download started for video file: ${file.filename}`);
                  // Save download id for potential cancellation
                  if (downloadResponse && downloadResponse.downloadId) {
                    activeDownloadIds.push(downloadResponse.downloadId);
                  }
                  if (window.videoStatusElement) {
                    window.videoStatusElement.textContent = `Completed: ${file.filename}`;
                    window.videoStatusElement.style.color = '#059669';
                  }
                  resolve();
                }
              });
            });

            videoDownloadPromises.push(videoDownloadPromise);
            videoDownloads.push(file.filename);

            // Update progress for video file download
            updateProgress({
              status: 'processing',
              message: `Downloading video: ${file.filename} (individual download)`,
              progress: Math.round(baseProgress + ((processedFiles + 1) / totalFiles) * progressRange)
            });
            processedFiles++;
            continue; // Skip ZIP processing for this file
          }

          updateProgress({
            status: 'downloading',
            message: `Downloading ${processedFiles + 1}/${totalFiles}: ${file.filename}`,
            progress: Math.round(baseProgress + (processedFiles / totalFiles) * progressRange)
          });
          const response = await new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({
              action: 'fetch_file',
              url: file.url,
              filename: file.filename,
              fileIndex: processedFiles + 1,
              totalFiles: totalFiles
            }, (response) => {
              if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message));
              } else if (response && response.error) {
                reject(new Error(response.error));
              } else {
                resolve(response);
              }
            });
          });

          if (!response || !response.success) {
            console.error(`Failed to fetch ${file.filename}`);
            updateProgress({
              status: 'error',
              message: `Failed to download: ${file.filename}`
            });
            continue;
          }

          // Validate response data
          if (!response.data || typeof response.data !== 'string') {
            console.error(`Invalid response data for ${file.filename}:`, response);
            updateProgress({
              status: 'error',
              message: `Invalid file data: ${file.filename}`
            });
            continue;
          }

          // Debug: check what we received
          console.log('Response received:', response);
          console.log('Response.data type:', typeof response.data);
          console.log('Response.data constructor:', response.data?.constructor?.name);

          // Decode base64 string back to Uint8Array
          let binaryString, uint8Array, data;
          try {
            console.log(`Starting base64 decode for ${file.filename}, data length: ${response.data.length}`);

            // Use chunked base64 decoding for very large files
            if (response.data.length > 50 * 1024 * 1024) { // 50MB base64 data threshold (reduced from 100MB)
              console.log('Using chunked base64 decoding for very large file...');
              const base64Chunks = [];
              const chunkSize = 10 * 1024 * 1024; // 10MB base64 chunks (reduced from 50MB)
              for (let i = 0; i < response.data.length; i += chunkSize) {
                const chunk = response.data.slice(i, i + chunkSize);
                base64Chunks.push(atob(chunk));
                // Allow UI to remain responsive - more frequent breaks
                if ((i / chunkSize) % 5 === 0) { // Every 50MB processed
                  await new Promise(resolve => setTimeout(resolve, 0));
                }
              }
              binaryString = base64Chunks.join('');
            } else {
              binaryString = atob(response.data);
            }

            console.log(`Decoded binaryString length: ${binaryString.length}`);

            if (binaryString.length === 0) {
              throw new Error('Empty decoded data');
            }
            // Increase limit for video files
            const maxSize = file.filename.toLowerCase().endsWith('.mp4') ? 4 * 1024 * 1024 * 1024 : 2 * 1024 * 1024 * 1024; // 4GB for MP4, 2GB for others
            if (binaryString.length > maxSize) {
              throw new Error(`Decoded data too large: ${formatBytes(binaryString.length)} (limit: ${formatBytes(maxSize)})`);
            }

            console.log(`Creating Uint8Array with length: ${binaryString.length}`);
            // Check if length is valid for Uint8Array
            if (binaryString.length < 0 || !Number.isFinite(binaryString.length)) {
              throw new Error(`Invalid array length: ${binaryString.length}`);
            }

            uint8Array = new Uint8Array(binaryString.length);
            console.log(`Uint8Array created successfully, filling data...`);

            // Use chunked processing for large files to avoid call stack issues
            if (binaryString.length > 50 * 1024 * 1024) { // 50MB threshold for chunked processing
              console.log('Using chunked conversion for very large file...');
              const chunkSize = 100 * 1024; // 100KB chunks (reduced from 1MB)
              for (let chunkStart = 0; chunkStart < binaryString.length; chunkStart += chunkSize) {
                const chunkEnd = Math.min(chunkStart + chunkSize, binaryString.length);
                const chunk = binaryString.slice(chunkStart, chunkEnd);
                for (let i = 0; i < chunk.length; i++) {
                  uint8Array[chunkStart + i] = chunk.charCodeAt(i) & 0xFF;
                }
                // Allow UI to remain responsive during large file processing - more frequent breaks
                if ((chunkStart / chunkSize) % 100 === 0) { // Every 100 chunks (10MB)
                  await new Promise(resolve => setTimeout(resolve, 0));
                }
              }
            } else if (binaryString.length > 10 * 1024 * 1024) { // 10MB
              console.log('Using efficient conversion for large file...');
              for (let i = 0; i < binaryString.length; i++) {
                uint8Array[i] = binaryString.charCodeAt(i) & 0xFF; // Ensure byte values
              }
            } else {
              for (let i = 0; i < binaryString.length; i++) {
                uint8Array[i] = binaryString.charCodeAt(i);
              }
            }

            data = uint8Array;
            console.log(`Data conversion completed, final data length: ${data.length}`);
          } catch (decodeError) {
            console.error(`Base64 decode error for ${file.filename}:`, decodeError);
            console.error(`Error details - response.data type: ${typeof response.data}, length: ${response.data ? response.data.length : 'undefined'}`);
            console.error(`Binary string length: ${binaryString ? binaryString.length : 'undefined'}`);
            updateProgress({
              status: 'error',
              message: `Failed to decode file data: ${file.filename} (${decodeError.message})`
            });
            continue;
          }

          console.log(`Fetched ${file.filename} (${data.length} bytes, type: ${response.type})`);

          // Track downloaded bytes
          totalBytesDownloaded += data.length;

          // Validate data
          if (!data || data.length === 0) {
            console.error(`Empty data for ${file.filename}`);
            updateProgress({
              status: 'error',
              message: `Empty file: ${file.filename}`
            });
            continue;
          }

          const fileName = autoRename ? `${sanitizeFilename(postData.title || 'post')}_${file.filename}` : file.filename;
          const path = fileName;

          // For very large files, download individually instead of adding to ZIP
          const maxZipFileSize = 100 * 1024 * 1024; // 100MB max per file in ZIP
          console.log(`Checking file size: ${file.filename}, data.length: ${data.length}, data type: ${data.constructor.name}, maxZipFileSize: ${maxZipFileSize}, is larger: ${data.length > maxZipFileSize}`);
          if (data.length > maxZipFileSize) {
            console.log(`File ${file.filename} is too large for ZIP (${formatBytes(data.length)}), downloading individually...`);

            // Trigger individual download for large file
            chrome.runtime.sendMessage({
              action: 'download',
              url: file.url,
              filename: fileName
            }, (downloadResponse) => {
              if (chrome.runtime.lastError) {
                console.error('Individual download failed:', chrome.runtime.lastError);
                updateProgress({
                  status: 'error',
                  message: `Failed to download large file: ${file.filename}`
                });
              } else {
                console.log(`Individual download started for large file: ${file.filename}`);
                if (downloadResponse && downloadResponse.downloadId) {
                  activeDownloadIds.push(downloadResponse.downloadId);
                }
              }
            });

            // Update progress but don't count as processed for ZIP
            updateProgress({
              status: 'processing',
              message: `Downloaded individually: ${file.filename} (${formatBytes(data.length)}) - Total: ${formatBytes(totalBytesDownloaded)}`,
              progress: Math.round(baseProgress + (processedFiles / totalFiles) * progressRange)
            });
            processedFiles++; // Still count as processed for progress tracking
            console.log(`Skipping ZIP addition for large file: ${file.filename}`);
            continue; // Skip adding to ZIP
          }

          console.log(`Adding ${file.filename} to ZIP (size: ${formatBytes(data.length)})`);
          zip.file(path, data);

          processedFiles++;
          updateProgress({
            status: 'processing',
            message: `Added ${processedFiles}/${totalFiles}: ${file.filename} (${formatBytes(data.length)}) - Total: ${formatBytes(totalBytesDownloaded)}`,
            progress: Math.round(baseProgress + (processedFiles / totalFiles) * progressRange)
          });

        } catch (error) {
          console.error(`Error adding ${file.filename} to ZIP:`, error);
          updateProgress({
            status: 'error',
            message: `Error downloading: ${file.filename}`
          });
        }
      }

      // Add text content
      if (downloadText) {
        const textFileName = autoRename ? `${sanitizeFilename(postData.title || 'post')}_content.txt` : 'content.txt';
        zip.file(textFileName, postData.content);
        console.log('Added text content to ZIP');

        updateProgress({
          status: 'processing',
          message: 'Adding text content...',
          progress: baseProgress
        });
      }

      // Generate ZIP
      console.log('Generating ZIP file...');
      updateProgress({
        status: 'compressing',
        message: `Compressing ${processedFiles} files (${formatBytes(totalBytesDownloaded)}) into ZIP...`,
        progress: 90
      });

      const zipBlob = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: { level: 6 }
      });

      // Create download URL for the ZIP
      const zipUrl = URL.createObjectURL(zipBlob);
      const zipFileName = `${sanitizeFilename(postData.title || 'post')}.zip`;
      console.log('ZIP created, downloading as:', zipFileName);

      updateProgress({
        status: 'downloading_zip',
        message: 'Starting ZIP download...',
        progress: 95
      });

      // Try direct download in the page context (works in incognito where background may not access page blob URLs)
      try {
        const a = document.createElement('a');
        a.href = zipUrl;
        a.download = zipFileName;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        console.log('Triggered direct ZIP download via anchor click');
      } catch (err) {
        console.error('Direct download failed, falling back to background download:', err);
        // Fallback to background download (may still fail for incognito blob URLs)
        chrome.runtime.sendMessage({
          action: 'download',
          url: zipUrl,
          filename: zipFileName
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('Fallback download failed:', chrome.runtime.lastError);
            updateProgress({
              status: 'error',
              message: 'ZIP download failed: ' + chrome.runtime.lastError.message
            });
          }
        });
      }

      // Wait for all video downloads to complete as before
      if (videoDownloadPromises.length > 0) {
        console.log(`Waiting for ${videoDownloadPromises.length} video downloads to complete...`);
        updateProgress({
          status: 'processing',
          message: 'ZIP created, waiting for video downloads to complete...',
          progress: 90
        });

        if (downloadCancelled) {
          console.log('Download cancelled before awaiting video downloads');
          updateProgress({ status: 'error', message: 'Download cancelled by user' });
          return false;
        }

        try {
          await Promise.all(videoDownloadPromises);
          console.log('All video downloads completed');
          if (window.videoStatusElement) {
            window.videoStatusElement.textContent = `All ${videoDownloads.length} video(s) downloaded successfully`;
            window.videoStatusElement.style.color = '#059669';
          }
        } catch (videoError) {
          console.error('Some video downloads failed:', videoError);
          updateProgress({
            status: 'error',
            message: 'Some video downloads failed: ' + videoError.message
          });
          return false;
        }
      }

      // Finalize progress (no downloadId available for direct anchor downloads)
      updateProgress({
        status: 'completed',
        message: `Download completed! ${processedFiles}/${totalFiles} files (${formatBytes(totalBytesDownloaded)}) saved${videoDownloads.length > 0 ? ` + ${videoDownloads.length} video(s) individually` : ''}`,
        progress: 100
      });

      // Clean up the blob URL
      setTimeout(() => URL.revokeObjectURL(zipUrl), 10000);

      return true;
    } catch (error) {
      console.error('ZIP creation failed:', error);
      updateProgress({
        status: 'error',
        message: 'ZIP creation failed: ' + error.message
      });
      return false;
    }
  }

  // Download individual files
  function downloadIndividual(selectedFiles, downloadText, autoRename) {
    // Reset cancellation state and active download ids
    downloadCancelled = false;

    selectedFiles.forEach(file => {
      const fileName = autoRename ? `${sanitizeFilename(postData.title || 'post')}_${file.filename}` : file.filename;
      chrome.runtime.sendMessage({
        action: 'download',
        url: file.url,
        filename: fileName
      }, (response) => {
        if (!chrome.runtime.lastError && response && response.downloadId) {
          activeDownloadIds.push(response.downloadId);
        }
      });
    });

    if (downloadText) {
      const textFileName = autoRename ? `${sanitizeFilename(postData.title || 'post')}_content.txt` : 'content.txt';
      const textBlob = new Blob([postData.content], { type: 'text/plain' });
      const textUrl = URL.createObjectURL(textBlob);

      // Trigger direct download from page context (works in incognito)
      try {
        const a = document.createElement('a');
        a.href = textUrl;
        a.download = textFileName;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } catch (err) {
        console.error('Direct text download failed, falling back to background download:', err);
        chrome.runtime.sendMessage({
          action: 'download',
          url: textUrl,
          filename: textFileName
        }, (response) => {
          if (!chrome.runtime.lastError && response && response.downloadId) {
            activeDownloadIds.push(response.downloadId);
          }
        });
      }

      setTimeout(() => URL.revokeObjectURL(textUrl), 10000);
    }

    // Mark progress as running so the Cancel button will act accordingly
    if (progressState !== 'running') {
      progressState = 'running';
    }
  }

  // Sanitize filename
  function sanitizeFilename(name) {
    return name.replace(/[<>:"/\\|?*]/g, '_').replace(/\s+/g, '_').substring(0, 50);
  }

  // Format bytes for display
  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Create floating button with dynamic behavior
  function createFloatingButton() {
    const button = document.createElement('button');

    if (isPostPage) {
      // Post page - download button
      const iconUrl = 'https://raw.githubusercontent.com/VoxDroid/KemonoDownloader/refs/heads/main/assets/icons/KemonoDownloader-48.png';
      button.innerHTML = '<img src="' + iconUrl + '" alt="Download" style="width: 24px; height: 24px;" onerror="console.error(\'Icon failed to load from CDN:\', \'' + iconUrl + '\')">';
      button.title = 'Download Post (Kemono Downloader)';
      // Try to fetch post data on click if it wasn't loaded during initialization
      button.onclick = async () => {
        if (!postData) {
          console.log('Post data missing on click — attempting to fetch now...');
          await fetchPostData();
        }

        if (postData) {
          const modal = createModal();
          document.body.appendChild(modal);
        } else {
          alert('Post data not loaded yet. Please try again. Check the Browser Console (Ctrl+Shift+J) for details.');
        }
      };
    } else {
      // Non-post page - info button
      const iconUrl = 'https://raw.githubusercontent.com/VoxDroid/KemonoDownloader/refs/heads/main/assets/icons/KemonoDownloader-48.png';
      button.innerHTML = '<img src="' + iconUrl + '" alt="Kemono Downloader" style="width: 24px; height: 24px; filter: brightness(0.3) contrast(1.2);" onerror="console.error(\'Icon failed to load from CDN:\', \'' + iconUrl + '\')">';
      button.title = 'Kemono Downloader - Find a post to download!';
      button.onclick = () => {
        const modal = createInfoModal();
        document.body.appendChild(modal);
      };
    }

    // Common button styles
    button.style.position = 'fixed';
    button.style.top = '20px';
    button.style.right = '20px';
    button.style.zIndex = '10000';
    button.style.width = '48px';
    button.style.height = '48px';
    button.style.padding = '0';
    button.style.backgroundColor = isPostPage ? '#6d28d9' : '#374151';
    button.style.color = 'white';
    button.style.border = '2px solid #ffffff';
    button.style.borderRadius = '50%';
    button.style.cursor = 'pointer';
    button.style.display = 'flex';
    button.style.alignItems = 'center';
    button.style.justifyContent = 'center';
    button.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
    button.style.transition = 'all 0.2s';

    button.onmouseover = () => {
      button.style.backgroundColor = isPostPage ? '#7c3aed' : '#4b5563';
      button.style.transform = 'scale(1.05)';
      button.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
    };
    button.onmouseout = () => {
      button.style.backgroundColor = isPostPage ? '#6d28d9' : '#374151';
      button.style.transform = 'scale(1)';
      button.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
    };

    return button;
  }

  // Initialize extension
  async function initializeExtension() {
    console.log('Initializing Kemono Downloader extension');

    // Fetch post data if on a post page
    if (isPostPage) {
      await fetchPostData();
    }

    // Create and add floating button
    currentButton = createFloatingButton();

    if (document.body) {
      document.body.appendChild(currentButton);
      console.log('Floating button added to page');
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        document.body.appendChild(currentButton);
        console.log('Floating button added after DOMContentLoaded');
      });
    }
  }

  // Start the extension
  initializeExtension();

  // URL change detection for dynamic page updates
  let currentUrl = window.location.href;
  // currentButton is already set by initializeExtension()

  // Function to update button based on current page
  function updateButtonForCurrentPage() {
    const newUrl = window.location.href;
    const newIsPostPage = newUrl.includes('/post/');
    const newIsKemonoDomain = newUrl.includes('kemono.cr') || newUrl.includes('coomer.st');

    console.log('updateButtonForCurrentPage called:', {
      newUrl,
      newIsPostPage,
      newIsKemonoDomain,
      currentUrl,
      currentButtonExists: !!currentButton
    });

    // Only update if we're still on a Kemono domain and the page type changed
    if (!newIsKemonoDomain) {
      if (currentButton) {
        currentButton.remove();
        currentButton = null;
      }
      return;
    }

    // Check if page type changed or button is missing
    const oldIsPostPage = currentUrl.includes('/post/');
    const pageTypeChanged = newIsPostPage !== oldIsPostPage;
    const buttonMissing = !currentButton;

    console.log('Update check:', { oldIsPostPage, pageTypeChanged, buttonMissing });

    // Always ensure we have a button on Kemono domains
    if (newIsKemonoDomain && !currentButton) {
      console.log('No button found on Kemono domain, creating one');
      isPostPage = newIsPostPage;
      isKemonoDomain = newIsKemonoDomain;

      if (isPostPage) {
        const parts = newUrl.split('/').filter(p => p);
        if (parts.length >= 7) {
          service = parts[parts.length - 5];
          creator_id = parts[parts.length - 3];
          post_id = parts[parts.length - 1];
          domain = newUrl.includes('coomer.st') ? 'coomer.st' : 'kemono.cr';
          api_base = `https://${domain}/api/v1`;
          fetchPostData();
        }
      }

      currentButton = createFloatingButton();
      if (document.body) {
        document.body.appendChild(currentButton);
        console.log('Button created for Kemono domain');
      }
      currentUrl = newUrl;
      return; // Don't continue with the page type change logic
    }

    // Handle page type changes
    if (pageTypeChanged) {
      console.log('Page type changed, updating button');

      // Remove old button
      if (currentButton) {
        currentButton.remove();
        currentButton = null;
      }

      // Update global variables for new page
      isPostPage = newIsPostPage;
      isKemonoDomain = newIsKemonoDomain;

      // Parse URL for new page if it's a post page
      if (isPostPage) {
        const parts = newUrl.split('/').filter(p => p);
        if (parts.length >= 7) {
          service = parts[parts.length - 5];
          creator_id = parts[parts.length - 3];
          post_id = parts[parts.length - 1];
          domain = newUrl.includes('coomer.st') ? 'coomer.st' : 'kemono.cr';
          api_base = `https://${domain}/api/v1`;

          console.log('Updated URL parsing:', { service, creator_id, post_id });

          // Fetch post data for new page
          fetchPostData();
        }
      }

      // Create new button
      currentButton = createFloatingButton();
      if (document.body) {
        document.body.appendChild(currentButton);
        console.log('Button updated for new page');
      }

      currentUrl = newUrl;
    }
  }

  // Monitor URL changes using multiple methods
  function startUrlMonitoring() {
    // Method 1: History API events
    window.addEventListener('popstate', () => {
      setTimeout(updateButtonForCurrentPage, 100);
    });

    // Method 2: PushState/replaceState interception
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = function(state, title, url) {
      originalPushState.apply(this, arguments);
      setTimeout(updateButtonForCurrentPage, 100);
    };

    history.replaceState = function(state, title, url) {
      originalReplaceState.apply(this, arguments);
      setTimeout(updateButtonForCurrentPage, 100);
    };

    // Method 3: MutationObserver for DOM changes (catches client-side routing)
    const observer = new MutationObserver((mutations) => {
      let shouldCheck = false;

      for (const mutation of mutations) {
        // Check if URL changed
        if (window.location.href !== currentUrl) {
          shouldCheck = true;
          break;
        }

        // Check for significant DOM changes that might indicate navigation
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE &&
                (node.matches && (node.matches('main') || node.matches('[data-page]') ||
                 node.matches('.post') || node.matches('#post')))) {
              shouldCheck = true;
              break;
            }
          }
        }

        if (shouldCheck) break;
      }

      if (shouldCheck) {
        setTimeout(updateButtonForCurrentPage, 200); // Slightly longer delay for DOM updates
      }
    });

    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Method 4: Periodic URL check as fallback - more frequent
    setInterval(() => {
      if (window.location.href !== currentUrl) {
        console.log('URL change detected by periodic check');
        updateButtonForCurrentPage();
      }
    }, 500); // Check every 500ms

    // Method 5: Visibility change (when user switches tabs)
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && window.location.href !== currentUrl) {
        console.log('URL change detected on visibility change');
        updateButtonForCurrentPage();
      }
    });

    // Method 6: Window focus event
    window.addEventListener('focus', () => {
      if (window.location.href !== currentUrl) {
        console.log('URL change detected on window focus');
        updateButtonForCurrentPage();
      }
    });

    console.log('URL monitoring started');
  }

  // Start monitoring after initial load
  setTimeout(startUrlMonitoring, 1000);

  // Progress tracking variables
  let progressModal = null;
  let progressBar = null;
  let progressText = null;
  let videoStatus = null;
  // Track cancellation and active downloads
  let downloadCancelled = false;
  let activeDownloadIds = [];
  let progressState = 'idle'; // 'idle' | 'running' | 'completed' | 'error'

  // Listen for progress updates from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'zip_progress') {
      updateProgress(request);
    }
  });

  // Update progress UI
  function updateProgress(progressData) {
    if (!progressModal) {
      createProgressModal();
    }

    // Handle video download messages separately
    if (progressData.message && progressData.message.includes('Downloading video:')) {
      if (window.videoStatusElement) {
        const videoMessage = progressData.message.replace('Downloading video: ', '');
        window.videoStatusElement.textContent = videoMessage;
        window.videoStatusElement.style.color = progressData.status === 'error' ? '#dc2626' : '#0369a1';
      }
      // Still update progress bar for overall progress
      if (progressBar && progressData.progress !== undefined) {
        progressBar.style.width = `${progressData.progress}%`;
      }
      return;
    }

    if (progressText) {
      progressText.textContent = progressData.message || 'Processing...';
    }

    if (progressBar && progressData.progress !== undefined) {
      progressBar.style.width = `${progressData.progress}%`;
    }

    // Handle completion
    if (progressData.status === 'completed') {
      progressState = 'completed';
      if (progressText) {
        progressText.textContent = 'All downloads completed successfully!';
        progressText.style.color = '#10b981';
      }
      if (progressBar) {
        progressBar.style.backgroundColor = '#10b981';
        progressBar.style.width = '100%';
      }
      // Add confirmation button instead of auto-close
      addCompletionButtons();
    }

    // Handle errors
    if (progressData.status === 'error') {
      progressState = 'error';
      if (progressText) {
        progressText.style.color = '#ef4444';
      }
      if (progressBar) {
        progressBar.style.backgroundColor = '#ef4444';
      }
      // Add error buttons instead of auto-close
      addErrorButtons();
    }

    // If progress indicates running-like states, mark as running
    const runningStates = ['initializing', 'preparing', 'downloading', 'processing', 'compressing', 'downloading_zip'];
    if (runningStates.includes(progressData.status)) {
      progressState = 'running';
    }
  }

  // Helper functions for progress modal buttons
  function addCompletionButtons() {
    const statusButtons = document.getElementById('statusButtons');
    if (!statusButtons) return;

    statusButtons.innerHTML = ''; // Clear any existing buttons

    const confirmButton = document.createElement('button');
    confirmButton.textContent = 'Done';
    confirmButton.style.padding = '8px 16px';
    confirmButton.style.backgroundColor = '#6d28d9';
    confirmButton.style.color = 'white';
    confirmButton.style.border = 'none';
    confirmButton.style.borderRadius = '6px';
    confirmButton.style.cursor = 'pointer';
    confirmButton.style.fontSize = '14px';
    confirmButton.style.fontWeight = '500';
    confirmButton.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    confirmButton.style.transition = 'all 0.3s ease';
    confirmButton.onclick = () => {
      if (progressModal) {
        progressModal.remove();
        progressModal = null;
      }
      // Return to the download modal
      const modal = createModal();
      document.body.appendChild(modal);
    };
    confirmButton.onmouseover = () => confirmButton.style.backgroundColor = '#7c3aed';
    confirmButton.onmouseout = () => confirmButton.style.backgroundColor = '#6d28d9';

    statusButtons.appendChild(confirmButton);
    statusButtons.style.display = 'block';
  }

  function addErrorButtons() {
    const statusButtons = document.getElementById('statusButtons');
    if (!statusButtons) return;

    statusButtons.innerHTML = ''; // Clear any existing buttons

    const retryButton = document.createElement('button');
    retryButton.textContent = 'Retry';
    retryButton.style.padding = '8px 16px';
    retryButton.style.backgroundColor = '#f59e0b';
    retryButton.style.color = 'white';
    retryButton.style.border = 'none';
    retryButton.style.borderRadius = '6px';
    retryButton.style.cursor = 'pointer';
    retryButton.style.fontSize = '14px';
    retryButton.style.fontWeight = '500';
    retryButton.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    retryButton.style.marginRight = '8px';
    retryButton.style.transition = 'all 0.3s ease';
    retryButton.onclick = () => {
      // Could implement retry logic here
      alert('Retry functionality not yet implemented. Please refresh the page and try again.');
    };
    retryButton.onmouseover = () => retryButton.style.backgroundColor = '#d97706';
    retryButton.onmouseout = () => retryButton.style.backgroundColor = '#f59e0b';

    const closeButton = document.createElement('button');
    closeButton.textContent = 'Close';
    closeButton.style.padding = '8px 16px';
    closeButton.style.backgroundColor = '#ef4444';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '6px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontSize = '14px';
    closeButton.style.fontWeight = '500';
    closeButton.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    closeButton.style.transition = 'all 0.3s ease';
    closeButton.onclick = () => {
      if (progressModal) {
        progressModal.remove();
        progressModal = null;
      }
      // Return to the download modal
      const modal = createModal();
      document.body.appendChild(modal);
    };
    closeButton.onmouseover = () => closeButton.style.backgroundColor = '#dc2626';
    closeButton.onmouseout = () => closeButton.style.backgroundColor = '#ef4444';

    statusButtons.appendChild(retryButton);
    statusButtons.appendChild(closeButton);
    statusButtons.style.display = 'block';
  }

  // Create progress modal
  function createProgressModal() {
    progressModal = document.createElement('div');
    progressModal.style.position = 'fixed';
    progressModal.style.top = '0';
    progressModal.style.left = '0';
    progressModal.style.width = '100%';
    progressModal.style.height = '100%';
    progressModal.style.backgroundColor = 'rgba(10, 14, 23, 0.8)';
    progressModal.style.zIndex = '10002';
    progressModal.style.display = 'flex';
    progressModal.style.alignItems = 'center';
    progressModal.style.justifyContent = 'center';
    progressModal.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';

    const progressContent = document.createElement('div');
    progressContent.style.backgroundColor = '#1a1f2e';
    progressContent.style.padding = '24px';
    progressContent.style.borderRadius = '12px';
    progressContent.style.maxWidth = '500px';
    progressContent.style.width = '90%';
    progressContent.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
    progressContent.style.border = '1px solid #374151';
    progressContent.style.color = '#e2e8f0';
    progressContent.style.textAlign = 'center';

    const title = document.createElement('h3');
    title.textContent = 'Downloading Files';
    title.style.marginTop = '0';
    title.style.marginBottom = '16px';
    title.style.color = '#ffffff';
    title.style.fontSize = '18px';
    title.style.fontWeight = '600';
    progressContent.appendChild(title);

    // Video downloads section
    const videoSection = document.createElement('div');
    videoSection.style.marginBottom = '16px';
    videoSection.style.padding = '12px';
    videoSection.style.backgroundColor = '#1f2937';
    videoSection.style.borderRadius = '8px';
    videoSection.style.border = '1px solid #374151';

    const videoTitle = document.createElement('h4');
    videoTitle.textContent = 'Video Downloads';
    videoTitle.style.margin = '0 0 8px 0';
    videoTitle.style.color = '#e2e8f0';
    videoTitle.style.fontSize = '14px';
    videoTitle.style.fontWeight = '600';
    videoSection.appendChild(videoTitle);

    const videoStatus = document.createElement('p');
    videoStatus.textContent = 'Scanning for videos...';
    videoStatus.style.margin = '0';
    videoStatus.style.color = '#94a3b8';
    videoStatus.style.fontSize = '12px';
    videoSection.appendChild(videoStatus);

    // Store reference for updates
    window.videoStatusElement = videoStatus;

    progressContent.appendChild(videoSection);

    // ZIP progress section
    const zipSection = document.createElement('div');
    zipSection.style.marginBottom = '16px';

    const zipTitle = document.createElement('h4');
    zipTitle.textContent = 'ZIP Archive Progress';
    zipTitle.style.margin = '0 0 8px 0';
    zipTitle.style.color = '#ffffff';
    zipTitle.style.fontSize = '14px';
    zipTitle.style.fontWeight = '600';
    zipSection.appendChild(zipTitle);

    // Progress bar container
    const progressContainer = document.createElement('div');
    progressContainer.style.width = '100%';
    progressContainer.style.height = '8px';
    progressContainer.style.backgroundColor = '#374151';
    progressContainer.style.borderRadius = '4px';
    progressContainer.style.marginBottom = '8px';
    progressContainer.style.overflow = 'hidden';

    progressBar = document.createElement('div');
    progressBar.style.height = '100%';
    progressBar.style.backgroundColor = '#6d28d9';
    progressBar.style.borderRadius = '4px';
    progressBar.style.width = '0%';
    progressBar.style.transition = 'width 0.3s ease';
    progressContainer.appendChild(progressBar);
    zipSection.appendChild(progressContainer);

    progressContent.appendChild(zipSection);

    progressText = document.createElement('p');
    progressText.textContent = 'Initializing...';
    progressText.style.margin = '0';
    progressText.style.color = '#94a3b8';
    progressText.style.fontSize = '14px';
    progressContent.appendChild(progressText);

    // Add buttons container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.display = 'flex';
    buttonsContainer.style.justifyContent = 'space-between';
    buttonsContainer.style.alignItems = 'center';
    buttonsContainer.style.marginTop = '16px';
    buttonsContainer.style.paddingTop = '16px';
    buttonsContainer.style.borderTop = '1px solid #374151';

    // Exit button (always visible)
    const exitButton = document.createElement('button');
    exitButton.textContent = 'Cancel';
    exitButton.style.padding = '8px 16px';
    exitButton.style.backgroundColor = '#374151';
    exitButton.style.color = '#e2e8f0';
    exitButton.style.border = 'none';
    exitButton.style.borderRadius = '6px';
    exitButton.style.cursor = 'pointer';
    exitButton.style.fontSize = '14px';
    exitButton.style.fontWeight = '500';
    exitButton.style.fontFamily = '"JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    exitButton.style.transition = 'all 0.3s ease';
    exitButton.onclick = () => {
      // If downloads are running, treat this as a cancel + reload
      if (progressState === 'running') {
        console.log('User requested cancel during active download');
        downloadCancelled = true;
        updateProgress({ status: 'error', message: 'Cancellation requested. Stopping downloads and reloading...' });
        // Try to cancel active downloads in the background
        if (activeDownloadIds.length > 0) {
          chrome.runtime.sendMessage({ action: 'cancel_downloads', downloadIds: activeDownloadIds });
        }
        // Give UI a moment to update, then reload
        setTimeout(() => window.location.reload(), 700);
        return;
      }

      // Otherwise behave as Exit: close progress modal and return to download modal
      if (progressModal) {
        progressModal.remove();
        progressModal = null;
      }
      const modal = createModal();
      document.body.appendChild(modal);
    };
    exitButton.onmouseover = () => exitButton.style.backgroundColor = '#4b5563';
    exitButton.onmouseout = () => exitButton.style.backgroundColor = '#374151';

    // Status button container (for completion/error buttons)
    const statusButtonContainer = document.createElement('div');
    statusButtonContainer.id = 'statusButtons';
    statusButtonContainer.style.display = 'none'; // Hidden initially

    buttonsContainer.appendChild(exitButton);
    buttonsContainer.appendChild(statusButtonContainer);
    progressContent.appendChild(buttonsContainer);

    progressModal.appendChild(progressContent);
    document.body.appendChild(progressModal);
  }
})();