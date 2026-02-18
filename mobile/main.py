"""
Offstream Mobile - Interface Kivy
App para download de vídeos e áudios
"""
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty

from downloader import MediaDownloader

# Interface KV - Usando Kivy puro para garantir compatibilidade
KV = '''
#:import Window kivy.core.window.Window

<RoundedButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.2, 0.45, 1, 1) if self.state == 'normal' else (0.15, 0.35, 0.8, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

<FormatCard@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    selected: False
    canvas.before:
        Color:
            rgba: (0.2, 0.35, 0.6, 1) if self.selected else (0.18, 0.18, 0.22, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.12, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    # Header
    Label:
        text: 'Offstream Mobile'
        font_size: '24sp'
        size_hint_y: None
        height: 50
        bold: True
    
    # URL Input
    BoxLayout:
        size_hint_y: None
        height: 50
        spacing: 10
        
        TextInput:
            id: url_input
            hint_text: 'Cole a URL do vídeo aqui...'
            multiline: False
            background_color: 0.18, 0.18, 0.22, 1
            foreground_color: 1, 1, 1, 1
            hint_text_color: 0.5, 0.5, 0.5, 1
            padding: [15, 15, 15, 15]
            font_size: '16sp'
        
        Button:
            text: 'COLAR'
            size_hint_x: None
            width: 70
            font_size: '12sp'
            background_color: 0.2, 0.35, 0.6, 1
            on_release: app.paste_url()
        
        Button:
            text: 'BUSCAR'
            size_hint_x: None
            width: 70
            font_size: '12sp'
            background_color: 0.2, 0.45, 1, 1
            on_release: app.check_url()
    
    # Video Info
    BoxLayout:
        id: info_box
        size_hint_y: None
        height: 60
        orientation: 'vertical'
        opacity: 0
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.18, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [12]
        
        Label:
            id: video_title
            text: 'Título do vídeo'
            font_size: '14sp'
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            padding: [15, 0]
            shorten: True
        
        Label:
            id: video_info
            text: 'Duração: --:--'
            font_size: '12sp'
            color: 0.7, 0.7, 0.7, 1
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            padding: [15, 0]
    
    # Format Label
    Label:
        text: 'Selecione o formato:'
        font_size: '14sp'
        size_hint_y: None
        height: 30
        halign: 'left'
        text_size: self.size
    
    # Format Cards
    BoxLayout:
        size_hint_y: None
        height: 100
        spacing: 15
        
        FormatCard:
            id: mp4_card
            text: 'MP4 - Video 1080p'
            selected: True
            on_release: app.select_format('mp4')
        
        FormatCard:
            id: mp3_card
            text: 'MP3 - Audio 320kbps'
            selected: False
            on_release: app.select_format('mp3')
    
    # Download Button
    RoundedButton:
        id: download_btn
        text: 'DOWNLOAD'
        size_hint_y: None
        height: 56
        font_size: '18sp'
        bold: True
        on_release: app.start_download()
    
    # Progress
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 50
        spacing: 5
        
        ProgressBar:
            id: progress_bar
            max: 100
            value: 0
        
        Label:
            id: status_label
            text: 'Pronto para download'
            font_size: '12sp'
            color: 0.7, 0.7, 0.7, 1
    
    # Spacer
    Widget:
    
    # History
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 120
        padding: 15
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.18, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [12]
        
        Label:
            text: 'Downloads Recentes'
            font_size: '14sp'
            size_hint_y: None
            height: 25
            halign: 'left'
            text_size: self.size
        
        ScrollView:
            Label:
                id: history_label
                text: 'Nenhum download ainda'
                font_size: '12sp'
                color: 0.6, 0.6, 0.6, 1
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
'''


class OffstreamApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.downloader = MediaDownloader()
        self.selected_format = 'mp4'
        self.selected_quality = '1080'
        
        # Callbacks
        self.downloader.progress_callback = self.on_progress
        self.downloader.complete_callback = self.on_complete
        self.downloader.error_callback = self.on_error
    
    def build(self):
        return Builder.load_string(KV)
    
    def paste_url(self):
        """Cola URL da área de transferência"""
        try:
            url = Clipboard.paste()
            if url:
                self.root.ids.url_input.text = url
        except Exception as e:
            print(f"Erro ao colar: {e}")
    
    def check_url(self):
        """Verifica URL e obtém informações"""
        url = self.root.ids.url_input.text
        if not url or not url.startswith('http'):
            self.root.ids.status_label.text = "URL inválida!"
            return
        
        self.root.ids.status_label.text = "Obtendo informações..."
        self.root.ids.info_box.opacity = 0
        
        self.downloader.get_video_info(url, self.on_video_info)
    
    def on_video_info(self, info):
        """Callback quando informações do vídeo são obtidas"""
        def update(dt):
            title = info['title']
            if len(title) > 40:
                title = title[:40] + "..."
            self.root.ids.video_title.text = title
            
            duration = info['duration']
            mins = duration // 60
            secs = duration % 60
            self.root.ids.video_info.text = f"Duração: {mins}:{secs:02d} • {info['uploader']}"
            
            self.root.ids.info_box.opacity = 1
            self.root.ids.status_label.text = "Pronto para download"
        
        Clock.schedule_once(update, 0)
    
    def select_format(self, format_type):
        """Seleciona formato de download"""
        self.selected_format = format_type
        
        self.root.ids.mp4_card.selected = (format_type == 'mp4')
        self.root.ids.mp3_card.selected = (format_type == 'mp3')
        
        if format_type == 'mp4':
            self.selected_quality = '1080'
        else:
            self.selected_quality = '320'
    
    def start_download(self):
        """Inicia download"""
        url = self.root.ids.url_input.text
        
        if not url:
            self.root.ids.status_label.text = "Cole uma URL primeiro!"
            return
        
        self.root.ids.download_btn.disabled = True
        self.root.ids.download_btn.text = "Baixando..."
        self.root.ids.progress_bar.value = 0
        self.root.ids.status_label.text = "Iniciando download..."
        
        self.downloader.download(url, self.selected_format, self.selected_quality)
    
    def on_progress(self, percent, speed):
        """Callback de progresso"""
        def update(dt):
            self.root.ids.progress_bar.value = percent
            self.root.ids.status_label.text = f"Baixando: {percent:.1f}% • {speed}"
        
        Clock.schedule_once(update, 0)
    
    def on_complete(self):
        """Callback quando download completa"""
        def update(dt):
            self.root.ids.download_btn.disabled = False
            self.root.ids.download_btn.text = "DOWNLOAD"
            self.root.ids.progress_bar.value = 100
            self.root.ids.status_label.text = "Download concluido!"
            
            # Adicionar ao historico
            title = self.root.ids.video_title.text
            current = self.root.ids.history_label.text
            if current == "Nenhum download ainda":
                self.root.ids.history_label.text = f"[OK] {title}"
            else:
                self.root.ids.history_label.text = f"[OK] {title}\n{current}"
        
        Clock.schedule_once(update, 0)
    
    def on_error(self, error):
        """Callback de erro"""
        def update(dt):
            self.root.ids.download_btn.disabled = False
            self.root.ids.download_btn.text = "DOWNLOAD"
            self.root.ids.status_label.text = f"ERRO: {error[:40]}..."
        
        Clock.schedule_once(update, 0)


if __name__ == '__main__':
    OffstreamApp().run()
