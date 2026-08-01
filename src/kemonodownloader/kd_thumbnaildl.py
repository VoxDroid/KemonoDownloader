from __future__ import annotations

import concurrent.futures
import hashlib
import os
import re
import time
import urllib.parse
from typing import Dict, List, Optional, Tuple

import qtawesome as qta
from bs4 import BeautifulSoup
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.creator_downloader import get_session
from kemonodownloader.domain_config import get_domain_config
from kemonodownloader.kd_language import translate
from kemonodownloader.post_downloader import MediaPreviewModal

SUPPORTED_THUMBNAIL_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def _sanitize(name: str, max_length: int = 100) -> str:
    """Sanitize a string for use as a folder/filename component."""
    if not name:
        return "unnamed"
    s = re.sub(r'[<>:"/\\|?*]', "_", str(name))
    s = s.replace(" ", "_")
    s = re.sub(r"_+", "_", s)
    s = s.strip("_. ")
    return s[:max_length] or "unnamed"


def make_thumbnail_url(raw_path_or_url: str, domain: str) -> str:
    """Convert a post file path, attachment path, or raw URL to a thumbnail URL for the given domain."""
    if not raw_path_or_url:
        return ""

    raw = str(raw_path_or_url).strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlparse(raw)
        path = parsed.path
        if (
            "img." in parsed.netloc or parsed.netloc.startswith("img.")
        ) and "/thumbnail/" in path:
            return raw
    else:
        path = raw

    if not path.startswith("/"):
        path = "/" + path

    if path.startswith("/data/"):
        thumb_path = "/thumbnail" + path
    elif path.startswith("/thumbnail/"):
        thumb_path = path
    else:
        thumb_path = "/thumbnail/data/" + path.lstrip("/")

    clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    return f"https://img.{clean_domain}{thumb_path}"


def classify_url(url: str) -> str:
    """Classify URL as 'post', 'creator', 'thumbnail', or 'invalid'."""
    url = url.strip()
    if not url:
        return "invalid"

    if "/thumbnail/data/" in url or "img." in url:
        return "thumbnail"

    post_match = re.search(
        r"https?://(?:www\.)?[^/]+/([^/]+)/user/([^/]+)/post/([^/\?\#]+)", url
    )
    if post_match:
        return "post"

    creator_match = re.search(r"https?://(?:www\.)?[^/]+/([^/]+)/user/([^/\?\#]+)", url)
    if creator_match:
        return "creator"

    return "invalid"


def parse_post_url(url: str) -> Optional[Tuple[str, str, str, str]]:
    """Parse post URL into (domain, service, user_id, post_id)."""
    domain_cfg = get_domain_config(url)
    domain = domain_cfg.get("domain", "kemono.cr")
    m = re.search(
        r"https?://(?:www\.)?[^/]+/([^/]+)/user/([^/]+)/post/([^/\?\#]+)", url
    )
    if m:
        return domain, m.group(1), m.group(2), m.group(3)
    return None


def parse_creator_url(url: str) -> Optional[Tuple[str, str, str]]:
    """Parse creator URL into (domain, service, user_id)."""
    domain_cfg = get_domain_config(url)
    domain = domain_cfg.get("domain", "kemono.cr")
    m = re.search(r"https?://(?:www\.)?[^/]+/([^/]+)/user/([^/\?\#]+)", url)
    if m:
        return domain, m.group(1), m.group(2)
    return None


