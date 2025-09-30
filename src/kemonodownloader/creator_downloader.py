import os
import re
import hashlib
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                         QGroupBox, QGridLayout, QProgressBar, QTextEdit, QListWidget, 
                         QListWidgetItem, QAbstractItemView, QMessageBox, QCheckBox, 
                         QLabel, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
import qtawesome as qta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from kemonodownloader.kd_language import translate
import locale
import ctypes
from fake_useragent import UserAgent
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
import threading


class ThreadSettings:
    """Settings container for thread operations"""
    def __init__(self, creator_posts_max_attempts, post_data_max_retries,
                 file_download_max_retries, api_request_max_retries, simultaneous_downloads):
        self.creator_posts_max_attempts = creator_posts_max_attempts
        self.post_data_max_retries = post_data_max_retries
        self.file_download_max_retries = file_download_max_retries
        self.api_request_max_retries = api_request_max_retries
        self.simultaneous_downloads = simultaneous_downloads


try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

if hasattr(ctypes, 'windll'):  
    lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
    system_language = locale.windows_locale.get(lcid, "en_US")
else:
    locale_info = locale.getlocale(locale.LC_ALL)
    system_language = locale_info[0] if locale_info and locale_info[0] else "en_US"

system_language = system_language.replace('_', '-')  
accept_language = f"{system_language},en;q=0.9"

ua = UserAgent()
user_agent = ua.chrome  

def get_domain_config(url):
    """Determine domain configuration based on URL"""
    if 'coomer.st' in url:
        return {
            'domain': 'coomer.st',
            'base_url': 'https://coomer.st',
            'api_base': 'https://coomer.st/api/v1',
            'referer': 'https://coomer.st/'
        }
    else:  # Default to kemono.cr
        return {
            'domain': 'kemono.cr',
            'base_url': 'https://kemono.cr',
            'api_base': 'https://kemono.cr/api/v1',
            'referer': 'https://kemono.cr/'
        }

