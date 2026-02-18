import sys
import os
import re
import threading
import queue
import concurrent.futures
import time
import base64
import urllib.request
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QFrame, QStackedWidget, QListWidget, QListWidgetItem, 
                               QAbstractItemView, QComboBox, QSlider, QScrollArea, 
                               QGraphicsDropShadowEffect, QSizePolicy, QFileDialog)
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QColor, QPixmap, QImage, QPainter, QPainterPath

from yt_dlp import YoutubeDL

# Configurações de Segurança (Ofuscação Simples)
_CID_OBF = "ZmVmYzdjZmQxMzllNmI0YjQ0NTQyY2E3ZDVmMzNhMWM="
_SEC_OBF = "OTI5OWRlMGQ0OWFjOTEzOTZiYjQ5NDIyNmY5N2Y5MTE="

def get_spotify_credentials():
    try:
        client_id = base64.b64decode(_CID_OBF).decode()[::-1]
        client_secret = base64.b64decode(_SEC_OBF).decode()[::-1]
        return client_id, client_secret
    except:
        return "", ""

SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET = get_spotify_credentials()

# Custom Logger for yt-dlp
class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        if "unavailable" in msg.lower() or "not available" in msg.lower():
            print(f"\\n[Offstream] ⚠️ VIDEO INDISPONÍVEL.")
            print("[Offstream] Pulando para o próximo da fila...\\n")
        else:
            print(f"Error: {msg}")

class ModernNavBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-right: 1px solid #2d2d3d;
            }
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-radius: 10px;
                color: #a0a0a0;
                font-size: 14px;
                background-color: transparent;
                margin: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2d2d3d;
                color: white;
            }
            QPushButton:checked {
                background-color: linear-gradient(90deg, #2d2d3d 0%, #1e1e2e 100%);
                color: white;
                border-left: 3px solid #4a90e2;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 20, 0, 20)
        
        # Logo Area
        logo_label = QLabel("Offstream")
        logo_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding-left: 20px;")
        layout.addWidget(logo_label)
        
        pro_label = QLabel("Pro")
        pro_label.setStyleSheet("color: #4a90e2; font-size: 12px; font-weight: bold; padding-left: 20px; margin-bottom: 20px;")
        layout.addWidget(pro_label)

        # Buttons
        self.btn_home = self.create_nav_button("🏠 Início")
        self.btn_history = self.create_nav_button("🕒 Histórico")
        self.btn_favorites = self.create_nav_button("⭐ Favoritos")
        self.btn_settings = self.create_nav_button("⚙️ Configurações")
        self.btn_theme = self.create_nav_button("🌗 Tema")

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_history)
        layout.addWidget(self.btn_favorites)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_theme)
        
        layout.addStretch()

    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        return btn

class DownloadItemWidget(QFrame):
    def __init__(self, title, progress=0, status="Baixando...", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #252535;
                border-radius: 12px;
                margin-bottom: 10px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_label = QLabel("▶️")
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet("background-color: #2d2d3d; border-radius: 20px; font-size: 20px; qproperty-alignment: AlignCenter;")
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.status_lbl = QLabel(status) # Percentage or Status
        self.status_lbl.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.status_lbl)
        layout.addLayout(info_layout)
        
        # Progress Bar
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("background-color: #2d2d3d; border-radius: 2px;")
        self.progress_fill = QFrame(self.progress_bar)
        self.progress_fill.setFixedHeight(4)
        self.progress_fill.setStyleSheet("background-color: #4a90e2; border-radius: 2px;")
        self.set_progress(progress)
        
        # We add the bar to a layout wrapper to position it below or beside text
        # For simplicity in this layout, let's put it at the bottom of info_layout
        info_layout.addWidget(self.progress_bar)

    def set_progress(self, value):
        width = self.width() if self.width() > 0 else 400 # Approximation
        fill_width = int(width * (value / 100))
        self.progress_fill.setFixedWidth(fill_width)
        if value < 100:
            self.status_lbl.setText(f"{value}%")
        else:
            self.status_lbl.setText("Concluído")