class ThumbnailDetectionThread(QThread):
    batch_received = pyqtSignal(list)
    detection_finished = pyqtSignal(list)
    log_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, urls: List[str], mode: str, settings_tab=None):
        super().__init__()
        self.urls = urls
        self.mode = mode  # "post" or "creator"
        self.settings_tab = settings_tab
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        all_detected: List[Tuple[str, str, List[str]]] = (
            []
        )  # (title, post_id, thumb_urls)
        session = get_session(self.settings_tab)
        from kemonodownloader.post_downloader import get_headers

        for url in self.urls:
            if self.is_cancelled:
                break

            url_type = classify_url(url)
            domain_cfg = get_domain_config(url)
            req_headers = get_headers().copy()
            req_headers["Referer"] = domain_cfg.get("referer", "https://kemono.cr/")

            self.log_message.emit(f"{translate('detecting_thumbnails')} ({url})")

            if url_type == "thumbnail":
                filename = os.path.basename(urllib.parse.urlparse(url).path)
                title = f"Thumbnail ({filename})"
                item = (title, "direct", [url])
                all_detected.append(item)
                self.batch_received.emit([item])
                continue

            if url_type == "post" or (url_type != "creator" and self.mode == "post"):
                parsed = parse_post_url(url)
                if not parsed:
                    self.log_message.emit(f"Invalid post URL: {url}")
                    continue
                domain, service, user_id, post_id = parsed
                api_url = (
                    f"https://{domain}/api/v1/{service}/user/{user_id}/post/{post_id}"
                )
                creator_name = self._fetch_creator_name(
                    session, domain, service, user_id, req_headers
                )

                try:
                    res = session.get(api_url, headers=req_headers, timeout=15)
                    if res.status_code == 200:
                        post_data = res.json()
                        if isinstance(post_data, list) and post_data:
                            post_data = post_data[0]
                        if isinstance(post_data, dict):
                            target_post = post_data.get("post", post_data)
                            if (
                                isinstance(target_post, dict)
                                and "attachments" not in target_post
                                and "attachments" in post_data
                            ):
                                target_post["attachments"] = post_data["attachments"]
                            items = self._extract_thumbnails_from_post(
                                target_post,
                                domain,
                                service,
                                user_id,
                                creator_name,
                                mode="post",
                            )
                            all_detected.extend(items)
                            self.batch_received.emit(items)
                    else:
                        self.log_message.emit(
                            f"API HTTP {res.status_code} for {api_url}"
                        )
                except Exception as e:
                    self.log_message.emit(f"Error fetching post {post_id}: {str(e)}")

            elif url_type == "creator" or (
                url_type != "post" and self.mode == "creator"
            ):
                parsed = parse_creator_url(url)
                if not parsed:
                    self.log_message.emit(f"Invalid creator URL: {url}")
                    continue
                domain, service, user_id = parsed
                creator_name = self._fetch_creator_name(
                    session, domain, service, user_id, req_headers
                )
                offset = 0

                endpoints = [
                    f"https://{domain}/api/v1/{service}/user/{user_id}/posts",
                    f"https://{domain}/api/v1/{service}/user/{user_id}",
                ]

                working_endpoint = endpoints[0]
                for ep in endpoints:
                    try:
                        test_res = session.get(
                            f"{ep}?o=0", headers=req_headers, timeout=10
                        )
                        if test_res.status_code == 200:
                            test_json = test_res.json()
                            if isinstance(test_json, list):
                                working_endpoint = ep
                                break
                    except Exception:
                        pass

                while not self.is_cancelled:
                    api_url = f"{working_endpoint}?o={offset}"
                    try:
                        res = session.get(api_url, headers=req_headers, timeout=15)
                        if res.status_code != 200:
                            break
                        posts = res.json()
                        if not isinstance(posts, list) or not posts:
                            break

                        batch_items = []
                        for post in posts:
                            if isinstance(post, dict):
                                items = self._extract_thumbnails_from_post(
                                    post,
                                    domain,
                                    service,
                                    user_id,
                                    creator_name,
                                    mode="creator",
                                )
                                batch_items.extend(items)

                        if batch_items:
                            all_detected.extend(batch_items)
                            self.batch_received.emit(batch_items)

                        if len(posts) < 50:
                            break
                        offset += 50
                    except Exception as e:
                        self.log_message.emit(
                            f"Error fetching creator posts (offset {offset}): {str(e)}"
                        )
                        break

        self.detection_finished.emit(all_detected)

    def _fetch_creator_name(
        self, session, domain: str, service: str, user_id: str, req_headers: dict
    ) -> str:
        """Fetch the creator name from the profile endpoint. Returns 'Unknown_Creator' on failure."""
        profile_url = f"https://{domain}/api/v1/{service}/user/{user_id}/profile"
        try:
            res = session.get(profile_url, headers=req_headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                name = data.get("name", "") if isinstance(data, dict) else ""
                return _sanitize(name) or "Unknown_Creator"
        except Exception:
            pass
        return "Unknown_Creator"

    def _extract_thumbnails_from_post(
        self,
        post: dict,
        domain: str,
        service: str,
        user_id: str,
        creator_name: str,
        mode: str = "post",
    ) -> List[Tuple]:
        """Extract thumbnail URLs from a post dict.
        Returns list of (title, post_id, thumb_urls, service, user_id, creator_name, domain).
        """
        post_id = str(post.get("id", "unknown"))
        post_title = post.get("title") or f"Post {post_id}"
        thumb_urls: List[str] = []

        file_info = post.get("file")
        if isinstance(file_info, dict) and file_info.get("path"):
            p = file_info["path"]
            if p.lower().endswith(SUPPORTED_THUMBNAIL_EXTS):
                t_url = make_thumbnail_url(p, domain)
                if t_url and t_url not in thumb_urls:
                    thumb_urls.append(t_url)

        attachments = post.get("attachments")
        if isinstance(attachments, list):
            for att in attachments:
                if isinstance(att, dict) and att.get("path"):
                    p = att["path"]
                    if p.lower().endswith(SUPPORTED_THUMBNAIL_EXTS):
                        t_url = make_thumbnail_url(p, domain)
                        if t_url and t_url not in thumb_urls:
                            thumb_urls.append(t_url)

        if not thumb_urls:
            return []

        display_title = f"[{service.capitalize()}] {post_title} (ID: {post_id}) [{len(thumb_urls)} Thumbnails]"
        return [
            (display_title, post_id, thumb_urls, service, user_id, creator_name, domain)
        ]


class ThumbnailDownloadThread(QThread):
    file_progress_updated = pyqtSignal(int, int)  # file bytes current, total
    overall_progress_updated = pyqtSignal(int, int)  # files current, total
    log_message = pyqtSignal(str)
    file_completed = pyqtSignal(str, str)  # title, filepath
    download_finished = pyqtSignal(int, int)  # success_count, total_count

    def __init__(
        self,
        download_items: List[
            Tuple[str, str, List[str]]
        ],  # (title, post_id, thumb_urls)
        save_dir: str,
        simultaneous_downloads: int = 3,
        skip_existing: bool = True,
        settings_tab=None,
        folder_strategy: str = "single_folder",  # single_folder|per_post|by_file_type
        auto_rename: bool = True,
        download_text: bool = True,
    ):
        super().__init__()
        self.download_items = download_items
        self.save_dir = save_dir
        self.simultaneous_downloads = max(1, simultaneous_downloads)
        self.skip_existing = skip_existing
        self.settings_tab = settings_tab
        self.folder_strategy = folder_strategy
        self.auto_rename = auto_rename
        self.download_text = download_text
        self.is_cancelled = False
        # Per-post file counters for auto-rename (shared across threads, protected by lock)
        self._post_file_counters: dict = {}
        self._post_file_counters_lock = __import__("threading").Lock()
        # Track which post text files we've already saved
        self._saved_texts: set = set()
        self._saved_texts_lock = __import__("threading").Lock()
        os.makedirs(self.save_dir, exist_ok=True)

    def cancel(self):
        self.is_cancelled = True

    def _get_save_path(
        self,
        title: str,
        post_id: str,
        thumb_url: str,
        service: str = "",
        user_id: str = "",
        creator_name: str = "Unknown_Creator",
        post_title: str = "",
        override_filename: Optional[str] = None,
    ) -> str:
        """Compute the full save filepath, mirroring the creator downloader folder layout.

        Layout:
          save_dir/
            {user_id}_{creator_name}/          <- creator root (skipped for 'direct' URLs)
              [per_post]  {post_id}_{post_title}/filename
              [by_file_type]  {ext}/filename
              [single_folder]  filename
        """
        parsed_url = urllib.parse.urlparse(thumb_url)
        filename = override_filename or os.path.basename(parsed_url.path)
        if not filename or not any(
            filename.lower().endswith(e) for e in SUPPORTED_THUMBNAIL_EXTS
        ):
            # Check if override_filename was given but lacks a valid extension
            base = override_filename or ""
            fallback = f"{hashlib.md5(thumb_url.encode()).hexdigest()[:12]}.jpg"
            if base:
                ext_part = os.path.splitext(base)[1]
                filename = base if ext_part else f"{base}.jpg"
            else:
                filename = fallback

        ext = (os.path.splitext(filename)[1].lstrip(".") or "other").lower()

        # Direct thumbnail URLs (not from a post) go flat into save_dir
        if post_id == "direct":
            return os.path.join(self.save_dir, filename)

        # Build the creator root folder: save_dir/{user_id}_{creator_name}/
        safe_creator_name = _sanitize(creator_name or "Unknown_Creator")
        safe_user_id = _sanitize(user_id or "unknown")
        creator_folder_name = f"{safe_user_id}_{safe_creator_name}"
        creator_folder = os.path.join(self.save_dir, creator_folder_name)

        # Extract clean post title from the display title string
        # Display title format: "[Service] Post Title (ID: post_id) [N Thumbnails]"
        clean_post_title = post_title
        if not clean_post_title:
            m = re.match(r"\[[^\]]+\]\s*(.*?)\s*\(ID:", title)
            clean_post_title = m.group(1).strip() if m else f"Post_{post_id}"
        safe_post_title = _sanitize(clean_post_title)[:80]

        if self.folder_strategy == "per_post":
            post_folder_name = f"{post_id}_{safe_post_title}"
            target_folder = os.path.join(creator_folder, post_folder_name)
        elif self.folder_strategy == "by_file_type":
            target_folder = os.path.join(creator_folder, ext)
        else:  # single_folder
            target_folder = creator_folder

        os.makedirs(target_folder, exist_ok=True)
        return os.path.join(target_folder, filename)

    def _save_post_text(
        self, post_id: str, service: str, user_id: str, domain: str, dest_folder: str
    ) -> None:
        """Fetch post content from the API and save it as desc_{post_id}.txt beside the thumbnails."""
        try:
            # For by_file_type strategy the desc goes into the creator root, not the ext subfolder
            if self.folder_strategy == "by_file_type":
                # Walk up one level from the ext folder to the creator root
                dest_folder = os.path.dirname(dest_folder)

            os.makedirs(dest_folder, exist_ok=True)
            desc_path = os.path.join(dest_folder, f"desc_{post_id}.txt")
            if os.path.exists(desc_path):
                return

            # Use the actual domain the post came from (kemono.cr, coomer.st, etc.)
            if not domain:
                domain_cfg = get_domain_config(
                    f"https://kemono.cr/{service}/user/{user_id}/post/{post_id}"
                )
            else:
                from .domain_config import _build_config

                domain_cfg = _build_config(domain)

            api_url = f"https://{domain_cfg['domain']}/api/v1/{service}/user/{user_id}/post/{post_id}"
            req_headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Referer": domain_cfg.get(
                    "referer", f"https://{domain_cfg['domain']}/"
                ),
            }
            session = get_session(self.settings_tab)
            res = None
            for attempt in range(3):
                try:
                    res = session.get(api_url, headers=req_headers, timeout=10)
                    if res.status_code == 200:
                        break
                    elif res.status_code == 403:
                        alt_headers = req_headers.copy()
                        alt_headers["Accept"] = "text/css"
                        res = session.get(api_url, headers=alt_headers, timeout=10)
                        if res.status_code == 200:
                            break
                except Exception:
                    pass
                time.sleep(1)

            if res is None or res.status_code != 200:
                code = res.status_code if res is not None else "Timeout"
                self.log_message.emit(
                    f"[PostText] API returned {code} for post {post_id} — skipping description."
                )
                return

            post_data = res.json()
            if isinstance(post_data, list) and post_data:
                post_data = post_data[0]
            post = (
                post_data
                if isinstance(post_data, dict) and "post" not in post_data
                else post_data.get("post", {})
            )
            if not isinstance(post, dict):
                return

            title_str = post.get("title", "").strip()
            content = post.get("content", "").strip()
            text_parts = []
            if title_str:
                text_parts.append(title_str)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                clean_content = soup.get_text(separator="\n\n").strip()
                if clean_content:
                    text_parts.append(clean_content)

            full_text = "\n\n".join(text_parts).strip()
            if full_text:
                with open(desc_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
                self.log_message.emit(translate("saved_post_description", post_id))
        except Exception as e:
            self.log_message.emit(
                translate("failed_save_post_description", post_id, str(e))
            )

    def run(self):
        # Flatten items — each entry is (title, post_id, thumb_urls, service, user_id, creator_name, domain)
        # flattened = (title, post_id, thumb_url, service, user_id, creator_name, domain, post_title)
        flattened_items = []
        for item in self.download_items:
            title = item[0]
            post_id = item[1]
            thumb_urls = item[2]
            service = item[3] if len(item) > 3 else ""
            user_id = item[4] if len(item) > 4 else ""
            creator_name = item[5] if len(item) > 5 else "Unknown_Creator"
            domain = item[6] if len(item) > 6 else ""

            # Extract clean post title from display title
            m = re.match(r"\[[^\]]+\]\s*(.*?)\s*\(ID:", title)
            post_title = m.group(1).strip() if m else ""

            if isinstance(thumb_urls, str):
                flattened_items.append(
                    (
                        title,
                        post_id,
                        thumb_urls,
                        service,
                        user_id,
                        creator_name,
                        domain,
                        post_title,
                    )
                )
            elif isinstance(thumb_urls, (list, tuple)):
                for u in thumb_urls:
                    flattened_items.append(
                        (
                            title,
                            post_id,
                            u,
                            service,
                            user_id,
                            creator_name,
                            domain,
                            post_title,
                        )
                    )

        total = len(flattened_items)
        completed = 0
        success_count = 0

        self.log_message.emit(f"Starting download of {total} thumbnail(s)...")

        hash_db = None
        if self.settings_tab and hasattr(self.settings_tab, "hash_db"):
            hash_db = self.settings_tab.hash_db

        def download_single(sub_item) -> bool:
            if self.is_cancelled:
                return False

            (
                title,
                post_id,
                thumb_url,
                service,
                user_id,
                creator_name,
                domain,
                post_title,
            ) = sub_item

            # --- Auto rename: prefix filename with sequential order number per post ---
            parsed_url = urllib.parse.urlparse(thumb_url)
            orig_filename = os.path.basename(parsed_url.path)

            if self.auto_rename and post_id != "direct":
                with self._post_file_counters_lock:
                    if post_id not in self._post_file_counters:
                        self._post_file_counters[post_id] = 0
                    self._post_file_counters[post_id] += 1
                    order = self._post_file_counters[post_id]
                # Prepend order index to filename (e.g. "1_filename.jpg")
                orig_filename = (
                    f"{order}_{orig_filename}" if orig_filename else f"{order}.jpg"
                )

            filepath = self._get_save_path(
                title,
                post_id,
                thumb_url,
                service,
                user_id,
                creator_name,
                post_title,
                override_filename=orig_filename if self.auto_rename else None,
            )
            out_filename = os.path.basename(filepath)

            if (
                self.skip_existing
                and os.path.exists(filepath)
                and os.path.getsize(filepath) > 0
            ):
                self.log_message.emit(f"Skipping existing: {out_filename}")
                self.file_completed.emit(title, filepath)
                return True

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # --- Download post text (desc file) once per post ---
            if self.download_text and post_id != "direct":
                with self._saved_texts_lock:
                    already_saved = post_id in self._saved_texts
                    if not already_saved:
                        self._saved_texts.add(post_id)
                if not already_saved:
                    self._save_post_text(
                        post_id, service, user_id, domain, os.path.dirname(filepath)
                    )

            session = get_session(self.settings_tab)
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Referer": get_domain_config(thumb_url)["referer"],
            }

            try:
                res = session.get(thumb_url, headers=headers, timeout=20, stream=True)
                res.raise_for_status()

                total_bytes = int(res.headers.get("content-length", 0))
                downloaded_bytes = 0

                temp_path = filepath + ".tmp"
                hasher = hashlib.md5()
                with open(temp_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        if self.is_cancelled:
                            f.close()
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            return False
                        if chunk:
                            f.write(chunk)
                            hasher.update(chunk)
                            downloaded_bytes += len(chunk)
                            if total_bytes > 0:
                                self.file_progress_updated.emit(
                                    downloaded_bytes, total_bytes
                                )

                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_path, filepath)

                if hash_db:
                    try:
                        hash_db.add_hash(hasher.hexdigest(), filepath)
                    except Exception:
                        pass

                self.log_message.emit(f"Downloaded: {out_filename}")
                self.file_completed.emit(title, filepath)
                return True

            except Exception as e:
                self.log_message.emit(f"Failed download ({thumb_url}): {str(e)}")
                return False

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.simultaneous_downloads
        ) as executor:
            futures = [
                executor.submit(download_single, item) for item in flattened_items
            ]
            for future in concurrent.futures.as_completed(futures):
                if self.is_cancelled:
                    break
                try:
                    res = future.result()
                    if res:
                        success_count += 1
                except Exception as e:
                    self.log_message.emit(f"Thread error: {str(e)}")

                completed += 1
                self.overall_progress_updated.emit(completed, total)

        self.download_finished.emit(success_count, total)


class ThumbnailDownloaderTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.main_window = parent

        if hasattr(parent, "cache_folder") and isinstance(parent.cache_folder, str):
            self.cache_dir = parent.cache_folder
        else:
            base = getattr(parent, "base_folder", None)
            base_str = (
                base
                if isinstance(base, str) and base
                else os.path.join(os.path.expanduser("~"), ".cache")
            )
            self.cache_dir = os.path.join(base_str, "Cache")

        if hasattr(parent, "other_files_folder") and isinstance(
            parent.other_files_folder, str
        ):
            self.other_files_dir = parent.other_files_folder
        else:
            base = getattr(parent, "base_folder", None)
            base_str = (
                base
                if isinstance(base, str) and base
                else os.path.join(os.path.expanduser("~"), "Other Files")
            )
            self.other_files_dir = os.path.join(base_str, "Other Files")

        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.other_files_dir, exist_ok=True)

        self.detection_thread: Optional[ThumbnailDetectionThread] = None
        self.download_thread: Optional[ThumbnailDownloadThread] = None
        self.detected_items: List[Tuple[str, str, str]] = (
            []
        )  # (title, post_id, thumb_url)
        self.post_url_map: Dict[str, Tuple[str, str]] = (
            {}
        )  # title -> (post_id, thumb_url)

        self.setup_ui()
        self.refresh_ui()

        if (
            hasattr(self.parent, "settings_tab")
            and self.parent.settings_tab is not None
        ):
            try:
                self.parent.settings_tab.settings_applied.connect(self.refresh_ui)
                self.parent.settings_tab.language_changed.connect(self.update_ui_text)
            except Exception:
                pass

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # ==========================================
        # LEFT PANEL: Inputs, Queue, Options & Actions
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Mode Selection Group
        self.mode_group = QGroupBox(translate("download_mode"))
        self.mode_group.setStyleSheet(
            "QGroupBox { color: white; font-weight: bold; padding: 10px; }"
        )
        mode_layout = QHBoxLayout(self.mode_group)
        self.mode_label = QLabel(translate("download_mode"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([translate("post_mode"), translate("creator_mode")])
        self.mode_combo.setStyleSheet(
            "background: #4A5B7A; color: white; padding: 5px; border-radius: 5px;"
        )
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_combo)
        left_layout.addWidget(self.mode_group)

        # URL Input & Queue controls
        self.queue_group = QGroupBox(translate("thumbnail_downloader_tab"))
        self.queue_group.setStyleSheet(
            "QGroupBox { color: white; font-weight: bold; padding: 10px; }"
        )
        queue_layout = QVBoxLayout(self.queue_group)
        queue_layout.setSpacing(8)

        input_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(translate("thumbnail_queue_placeholder"))
        self.url_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.url_input.returnPressed.connect(self.add_url_to_queue)

        self.add_url_button = QPushButton(qta.icon("fa5s.plus", color="white"), "")
        self.add_url_button.setStyleSheet(
            "background: #4A5B7A; padding: 5px; border-radius: 5px;"
        )
        self.add_url_button.setToolTip(translate("added_to_queue"))
        self.add_url_button.clicked.connect(self.add_url_to_queue)

        self.import_file_button = QPushButton(
            qta.icon("fa5s.file-import", color="white"), ""
        )
        self.import_file_button.setStyleSheet(
            "background: #4A5B7A; padding: 5px; border-radius: 5px;"
        )
        self.import_file_button.setToolTip(translate("add_links_from_file_title"))
        self.import_file_button.clicked.connect(self.import_urls_from_file)

        input_row.addWidget(self.url_input)
        input_row.addWidget(self.add_url_button)
        input_row.addWidget(self.import_file_button)
        queue_layout.addLayout(input_row)

        # Multi-line URL area
        self.multi_url_input = QTextEdit()
        self.multi_url_input.setPlaceholderText(translate("multi_url_placeholder"))
        self.multi_url_input.setStyleSheet(
            "background: #2A3B5A; border-radius: 5px; padding: 5px; color: white;"
        )
        self.multi_url_input.setFixedHeight(70)
        self.multi_url_input.setVisible(False)
        queue_layout.addWidget(self.multi_url_input)

        # Queue List
        self.queue_list = QListWidget()
        self.queue_list.setFixedHeight(110)
        self.queue_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.queue_list.setStyleSheet(
            "QListWidget { background: #2A3B5A; border: 1px solid #3A4B6A; border-radius: 6px; color: white; }"
        )
        queue_layout.addWidget(self.queue_list)

        queue_btn_row = QHBoxLayout()
        self.remove_queue_btn = QPushButton(
            qta.icon("fa5s.trash-alt", color="white"), translate("remove")
        )
        self.remove_queue_btn.setStyleSheet(
            "background: #4A5B7A; padding: 5px; border-radius: 5px;"
        )
        self.remove_queue_btn.clicked.connect(self.remove_selected_from_queue)

        self.clear_queue_btn = QPushButton(
            qta.icon("fa5s.eraser", color="white"), translate("clear")
        )
        self.clear_queue_btn.setStyleSheet(
            "background: #4A5B7A; padding: 5px; border-radius: 5px;"
        )
        self.clear_queue_btn.clicked.connect(self.clear_queue)

        queue_btn_row.addWidget(self.remove_queue_btn)
        queue_btn_row.addWidget(self.clear_queue_btn)
        queue_layout.addLayout(queue_btn_row)

        self.detect_button = QPushButton(
            qta.icon("fa5s.search", color="white"), translate("detect_thumbnails")
        )
        self.detect_button.setStyleSheet(
            "background: #3A5B7A; padding: 8px; border-radius: 5px; font-weight: bold; color: white;"
        )
        self.detect_button.clicked.connect(self.start_detection)
        queue_layout.addWidget(self.detect_button)

        left_layout.addWidget(self.queue_group)

        # Settings Options Group
        self.options_group = QGroupBox(translate("download_options"))
        self.options_group.setStyleSheet(
            "QGroupBox { color: white; font-weight: bold; padding: 10px; }"
        )
        options_layout = QVBoxLayout(self.options_group)

        sim_row = QHBoxLayout()
        sim_label = QLabel(translate("simultaneous_downloads"))
        sim_label.setStyleSheet("color: white;")
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 10)
        default_threads = 3
        if hasattr(self.parent, "settings_tab") and hasattr(
            self.parent.settings_tab, "settings"
        ):
            default_threads = self.parent.settings_tab.settings.get(
                "simultaneous_downloads", 3
            )
        self.threads_spin.setValue(default_threads)
        self.threads_spin.setStyleSheet(
            "background: #2A3B5A; color: white; padding: 3px; border-radius: 4px;"
        )
        sim_row.addWidget(sim_label)
        sim_row.addWidget(self.threads_spin)
        options_layout.addLayout(sim_row)

        self.skip_existing_check = QCheckBox(translate("skip_existing_files"))
        self.skip_existing_check.setChecked(True)
        self.skip_existing_check.setStyleSheet("color: white;")
        options_layout.addWidget(self.skip_existing_check)

        self.auto_rename_check = QCheckBox(translate("auto_rename"))
        self.auto_rename_check.setChecked(True)
        self.auto_rename_check.setStyleSheet("color: white;")
        options_layout.addWidget(self.auto_rename_check)

        self.download_text_check = QCheckBox(translate("download_text"))
        self.download_text_check.setChecked(True)
        self.download_text_check.setStyleSheet("color: white;")
        options_layout.addWidget(self.download_text_check)

        left_layout.addWidget(self.options_group)

        # Progress Section
        progress_layout = QVBoxLayout()
        self.file_progress_label = QLabel(translate("file_progress", 0))
        self.file_progress_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.file_progress_label)

        self.file_progress_bar = QProgressBar()
        self.file_progress_bar.setRange(0, 100)
        self.file_progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; text-align: center; color: white; }"
            "QProgressBar::chunk { background: #4A5B7A; border-radius: 5px; }"
        )
        progress_layout.addWidget(self.file_progress_bar)

        self.overall_progress_label = QLabel(
            translate("thumbnail_overall_progress", 0, 0)
        )
        self.overall_progress_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.overall_progress_label)

        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setRange(0, 100)
        self.overall_progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #4A5B7A; border-radius: 5px; background: #2A3B5A; text-align: center; color: white; }"
            "QProgressBar::chunk { background: #4A5B7A; border-radius: 5px; }"
        )
        progress_layout.addWidget(self.overall_progress_bar)
        left_layout.addLayout(progress_layout)

        # Action Buttons Row
        action_btn_layout = QHBoxLayout()
        self.download_button = QPushButton(
            qta.icon("fa5s.download", color="white"), translate("start_download")
        )
        self.download_button.setStyleSheet(
            "background: #4A6B9A; padding: 8px; border-radius: 5px; font-weight: bold; color: white;"
        )
        self.download_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton(
            qta.icon("fa5s.times", color="white"), translate("cancel")
        )
        self.cancel_button.setStyleSheet(
            "background: #A94A4A; padding: 8px; border-radius: 5px; font-weight: bold; color: white;"
        )
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_operation)

        action_btn_layout.addWidget(self.download_button)
        action_btn_layout.addWidget(self.cancel_button)
        left_layout.addLayout(action_btn_layout)

        self.status_label = QLabel(translate("idle"))
        self.status_label.setStyleSheet("color: white; font-size: 12px;")
        left_layout.addWidget(self.status_label)

        # ==========================================
        # RIGHT PANEL: Detected Thumbnails & Log Output
        # ==========================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Group Box for Thumbnails List
        self.thumbnails_group = QGroupBox(translate("thumbnails_to_download"))
        self.thumbnails_group.setStyleSheet(
            "QGroupBox { color: white; font-weight: bold; padding: 10px; }"
        )
        thumbnails_group_layout = QVBoxLayout(self.thumbnails_group)
        thumbnails_group_layout.setSpacing(8)

        # Filter & Selection Header
        filter_row = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(translate("filter_placeholder"))
        self.filter_input.setStyleSheet("padding: 5px; border-radius: 5px;")
        self.filter_input.textChanged.connect(self.filter_detected_items)
        filter_row.addWidget(self.filter_input)
        thumbnails_group_layout.addLayout(filter_row)

        selection_row = QHBoxLayout()
        self.check_all_cb = QCheckBox(translate("check_all"))
        self.check_all_cb.setChecked(True)
        self.check_all_cb.setStyleSheet("color: white;")
        self.check_all_cb.stateChanged.connect(self.toggle_check_all)

        self.selected_count_label = QLabel(translate("selected_count", 0, 0))
        self.selected_count_label.setStyleSheet("color: #CCCCCC; font-size: 11px;")

        selection_row.addWidget(self.check_all_cb)
        selection_row.addStretch()
        selection_row.addWidget(self.selected_count_label)
        thumbnails_group_layout.addLayout(selection_row)

        # Detected Items List
        self.detected_list = QListWidget()
        self.detected_list.setStyleSheet(
            "QListWidget { background: #2A3B5A; border: 1px solid #3A4B6A; border-radius: 6px; color: white; }"
            "QListWidget::item { padding: 4px; }"
        )
        self.detected_list.itemChanged.connect(self.update_selected_count)
        thumbnails_group_layout.addWidget(self.detected_list, stretch=2)

        # Item actions (Preview button)
        item_action_row = QHBoxLayout()
        self.preview_button = QPushButton(qta.icon("fa5s.eye", color="white"), "")
        self.preview_button.setStyleSheet(
            "background: #4A5B7A; padding: 5px; border-radius: 5px;"
        )
        self.preview_button.setToolTip(translate("media_preview"))
        self.preview_button.clicked.connect(self.preview_selected_thumbnail)
        item_action_row.addWidget(self.preview_button)
        item_action_row.addStretch()
        thumbnails_group_layout.addLayout(item_action_row)

        right_layout.addWidget(self.thumbnails_group, stretch=2)

        # Log Output Console
        log_header = QHBoxLayout()
        log_label = QLabel(translate("log_console"))
        log_label.setStyleSheet("font-weight: bold; color: white;")
        self.toggle_logs_btn = QPushButton(
            qta.icon("fa5s.chevron-down", color="white"), ""
        )
        self.toggle_logs_btn.setFixedSize(24, 24)
        self.toggle_logs_btn.setStyleSheet("background: #4A5B7A; border-radius: 5px;")
        self.toggle_logs_btn.setToolTip(translate("expand_logs"))
        self.toggle_logs_btn.clicked.connect(self.toggle_log_console)
        log_header.addWidget(log_label)
        log_header.addStretch()
        log_header.addWidget(self.toggle_logs_btn)
        right_layout.addLayout(log_header)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet(
            "QTextEdit { background: #1A2A44; border: 1px solid #3A4B6A; color: #A0C0FF; font-family: monospace; }"
        )
        right_layout.addWidget(self.log_console, stretch=1)

        main_layout.addWidget(left_panel, stretch=2)
        main_layout.addWidget(right_panel, stretch=3)

    def refresh_ui(self):
        """Update translation texts across controls."""
        self.update_ui_text()

    def update_ui_text(self):
        self.mode_group.setTitle(translate("download_mode"))
        self.mode_label.setText(translate("download_mode"))

        curr_mode_idx = self.mode_combo.currentIndex()
        self.mode_combo.blockSignals(True)
        self.mode_combo.clear()
        self.mode_combo.addItems([translate("post_mode"), translate("creator_mode")])
        self.mode_combo.setCurrentIndex(curr_mode_idx if curr_mode_idx in (0, 1) else 0)
        self.mode_combo.blockSignals(False)

        self.queue_group.setTitle(translate("thumbnail_downloader_tab"))
        self.options_group.setTitle(translate("download_options"))
        self.thumbnails_group.setTitle(translate("thumbnails_to_download"))

        self.detect_button.setText(translate("detect_thumbnails"))
        self.download_button.setText(translate("start_download"))
        self.cancel_button.setText(translate("cancel"))
        self.remove_queue_btn.setText(translate("remove"))
        self.clear_queue_btn.setText(translate("clear"))
        self.check_all_cb.setText(translate("check_all"))
        self.url_input.setPlaceholderText(translate("thumbnail_queue_placeholder"))
        self.filter_input.setPlaceholderText(translate("filter_placeholder"))
        self.skip_existing_check.setText(translate("skip_existing_files"))
        self.auto_rename_check.setText(translate("auto_rename"))
        self.download_text_check.setText(translate("download_text"))
        self.file_progress_label.setText(translate("file_progress", 0))
        self.overall_progress_label.setText(
            translate("thumbnail_overall_progress", 0, 0)
        )

        self.update_selected_count()

    def get_current_mode(self) -> str:
        idx = self.mode_combo.currentIndex()
        return "post" if idx == 0 else "creator"

    def on_mode_changed(self, index: int):
        if self.queue_list.count() > 0:
            msg = QMessageBox(self)
            msg.setWindowTitle(translate("mode_switch_warning_title"))
            msg.setText(translate("mode_switch_warning_msg"))
            msg.setStandardButtons(
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            reply = msg.exec()
            if reply == QMessageBox.StandardButton.Ok:
                self.queue_list.clear()
            else:
                self.mode_combo.blockSignals(True)
                self.mode_combo.setCurrentIndex(0 if index == 1 else 1)
                self.mode_combo.blockSignals(False)

    def add_url_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            return

        current_mode = self.get_current_mode()
        url_type = classify_url(url)

        if current_mode == "post" and url_type == "creator":
            QMessageBox.warning(
                self, translate("error"), translate("mixed_links_error")
            )
            return
        elif current_mode == "creator" and url_type == "post":
            QMessageBox.warning(
                self, translate("error"), translate("mixed_links_error")
            )
            return
        elif url_type == "invalid":
            QMessageBox.warning(
                self, translate("error"), translate("invalid_url_format_from_txt")
            )
            return

        for i in range(self.queue_list.count()):
            if self.queue_list.item(i).text() == url:
                QMessageBox.information(
                    self, translate("warning"), translate("url_already_in_queue")
                )
                return

        self.queue_list.addItem(url)
        self.url_input.clear()
        self.append_log(f"{translate('added_to_queue')}: {url}")

    def import_urls_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translate("select_links_file"),
            "",
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            added = 0
            skipped = 0
            current_mode = self.get_current_mode()

            for line in lines:
                url = line.strip()
                if not url:
                    continue
                url_type = classify_url(url)
                if (
                    (current_mode == "post" and url_type == "creator")
                    or (current_mode == "creator" and url_type == "post")
                    or url_type == "invalid"
                ):
                    skipped += 1
                    continue

                dup = False
                for i in range(self.queue_list.count()):
                    if self.queue_list.item(i).text() == url:
                        dup = True
                        break
                if not dup:
                    self.queue_list.addItem(url)
                    added += 1
                else:
                    skipped += 1

            QMessageBox.information(
                self,
                translate("bulk_add_complete"),
                translate("bulk_add_summary", added, skipped),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                translate("file_read_error_title"),
                translate("file_read_error", str(e)),
            )

    def remove_selected_from_queue(self):
        for item in self.queue_list.selectedItems():
            self.queue_list.takeItem(self.queue_list.row(item))

    def clear_queue(self):
        self.queue_list.clear()

    def start_detection(self):
        urls = [self.queue_list.item(i).text() for i in range(self.queue_list.count())]
        current_input = self.url_input.text().strip()
        if current_input and current_input not in urls:
            urls.append(current_input)

        if not urls:
            QMessageBox.warning(
                self, translate("warning"), translate("thumbnail_queue_placeholder")
            )
            return

        self.detected_list.clear()
        self.detected_items.clear()
        self.post_url_map.clear()

        self.set_working_ui_state(True)
        self.status_label.setText(translate("detecting_thumbnails"))

        self.detection_thread = ThumbnailDetectionThread(
            urls=urls,
            mode=self.get_current_mode(),
            settings_tab=getattr(self.parent, "settings_tab", None),
        )
        self.detection_thread.batch_received.connect(self.on_detection_batch)
        self.detection_thread.detection_finished.connect(self.on_detection_finished)
        self.detection_thread.log_message.connect(self.append_log)
        self.detection_thread.start()

    def on_detection_batch(self, items):
        for item in items:
            # item is (title, post_id, thumb_urls, service, user_id, creator_name, domain)
            title = item[0]
            post_id = item[1]
            thumb_urls = item[2]
            service = item[3] if len(item) > 3 else ""
            user_id = item[4] if len(item) > 4 else ""
            creator_name = item[5] if len(item) > 5 else "Unknown_Creator"
            domain = item[6] if len(item) > 6 else ""

            unique_title = title
            counter = 1
            while unique_title in self.post_url_map:
                counter += 1
                unique_title = f"{title} ({counter})"

            self.detected_items.append(
                (
                    unique_title,
                    post_id,
                    thumb_urls,
                    service,
                    user_id,
                    creator_name,
                    domain,
                )
            )
            self.post_url_map[unique_title] = (
                post_id,
                thumb_urls,
                service,
                user_id,
                creator_name,
                domain,
            )

            list_item = QListWidgetItem(unique_title)
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked)
            self.detected_list.addItem(list_item)

        self.update_selected_count()

    def on_detection_finished(self, all_items: List[Tuple[str, str, List[str]]]):
        self.set_working_ui_state(False)
        count = len(self.detected_items)
        self.status_label.setText(translate("thumbnails_detected", count))
        self.append_log(translate("thumbnails_detected", count))
        if count == 0:
            QMessageBox.information(
                self, translate("information"), translate("no_thumbnails_found")
            )

    def start_download(self):
        checked_items = []
        for i in range(self.detected_list.count()):
            item = self.detected_list.item(i)
            if item.checkState() == Qt.CheckState.Checked and not item.isHidden():
                title = item.text()
                if title in self.post_url_map:
                    entry = self.post_url_map[title]
                    post_id = entry[0]
                    thumb_urls = entry[1]
                    service = entry[2] if len(entry) > 2 else ""
                    user_id = entry[3] if len(entry) > 3 else ""
                    creator_name = entry[4] if len(entry) > 4 else "Unknown_Creator"
                    domain = entry[5] if len(entry) > 5 else ""
                    checked_items.append(
                        (
                            title,
                            post_id,
                            thumb_urls,
                            service,
                            user_id,
                            creator_name,
                            domain,
                        )
                    )

        if not checked_items:
            QMessageBox.warning(
                self, translate("warning"), translate("no_items_selected_download")
            )
            return

        download_folder = getattr(
            self.parent,
            "download_folder",
            os.path.join(os.path.expanduser("~"), "Downloads"),
        )
        save_dir = os.path.join(download_folder, "Thumbnails")
        sim_downloads = self.threads_spin.value()
        skip_exist = self.skip_existing_check.isChecked()

        # Resolve folder strategy from settings
        folder_strategy = "single_folder"
        if hasattr(self.parent, "settings_tab") and hasattr(
            self.parent.settings_tab, "get_creator_folder_strategy"
        ):
            folder_strategy = self.parent.settings_tab.get_creator_folder_strategy()

        self.set_working_ui_state(True)
        self.file_progress_bar.setValue(0)
        self.file_progress_label.setText(translate("file_progress", 0))
        self.overall_progress_bar.setValue(0)
        self.overall_progress_label.setText(
            translate("thumbnail_overall_progress", 0, 0)
        )
        self.status_label.setText(translate("downloading_thumbnails"))

        if hasattr(self.parent, "settings_tab") and hasattr(
            self.parent.settings_tab, "download_started"
        ):
            self.parent.settings_tab.download_started.emit()

        self.download_thread = ThumbnailDownloadThread(
            download_items=checked_items,
            save_dir=save_dir,
            simultaneous_downloads=sim_downloads,
            skip_existing=skip_exist,
            settings_tab=getattr(self.parent, "settings_tab", None),
            folder_strategy=folder_strategy,
            auto_rename=self.auto_rename_check.isChecked(),
            download_text=self.download_text_check.isChecked(),
        )
        self.download_thread.file_progress_updated.connect(self.on_file_progress)
        self.download_thread.overall_progress_updated.connect(self.on_overall_progress)
        self.download_thread.log_message.connect(self.append_log)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_file_progress(self, current: int, total: int):
        pct = int((current / total) * 100) if total > 0 else 0
        pct = min(pct, 100)
        self.file_progress_bar.setValue(pct)
        self.file_progress_label.setText(translate("file_progress", pct))

    def on_overall_progress(self, completed: int, total: int):
        pct = int((completed / total) * 100) if total > 0 else 0
        self.overall_progress_bar.setValue(min(pct, 100))
        self.overall_progress_label.setText(
            translate("thumbnail_overall_progress", completed, total)
        )
        self.status_label.setText(
            f"{translate('downloading_thumbnails')} ({completed}/{total})"
        )

    def on_download_finished(self, success_count: int, total_count: int):
        self.set_working_ui_state(False)
        self.status_label.setText(translate("thumbnails_downloaded", success_count))
        self.append_log(translate("thumbnails_downloaded", success_count))

        if hasattr(self.parent, "settings_tab") and hasattr(
            self.parent.settings_tab, "download_finished"
        ):
            self.parent.settings_tab.download_finished.emit()

        QMessageBox.information(
            self,
            translate("completed"),
            translate("thumbnails_downloaded", success_count),
        )

    def cancel_operation(self):
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.cancel()
            self.append_log("Cancelling detection...")
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.append_log("Cancelling download...")

        self.cancel_button.setEnabled(False)

    def set_working_ui_state(self, working: bool):
        self.detect_button.setEnabled(not working)
        self.download_button.setEnabled(not working)
        self.mode_combo.setEnabled(not working)
        self.url_input.setEnabled(not working)
        self.add_url_button.setEnabled(not working)
        self.import_file_button.setEnabled(not working)
        self.remove_queue_btn.setEnabled(not working)
        self.clear_queue_btn.setEnabled(not working)
        self.skip_existing_check.setEnabled(not working)
        self.auto_rename_check.setEnabled(not working)
        self.download_text_check.setEnabled(not working)
        self.cancel_button.setEnabled(working)

    def toggle_check_all(self, state: int):
        check_state = (
            Qt.CheckState.Checked
            if state == 2 or state == Qt.CheckState.Checked.value
            else Qt.CheckState.Unchecked
        )
        for i in range(self.detected_list.count()):
            item = self.detected_list.item(i)
            if not item.isHidden():
                item.setCheckState(check_state)
        self.update_selected_count()

    def filter_detected_items(self, query: str):
        query = query.lower().strip()
        for i in range(self.detected_list.count()):
            item = self.detected_list.item(i)
            item.setHidden(query not in item.text().lower())
        self.update_selected_count()

    def update_selected_count(self):
        total = self.detected_list.count()
        selected = 0
        for i in range(total):
            item = self.detected_list.item(i)
            if item.checkState() == Qt.CheckState.Checked and not item.isHidden():
                selected += 1
        self.selected_count_label.setText(translate("selected_count", selected, total))

    def preview_selected_thumbnail(self):
        selected = self.detected_list.selectedItems()
        if not selected:
            QMessageBox.information(
                self,
                translate("information"),
                "Please select an item from the list to preview.",
            )
            return

        title = selected[0].text()
        if title in self.post_url_map:
            entry = self.post_url_map[title]
            thumb_urls = entry[
                1
            ]  # (post_id, thumb_urls, service, user_id, creator_name)
            target_url = (
                thumb_urls[0] if isinstance(thumb_urls, (list, tuple)) else thumb_urls
            )
            modal = MediaPreviewModal(target_url, self.cache_dir, tab_parent=self)
            modal.exec()

    def toggle_log_console(self):
        is_visible = self.log_console.isVisible()
        self.log_console.setVisible(not is_visible)
        icon_name = "fa5s.chevron-up" if not is_visible else "fa5s.chevron-down"
        self.toggle_logs_btn.setIcon(qta.icon(icon_name, color="white"))

    def append_log(self, text: str):
        self.log_console.append(text)