# Default headers (will be updated per request based on domain)
HEADERS = {
    "User-Agent": user_agent,
    "Referer": "https://kemono.cr/", 
    "Accept": "text/css",
    "Accept-Language": accept_language, 
    "Accept-Encoding": "gzip, deflate",  
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
API_BASE = "https://kemono.cr/api/v1"

class PreviewThread(QThread):
    preview_ready = pyqtSignal(str, object)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url, cache_dir):
        super().__init__()
        self.url = url
        self.cache_dir = cache_dir
        self.total_size = 0
        self.downloaded_size = 0
        os.makedirs(self.cache_dir, exist_ok=True)

    def run(self):
        if self.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            cache_key = hashlib.md5(self.url.encode()).hexdigest() + os.path.splitext(self.url)[1]
            cache_path = os.path.join(self.cache_dir, cache_key)
            if os.path.exists(cache_path):
                pixmap = QPixmap()
                if pixmap.load(cache_path):
                    self.preview_ready.emit(self.url, pixmap)
                    return

            try:
                response = requests.get(self.url, headers=HEADERS, stream=True)
                response.raise_for_status()
                self.total_size = int(response.headers.get('content-length', 0)) or 1
                downloaded_data = bytearray()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_data.extend(chunk)
                        self.downloaded_size += len(chunk)
                        progress = int((self.downloaded_size / self.total_size) * 100)
                        self.progress.emit(min(progress, 100))
                pixmap = QPixmap()
                if not pixmap.loadFromData(downloaded_data):
                    self.error.emit(translate("failed_to_download", f"{self.url}: {translate('invalid_image_data')}"))
                    return
                scaled_pixmap = pixmap.scaled(800, 800, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                scaled_pixmap.save(cache_path)
                self.preview_ready.emit(self.url, scaled_pixmap)
            except requests.RequestException as e:
                self.error.emit(translate("failed_to_download", f"{self.url}: {str(e)}"))
            except Exception as e:
                self.error.emit(translate("unexpected_error", f"{self.url}: {str(e)}"))

class ImageModal(QDialog):
    def __init__(self, url, cache_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translate("media_preview"))
        self.setModal(True)
        self.resize(800, 800)
        self.layout = QVBoxLayout()
        self.label = QLabel(translate("loading_image_simple"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; } QProgressBar::chunk { background: #4A5B7A; }")
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)
        
        self.preview_thread = PreviewThread(url, cache_dir)
        self.preview_thread.preview_ready.connect(self.display_image)
        self.preview_thread.progress.connect(self.update_progress)
        self.preview_thread.error.connect(self.display_error)
        self.preview_thread.finished.connect(self.preview_thread.deleteLater)
        self.preview_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.label.setText(translate("loading_image", value))

    def display_image(self, url, pixmap):
        self.label.setText("")
        self.progress_bar.hide()
        self.label.setPixmap(pixmap)

    def display_error(self, error_message):
        self.label.setText(translate("error_loading_image"))
        self.progress_bar.hide()
        QMessageBox.critical(self, translate("image_load_error"), error_message)

class PostDetectionThread(QThread):
    finished = pyqtSignal(list)
    log = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, url, post_titles_map, settings):
        super().__init__()
        self.url = url
        self.post_titles_map = post_titles_map  # Shared dictionary to store post titles
        self.settings = settings
        self.is_running = True
        self.domain_config = get_domain_config(url)

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        self.log.emit(translate("log_info", translate("checking_creator_with_url", self.url)), "INFO")
        parts = self.url.split('/')
        if len(parts) < 5 or (self.domain_config['domain'] not in self.url) or parts[-2] != 'user':
            self.error.emit(translate("invalid_url_format"))
            return
        service, creator_id = parts[-3], parts[-1]

        self.log.emit(translate("log_debug", translate("parsed_url_service_creator", service, creator_id)), "INFO")

        base_api_url = f"{self.domain_config['api_base']}/{service}/user/{creator_id}"
        self.log.emit(translate("log_debug", translate("base_api_url", base_api_url)), "INFO")

        all_posts = []
        offset = 0
        page_size = 50
        max_attempts = self.settings.creator_posts_max_attempts

        attempt = 1
        while attempt <= max_attempts and self.is_running:
            alternative_urls = [
                f"{self.domain_config['api_base']}/{service}/user/{creator_id}/posts?o={offset}",  # Try with /posts suffix
                f"{base_api_url}?o={offset}",  # Original format as fallback
                f"{self.domain_config['base_url']}/api/{service}/user/{creator_id}?o={offset}",  # Try without v1
                f"{base_api_url}?offset={offset}&limit={page_size}",  # Try different parameter names
            ]
            
            success = False
            response = None
            likely_last_page = len(all_posts) > 0 and len(all_posts) % page_size != 0
            
            for alt_url in alternative_urls:
                if not self.is_running:
                    return
                self.log.emit(translate("log_debug", translate("trying_endpoint", alt_url)), "DEBUG")

                
                fallback_headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/css',
                    'Accept-Language': accept_language,
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'Referer': self.domain_config['referer']
                }
                
                try:
                    alt_response = requests.get(alt_url, headers=fallback_headers, timeout=15)
                    if alt_response.status_code == 200:
                        response = alt_response
                        self.log.emit(translate("log_info", translate("endpoint_successful", alt_url)), "INFO")
                        success = True
                        break
                    else:
                        if likely_last_page or len(all_posts) > 0:
                            self.log.emit(translate("log_debug", translate("endpoint_returned_status_likely_end", alt_response.status_code, alt_url)), "DEBUG")
                        else:
                            self.log.emit(translate("log_debug", translate("endpoint_failed_with_status", alt_url, alt_response.status_code)), "DEBUG")
                except requests.RequestException as alt_e:
                    if likely_last_page or len(all_posts) > 0:
                        self.log.emit(translate("log_debug", translate("endpoint_unavailable_likely_end", alt_url, str(alt_e))), "DEBUG")
                    else:
                        self.log.emit(translate("log_debug", translate("endpoint_error_with_exception", alt_url, str(alt_e))), "DEBUG")

            
            if not success:
                if len(all_posts) > 0:
                    self.log.emit(translate("log_info", translate("reached_last_page", creator_id, len(all_posts))), "INFO")
                    break
                else:
                    self.log.emit(translate("log_error", translate("all_api_endpoints_failed", creator_id)), "ERROR")
                    break
                
            try:
                response_text = None
                
                is_gzipped = response.content[:2] == b'\x1f\x8b'
                
                if is_gzipped:
                    try:
                        import gzip
                        decompressed = gzip.decompress(response.content)
                        response_text = decompressed.decode('utf-8')
                        self.log.emit(translate("log_debug", translate("successfully_decompressed_gzipped_response")), "DEBUG")
                    except (gzip.BadGzipFile, UnicodeDecodeError) as e:
                        self.log.emit(translate("log_warning", translate("gzip_decompression_failed", str(e))), "WARNING")
                        response_text = response.text
                else:
                    # Content is not gzipped, use as plain text
                    response_text = response.text
                
                # Check if response is empty or just whitespace
                if not response_text.strip(): 
                    self.log.emit(translate("log_info", translate("empty_response_at_offset", offset)), "INFO")
                    break
                
                posts_data = json.loads(response_text)
                
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.log.emit(translate("log_error", translate("failed_to_parse_response", str(e))), "ERROR")
                self.log.emit(translate("log_debug", translate("response_content_first_500_chars", response.text[:500])), "DEBUG")
                break
                
            if not isinstance(posts_data, list):
                # Sometimes the API returns an object with a posts array
                if isinstance(posts_data, dict):
                    if 'posts' in posts_data:
                        posts_data = posts_data['posts']
                    elif 'data' in posts_data:
                        posts_data = posts_data['data']
                    else:
                        self.log.emit(translate("log_error", translate("unexpected_response_structure", list(posts_data.keys()) if posts_data else 'empty dict')), "ERROR")
                        break
                else:
                    self.log.emit(translate("log_error", translate("invalid_posts_data_type", type(posts_data))), "ERROR")
                    break

            self.log.emit(translate("log_debug", translate("fetched_posts_at_offset", len(posts_data), offset)), "DEBUG")

            if len(posts_data) < page_size and len(posts_data) > 0:
                self.log.emit(translate("log_info", translate("received_less_than_page_size", len(posts_data), page_size)), "INFO")

            for post in posts_data:
                if not isinstance(post, dict):
                    continue
                post_id = post.get('id')
                if not post_id:
                    continue
                title = post.get('title', f"Post {post_id}")
                self.log.emit(translate("log_debug", translate("post_id_and_title", post_id, title)), "DEBUG")
                # Store title in shared post_titles_map
                self.post_titles_map[(service, creator_id, post_id)] = sanitize_filename(title)

            if not posts_data:
                self.log.emit(translate("log_info", translate("no_more_posts_at_offset", offset)), "INFO")
                break

            all_posts.extend(posts_data)

            if len(posts_data) < page_size:
                self.log.emit(translate("log_info", translate("last_page_reached_with_counts", len(posts_data), page_size, len(all_posts))), "INFO")
                break
                
            offset += page_size
            attempt += 1
            time.sleep(0.5)

        if self.is_running:
            detected_posts = []
            for post in all_posts:
                post_id = post.get('id')
                title = post.get('title', f"Post {post_id}")
                thumbnail_url = None
                if 'file' in post and post['file'] and 'path' in post['file']:
                    if post['file']['path'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        thumbnail_url = urljoin(self.domain_config['base_url'], post['file']['path'])
                if not thumbnail_url and 'attachments' in post:
                    for attachment in post['attachments']:
                        if isinstance(attachment, dict) and 'path' in attachment and attachment['path'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            thumbnail_url = urljoin(self.domain_config['base_url'], attachment['path'])
                            break
                if not thumbnail_url and 'file' in post and post['file'] and 'path' in post['file']:
                    thumbnail_url = urljoin(self.domain_config['base_url'], post['file']['path'])
                detected_posts.append((title, (post_id, thumbnail_url)))

            self.log.emit(translate("log_info", translate("total_posts_fetched_for_creator", self.url, len(detected_posts))), "INFO")
            self.finished.emit(detected_posts)

class PostPopulationThread(QThread):
    finished = pyqtSignal(dict, list)
    log = pyqtSignal(str, str)

    def __init__(self, detected_posts):
        super().__init__()
        self.detected_posts = detected_posts
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        post_url_map = {}
        for post_title, (post_id, thumbnail_url) in self.detected_posts:
            unique_title = f"{post_title} (ID: {post_id})"
            post_url_map[unique_title] = (post_id, thumbnail_url)
            self.log.emit(translate("log_debug", translate("mapped_title_to_id_and_thumbnail", unique_title, post_id, thumbnail_url)), "INFO")
        self.log.emit(translate("log_debug", translate("prepared_posts_for_population", len(self.detected_posts), len(post_url_map))), "INFO")
        self.finished.emit(post_url_map, self.detected_posts)
        
class FilterThread(QThread):
    finished = pyqtSignal(list)
    log = pyqtSignal(str, str)

    def __init__(self, all_detected_posts, checked_urls, search_text):
        super().__init__()
        self.all_detected_posts = all_detected_posts
        self.checked_urls = checked_urls.copy()
        self.search_text = search_text.lower()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        filtered_items = []
        for post_title, (post_id, thumbnail_url) in self.all_detected_posts:
            if not self.search_text or self.search_text in post_title.lower():
                is_checked = self.checked_urls.get(post_id, False)
                filtered_items.append((post_title, post_id, thumbnail_url, is_checked))
                self.log.emit(translate("log_debug", translate("filtered_post", post_title, post_id)), "INFO")
        self.finished.emit(filtered_items)

class FilePreparationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list, dict)
    log = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, post_ids, all_files_map, creator_ext_checks, creator_main_check, creator_attachments_check, creator_content_check, settings, max_concurrent=20):
        super().__init__()
        self.post_ids = post_ids
        self.all_files_map = all_files_map
        self.creator_ext_checks = creator_ext_checks
        self.creator_main_check = creator_main_check
        self.creator_attachments_check = creator_attachments_check
        self.creator_content_check = creator_content_check
        self.settings = settings
        self.max_concurrent = max_concurrent
        self.is_running = True

    def stop(self):
        self.is_running = False

    def detect_files(self, post, allowed_extensions, domain_config):
        files_to_download = []
        self.log.emit(translate("log_debug", translate("detecting_files_for_post", allowed_extensions)), "INFO")
        
        def get_effective_extension(file_path, file_name):
            name_ext = os.path.splitext(file_name)[1].lower()
            path_ext = os.path.splitext(file_path)[1].lower()
            return name_ext if name_ext else path_ext

        # Main file detection
        if self.creator_main_check and 'file' in post and post['file'] and 'path' in post['file']:
            file_path = post['file']['path']
            file_name = post['file'].get('name', '')
            file_ext = get_effective_extension(file_path, file_name)
            file_url = urljoin(domain_config['base_url'], file_path)
            if 'f=' not in file_url and file_name:
                file_url += f"?f={file_name}"
            self.log.emit(translate("log_debug", translate("checking_main_file", file_name, file_ext)), "INFO")
            if '.jpg' in allowed_extensions and file_ext in ['.jpg', '.jpeg']:
                self.log.emit(translate("log_debug", translate("added_main_file", file_name)), "INFO")
                files_to_download.append((file_name, file_url))
            elif file_ext in allowed_extensions:
                self.log.emit(translate("log_debug", translate("added_main_file", file_name)), "INFO")
                files_to_download.append((file_name, file_url))

        # Attachments detection
        if self.creator_attachments_check and 'attachments' in post:
            for attachment in post['attachments']:
                if isinstance(attachment, dict) and 'path' in attachment:
                    attachment_path = attachment['path']
                    attachment_name = attachment.get('name', '')
                    attachment_ext = get_effective_extension(attachment_path, attachment_name)
                    attachment_url = urljoin(domain_config['base_url'], attachment_path)
                    if 'f=' not in attachment_url and attachment_name:
                        attachment_url += f"?f={attachment_name}"
                    self.log.emit(translate("log_debug", translate("checking_attachment", attachment_name, attachment_ext)), "INFO")
                    if '.jpg' in allowed_extensions and attachment_ext in ['.jpg', '.jpeg']:
                        self.log.emit(translate("log_debug", translate("added_attachment", attachment_name)), "INFO")
                        files_to_download.append((attachment_name, attachment_url))
                    elif attachment_ext in allowed_extensions:
                        self.log.emit(translate("log_debug", translate("added_attachment", attachment_name)), "INFO")
                        files_to_download.append((attachment_name, attachment_url))

        # Content images detection
        if self.creator_content_check and 'content' in post and post['content']:
            soup = BeautifulSoup(post['content'], 'html.parser')
            for img in soup.select('img[src]'):
                img_url = urljoin(domain_config['base_url'], img['src'])
                img_ext = os.path.splitext(img_url)[1].lower()
                img_name = os.path.basename(img_url)
                self.log.emit(translate("log_debug", translate("checking_content_image", img_name, img_ext)), "INFO")
                if '.jpg' in allowed_extensions and img_ext in ['.jpg', '.jpeg']:
                    self.log.emit(translate("log_debug", translate("added_content_image", img_name)), "INFO")
                    files_to_download.append((img_name, img_url))
                elif img_ext in allowed_extensions:
                    self.log.emit(translate("log_debug", translate("added_content_image", img_name)), "INFO")
                    files_to_download.append((img_name, img_url))

        self.log.emit(translate("log_debug", translate("total_files_detected", len(files_to_download))), "INFO")
        return list(dict.fromkeys(files_to_download))

    def fetch_and_detect_files(self, post_id, creator_url):
        parts = creator_url.split('/')
        service, creator_id = parts[-3], parts[-1]
        domain_config = get_domain_config(creator_url)
        api_url = f"{domain_config['api_base']}/{service}/user/{creator_id}/post/{post_id}"
        max_retries = self.settings.post_data_max_retries
        retry_delay_seconds = 5
        for attempt in range(1, max_retries + 1):
            try:
                headers = HEADERS.copy()
                headers['Referer'] = domain_config['referer']
                response = requests.get(api_url, headers=headers)
                if response.status_code != 200:
                    if response.status_code == 429 and attempt < max_retries:
                        self.log.emit(translate("log_warning", translate("rate_limit_hit", api_url, attempt, max_retries)), "WARNING")
                        for i in range(retry_delay_seconds, 0, -1):
                            self.log.emit(translate("log_info", translate("trying_again_in", i)), "INFO")
                            time.sleep(1)
                        continue
                    self.log.emit(translate("log_error", translate("failed_to_fetch_api", api_url, response.status_code)), "ERROR")
                    return None
                post_data = response.json()
                post = post_data if isinstance(post_data, dict) and 'post' not in post_data else post_data.get('post', {})
                self.log.emit(translate("log_debug", translate("post_data_for_id", post_id, json.dumps(post, indent=2))), "INFO")
                allowed_extensions = [ext.lower() for ext, checkbox in self.creator_ext_checks.items() if checkbox.isChecked()]
                detected_files = self.detect_files(post, allowed_extensions, domain_config)
                files_to_download = [(file_name, file_url) for file_name, file_url in detected_files]
                return (post_id, files_to_download)
            except Exception as e:
                if attempt == max_retries:
                    self.log.emit(translate("log_error", translate("error_fetching_post_max_attempts", post_id, max_retries, str(e))), "ERROR")
                    return None
                self.log.emit(translate("log_warning", translate("error_fetching_post", post_id, attempt, max_retries, str(e))), "WARNING")
                for i in range(retry_delay_seconds, 0, -1):
                    self.log.emit(translate("log_info", translate("trying_again_in", i)), "INFO")
                    time.sleep(1)

    def run(self):
        if not self.is_running:
            return
        files_to_download = []
        files_to_posts_map = {}
        allowed_extensions = [ext.lower() for ext, checkbox in self.creator_ext_checks.items() if checkbox.isChecked()]
        self.log.emit(translate("log_debug", translate("allowed_extensions_for_download", allowed_extensions)), "INFO")

        total_posts = len(self.post_ids)
        completed_posts = 0

        # Find the creator URL(s) associated with these post_ids
        creator_urls = set()
        for creator_url, posts in self.all_files_map.items():
            for _, (post_id, _) in posts:
                if post_id in self.post_ids:
                    creator_urls.add(creator_url)
                    break

        if not creator_urls:
            self.log.emit(translate("log_error", translate("no_matching_creator_urls")), "ERROR")
            self.finished.emit([], {})
            return

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_post = {}
            for creator_url in creator_urls:
                for post_id in self.post_ids:
                    if any(p[1][0] == post_id for p in self.all_files_map.get(creator_url, [])):
                        future_to_post[executor.submit(self.fetch_and_detect_files, post_id, creator_url)] = post_id
            
            for future in as_completed(future_to_post):
                if not self.is_running:
                    break
                result = future.result()
                if result:
                    post_id, detected_files = result
                    for file_name, file_url in detected_files:
                        self.log.emit(translate("log_debug", translate("detected_file", file_name, file_url)), "INFO")
                        files_to_download.append(file_url)
                        files_to_posts_map[file_url] = post_id
                    completed_posts += 1
                    progress = min(int((completed_posts / total_posts) * 100), 100)
                    self.progress.emit(progress)

        if self.is_running:
            files_to_download = list(dict.fromkeys(files_to_download))
            self.log.emit(translate("log_debug", translate("total_files_to_download", len(files_to_download))), "INFO")
            self.finished.emit(files_to_download, files_to_posts_map)

