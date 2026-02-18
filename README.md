
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

## 🌟 About the Project

**Offstream** is a powerful and versatile media downloader designed to provide a seamless experience for downloading videos and audio from various platforms. Built with Python, PySide6, and Kivy, it offers a modern, dark-themed interface for both desktop (Windows) and mobile (Android) users.

Whether you want to save your favorite YouTube videos in high quality (up to 4K/8K if the video is available in that quality) or download entire Spotify playlists directly to your device, Offstream handles it all with ease and style. It combines robust functionality with a premium user experience, making media archiving simple and enjoyable.


## 🧩 Architecture

```mermaid
graph TD
    subgraph Desktop [Windows Desktop]
        UI_D[Offstream Pro UI] --> Logic_D[App Logic]
    end

    subgraph Mobile [Android Mobile]
        UI_M[Mobile UI] --> Logic_M[MediaDownloader Lib]
    end

    Logic_D --> Core
    Logic_M --> Core

    subgraph Core [Core Engine]
        DL[yt-dlp / FFmpeg]
        SP[SpotDL]
    end
```

## 🚀 Features

- **Multi-Platform**: Desktop (Windows) and Mobile (Android) (Obs: The mobile app is still under development).
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