class MediaDownloaderPro(QMainWindow):
    update_video_info_signal = Signal(dict)
    update_spotify_info_signal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offstream Pro")
        self.setMinimumSize(1100, 700)
        
        # Logic Variables (Initialize these first!)
        self.download_queue = queue.Queue()
        self.active_downloads = []
        self.download_pool = None
        self.is_spotify_url = False
        self.spotify_songs = None
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Main Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.navbar = ModernNavBar()
        self.main_layout.addWidget(self.navbar)
        
        # Content Area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #181825;")
        self.main_layout.addWidget(self.content_area)
        
        self.setup_home_page()
        self.setup_history_page()
        self.setup_favorites_page()
        self.setup_settings_page()
        
        self.setup_connections()
        
        # Logic Variables
        self.download_queue = queue.Queue()
        self.active_downloads = []
        self.download_pool = None
        self.is_spotify_url = False
        self.spotify_songs = None
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Load Data
        self.history = [] # Load from file in real app
        self.favorites = []

    def setup_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Search Bar Area
        search_frame = QFrame()
        search_frame.setFixedHeight(60)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #252535;
                border-radius: 30px;
                border: 1px solid #353545;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(40, 40)
        plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #353545;
                border-radius: 20px;
                color: white;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover { background-color: #454555; }
        """)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole ou Arraste o URL da Mídia")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                padding-left: 10px;
            }
        """)
        self.url_input.returnPressed.connect(self.check_url)
        
        paste_btn = QPushButton("Paste URL")
        paste_btn.setCursor(Qt.PointingHandCursor)
        paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #353545;
                border-radius: 15px;
                color: white;
                padding: 8px 15px;
                border: none;
            }
            QPushButton:hover { background-color: #454555; }
        """)
        paste_btn.clicked.connect(self.paste_from_clipboard)

        search_layout.addWidget(plus_btn)
        search_layout.addWidget(self.url_input)
        search_layout.addWidget(paste_btn)
        
        layout.addWidget(search_frame)
        
        # Main Content Grid (Preview + Controls)
        content_grid_frame = QFrame()
        content_grid_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 20px;
                border: 1px solid #2d2d3d;
            }
        """)
        grid_layout = QHBoxLayout(content_grid_frame)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(30)
        
        # Left: Preview Box
        self.preview_frame = QLabel("Preview")
        self.preview_frame.setAlignment(Qt.AlignCenter)
        self.preview_frame.setFixedSize(320, 180)
        self.preview_frame.setStyleSheet("""
            QLabel {
                background-color: #181825;
                border-radius: 15px;
                color: #505060;
                font-size: 14px;
            }
        """)
        grid_layout.addWidget(self.preview_frame)
        
        # Right: Controls
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        
        # Format & Quality Row
        fq_layout = QHBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MP3", "WAV", "WEBM"])
        self.format_combo.setStyleSheet(self.get_combo_style())
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High (1080p/320k)", "Medium (720p/128k)", "Low (480p/64k)"])
        self.quality_combo.setStyleSheet(self.get_combo_style())

        fq_lbl = QLabel("Formato")
        fq_lbl.setStyleSheet("color: #a0a0a0;")
        fq_layout.addWidget(fq_lbl)
        fq_layout.addWidget(self.format_combo)
        fq_layout.addWidget(QLabel("Qualidade"))
        fq_layout.addWidget(self.quality_combo)
        controls_layout.addLayout(fq_layout)
        
        # Sliders
        slider_layout = QHBoxLayout()
        slider_lbl = QLabel("Downloads Simultâneos")
        slider_lbl.setStyleSheet("color: #a0a0a0;")
        self.simultaneous_slider = QSlider(Qt.Horizontal)
        self.simultaneous_slider.setRange(1, 5)
        self.simultaneous_slider.setValue(3)
        self.simultaneous_slider.setStyleSheet("""
             QSlider::groove:horizontal {
                border: 1px solid #3d3d4d;
                height: 4px;
                background: #2d2d3d;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4a90e2;
                border: 1px solid #4a90e2;
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
        """)
        slider_layout.addWidget(slider_lbl)
        slider_layout.addWidget(self.simultaneous_slider)
        controls_layout.addLayout(slider_layout)
        
        # Directory
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit(self.download_directory)
        self.dir_input.setReadOnly(True)
        self.dir_input.setStyleSheet("""
            QLineEdit {
                background-color: #252535;
                border: 1px solid #353545;
                border-radius: 8px;
                color: #a0a0a0;
                padding: 8px;
            }
        """)
        dir_btn = QPushButton("📂")
        dir_btn.setFixedSize(35, 35)
        dir_btn.clicked.connect(self.choose_directory)
        dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #353545;
                border-radius: 8px;
                color: white;
                border: none;
            }
            QPushButton:hover { background-color: #454555; }
        """)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_btn)
        controls_layout.addWidget(QLabel("Diretório de Download"))
        controls_layout.addLayout(dir_layout)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        action_layout.setAlignment(Qt.AlignCenter)
        action_layout.setSpacing(20)
        
        self.download_btn = QPushButton("⬇️ Download")
        self.download_btn.setFixedHeight(45)
        self.download_btn.setFixedWidth(140)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #357abd);
                border-radius: 22px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #5ca0f2;
            }
            QPushButton:hover { background-color: #357abd; }
             QPushButton:pressed { margin-top: 2px; }
        """)
        
        self.pause_btn = QPushButton("⏸️ Pausar")
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setStyleSheet(self.get_secondary_btn_style())
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.cancel_btn = QPushButton("⏹️ Cancelar")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setStyleSheet(self.get_secondary_btn_style())
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        
        action_layout.addWidget(self.download_btn)
        action_layout.addWidget(self.pause_btn)
        action_layout.addWidget(self.cancel_btn)
        
        controls_layout.addStretch()
        controls_layout.addLayout(action_layout)
        
        grid_layout.addLayout(controls_layout)
        layout.addWidget(content_grid_frame)
        
        # Active Downloads Section
        downloads_group = QFrame()
        downloads_group.setStyleSheet("""
             QFrame {
                background-color: #1e1e2e;
                border-radius: 20px;
                border: 1px solid #2d2d3d;
            }
        """)
        dl_layout = QVBoxLayout(downloads_group)
        dl_layout.addWidget(QLabel("Downloads Ativos", styleSheet="font-weight: bold; font-size: 16px; color: white;"))
        
        self.downloads_scroll_area = QScrollArea()
        self.downloads_scroll_area.setWidgetResizable(True)
        self.downloads_scroll_area.setStyleSheet("background: transparent; border: none;")
        self.downloads_container = QWidget()
        self.downloads_container_layout = QVBoxLayout(self.downloads_container)
        self.downloads_container_layout.setAlignment(Qt.AlignTop)
        self.downloads_scroll_area.setWidget(self.downloads_container)
        
        dl_layout.addWidget(self.downloads_scroll_area)
        
        layout.addWidget(downloads_group)
        
        self.content_area.addWidget(page)
    
    def setup_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Histórico de Downloads")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border-radius: 15px;
                border: 1px solid #2d2d3d;
                padding: 10px;
                color: #a0a0a0;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2d2d3d;
            }
        """)
        layout.addWidget(self.history_list)
        
        clear_btn = QPushButton("Limpar Histórico")
        clear_btn.setStyleSheet(self.get_secondary_btn_style())
        clear_btn.setFixedSize(150, 40)
        layout.addWidget(clear_btn, alignment=Qt.AlignRight)
        
        self.content_area.addWidget(page)

    def setup_favorites_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Favoritos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        self.favorites_list = QListWidget()
        self.favorites_list.setStyleSheet("""
             QListWidget {
                background-color: #1e1e2e;
                border-radius: 15px;
                border: 1px solid #2d2d3d;
                padding: 10px;
                color: #a0a0a0;
            }
        """)
        layout.addWidget(self.favorites_list)
        
        self.content_area.addWidget(page)

    def setup_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Configurações")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Example Settings
        setting_frame = QFrame()
        setting_frame.setStyleSheet("background-color: #1e1e2e; border-radius: 15px;")
        s_layout = QVBoxLayout(setting_frame)
        
        s_layout.addWidget(QLabel("Gerais", styleSheet="font-weight: bold; font-size: 16px; color: white;"))
        s_layout.addWidget(QLabel("Mais configurações em breve...", styleSheet="color: #a0a0a0;"))
        
        layout.addWidget(setting_frame)
        layout.addStretch()
        
        self.content_area.addWidget(page)


    def get_combo_style(self):
        return """
            QComboBox {
                background-color: #252535;
                border: 1px solid #353545;
                border-radius: 8px;
                padding: 5px 10px;
                color: white;
                min-width: 100px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #252535;
                color: white;
                selection-background-color: #4a90e2;
            }
        """

    def get_secondary_btn_style(self):
        return """
            QPushButton {
                background-color: #353545;
                border-radius: 20px;
                color: #a0a0a0;
                border: 1px solid #454555;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #454555;
                color: white;
            }
             QPushButton:disabled {
                opacity: 0.5;
                background-color: #2a2a35;
             }
        """

    def setup_connections(self):
        # Navbar connections
        self.navbar.btn_home.clicked.connect(lambda: self.switch_tab(0))
        self.navbar.btn_history.clicked.connect(lambda: self.switch_tab(1))
        self.navbar.btn_favorites.clicked.connect(lambda: self.switch_tab(2))
        self.navbar.btn_settings.clicked.connect(lambda: self.switch_tab(3))
        # Theme (Toggle)
        self.navbar.btn_theme.clicked.connect(self.toggle_theme)

        # Logic connections
        self.update_video_info_signal.connect(self.update_video_info_ui)
        self.update_spotify_info_signal.connect(self.update_spotify_info_ui)

    def switch_tab(self, index):
        self.content_area.setCurrentIndex(index)
        
        # Reset all buttons
        buttons = [self.navbar.btn_home, self.navbar.btn_history, self.navbar.btn_favorites, self.navbar.btn_settings]
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

    def toggle_theme(self):
        # Placeholder for theme toggle implementation
        pass

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
        self.check_url()

    def check_url(self):
        url = self.url_input.text()
        if not url: return
        
        if "spotify.com" in url:
            self.is_spotify_url = True
            threading.Thread(target=self._fetch_spotify_info, args=(url,)).start()
        else:
            self.is_spotify_url = False
            threading.Thread(target=self._fetch_video_info, args=(url,)).start()

    def _fetch_video_info(self, url):
        try:
            ydl_opts = {
                'extract_flat': 'in_playlist', # Prevent crash on playlist preview
                'ignoreerrors': True,
                'quiet': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    self.update_video_info_signal.emit(info)
        except Exception as e:
            print(f"Error fetching video info: {e}")

    def _fetch_spotify_info(self, url):
        try:
            from spotdl import Spotdl
            from spotdl.utils.config import DEFAULT_CONFIG
            
            spotdl = Spotdl(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, downloader_settings=DEFAULT_CONFIG)
            songs = spotdl.search([url])
            
            if not songs: return

            # Basic info gathering similar to previous version
            info = {
                'title': songs[0].name if len(songs) == 1 else (songs[0].list_name or 'Playlist'),
                'thumbnail': songs[0].cover_url,
                'songs': songs
            }
            self.update_spotify_info_signal.emit(info)
        except Exception as e:
            print(f"Error fetching spotify info: {e}")

    def update_video_info_ui(self, info):
        # Update Thumbnail
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            self.load_thumbnail(thumbnail_url)
        # Update Title placeholder (in real implementation, update a title label)
        print(f"Video Found: {info.get('title')}")

    def update_spotify_info_ui(self, info):
        self.spotify_songs = info.get('songs')
        if info.get('thumbnail'):
            self.load_thumbnail(info['thumbnail'])
        print(f"Spotify Found: {info.get('title')}")

    def load_thumbnail(self, url):
        try:
            data = urllib.request.urlopen(url).read()
            image = QImage()
            image.loadFromData(data)
            pixmap = QPixmap(image)
            
            # Rounded corners for thumbnail
            size = self.preview_frame.size()
            rounded = QPixmap(size)
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, size.width(), size.height(), 15, 15)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, size.width(), size.height(), pixmap)
            painter.end()
            
            self.preview_frame.setPixmap(rounded)
        except Exception as e:
            print(f"Thumbnail error: {e}")

    def choose_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Escolher Diretório", self.download_directory)
        if dir_path:
            self.download_directory = dir_path
            self.dir_input.setText(dir_path)

    def start_download(self):
        url = self.url_input.text()
        if not url and not self.spotify_songs: 
            return
        
        formato = self.format_combo.currentText()
        
        # Spotify Download
        if self.is_spotify_url and self.spotify_songs:
            # Create a group item for the playlist/album or single song
            title = "Spotify Download"
            if len(self.spotify_songs) == 1:
                title = f"{self.spotify_songs[0].artist} - {self.spotify_songs[0].name}"
            else:
                title = f"Playlist/Album ({len(self.spotify_songs)} songs)"
                
            item_widget = DownloadItemWidget(title, 0, "Preparando...")
            self.downloads_container_layout.addWidget(item_widget)
            
            threading.Thread(target=self._execute_spotify_download, args=(formato, item_widget)).start()
            
        else:
            # YouTube/Direct Download
            self.download_queue.put((url, formato))
            
            # Create UI Item immediately
            item_widget = DownloadItemWidget("Aguardando...", 0, "Na fila")
            item_widget.url = url # Store URL to identify later if needed
            self.downloads_container_layout.addWidget(item_widget)
            self.active_downloads.append(item_widget) # Track active widgets

            if self.download_pool is None:
                max_workers = self.simultaneous_slider.value()
                self.download_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
                threading.Thread(target=self.process_download_queue).start()

    def process_download_queue(self):
        while True:
            try:
                url, formato = self.download_queue.get(timeout=1)
                # Find the widget for this URL (simple matching)
                widget = next((w for w in self.active_downloads if getattr(w, 'url', '') == url), None)
                
                if widget:
                    self.download_pool.submit(self._download_worker, url, formato, widget)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Queue error: {e}")

    def _download_worker(self, url, formato, widget):
        try:
            print(f"\\n[Offstream] Iniciando download: {url}")
            QTimer.singleShot(0, lambda: widget.status_lbl.setText("Baixando..."))
            
            # Configure Options
            ydl_opts = {
                'format': self._get_format_string(formato),
                'outtmpl': os.path.join(self.download_directory, '%(title)s.%(ext)s'),
                'progress_hooks': [lambda d: self._progress_hook(d, widget)],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True, # Skip unavailable videos
                'logger': MyLogger(), # Use custom logger
            }
            
            # Audio conversion options
            if 'MP3' in formato or 'WAV' in formato:
                 ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3' if 'MP3' in formato else 'wav',
                    'preferredquality': '192',
                }]
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info:
                    title = info.get('title', 'Video')
                    QTimer.singleShot(0, lambda: widget.title_lbl.setText(title))
                    QTimer.singleShot(0, lambda: widget.set_progress(100))
                    QTimer.singleShot(0, lambda: widget.status_lbl.setText("Concluído"))
                    print(f"[Offstream] Download concluído: {title}")
                else:
                    # Video unavailable (handled by logger)
                    QTimer.singleShot(0, lambda: widget.status_lbl.setText("Indisponível"))
            
        except Exception as e:
            # Critical errors not caught by ignoreerrors
            error_msg = str(e)
            QTimer.singleShot(0, lambda: widget.status_lbl.setText(f"Erro: {error_msg[:20]}..."))
            print(f"Download Critical Error: {e}")
        finally:
            if widget in self.active_downloads:
                self.active_downloads.remove(widget)

    def _progress_hook(self, d, widget):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                progress = float(p)
                QTimer.singleShot(0, lambda: widget.set_progress(int(progress)))
                
                # Print progress to terminal periodically (e.g. every 10%) or just update line
                # Simple version: Print every update (might be spammy, but confirms activity)
                # Better: Print only integer changes
                if int(progress) % 10 == 0:
                    sys.stdout.write(f"\\r[Offstream] Baixando: {int(progress)}%")
                    sys.stdout.flush()
            except:
                pass
        elif d['status'] == 'finished':
            sys.stdout.write(f"\\r[Offstream] Baixando: 100%\\n")
            QTimer.singleShot(0, lambda: widget.set_progress(100))
            QTimer.singleShot(0, lambda: widget.status_lbl.setText("Processando..."))

    def _get_format_string(self, formato):
        if 'MP4' in formato:
            return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif 'WEBM' in formato:
            return 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best'
        else: # Audio only
            return 'bestaudio/best'

    def _execute_spotify_download(self, formato, widget):
        try:
            from spotdl import Spotdl
            from spotdl.utils.config import DEFAULT_CONFIG
            
            QTimer.singleShot(0, lambda: widget.status_lbl.setText("Inicializando SpotDL..."))
            
            audio_format = "mp3"
            if "wav" in formato.lower(): audio_format = "wav"
            
            downloader_settings = {
                'output': self.download_directory,
                'format': audio_format,
                'ffmpeg': 'ffmpeg', # Assume system ffmpeg or path
            }
            
            spotdl = Spotdl(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                downloader_settings=downloader_settings
            )
            
            songs = self.spotify_songs
            total = len(songs)
            
            for i, song in enumerate(songs, 1):
                # Update status
                msg = f"Baixando {i}/{total}: {song.name}"
                progress = int((i-1)/total * 100)
                
                QTimer.singleShot(0, lambda m=msg, p=progress: (
                    widget.status_lbl.setText(m),
                    widget.set_progress(p)
                ))
                
                try:
                    spotdl.download(song)
                except Exception as e:
                    print(f"Error downloading {song.name}: {e}")
            
            QTimer.singleShot(0, lambda: widget.set_progress(100))
            QTimer.singleShot(0, lambda: widget.status_lbl.setText("Download Spotify Concluído"))
            
        except Exception as e:
             QTimer.singleShot(0, lambda: widget.status_lbl.setText(f"Erro: {str(e)[:20]}"))

    def toggle_pause(self):
        pass 

    def cancel_download(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediaDownloaderPro()
    window.show()
    sys.exit(app.exec())