def sanitize_filename(name, max_length=100):
    """Sanitize a filename by removing invalid characters, trailing dots, and limiting length."""
    if not name:
        return "unnamed"
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove trailing dots (Windows compatibility)
    sanitized = sanitized.rstrip('.')
    # Trim leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('.').strip('_')
    # Ensure non-empty
    return sanitized if sanitized else "unnamed"

class CreatorDownloadThread(QThread):
    file_progress = pyqtSignal(int, int) 
    file_completed = pyqtSignal(int, str, bool)  # Added success flag
    post_completed = pyqtSignal(str)
    log = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, service, creator_id, download_folder, selected_posts, files_to_download, files_to_posts_map, console, other_files_dir, post_titles_map, auto_rename_enabled, settings, max_concurrent=20):
        super().__init__()
        self.service = service
        self.creator_id = creator_id
        self.download_folder = download_folder
        self.selected_posts = selected_posts
        self.files_to_download = files_to_download
        self.files_to_posts_map = files_to_posts_map
        self.console = console
        self.settings = settings
        self.is_running = True
        self.other_files_dir = other_files_dir
        self.hash_file_path = os.path.join(self.other_files_dir, "file_hashes.json")
        self.file_hashes = self.load_hashes()
        self.max_concurrent = max_concurrent
        self.post_files_map = self.build_post_files_map()
        self.completed_files = set()
        self.failed_files = {}  # Map file_url to error message
        self.post_titles_map = post_titles_map
        self.creator_name = None
        self.auto_rename_enabled = auto_rename_enabled
        self.post_file_counters = {}  # Track file counter per post for auto-rename
        self.domain_config = self._get_domain_config_from_files()
        # Locks for thread-safe access to shared dictionaries
        self.failed_files_lock = threading.Lock()
        self.post_file_counters_lock = threading.Lock()
        self.completed_files_lock = threading.Lock()
        self.file_hashes_lock = threading.Lock()

    def _get_domain_config_from_files(self):
        """Determine domain configuration from the files to download"""
        if self.files_to_download:
            first_url = self.files_to_download[0]
            return get_domain_config(first_url)
        # Default fallback
        return get_domain_config("https://kemono.cr/")

    def build_post_files_map(self):
        post_files_map = {post_id: [] for post_id in self.selected_posts}
        for file_url in self.files_to_download:
            post_id = self.files_to_posts_map.get(file_url)
            if post_id in post_files_map:
                post_files_map[post_id].append(file_url)
        return post_files_map

    def load_hashes(self):
        os.makedirs(self.other_files_dir, exist_ok=True)
        if os.path.exists(self.hash_file_path):
            try:
                with open(self.hash_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.log.emit(translate("log_error", translate("failed_to_load_file_hashes", str(e))), "ERROR")
                return {}
        return {}

    def save_hashes(self):
        os.makedirs(self.other_files_dir, exist_ok=True)
        try:
            with open(self.hash_file_path, 'w') as f:
                json.dump(self.file_hashes, f, indent=4)
        except IOError as e:
            self.log.emit(translate("log_error", translate("failed_to_save_file_hashes", str(e))), "ERROR")

    def fetch_creator_and_post_info(self):
        """Fetch creator name and retrieve post titles from post_titles_map."""
        profile_url = f"{self.domain_config['api_base']}/{self.service}/user/{self.creator_id}/profile"
        try:
            headers = HEADERS.copy()
            headers['Referer'] = self.domain_config['referer']
            profile_response = requests.get(profile_url, headers=headers, timeout=10)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                self.creator_name = sanitize_filename(profile_data.get('name', 'Unknown_Creator'))
            else:
                self.creator_name = "Unknown_Creator"
                self.log.emit(translate("log_warning", translate("failed_to_fetch_creator_name", self.creator_name)), "WARNING")
        except requests.RequestException as e:
            self.log.emit(translate("log_error", translate("error_fetching_creator_name", str(e))), "ERROR")
            self.creator_name = "Unknown_Creator"

        for post_id in self.selected_posts:
            key = (self.service, self.creator_id, post_id)
            if key not in self.post_titles_map:
                post_url = f"{self.domain_config['api_base']}/{self.service}/user/{self.creator_id}/post/{post_id}"
                try:
                    headers = HEADERS.copy()
                    headers['Referer'] = self.domain_config['referer']
                    response = requests.get(post_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        post_data = response.json()
                        title = post_data.get('title', f"Post_{post_id}")
                        self.post_titles_map[key] = sanitize_filename(title)
                        self.log.emit(translate("log_info", translate("fetched_title_for_post", post_id, title)), "INFO")
                    else:
                        self.post_titles_map[key] = sanitize_filename(f"Post_{post_id}")
                        self.log.emit(translate("log_warning", translate("failed_to_fetch_title_for_post", post_id)), "WARNING")
                except requests.RequestException as e:
                    self.post_titles_map[key] = sanitize_filename(f"Post_{post_id}")
                    self.log.emit(translate("log_error", translate("error_fetching_title_for_post", post_id, str(e))), "ERROR")

    def stop(self):
        self.is_running = False

    async def download_file(self, file_url, folder, file_index, total_files, session):
        if not self.is_running or file_url not in self.files_to_download:
            self.log.emit(translate("log_info", f"Skipping {file_url}"), "INFO")
            return

        post_id = self.files_to_posts_map.get(file_url, self.creator_id)
        key = (self.service, self.creator_id, post_id)
        post_title = self.post_titles_map.get(key, f"Post_{post_id}")
        post_folder_name = f"{post_id}_{post_title}"
        post_folder = os.path.join(folder, post_folder_name)
        try:
            os.makedirs(post_folder, exist_ok=True)
        except OSError as e:
            error_msg = translate("failed_to_create_post_folder", post_folder, str(e))
            self.log.emit(translate("log_error", error_msg), "ERROR")
            with self.failed_files_lock:
                self.failed_files[file_url] = error_msg
            self.file_completed.emit(file_index, file_url, False)
            self.check_post_completion(file_url)
            return

        filename = file_url.split('f=')[-1] if 'f=' in file_url else file_url.split('/')[-1].split('?')[0]

        # Apply auto rename if enabled
        if self.auto_rename_enabled:
            # Initialize counter for this post if not exists
            with self.post_file_counters_lock:
                if post_id not in self.post_file_counters:
                    self.post_file_counters[post_id] = 0

                # Increment counter for this post
                self.post_file_counters[post_id] += 1
                file_counter = self.post_file_counters[post_id]
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1]
            # Get original filename without extension
            original_name = os.path.splitext(filename)[0]
            # Create new filename with counter and original name
            filename = f"{file_counter}_{original_name}{file_ext}"
        
        full_path = os.path.join(post_folder, filename.replace('/', '_'))
        url_hash = hashlib.md5(file_url.encode()).hexdigest()

        with self.file_hashes_lock:
            file_hashes_keys = list(self.file_hashes.keys())

        for hash_key in file_hashes_keys:
            if hash_key == url_hash:
                with self.file_hashes_lock:
                    existing_path = self.file_hashes[hash_key]["file_path"]
                if os.path.exists(existing_path):
                    with open(existing_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    with self.file_hashes_lock:
                        stored_hash = self.file_hashes[hash_key]["file_hash"]
                    if file_hash == stored_hash:
                        self.log.emit(translate("log_info", translate("file_already_downloaded", filename, existing_path)), "INFO")
                        self.file_progress.emit(file_index, 100)
                        self.file_completed.emit(file_index, file_url, True)
                        with self.completed_files_lock:
                            self.completed_files.add(file_url)
                        self.check_post_completion(file_url)
                        return

        self.log.emit(translate("log_info", translate("starting_download", file_index + 1, total_files, file_url, post_folder)), "INFO")
        
        max_retries = self.settings.file_download_max_retries
        file_handle = None
        for attempt in range(1, max_retries + 1):
            try:
                headers = HEADERS.copy()
                headers['Referer'] = self.domain_config['referer']
                async with session.get(file_url, headers=headers, timeout=ClientTimeout(total=3600)) as response:
                    response.raise_for_status()
                    file_size = int(response.headers.get('content-length', 0)) or 1
                    downloaded_size = 0

                    file_handle = open(full_path, 'wb')
                    async for chunk in response.content.iter_chunked(8192):
                        if not self.is_running:
                            file_handle.close()
                            file_handle = None
                            if os.path.exists(full_path):
                                try:
                                    os.remove(full_path)
                                except OSError as e:
                                    self.log.emit(translate("log_error", translate("failed_to_remove_interrupted_file", full_path, str(e))), "ERROR")
                            with self.failed_files_lock:
                                self.failed_files[file_url] = "Download interrupted by user"
                            self.file_completed.emit(file_index, file_url, False)
                            self.check_post_completion(file_url)
                            return
                        if chunk:
                            file_handle.write(chunk)
                            downloaded_size += len(chunk)
                            progress = int((downloaded_size / file_size) * 100)
                            self.file_progress.emit(file_index, progress)
                            if progress == 100:
                                self.file_completed.emit(file_index, file_url, True)

                    file_handle.close()
                    file_handle = None
                    with open(full_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    with self.file_hashes_lock:
                        self.file_hashes[url_hash] = {
                            "file_path": full_path,
                            "file_hash": file_hash,
                            "url": file_url
                        }
                        self.save_hashes()
                    self.log.emit(translate("log_info", translate("successfully_downloaded", full_path)), "INFO")
                    with self.completed_files_lock:
                        self.completed_files.add(file_url)
                    self.file_completed.emit(file_index, file_url, True)
                    self.check_post_completion(file_url)
                    return

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if file_handle:
                    file_handle.close()
                    file_handle = None
                if attempt == max_retries:
                    error_msg = translate("error_downloading_after_retries", file_url, max_retries, str(e))
                    self.log.emit(translate("log_error", error_msg), "ERROR")
                    with self.failed_files_lock:
                        self.failed_files[file_url] = str(e)
                    self.file_progress.emit(file_index, 0)
                    self.file_completed.emit(file_index, file_url, False)
                    self.check_post_completion(file_url)
                    return
                else:
                    self.log.emit(translate("log_warning", translate("download_failed_retrying", file_url, attempt, max_retries, str(e))), "WARNING")
                    await asyncio.sleep(1)
            except Exception as e:
                if file_handle:
                    file_handle.close()
                    file_handle = None
                self.log.emit(translate("log_error", translate("unexpected_error_downloading", file_url, str(e))), "ERROR")
                with self.failed_files_lock:
                    self.failed_files[file_url] = str(e)
                self.file_progress.emit(file_index, 0)
                self.file_completed.emit(file_index, file_url, False)
                self.check_post_completion(file_url)
                return
            finally:
                if file_handle:
                    file_handle.close()
                    file_handle = None

    def check_post_completion(self, file_url):
        post_id = self.files_to_posts_map.get(file_url)
        if post_id in self.post_files_map:
            post_files = self.post_files_map[post_id]
            if all(f in self.completed_files for f in post_files):
                self.post_completed.emit(post_id)

    async def download_worker(self, queue, folder, total_files, session):
        while self.is_running:
            try:
                file_index, file_url = await queue.get()
                await self.download_file(file_url, folder, file_index, total_files, session)
                queue.task_done()
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                self.log.emit(translate("log_error", translate("error_in_download_worker", str(e))), "ERROR")
                queue.task_done()

    def run(self):
        if not self.is_running:
            return
        self.log.emit(translate("log_info", translate("creator_download_thread_started", self.service, self.creator_id)), "INFO")
        self.fetch_creator_and_post_info()
        total_posts = len(self.selected_posts)
        self.log.emit(translate("log_info", translate("total_posts", total_posts)), "INFO")

        creator_folder_name = f"{self.creator_id}_{self.creator_name}"
        creator_folder = os.path.join(self.download_folder, creator_folder_name)
        try:
            os.makedirs(creator_folder, exist_ok=True)
        except OSError as e:
            self.log.emit(translate("log_error", translate("failed_to_create_creator_folder", creator_folder, str(e))), "ERROR")
        self.log.emit(translate("log_info", translate("created_directory", creator_folder)), "INFO")

        total_files = len(self.files_to_download)
        self.log.emit(translate("log_info", translate("total_selected_files_to_download", total_files)), "INFO")

        if total_files > 0:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                queue = asyncio.Queue()
                for i, file_url in enumerate(self.files_to_download):
                    queue.put_nowait((i, file_url))

                async def main():
                    async with ClientSession() as session:
                        tasks = [
                            loop.create_task(self.download_worker(queue, creator_folder, total_files, session))
                            for _ in range(self.max_concurrent)
                        ]
                        await queue.join()
                        await asyncio.gather(*tasks, return_exceptions=True)

                loop.run_until_complete(main())
            except Exception as e:
                self.log.emit(translate("log_error", translate("error_in_async_download_loop", str(e))), "ERROR")
            finally:
                if not loop.is_closed():
                    loop.run_until_complete(loop.shutdown_asyncgens())
                    loop.close()
        else:
            self.log.emit(translate("log_warning", translate("no_files_selected_for_download")), "WARNING")

        # Log summary of failed files
        if self.failed_files:
            self.log.emit(translate("log_warning", translate("download_completed_with_failed_files", len(self.failed_files))), "WARNING")
            for file_url, error in self.failed_files.items():
                self.log.emit(translate("log_error", translate("failed_to_download_file", file_url, error)), "ERROR")

        if self.is_running:
            self.finished.emit()

class ValidationThread(QThread):
    result = pyqtSignal(bool)
    log = pyqtSignal(str, str)

    def __init__(self, url, settings):
        super().__init__()
        self.url = url
        self.settings = settings
        self.is_running = True
        self.domain_config = get_domain_config(url)

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        
        parts = self.url.split('/')
        if len(parts) < 5 or (self.domain_config['domain'] not in self.url) or parts[-2] != 'user':
            self.log.emit(translate("log_error", translate("invalid_url_format_link", self.url)), "ERROR")
            self.result.emit(False)
            return
            
        max_retries = self.settings.api_request_max_retries
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                # Use fallback validation with robust headers
                fallback_headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': accept_language,
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'Referer': self.domain_config['referer']
                }
                
                direct_response = requests.get(self.url, headers=fallback_headers, timeout=10)
                domain_check = self.domain_config['domain'].split('.')[0]  # 'kemono' or 'coomer'
                if direct_response.status_code == 200 and domain_check in direct_response.text.lower():
                    self.log.emit(translate("log_info", translate("successfully_validated_url", self.url)), "INFO")
                    self.result.emit(True)
                    return
                
                if attempt < max_retries:
                    self.log.emit(translate("log_warning", translate("validation_attempt_failed", attempt, retry_delay)), "WARNING")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
            except requests.RequestException as e:
                if attempt < max_retries:
                    
                    self.log.emit(translate("log_warning", translate("network_error_attempt", attempt, str(e))), "WARNING")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    self.log.emit(translate("log_error", translate("failed_to_validate", self.url, max_retries, str(e))), "ERROR")
        
        self.result.emit(False)

class CheckboxToggleThread(QThread):
    finished = pyqtSignal(dict, list)
    log = pyqtSignal(str, str)

    def __init__(self, visible_posts, checked_urls, check_all_state):
        super().__init__()
        self.visible_posts = visible_posts  # Use visible posts instead of all_detected_posts
        self.checked_urls = checked_urls.copy()
        self.check_all_state = check_all_state
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        is_checked = self.check_all_state == 2  # Qt.CheckState.Checked
        new_state = Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
        
        # Only update checked_urls for posts that are currently visible
        affected_post_ids = set()
        for post_title, (post_id, _) in self.visible_posts:
            self.checked_urls[post_id] = (new_state == Qt.CheckState.Checked)
            affected_post_ids.add(post_id)
        
        # Update posts_to_download based on all checked posts, not just visible ones
        posts_to_download = [post_id for post_id, checked in self.checked_urls.items() if checked]
        self.log.emit(translate("log_debug", translate("checkbox_toggle_completed", is_checked, len(affected_post_ids), len(posts_to_download))), "INFO")
        self.finished.emit(self.checked_urls, posts_to_download)

class LogsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(translate("full_logs"))
        self.setModal(False)
        self.resize(800, 600)
        self.setStyleSheet("background: #1A2B4A; color: white;")
        
        layout = QVBoxLayout(self)
        
        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setStyleSheet("background: #2A3B5A; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.logs_display)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.clear_logs_btn = QPushButton(translate("clear_logs"))
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.clear_logs_btn.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        buttons_layout.addWidget(self.clear_logs_btn)
        
        self.download_logs_btn = QPushButton(translate("download_logs"))
        self.download_logs_btn.clicked.connect(self.download_logs)
        self.download_logs_btn.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        buttons_layout.addWidget(self.download_logs_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Update logs content
        self.update_logs_content()
    
    def update_logs_content(self):
        """Update the logs display with current console content"""
        if self.parent and hasattr(self.parent, 'creator_console'):
            self.logs_display.setHtml(self.parent.creator_console.toHtml())
    
    def clear_logs(self):
        """Clear both the logs window and parent console"""
        self.logs_display.clear()
        if self.parent and hasattr(self.parent, 'creator_console'):
            self.parent.creator_console.clear()
    
    def download_logs(self):
        """Download logs as a txt file"""
        from PyQt6.QtWidgets import QFileDialog
        import os
        from datetime import datetime
        
        # Get plain text content (without HTML formatting)
        logs_content = self.logs_display.toPlainText()
        
        if not logs_content.strip():
            return
        
        # Default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"kemono_logs_{timestamp}.txt"
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.windowTitle(),
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(logs_content)
                self.parent.append_log_to_console(f"Logs saved to: {file_path}", "INFO")
            except Exception as e:
                self.parent.append_log_to_console(f"Failed to save logs: {str(e)}", "ERROR")

class CreatorDownloaderTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.posts_to_download = []
        self.post_url_map = {}
        self.all_detected_posts = []
        self.creator_queue = []
        self.downloading = False
        self.current_preview_url = None
        self.previous_selected_widget = None
        self.cache_dir = self.parent.cache_folder
        self.other_files_dir = self.parent.other_files_folder
        self.current_creator_url = None
        self.all_files_map = {}
        self.checked_urls = {}
        self.current_file_index = -1
        self.active_threads = []
        self.completed_posts = set()
        self.total_posts_to_download = 0
        self.total_files_to_download = 0
        self.completed_files = set()
        self.failed_files = {}  # Map file_url to error message
        # Locks for thread-safe access to shared data structures
        self.completed_files_lock = threading.Lock()
        self.failed_files_lock = threading.Lock()
        self.validation_thread = None
        self.post_detection_thread = None
        self.post_population_thread = None
        self.filter_thread = None
        self.file_preparation_thread = None
        self.checkbox_toggle_thread = None
        self.post_titles_map = {}
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.other_files_dir, exist_ok=True)
        self.setup_ui()
        self.parent.settings_tab.settings_applied.connect(self.refresh_ui)
        self.parent.settings_tab.language_changed.connect(self.update_ui_text)

    def _create_thread_settings(self):
        """Create a ThreadSettings object with current settings values"""
        return ThreadSettings(
            creator_posts_max_attempts=self.parent.settings_tab.get_creator_posts_max_attempts(),
            post_data_max_retries=self.parent.settings_tab.get_post_data_max_retries(),
            file_download_max_retries=self.parent.settings_tab.get_file_download_max_retries(),
            api_request_max_retries=self.parent.settings_tab.get_api_request_max_retries(),
            simultaneous_downloads=self.parent.settings_tab.get_simultaneous_downloads()
        )

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left widget
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Creator URL input layout
        creator_url_layout = QHBoxLayout()
        self.creator_url_input = QLineEdit()
        self.creator_url_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        creator_url_layout.addWidget(self.creator_url_input)
        
        self.creator_add_to_queue_btn = QPushButton(qta.icon('fa5s.plus', color='white'), "")
        self.creator_add_to_queue_btn.clicked.connect(self.add_creator_to_queue)
        self.creator_add_to_queue_btn.setStyleSheet("background: #4A5B7A; padding: 5px; border-radius: 5px;")
        creator_url_layout.addWidget(self.creator_add_to_queue_btn)
        left_layout.addLayout(creator_url_layout)

        # Creator Queue Group
        self.creator_queue_group = QGroupBox()
        self.creator_queue_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        creator_queue_layout = QVBoxLayout()
        self.creator_queue_list = QListWidget()
        self.creator_queue_list.setFixedHeight(100)
        self.creator_queue_list.setStyleSheet("background: #2A3B5A; border-radius: 5px;")
        creator_queue_layout.addWidget(self.creator_queue_list)
        self.creator_queue_group.setLayout(creator_queue_layout)
        left_layout.addWidget(self.creator_queue_group)

        # Download Options Group
        self.creator_options_group = QGroupBox()
        self.creator_options_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        creator_options_layout = QVBoxLayout()
        
        creator_categories_layout = QHBoxLayout()
        self.creator_main_check = QCheckBox()
        self.creator_main_check.setChecked(True)
        creator_categories_layout.addWidget(self.creator_main_check)
        self.creator_attachments_check = QCheckBox()
        self.creator_attachments_check.setChecked(True)
        creator_categories_layout.addWidget(self.creator_attachments_check)
        self.creator_content_check = QCheckBox()
        self.creator_content_check.setChecked(True)
        creator_categories_layout.addWidget(self.creator_content_check)
        creator_categories_layout.addStretch()
        creator_options_layout.addLayout(creator_categories_layout)

        # Auto rename checkbox
        self.creator_auto_rename_check = QCheckBox()
        self.creator_auto_rename_check.setChecked(True)  # Default to enabled
        self.creator_auto_rename_check.setStyleSheet("color: white;")
        creator_options_layout.addWidget(self.creator_auto_rename_check)

        self.creator_ext_group = QGroupBox()
        self.creator_ext_group.setStyleSheet("QGroupBox { color: white; }")
        creator_ext_layout = QGridLayout()
        creator_ext_layout.setHorizontalSpacing(20)
        creator_ext_layout.setVerticalSpacing(10)
        self.creator_ext_checks = {
            '.jpg': QCheckBox("JPG/JPEG"),
            '.png': QCheckBox("PNG"),
            '.zip': QCheckBox("ZIP"),
            '.mp4': QCheckBox("MP4"),
            '.gif': QCheckBox("GIF"),
            '.pdf': QCheckBox("PDF"),
            '.7z': QCheckBox("7Z"),
            '.mp3': QCheckBox("MP3"),
            '.wav': QCheckBox("WAV"),
            '.rar': QCheckBox("RAR"),
            '.mov': QCheckBox("MOV"),
            '.docx': QCheckBox("DOCX"),
            '.psd': QCheckBox("PSD"),
            '.clip': QCheckBox("CLIP"),
            '.jpe':QCheckBox("JPE"),
            '.webp':QCheckBox("WEBP")
        }
        for i, (ext, check) in enumerate(self.creator_ext_checks.items()):
            check.setChecked(True)
            check.stateChanged.connect(self.filter_items)
            creator_ext_layout.addWidget(check, i // 5, i % 5)
        self.creator_ext_group.setLayout(creator_ext_layout)
        creator_options_layout.addWidget(self.creator_ext_group)
        self.creator_options_group.setLayout(creator_options_layout)
        left_layout.addWidget(self.creator_options_group)

        # Progress layout
        creator_progress_layout = QVBoxLayout()
        self.creator_file_progress_label = QLabel()
        creator_progress_layout.addWidget(self.creator_file_progress_label)
        self.creator_file_progress = QProgressBar()
        self.creator_file_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #4A5B7A; }")
        self.creator_file_progress.setRange(0, 100)
        creator_progress_layout.addWidget(self.creator_file_progress)
        self.creator_overall_progress_label = QLabel()
        creator_progress_layout.addWidget(self.creator_overall_progress_label)
        self.creator_overall_progress = QProgressBar()
        self.creator_overall_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #4A5B7A; }")
        self.creator_overall_progress.setRange(0, 100)
        creator_progress_layout.addWidget(self.creator_overall_progress)
        left_layout.addLayout(creator_progress_layout)

        # Console
        self.creator_console = QTextEdit()
        self.creator_console.setReadOnly(True)
        self.creator_console.setStyleSheet("background: #2A3B5A; border-radius: 5px; padding: 5px;")
        left_layout.addWidget(self.creator_console)

        # Buttons layout
        creator_btn_layout = QHBoxLayout()
        self.creator_download_btn = QPushButton(qta.icon('fa5s.download', color='white'), "")
        self.creator_download_btn.clicked.connect(self.start_creator_download)
        self.creator_download_btn.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        creator_btn_layout.addWidget(self.creator_download_btn)
        self.creator_cancel_btn = QPushButton(qta.icon('fa5s.times', color='white'), "")
        self.creator_cancel_btn.clicked.connect(self.cancel_creator_download)
        self.creator_cancel_btn.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        self.creator_cancel_btn.setEnabled(False)
        creator_btn_layout.addWidget(self.creator_cancel_btn)
        
        self.creator_expand_logs_btn = QPushButton(qta.icon('fa5s.expand', color='white'), "")
        self.creator_expand_logs_btn.clicked.connect(self.expand_logs)
        self.creator_expand_logs_btn.setStyleSheet("background: #4A5B7A; padding: 8px; border-radius: 5px;")
        self.creator_expand_logs_btn.setToolTip("Expand Logs")
        creator_btn_layout.addWidget(self.creator_expand_logs_btn)
        
        left_layout.addLayout(creator_btn_layout)

        left_layout.addStretch()
        layout.addWidget(left_widget, stretch=2)

        # Right widget
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Posts to Download Group
        self.post_list_group = QGroupBox()
        self.post_list_group.setStyleSheet("QGroupBox { color: white; font-weight: bold; padding: 10px; }")
        post_list_layout = QVBoxLayout()

        self.creator_search_input = QLineEdit()
        self.creator_search_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.creator_search_input.textChanged.connect(self.filter_items)
        post_list_layout.addWidget(self.creator_search_input)

        checkbox_layout = QHBoxLayout()
        self.creator_check_all = QCheckBox()
        self.creator_check_all.setChecked(False)
        self.creator_check_all.setStyleSheet("color: white;")
        self.creator_check_all.stateChanged.connect(self.toggle_check_all)
        checkbox_layout.addWidget(self.creator_check_all)
        post_list_layout.addLayout(checkbox_layout)

        self.creator_post_list = QListWidget()
        self.creator_post_list.setStyleSheet("background: #2A3B5A; border-radius: 5px;")
        self.creator_post_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.creator_post_list.itemClicked.connect(self.handle_item_click)
        self.creator_post_list.currentItemChanged.connect(self.update_current_preview_url)
        post_list_layout.addWidget(self.creator_post_list)

        bottom_layout = QHBoxLayout()
        self.creator_post_count_label = QLabel()
        self.creator_post_count_label.setStyleSheet("color: white;")
        bottom_layout.addWidget(self.creator_post_count_label)

        self.creator_view_button = QPushButton(qta.icon('fa5s.eye', color='white'), "")
        self.creator_view_button.setStyleSheet("background: #4A5B7A; padding: 2px; border-radius: 5px; min-width: 30px; max-width: 30px; min-height: 30px; max-height: 30px;")
        self.creator_view_button.clicked.connect(self.view_current_item)
        self.creator_view_button.setEnabled(False)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.creator_view_button)

        post_list_layout.addLayout(bottom_layout) 
        self.post_list_group.setLayout(post_list_layout)
        right_layout.addWidget(self.post_list_group)

        # Background task indicators
        self.background_task_label = QLabel()
        self.background_task_label.setStyleSheet("color: white;")
        right_layout.addWidget(self.background_task_label)

        self.background_task_progress = QProgressBar()
        self.background_task_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #4A5B7A; }")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        right_layout.addWidget(self.background_task_progress)

        right_layout.addStretch()
        layout.addWidget(right_widget, stretch=1)

        # Button hover animations
        self.creator_download_btn.enterEvent = lambda e: self.parent.animate_button(self.creator_download_btn, True)
        self.creator_download_btn.leaveEvent = lambda e: self.parent.animate_button(self.creator_download_btn, False)
        self.creator_cancel_btn.enterEvent = lambda e: self.parent.animate_button(self.creator_cancel_btn, True)
        self.creator_cancel_btn.leaveEvent = lambda e: self.parent.animate_button(self.creator_cancel_btn, False)

        # Initial text update
        self.update_ui_text()

    def update_ui_text(self):
        self.creator_url_input.setPlaceholderText(translate("enter_creator_url"))
        self.creator_add_to_queue_btn.setText(translate("add_to_queue"))
        
        self.creator_queue_group.setTitle(translate("creator_queue"))
        self.creator_options_group.setTitle(translate("download_options"))
        self.creator_ext_group.setTitle(translate("file_extensions"))
        self.post_list_group.setTitle(translate("posts_to_download"))
        
        self.creator_main_check.setText(translate("main_file"))
        self.creator_attachments_check.setText(translate("attachments"))
        self.creator_content_check.setText(translate("content_images"))
        self.creator_check_all.setText(translate("check_all"))
        self.creator_auto_rename_check.setText(translate("auto_rename"))
        
        self.creator_file_progress_label.setText(translate("file_progress", 0))
        self.creator_overall_progress_label.setText(translate("overall_progress", 0, 0, 0, 0))
        self.creator_post_count_label.setText(translate("posts_count", 0))
        self.background_task_label.setText(translate("idle"))
        
        self.creator_download_btn.setText(translate("download"))
        self.creator_cancel_btn.setText(translate("cancel"))
        self.creator_expand_logs_btn.setText(translate("expand_logs"))
        
        self.creator_search_input.setPlaceholderText(translate("search_posts"))
        
        self.update_creator_queue_list()

    def update_progress_bar_style(self):
        separator_style = "QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #4A5B7A; }"
        self.creator_file_progress.setStyleSheet(separator_style)
        self.creator_overall_progress.setStyleSheet(separator_style)
        self.background_task_progress.setStyleSheet(separator_style)

    def refresh_ui(self):
        self.update_progress_bar_style()
        if not self.downloading:
            self.creator_file_progress.setValue(0)
            self.creator_file_progress_label.setText(translate("file_progress", 0))
            self.creator_overall_progress.setValue(0)
            self.creator_overall_progress_label.setText(translate("overall_progress", 0, 0, 0, 0))
            self.current_file_index = -1
            self.completed_posts.clear()
            self.completed_files.clear()
            self.total_files_to_download = 0
            self.background_task_progress.setRange(0, 100)
            self.background_task_progress.setValue(0)
            self.background_task_label.setText(translate("idle"))

    def add_creator_to_queue(self):
        url = self.creator_url_input.text().strip()
        if not url:
            self.append_log_to_console(translate("log_error", translate("no_url_entered")), "ERROR")
            return
        if any(item[0] == url for item in self.creator_queue):
            self.append_log_to_console(translate("log_warning", translate("url_already_in_queue")), "WARNING")
            return
        if hasattr(self, 'validation_thread') and self.validation_thread is not None and self.validation_thread.isRunning():
            self.append_log_to_console(translate("log_warning", translate("validation_in_progress")), "WARNING")
            return
        self.background_task_label.setText(translate("validating_url"))
        self.background_task_progress.setRange(0, 0)
        self.validation_thread = ValidationThread(url, self._create_thread_settings())
        self.validation_thread.result.connect(lambda valid: self.on_validation_finished(url, valid))
        self.validation_thread.log.connect(self.append_log_to_console)
        self.validation_thread.finished.connect(self.cleanup_validation_thread)
        self.active_threads.append(self.validation_thread)
        self.validation_thread.start()

    def cleanup_validation_thread(self):
        """Clean up the validation thread after it finishes."""
        if self.validation_thread in self.active_threads:
            self.active_threads.remove(self.validation_thread)
        self.validation_thread.deleteLater()
        self.validation_thread = None

    def on_validation_finished(self, url, valid):
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        if valid:
            self.creator_queue.append((url, False))
            self.update_creator_queue_list()
            self.creator_url_input.clear()
            self.append_log_to_console(translate("log_info", translate("added_creator_url", url)), "INFO")
        else:
            self.append_log_to_console(translate("log_error", translate("invalid_creator_url", url)), "ERROR")

    def create_view_handler(self, url, checked):
        def handler():
            self.check_creator_from_queue(url)
        return handler

    def create_remove_handler(self, url):
        def handler():
            reply = QMessageBox.question(self, translate("confirm_removal"), 
                                        translate("confirm_removal_message", url),
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                found = False
                for i, (queue_url, _) in enumerate(self.creator_queue):
                    if queue_url == url:
                        del self.creator_queue[i]
                        found = True
                        break
                if found:
                    self.update_creator_queue_list()
                    self.append_log_to_console(translate("log_info", translate("link_removed", url)), "INFO")
                    if not any(c for _, c in self.creator_queue):
                        self.creator_post_list.clear()
                        self.all_detected_posts = []
                        self.posts_to_download = []
                        self.post_url_map = {}
                        self.checked_urls = {}
                        self.all_files_map = {}
                        self.current_creator_url = None
                        self.previous_selected_widget = None
                        self.update_checked_posts()
                        self.filter_items()
                else:
                    self.append_log_to_console(translate("log_warning", translate("url_not_found", url)), "WARNING")
        return handler

    def update_creator_queue_list(self):
        self.creator_queue_list.clear()
        for url, checked in self.creator_queue:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)

            view_button = QPushButton(qta.icon('fa5s.eye', color='white'), "")
            view_button.setStyleSheet("background: #4A5B7A; padding: 2px; border-radius: 5px; min-width: 30px; max-width: 30px; min-height: 30px; max-height: 30px;")
            view_button.clicked.connect(self.create_view_handler(url, checked))
            layout.addWidget(view_button)

            label = QLabel(url)
            label.setStyleSheet("color: white;")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(label, stretch=1)

            remove_button = QPushButton(qta.icon('fa5s.times', color='white'), "")
            remove_button.setStyleSheet("background: #4A5B7A; padding: 2px; border-radius: 5px; min-width: 30px; max-width: 30px; min-height: 30px; max-height: 30px;")
            remove_button.clicked.connect(self.create_remove_handler(url))
            layout.addWidget(remove_button)

            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.creator_queue_list.addItem(item)
            self.creator_queue_list.setItemWidget(item, widget)
            widget.view_button = view_button
            widget.label = label
            widget.remove_button = remove_button

    def check_creator_from_queue(self, url):
        if not isinstance(url, str):
            self.append_log_to_console(translate("log_error", translate("invalid_url_type", type(url))), "ERROR")
            return
        self.append_log_to_console(translate("log_info", translate("viewing_creator", url)), "INFO")
        
        self.current_creator_url = url
        self.checked_urls.clear()
        self.posts_to_download = []
        
        self.creator_post_list.clear()
        self.previous_selected_widget = None
        
        if url in self.all_files_map:
            self.all_detected_posts = self.all_files_map.get(url, [])
            self.start_population_thread(self.all_detected_posts)
            for i, (queue_url, _) in enumerate(self.creator_queue):
                if queue_url == url:
                    self.creator_queue[i] = (url, True)
                    self.update_creator_queue_list()
                    break
        else:
            if hasattr(self, 'post_detection_thread') and self.post_detection_thread is not None and self.post_detection_thread.isRunning():
                self.append_log_to_console(translate("log_warning", translate("post_detection_in_progress")), "WARNING")
                return
            self.background_task_label.setText(translate("detecting_posts"))
            self.background_task_progress.setRange(0, 0)
            self.post_detection_thread = PostDetectionThread(url, self.post_titles_map, self._create_thread_settings())
            self.post_detection_thread.finished.connect(self.on_post_detection_finished)
            self.post_detection_thread.log.connect(self.append_log_to_console)
            self.post_detection_thread.error.connect(self.on_post_detection_error)
            self.post_detection_thread.finished.connect(self.cleanup_post_detection_thread) 
            self.active_threads.append(self.post_detection_thread)
            self.post_detection_thread.start()
            
    def cleanup_post_detection_thread(self):
        """Clean up the post detection thread after it finishes."""
        if self.post_detection_thread in self.active_threads:
            self.active_threads.remove(self.post_detection_thread)
        self.post_detection_thread = None  
            
    def on_post_detection_finished(self, detected_posts):
        self.all_files_map[self.current_creator_url] = detected_posts
        self.all_detected_posts = detected_posts
        self.start_population_thread(self.all_detected_posts)

    def start_population_thread(self, detected_posts):
        self.background_task_label.setText(translate("populating_posts"))
        self.background_task_progress.setRange(0, 0)
        self.post_population_thread = PostPopulationThread(detected_posts)
        self.post_population_thread.finished.connect(self.on_post_population_finished)
        self.post_population_thread.log.connect(self.append_log_to_console)
        self.active_threads.append(self.post_population_thread)
        self.post_population_thread.start()

    def on_post_population_finished(self, post_url_map, all_detected_posts):
        self.post_url_map = post_url_map
        self.all_detected_posts = all_detected_posts
        for post_title, (post_id, thumbnail_url) in self.all_detected_posts:
            self.checked_urls[post_id] = False
        for i, (queue_url, _) in enumerate(self.creator_queue):
            if queue_url == self.current_creator_url:
                self.creator_queue[i] = (self.current_creator_url, True)
                self.update_creator_queue_list()
                break
        self.filter_items()
        self.append_log_to_console(translate("log_debug", translate("populated_posts_for_creator", len(self.all_detected_posts), self.current_creator_url)), "INFO")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))

    def on_post_detection_error(self, error_message):
        self.append_log_to_console(translate("log_error", error_message), "ERROR")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        if hasattr(self, 'post_detection_thread') and self.post_detection_thread is not None:
            self.cleanup_post_detection_thread()

    def start_creator_download(self):
        if not self.creator_queue:
            self.append_log_to_console(translate("log_warning", translate("no_creators_queue")), "WARNING")
            return

        if not self.posts_to_download:
            self.append_log_to_console(translate("log_warning", translate("no_posts_selected")), "WARNING")
            return

        self.downloading = True
        self.parent.tabs.setTabEnabled(0, False)
        self.parent.status_label.setText(translate("preparing_files"))
        self.creator_download_btn.setEnabled(False)
        self.creator_cancel_btn.setEnabled(True)
        self.creator_overall_progress.setValue(0)
        self.total_posts_to_download = len(self.posts_to_download)
        self.completed_posts.clear()
        self.completed_files.clear()
        self.total_files_to_download = 0
        self.creator_overall_progress_label.setText(translate("overall_progress", 0, 0, 0, self.total_posts_to_download))
        self.current_file_index = -1
        self.creator_file_progress.setValue(0)
        self.creator_file_progress_label.setText(translate("file_progress", 0))
        self.update_progress_bar_style()

        self.background_task_label.setText(translate("preparing_files"))
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)

        if not self.current_creator_url:
            self.append_log_to_console(translate("log_warning", translate("no_creator_viewed")), "WARNING")
            self.creator_download_finished()
            return
        urls = [self.current_creator_url]
        self.append_log_to_console(translate("log_info", translate("preparing_files_creator", self.current_creator_url)), "INFO")

        self.append_log_to_console(translate("log_info", translate("posts_to_download_num", self.posts_to_download)), "INFO")
        self.prepare_files_for_download(urls)

    def prepare_files_for_download(self, urls):
        if hasattr(self, 'file_preparation_thread') and self.file_preparation_thread is not None and self.file_preparation_thread.isRunning():
            self.append_log_to_console(translate("log_warning", translate("file_preparation_in_progress")), "WARNING")
            return

        if not self.current_creator_url:
            self.append_log_to_console(translate("log_warning", translate("no_creator_viewed")), "WARNING")
            self.creator_download_finished()
            return
        current_creator_posts = {post_id for _, (post_id, _) in self.all_files_map.get(self.current_creator_url, [])}
        post_ids = [post_id for post_id in self.posts_to_download if post_id in current_creator_posts]
        if set(post_ids) != set(self.posts_to_download):
            self.append_log_to_console(translate("log_error", translate("post_id_mismatch", self.posts_to_download, post_ids)), "ERROR")

        if not post_ids:
            self.append_log_to_console(translate("log_warning", translate("no_posts_available")), "WARNING")
            self.background_task_progress.setRange(0, 100)
            self.background_task_progress.setValue(0)
            self.background_task_label.setText(translate("idle"))
            self.creator_download_finished()
            return

        self.file_preparation_thread = FilePreparationThread(
            post_ids,
            self.all_files_map,
            self.creator_ext_checks,
            self.creator_main_check.isChecked(),
            self.creator_attachments_check.isChecked(),
            self.creator_content_check.isChecked(),
            self._create_thread_settings(),
            max_concurrent=5
        )
        self.file_preparation_thread.progress.connect(self.update_background_progress)
        self.file_preparation_thread.finished.connect(lambda files, files_map: self.on_file_preparation_finished(urls, files, files_map))
        self.file_preparation_thread.log.connect(self.append_log_to_console)
        self.file_preparation_thread.error.connect(self.on_file_preparation_error)
        self.active_threads.append(self.file_preparation_thread)
        self.file_preparation_thread.start()

    def cleanup_file_preparation_thread(self):
        """Clean up the file preparation thread after it finishes."""
        if self.file_preparation_thread is not None and self.file_preparation_thread in self.active_threads:
            self.active_threads.remove(self.file_preparation_thread)
            self.file_preparation_thread.deleteLater()
        self.file_preparation_thread = None

    def update_background_progress(self, value):
        self.background_task_progress.setValue(value)

    def on_file_preparation_finished(self, urls, files_to_download, files_to_posts_map):
        self.total_files_to_download = len(files_to_download)
        self.append_log_to_console(translate("log_debug", translate("prepared_files_for_download", self.total_files_to_download)), "INFO")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))

        if not files_to_download:
            self.append_log_to_console(translate("log_warning", translate("no_files_detected")), "WARNING")
            self.process_next_creator(urls[1:] if len(urls) > 1 else [])
            return

        url = urls[0]
        remaining_urls = urls[1:]
        parts = url.split('/')
        service, creator_id = parts[-3], parts[-1]

        self.creator_overall_progress_label.setText(
            translate("overall_progress", 0, self.total_files_to_download, 0, self.total_posts_to_download)
        )
        settings = self._create_thread_settings()
        thread = CreatorDownloadThread(service, creator_id, self.parent.download_folder,
                                    self.posts_to_download, files_to_download, files_to_posts_map,
                                    self.creator_console, self.other_files_dir, self.post_titles_map,
                                    self.creator_auto_rename_check.isChecked(), settings, settings.simultaneous_downloads)
        thread.file_progress.connect(self.update_creator_file_progress)
        thread.file_completed.connect(self.update_file_completion)
        thread.post_completed.connect(self.update_post_completion)
        thread.log.connect(self.append_log_to_console)
        thread.finished.connect(lambda: self.cleanup_thread(thread, remaining_urls))
        self.active_threads.append(thread)
        thread.start()

    def on_file_preparation_error(self, error_message):
        self.append_log_to_console(translate("log_error", error_message), "ERROR")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        self.cleanup_file_preparation_thread()
        self.creator_download_finished()

    def process_next_creator(self, remaining_urls):
        """Process the next creator or finish if no more remain."""
        if not remaining_urls:
            self.creator_download_finished()
            return
        url = remaining_urls[0]
        new_remaining_urls = remaining_urls[1:]
        self.append_log_to_console(translate("log_info", translate("moving_to_next_creator", url)), "INFO")
        self.completed_files.clear()
        self.completed_posts.clear()
        self.prepare_files_for_download([url] + new_remaining_urls)

    def cleanup_thread(self, thread, remaining_urls):
        """Clean up a download thread and proceed to the next creator or finish."""
        if thread in self.active_threads:
            self.active_threads.remove(thread)
            self.append_log_to_console(translate("log_debug", translate("remove_thread", thread.__class__.__name__)), "INFO")
            # Transfer failed files from thread to tab
            if isinstance(thread, CreatorDownloadThread):
                self.failed_files.update(thread.failed_files)
                self.append_log_to_console(translate("log_debug", translate("transferred_from", len(thread.failed_files), thread.__class__.__name__)), "INFO")
        
        # Check if all files for the current creator have been attempted
        if self.total_files_to_download > 0 and len(self.completed_files) + len(self.failed_files) >= self.total_files_to_download:
            self.append_log_to_console(translate("log_debug", translate("all_files_attempted_for_creator")), "INFO")
            # Clear any remaining active threads
            for t in self.active_threads[:]:
                try:
                    if t.isRunning():
                        t.terminate()
                        t.wait()
                        self.append_log_to_console(translate("log_info", translate("terminated_lingering_thread", t.__class__.__name__)), "INFO")
                    self.active_threads.remove(t)
                    t.deleteLater()
                except RuntimeError:
                    self.append_log_to_console(translate("log_warning", translate("thread_already_deleted", t.__class__.__name__)), "WARNING")
            self.active_threads.clear()
            # If there are remaining URLs, process the next creator; otherwise, finish
            if remaining_urls:
                self.process_next_creator(remaining_urls)
            else:
                self.creator_download_finished()
        elif not self.active_threads and not remaining_urls:
            self.append_log_to_console(translate("log_debug", translate("no_more_active_threads")), "INFO")
            self.creator_download_finished()
        else:
            self.append_log_to_console(translate("log_debug", translate("waiting_for_remaining_files", len(self.completed_files), self.total_files_to_download, len(self.failed_files), len(self.active_threads))),"INFO")

    def cancel_creator_download(self):
        if not self.active_threads:
            self.append_log_to_console(translate("log_warning", translate("no_active_downloads_to_cancel")), "WARNING")
            return

        self.append_log_to_console(translate("log_warning", translate("all_downloads_cancelled")), "WARNING")
        self.background_task_label.setText(translate("cancelling_downloads"))
        self.background_task_progress.setRange(0, 0)

        # Start cancellation thread to handle cleanup
        cancellation_thread = CancellationThread(self.active_threads[:])
        cancellation_thread.finished.connect(self.on_cancellation_finished)
        cancellation_thread.log.connect(self.append_log_to_console)
        self.active_threads.append(cancellation_thread)
        cancellation_thread.start()
        
    def on_cancellation_finished(self):
        threads_to_delete = self.active_threads[:]
        self.active_threads = []
        for thread in threads_to_delete:
            try:
                self.append_log_to_console(translate("log_debug", translate("deleting_thread", thread.__class__.__name__)), "INFO")
                thread.deleteLater()
            except RuntimeError:
                self.append_log_to_console(translate("log_warning", translate("thread_already_deleted", thread.__class__.__name__)), "WARNING")

        self.creator_file_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #D4A017; }")
        self.creator_overall_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: #D4A017; }")
        self.creator_file_progress_label.setText(translate("downloads_terminated"))
        self.creator_overall_progress_label.setText(translate("downloads_terminated"))
        self.downloading = False
        self.parent.tabs.setTabEnabled(0, True)
        self.parent.status_label.setText(translate("idle"))
        self.creator_download_btn.setEnabled(True)
        self.creator_cancel_btn.setEnabled(False)
        self.total_files_to_download = 0
        self.completed_files.clear()
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        self.file_preparation_thread = None
        self.post_detection_thread = None
        self.post_population_thread = None
        self.filter_thread = None
        self.checkbox_toggle_thread = None
        self.validation_thread = None

    def update_creator_file_progress(self, file_index, progress):
        if self.current_file_index == file_index or self.current_file_index == -1:
            self.current_file_index = file_index
            self.creator_file_progress.setValue(progress)
            self.creator_file_progress_label.setText(translate("file_progress", progress))

    def update_file_completion(self, file_index, file_url, success):
        """Update file completion status and check overall progress."""
        with self.completed_files_lock, self.failed_files_lock:
            if file_url not in self.completed_files and file_url not in self.failed_files:
                if success:
                    self.completed_files.add(file_url)
                self.append_log_to_console(translate("log_debug", translate("file_completed", file_url, len(self.completed_files), self.total_files_to_download)), "INFO")
            else:
                # Find the CreatorDownloadThread to get the error message
                error_message = "Unknown error"
                for thread in self.active_threads:
                    if isinstance(thread, CreatorDownloadThread):
                        error_message = thread.failed_files.get(file_url, "Unknown error")
                        break
                self.failed_files[file_url] = error_message
                self.append_log_to_console(translate("log_debug", translate("file_failed", file_url, len(self.failed_files))), "INFO")
            self.update_overall_progress()
            # Check if all files have been attempted (successful or failed)
            if self.total_files_to_download > 0 and len(self.completed_files) + len(self.failed_files) >= self.total_files_to_download:
                self.append_log_to_console(translate("log_debug", translate("all_files_attempted")), "INFO")
                self.creator_download_finished()
        if self.current_file_index == file_index:
            self.current_file_index = -1
            self.creator_file_progress.setValue(0)
            self.creator_file_progress_label.setText(translate("file_progress", 0))

    def update_overall_progress(self):
        """Update the overall progress bar and label."""
        if self.total_files_to_download > 0:
            completed_count = len(self.completed_files)
            percentage = int((completed_count / self.total_files_to_download) * 100)
            self.creator_overall_progress.setValue(percentage)
            self.append_log_to_console(translate("log_debug", translate("overall_progress_updated", completed_count, self.total_files_to_download, percentage)), "INFO")

            self.creator_overall_progress_label.setText(
                translate("overall_progress", completed_count, self.total_files_to_download, len(self.completed_posts), self.total_posts_to_download)
            )
        else:
            self.creator_overall_progress.setValue(0)
            self.creator_overall_progress_label.setText(
                translate("overall_progress", 0, 0, len(self.completed_posts), self.total_posts_to_download)
            )

    def update_post_completion(self, post_id):
        """Update post completion status and check overall progress."""
        self.completed_posts.add(post_id)
        self.append_log_to_console(translate("log_info", translate("post_fully_downloaded", post_id)), "INFO")
        self.update_overall_progress()
        if len(self.completed_posts) == self.total_posts_to_download and self.total_files_to_download == len(self.completed_files):
            self.append_log_to_console(translate("log_debug", translate("all_posts_and_files_completed")), "INFO")

    def creator_download_finished(self):
        """Reset UI state after download completes or is cancelled."""
        self.downloading = False
        self.parent.tabs.setTabEnabled(0, True)
        self.parent.status_label.setText(translate("idle"))
        self.creator_download_btn.setEnabled(True)
        self.creator_cancel_btn.setEnabled(False)
        
        # Log summary of failed files
        if self.failed_files:
            self.append_log_to_console(translate("log_warning", translate("download_completed_with_failed_files", len(self.failed_files))), "WARNING")
            for file_url, error in self.failed_files.items():
                self.append_log_to_console(translate("log_error", translate("download_file_failed_with_error", file_url, error)), "ERROR")
        
        self.append_log_to_console(translate("log_info", translate("download_process_completed")), "INFO")
        
        # Always show Downloads Complete, even if some files failed
        self.creator_file_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: green; }")
        self.creator_overall_progress.setStyleSheet("QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; } QProgressBar::chunk { background: green; }")
        self.creator_file_progress_label.setText(translate("downloads_complete"))
        self.creator_overall_progress_label.setText(translate("downloads_complete"))
        
        self.total_files_to_download = 0
        self.completed_files.clear()
        self.failed_files.clear()
        self.completed_posts.clear()
        self.current_file_index = -1
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        self.file_preparation_thread = None
        self.post_detection_thread = None
        self.post_population_thread = None
        self.filter_thread = None
        self.checkbox_toggle_thread = None
        self.validation_thread = None

    def expand_logs(self):
        """Open the full logs window"""
        if not hasattr(self, 'logs_window') or not self.logs_window.isVisible():
            self.logs_window = LogsWindow(self)
            self.logs_window.show()
        else:
            self.logs_window.raise_()
            self.logs_window.activateWindow()
            self.logs_window.update_logs_content()

    def toggle_check_all(self, state):
        if hasattr(self, 'checkbox_toggle_thread') and self.checkbox_toggle_thread is not None and self.checkbox_toggle_thread.isRunning():
            self.append_log_to_console(translate("log_warning", translate("checkbox_toggle_already_in_progress")), "WARNING")
            return
        
        # Get the currently visible posts from creator_post_list
        visible_posts = []
        for i in range(self.creator_post_list.count()):
            item = self.creator_post_list.item(i)
            if not item.isHidden():  # Only include visible items
                post_title = self.creator_post_list.itemWidget(item).label.text()
                post_id, thumbnail_url = self.post_url_map.get(post_title, (None, None))
                if post_id:
                    visible_posts.append((post_title, (post_id, thumbnail_url)))

        if not visible_posts:
            self.append_log_to_console(translate("log_warning", translate("no_visible_posts_to_toggle")), "WARNING")
            return

        self.background_task_label.setText(translate("updating_checkboxes"))
        self.background_task_progress.setRange(0, 0)
        self.checkbox_toggle_thread = CheckboxToggleThread(visible_posts, self.checked_urls, state)
        self.checkbox_toggle_thread.finished.connect(self.on_toggle_check_all_finished)
        self.checkbox_toggle_thread.log.connect(self.append_log_to_console)
        self.checkbox_toggle_thread.finished.connect(self.cleanup_checkbox_toggle_thread)
        self.active_threads.append(self.checkbox_toggle_thread)
        self.checkbox_toggle_thread.start()

    def cleanup_checkbox_toggle_thread(self):
        """Clean up the checkbox toggle thread after it finishes."""
        if self.checkbox_toggle_thread in self.active_threads:
            self.active_threads.remove(self.checkbox_toggle_thread)
        self.checkbox_toggle_thread.deleteLater()
        self.checkbox_toggle_thread = None

    def on_toggle_check_all_finished(self, checked_urls, posts_to_download):
        self.checked_urls = checked_urls
        self.posts_to_download = posts_to_download
        self.filter_items()
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        visible_count = sum(1 for i in range(self.creator_post_list.count()) if not self.creator_post_list.item(i).isHidden())
        self.append_log_to_console(translate("log_debug", translate("checkbox_toggle_finished", len(self.posts_to_download), visible_count)), "INFO")

    def update_checked_posts(self):
        self.posts_to_download = []
        seen_ids = set()
        if not self.current_creator_url:
            self.append_log_to_console(translate("log_warning", translate("no_current_creator_url_set")), "WARNING")
            return
        current_creator_posts = {post_id for _, (post_id, _) in self.all_files_map.get(self.current_creator_url, [])}
        for post_id, is_checked in self.checked_urls.items():
            if is_checked and post_id in current_creator_posts and post_id not in seen_ids:
                self.posts_to_download.append(post_id)
                seen_ids.add(post_id)
        if not self.posts_to_download and current_creator_posts:
            self.append_log_to_console(translate("log_warning", translate("no_posts_selected_for_creator", self.current_creator_url, self.checked_urls)), "WARNING")
        self.creator_post_count_label.setText(translate("posts_count", len(self.posts_to_download)))
        self.append_log_to_console(translate("log_debug", translate("updated_checked_posts_count", len(self.posts_to_download), len(self.checked_urls), len(self.all_detected_posts), self.posts_to_download)), "INFO")

    def filter_items(self):
        if hasattr(self, 'filter_thread') and self.filter_thread is not None and self.filter_thread.isRunning():
            self.append_log_to_console(translate("log_warning", translate("filtering_already_in_progress")), "WARNING")
            return
        self.background_task_label.setText(translate("filtering_posts"))
        self.background_task_progress.setRange(0, 0)
        self.filter_thread = FilterThread(self.all_detected_posts, self.checked_urls, self.creator_search_input.text())
        self.filter_thread.finished.connect(self.on_filter_finished)
        self.filter_thread.log.connect(self.append_log_to_console)
        self.filter_thread.finished.connect(self.cleanup_filter_thread)
        self.active_threads.append(self.filter_thread)
        self.filter_thread.start()

    def on_filter_finished(self, filtered_items):
        self.creator_post_list.clear()
        self.previous_selected_widget = None
        self.post_url_map = {}
        for post_title, post_id, thumbnail_url, is_checked in filtered_items:
            unique_title = f"{post_title} (ID: {post_id})"
            self.post_url_map[unique_title] = (post_id, thumbnail_url)
            self.add_list_item(unique_title, thumbnail_url, is_checked)

        self.update_check_all_state()
        self.update_checked_posts()
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))
        self.append_log_to_console(translate("log_debug", translate("filtering_completed_displayed_posts", self.creator_post_list.count())), "INFO")

    def cleanup_filter_thread(self):
        """Clean up the filter thread after it finishes."""
        if self.filter_thread in self.active_threads:
            self.active_threads.remove(self.filter_thread)
        self.filter_thread.deleteLater()
        self.filter_thread = None
            
    def add_list_item(self, text, url, is_checked):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, url)  
        post_id = self.post_url_map[text][0]
        item.setData(Qt.UserRole + 1, post_id) 
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        check_box = QCheckBox()
        check_box.setStyleSheet("color: white;")
        check_box.setChecked(is_checked)
        check_box.clicked.connect(lambda: self.toggle_checkbox_state(text))
        layout.addWidget(check_box)

        label = QLabel(text)
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label, stretch=1)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        check_box = QCheckBox()
        check_box.setStyleSheet("color: white;")
        check_box.setChecked(is_checked)
        check_box.clicked.connect(lambda: self.toggle_checkbox_state(text))
        layout.addWidget(check_box)

        label = QLabel(text)
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label, stretch=1)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.creator_post_list.addItem(item)
        self.creator_post_list.setItemWidget(item, widget)
        widget.check_box = check_box
        widget.label = label
        widget.setStyleSheet("background-color: #2A3B5A; border-radius: 5px;")

    def toggle_checkbox_state(self, post_title):
        self.background_task_label.setText(translate("toggling_checkbox"))
        self.background_task_progress.setRange(0, 0)
        post_id, thumbnail_url = self.post_url_map.get(post_title, (None, None))
        if not post_id:
            self.append_log_to_console(translate("log_error", translate("no_post_id_found_for_title", post_title)), "ERROR")
            self.background_task_progress.setRange(0, 100)
            self.background_task_progress.setValue(0)
            self.background_task_label.setText(translate("idle"))
            return
        current_state = self.checked_urls.get(post_id, False)
        new_state = not current_state
        self.checked_urls[post_id] = new_state
        widget = self.get_widget_for_post_title(post_title)
        if widget:
            widget.check_box.blockSignals(True)
            widget.check_box.setChecked(new_state)
            widget.check_box.blockSignals(False)
        self.update_checked_posts()
        self.update_check_all_state()
        self.append_log_to_console(translate("log_debug", translate("checkbox_toggled_for_post", post_title, post_id, new_state)), "INFO")
        self.background_task_progress.setRange(0, 100)
        self.background_task_progress.setValue(0)
        self.background_task_label.setText(translate("idle"))

    def get_widget_for_post_title(self, post_title):
        for i in range(self.creator_post_list.count()):
            item = self.creator_post_list.item(i)
            widget = self.creator_post_list.itemWidget(item)
            if widget and widget.label.text() == post_title:
                return widget
        return None

    def update_check_all_state(self):
        all_visible_checked = all(
            self.creator_post_list.itemWidget(self.creator_post_list.item(i)).check_box.isChecked()
            for i in range(self.creator_post_list.count()) if not self.creator_post_list.item(i).isHidden()
        ) and self.creator_post_list.count() > 0
        self.creator_check_all.blockSignals(True)
        self.creator_check_all.setChecked(all_visible_checked)
        self.creator_check_all.blockSignals(False)
        self.append_log_to_console(translate("log_debug", translate("check_all_state_updated", all_visible_checked)), "INFO")

    def update_current_preview_url(self, current, previous):
        if current:
            widget = self.creator_post_list.itemWidget(current)
            if widget:
                self.current_preview_url = current.data(Qt.UserRole)
                self.creator_view_button.setEnabled(True)
            else:
                self.current_preview_url = None
                self.creator_view_button.setEnabled(False)
        else:
            self.current_preview_url = None
            self.creator_view_button.setEnabled(False)

    def view_current_item(self):
        if self.current_preview_url:
            if self.current_preview_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                modal = ImageModal(self.current_preview_url, self.cache_dir, self)
                modal.exec()
            else:
                self.append_log_to_console(translate("log_warning", translate("viewing_not_supported_for_url", self.current_preview_url)), "WARNING")

    def handle_item_click(self, item):
        if item:
            if self.previous_selected_widget:
                self.previous_selected_widget.setStyleSheet("background-color: #2A3B5A; border-radius: 5px;")
            widget = self.creator_post_list.itemWidget(item)
            if widget:
                widget.setStyleSheet("background-color: #4A5B7A; border-radius: 5px;")
                self.previous_selected_widget = widget
                self.current_preview_url = item.data(Qt.UserRole)
                self.creator_view_button.setEnabled(True)
            else:
                self.current_preview_url = None
                self.creator_view_button.setEnabled(False)
        else:
            if self.previous_selected_widget:
                self.previous_selected_widget.setStyleSheet("background-color: #2A3B5A; border-radius: 5px;")
                self.previous_selected_widget = None
            self.current_preview_url = None
            self.creator_view_button.setEnabled(False)

    def append_log_to_console(self, message, level="INFO"):
        color = {"INFO": "green", "WARNING": "yellow", "ERROR": "red"}.get(level, "white")
        self.creator_console.append(f"<span style='color:{color}'>{message}</span>")
        
        if hasattr(self, 'logs_window') and self.logs_window.isVisible():
            self.logs_window.update_logs_content()

