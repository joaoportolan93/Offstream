
<div align="center">
  <img src="assets/banner_offstream.png" alt="Offstream" width="100%">
  
  # Offstream
  
  **Your Premium Media Downloader for Windows & Mobile**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Kivy](https://img.shields.io/badge/Kivy-2.3.0-green.svg)](https://kivy.org/)
  [![PySide6](https://img.shields.io/badge/PySide6-6.6.1-green.svg)](https://pypi.org/project/PySide6/)

  [🇧🇷 Português](README_PT.md) | [🇺🇸 English](README.md)
  
</div>

---

### 📖 Documentation / Documentação
| [CODE OF CONDUCT](CODE_OF_CONDUCT.md) | [CONTRIBUTING](CONTRIBUTING.md) | [SECURITY](SECURITY.md) |
| :---: | :---: | :---: |
| [CÓDIGO DE CONDUTA](CODE_OF_CONDUCT_PT.md) | [CONTRIBUINDO](CONTRIBUTING_PT.md) | [SEGURANÇA](SECURITY_PT.md) |

---

## 📸 Screenshots

<div align="center">
  <!-- Place the user provided screenshot here -->
  <img src="assets/app_screenshot.png" alt="Offstream Application Interface" width="800">
</div>

## 🧩 Architecture

```mermaid
classDiagram
    class OffstreamPro {
        +queue : Queue
        +setup_ui()
        +start_download()
    }
    class ModernNavBar {
        +create_nav_button()
    }
    class DownloadItemWidget {
        +update_progress()
    }
    class OffstreamMobile {
        +build()
        +download()
    }
    class MobileDownloader {
        +get_video_info()
        +download_background()
    }

    OffstreamPro *-- ModernNavBar
    OffstreamPro *-- DownloadItemWidget
    OffstreamMobile *-- MobileDownloader
```

## 🚀 Features

- **Multi-Platform**: Desktop (Windows) and Mobile (Android).
- **High Quality**: Downloads up to 4K/8K.
- **Spotify Support**: Download songs and playlists directly.
- **Smart Queue**: Manage multiple downloads simultaneously.
- **Modern UI**: Sleek dark mode interface.

## 🛠️ Installation

### Desktop (Windows)
1. Clone the repository:
   ```bash
   git clone https://github.com/joaoportolan93/Video-downloader.git
   cd Video-downloader
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

### Mobile (Android)
Requires [Buildozer](https://buildozer.readthedocs.io/en/latest/) (Linux/WSL).
```bash
cd mobile
buildozer android debug
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.