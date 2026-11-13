"""Warning windows about files that can't be downloaded.

Some sites (Pawchive) list files whose full copy is gone and only the preview
image remains. Downloading them fails with HTTP 404, which looks like a broken
app, so the downloaders skip them and this window tells the user why.
"""

from typing import Dict, Iterable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QWidget

from kemonodownloader.download_utils import PreviewOnlyFile, filename_from_url
from kemonodownloader.kd_language import translate

# Lines shown under "Show Details"; a creator can have thousands of these.
DETAIL_LIMIT = 1000


class PreviewOnlyNotice:
    """Collect preview-only files during one download run and tell the user.

    The window is non-blocking, so an unattended queue keeps downloading. It
    opens the first time such files are found and is updated as later posts
    or creators add more. Once the user closes it, it stays closed for the
    rest of the run; the log and the final summary still report the files.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        self._parent = parent
        self._files: Dict[str, PreviewOnlyFile] = {}
        self._box: Optional[QMessageBox] = None
        self._dismissed = False

    @property
    def count(self) -> int:
        return len(self._files)

    @property
    def files(self):
        return list(self._files.values())

    def reset(self) -> None:
        """Start a new download run."""
        # Close first: closing emits finished(), which marks it dismissed.
        if self._box is not None:
            self._box.close()
        self._files.clear()
        self._dismissed = False

    def add(self, files: Iterable[PreviewOnlyFile]) -> int:
        """Record *files*, show or update the window, and return how many were new."""
        new = 0
        for file in files:
            if file.url not in self._files:
                self._files[file.url] = file
                new += 1
        if new and not self._dismissed:
            self._show()
        return new

    def _show(self) -> None:
        box = self._box
        if box is None:
            box = QMessageBox(self._parent)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setStandardButtons(QMessageBox.StandardButton.Ok)
            box.setWindowModality(Qt.WindowModality.NonModal)
            box.finished.connect(self._on_closed)
            self._box = box
        box.setWindowTitle(translate("preview_only_title"))
        box.setText(translate("preview_only_text", self.count))
        saved = any(f.preview_saved for f in self._files.values())
        box.setInformativeText(
            translate("preview_only_info_saved" if saved else "preview_only_info")
        )
        box.setDetailedText(self._details())
        box.show()
        box.raise_()

    def _on_closed(self, _result: int) -> None:
        self._dismissed = True

    def _details(self) -> str:
        lines = []
        for file in list(self._files.values())[:DETAIL_LIMIT]:
            title = file.post_title or file.post_id
            lines.append(f"{title} — {file.name}" if title else file.name)
        extra = self.count - DETAIL_LIMIT
        if extra > 0:
            lines.append(translate("preview_only_more", extra))
        return "\n".join(lines)


class MissingFilesNotice:
    """Tell the user, at the end of a run, which files the server didn't have.

    Kemono and Coomer don't mark files that are gone, so these are only found
    when a download answers HTTP 404 or 410. Shown once per run, non-blocking.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        self._parent = parent
        self._box: Optional[QMessageBox] = None

    def show(self, urls: Iterable[str]) -> None:
        urls = sorted(set(urls))
        if not urls:
            return
        box = self._box
        if box is None:
            box = QMessageBox(self._parent)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setStandardButtons(QMessageBox.StandardButton.Ok)
            box.setWindowModality(Qt.WindowModality.NonModal)
            self._box = box
        box.setWindowTitle(translate("missing_files_title"))
        box.setText(translate("missing_files_text", len(urls)))
        box.setInformativeText(translate("missing_files_info"))
        lines = [f"{filename_from_url(url)}  ({url})" for url in urls[:DETAIL_LIMIT]]
        if len(urls) > DETAIL_LIMIT:
            lines.append(translate("preview_only_more", len(urls) - DETAIL_LIMIT))
        box.setDetailedText("\n".join(lines))
        box.show()
        box.raise_()

    def close(self) -> None:
        if self._box is not None:
            self._box.close()