class CancellationThread(QThread):
    finished = pyqtSignal()
    log = pyqtSignal(str, str)

    def __init__(self, threads):
        super().__init__()
        self.threads = threads
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        self.log.emit(translate("log_info", translate("starting_cancellation_of_active_threads")), "INFO")
        # Signal all threads to stop
        for thread in self.threads:
            if hasattr(thread, 'stop'):
                try:
                    thread.stop()
                    self.log.emit(translate("log_debug", translate("signaled_stop_for_thread", thread.__class__.__name__)), "INFO")
                except RuntimeError:
                    self.log.emit(translate("log_warning", translate("thread_already_deleted", thread.__class__.__name__)), "WARNING")

        
        # Wait for threads to exit gracefully
        timeout = 5.0  # Maximum wait time in seconds
        start_time = time.time()
        while any(thread.isRunning() for thread in self.threads if hasattr(thread, 'isRunning')) and time.time() - start_time < timeout:
            try:
                time.sleep(0.1)  # Short sleep to avoid freezing
            except RuntimeError:
                self.log.emit(translate("log_warning", translate("thread_deleted_during_cancellation_wait")), "WARNING")
        
        # Log any threads that are still running
        for thread in self.threads:
            try:
                if hasattr(thread, 'isRunning') and thread.isRunning():
                    self.log.emit(translate("log_warning", translate("thread_not_exited_gracefully", thread.__class__.__name__)), "WARNING")
                    try:
                        thread.terminate()
                        thread.wait()
                        self.log.emit(translate("log_info", translate("terminated_thread", thread.__class__.__name__)), "INFO")
                    except RuntimeError:
                        self.log.emit(translate("log_warning", translate("thread_already_deleted_during_termination", thread.__class__.__name__)), "WARNING")
            except RuntimeError:
                self.log.emit(translate("log_warning", translate("thread_already_deleted", thread.__class__.__name__)), "WARNING")

        self.log.emit(translate("log_info", translate("cancellation_process_completed")), "INFO")

        if self.is_running:
            self.finished.emit()
