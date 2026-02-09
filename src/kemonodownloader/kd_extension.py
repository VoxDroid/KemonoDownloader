from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from kemonodownloader.kd_language import translate


class ExtensionTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        self.parent.settings_tab.language_changed.connect(self.update_ui_text)

    def setup_ui(self):
        # Main layout for the Extension tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: #2A3B5A;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #3A4B6A;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4A5B7A;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(20)

        self.update_ui_text()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        self.setMinimumSize(300, 400)

    def update_ui_text(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear the layout and delete its contents
                layout = item.layout()
                while layout.count():
                    sub_item = layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                # The layout itself will be deleted when the parent layout is cleared

        # Title
        title_label = QLabel(f"<h1>{translate('extension_title')}</h1>")
        title_label.setFont(QFont("Poppins", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title_label)

        # Introduction
        intro_label = QLabel(translate("extension_intro"))
        intro_label.setFont(QFont("Poppins", 12))
        intro_label.setStyleSheet("color: #D0D0D0; padding: 5px;")
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(intro_label)

        # Usage Section
        usage_title = QLabel(f"<h2>{translate('extension_download_title')}</h2>")
        usage_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        usage_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(usage_title)

        usage_text = QLabel(translate("extension_download_text"))
        usage_text.setFont(QFont("Poppins", 12))
        usage_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        usage_text.setWordWrap(True)
        usage_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        usage_text.setOpenExternalLinks(True)
        self.content_layout.addWidget(usage_text)

        # Download button
        download_button_layout = QHBoxLayout()
        download_button_layout.addStretch()

        download_button = QPushButton("📦 " + translate("download"))
        download_button.setFont(QFont("Poppins", 12, QFont.Weight.Bold))
        download_button.setStyleSheet(
            """
            QPushButton {
                background: #4A5B7A;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5A6B8A;
            }
            QPushButton:pressed {
                background: #3A4B6A;
            }
        """
        )
        download_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/VoxDroid/KemonoDownloader/releases")
            )
        )
        download_button_layout.addWidget(download_button)
        download_button_layout.addStretch()
        self.content_layout.addLayout(download_button_layout)

        # Install Section
        install_title = QLabel(f"<h2>{translate('extension_install_title')}</h2>")
        install_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        install_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(install_title)

        install_text = QLabel(translate("extension_install_text"))
        install_text.setFont(QFont("Poppins", 12))
        install_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        install_text.setWordWrap(True)
        install_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        install_text.setOpenExternalLinks(True)
        self.content_layout.addWidget(install_text)

        # Chrome/Edge installation
        chrome_install = QLabel(translate("extension_install_chrome"))
        chrome_install.setFont(QFont("Poppins", 12))
        chrome_install.setStyleSheet("color: #D0D0D0; padding: 5px;")
        chrome_install.setWordWrap(True)
        chrome_install.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(chrome_install)

        # Firefox installation
        firefox_install = QLabel(translate("extension_install_firefox"))
        firefox_install.setFont(QFont("Poppins", 12))
        firefox_install.setStyleSheet("color: #D0D0D0; padding: 5px;")
        firefox_install.setWordWrap(True)
        firefox_install.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(firefox_install)

        # Setup Section
        setup_title = QLabel(f"<h2>{translate('extension_setup_title')}</h2>")
        setup_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        setup_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(setup_title)

        setup_text = QLabel(translate("extension_setup_text"))
        setup_text.setFont(QFont("Poppins", 12))
        setup_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        setup_text.setWordWrap(True)
        setup_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(setup_text)

        # Manifest compatibility / notes
        manifest_title = QLabel(f"<h2>{translate('extension_manifest_title')}</h2>")
        manifest_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        manifest_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(manifest_title)

        manifest_text = QLabel(translate("extension_manifest_text"))
        manifest_text.setFont(QFont("Poppins", 12))
        manifest_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        manifest_text.setWordWrap(True)
        manifest_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        manifest_text.setOpenExternalLinks(True)
        self.content_layout.addWidget(manifest_text)

        chrome_manifest = QLabel(translate("extension_manifest_chrome"))
        chrome_manifest.setFont(QFont("Poppins", 12))
        chrome_manifest.setStyleSheet("color: #D0D0D0; padding: 5px;")
        chrome_manifest.setWordWrap(True)
        chrome_manifest.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(chrome_manifest)

        firefox_manifest = QLabel(translate("extension_manifest_firefox"))
        firefox_manifest.setFont(QFont("Poppins", 12))
        firefox_manifest.setStyleSheet("color: #D0D0D0; padding: 5px;")
        firefox_manifest.setWordWrap(True)
        firefox_manifest.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(firefox_manifest)

        manifest_quick = QLabel(translate("extension_manifest_quickcopy"))
        manifest_quick.setFont(QFont("Poppins", 12))
        manifest_quick.setStyleSheet("color: #D0D0D0; padding: 5px;")
        manifest_quick.setWordWrap(True)
        manifest_quick.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(manifest_quick)

        # Troubleshooting Section
        troubleshooting_title = QLabel(
            f"<h2>{translate('extension_troubleshooting_title')}</h2>"
        )
        troubleshooting_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        troubleshooting_title.setStyleSheet("color: white; padding: 10px 5px 5px 5px;")
        self.content_layout.addWidget(troubleshooting_title)

        troubleshooting_text = QLabel(translate("extension_troubleshooting_text"))
        troubleshooting_text.setFont(QFont("Poppins", 12))
        troubleshooting_text.setStyleSheet("color: #D0D0D0; padding: 5px;")
        troubleshooting_text.setWordWrap(True)
        troubleshooting_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.content_layout.addWidget(troubleshooting_text)

        self.content_layout.addStretch()

    def refresh_ui(self):
        self.update_ui_text()
