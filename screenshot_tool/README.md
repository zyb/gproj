# Screenshot Tool Pro / 截图工具专业版

## English

### 1. Project Title
Screenshot Tool Pro

### 2. Brief Description
Screenshot Tool Pro is a comprehensive desktop application designed for capturing screenshots, recording screen activity, and performing image edits and OCR. It offers a versatile suite of tools to enhance productivity for users who need to capture, annotate, and share screen content.

### 3. Key Features
*   **Fullscreen Screenshot**: Captures the entire screen. The captured image is then opened in the built-in editor for further actions.
*   **Region Screenshot**: Allows users to select a specific rectangular area of the screen for capture. The selected area is then opened in the editor.
*   **Image Editing & Annotation**: After a screenshot is taken, it opens in an editor that provides tools for:
    *   Drawing shapes (rectangles, ellipses, lines, arrows).
    *   Adding text annotations.
    *   Cropping the image.
    *   Applying blur or mosaic effects to selected areas.
    *   Freehand pen drawing.
    *   Saving the edited image or copying it to the clipboard.
*   **Screen Recording**: Records screen activity of the primary monitor and saves it as a video file (MP4 or AVI format, configurable).
*   **Scrolling Capture**: Captures long web pages or documents by automatically scrolling and stitching together multiple screenshots.
*   **OCR (Optical Character Recognition)**: Extracts text from images (either captured screenshots or imported image files) using the Tesseract OCR engine. Supports multiple languages.
*   **User Customization**: Allows users to configure settings such as default save paths, filename formats, image/video output formats, and more via a settings panel. Configurations are saved in a `config.json` file.
*   **Multilingual Interface**: Supports interface language switching between English and Chinese.

### 4. Dependencies and Installation

#### 4.1. Python Version
*   Python 3.7 or higher is recommended.

#### 4.2. Python Packages
Install the required Python packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
The `requirements.txt` file includes libraries such as `mss`, `Pillow`, `pyperclip`, `opencv-python`, `numpy`, `pyautogui`, `pytesseract`, and `appdirs`.

#### 4.3. Tesseract OCR Engine (Crucial for OCR Feature)
The OCR functionality relies on the **Tesseract OCR engine**, which must be installed separately from this Python application. `pytesseract` is only a Python wrapper for Tesseract.

*   **General Installation**:
    *   Download and install Tesseract OCR for your operating system from its official sources or trusted repositories. For detailed instructions, refer to the [official Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/).
    *   **Windows**: Installers are often available from projects like UB Mannheim Tesseract.
    *   **macOS**: Typically installed via Homebrew (`brew install tesseract`).
    *   **Linux**: Typically installed via your distribution's package manager (e.g., `sudo apt-get install tesseract-ocr` for Debian/Ubuntu, `sudo yum install tesseract` for Fedora).

*   **PATH Configuration**:
    *   Ensure that the Tesseract installation directory is added to your system's PATH environment variable.
    *   Alternatively, the path to the Tesseract executable can be specified within the application's code (`ocr.py`) by setting `pytesseract.tesseract_cmd` (this is usually not required if Tesseract is correctly installed and in PATH).

*   **Language Packs**:
    *   Tesseract requires language data files (`.traineddata`) for OCR. English (`eng`) is often included by default.
    *   To perform OCR for other languages (e.g., Simplified Chinese - `chi_sim`), you must install the corresponding language pack.
    *   **Debian/Ubuntu**: `sudo apt-get install tesseract-ocr-<lang_code>` (e.g., `sudo apt-get install tesseract-ocr-chi-sim` for Simplified Chinese, `sudo apt-get install tesseract-ocr-jpn` for Japanese). Use `tesseract-ocr-all` to install all available language packs.
    *   **Windows**: Language data files can often be selected during Tesseract installation. If not, download the required `.traineddata` files (e.g., `chi_sim.traineddata`) from the [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast) or [tessdata_best](https://github.com/tesseract-ocr/tessdata_best) repositories and place them in Tesseract's `tessdata` subdirectory (e.g., `C:\Program Files\Tesseract-OCR\tessdata`).
    *   **macOS (Homebrew)**: Language packs can be installed with `brew install tesseract-lang` or by installing specific language data files.

### 5. How to Run the Application
Navigate to the `src` directory of the project and run:
```bash
python main.py
```
(If your entry point is structured differently, adjust the command accordingly, e.g., `python screenshot_tool/src/main.py` from the project root if `src` is not directly in PYTHONPATH).

### 6. Settings
*   User-configurable settings are available through the application's "Settings" menu.
*   These settings are stored in a `config.json` file located in a user-specific configuration directory (e.g., `~/.config/ScreenshotTool/config.json` on Linux).

---

## 中文 (Chinese)

### 1. 项目标题
截图工具专业版 (Screenshot Tool Pro)

### 2. 简短描述
截图工具专业版是一款功能全面的桌面应用程序，专为屏幕截图、屏幕录制、图像编辑和OCR文字识别而设计。它提供了一套多样化的工具，旨在提高需要捕捉、注释和分享屏幕内容用户的生产力。

### 3. 主要功能
*   **全屏截图 (Fullscreen Screenshot)**: 捕捉整个屏幕。捕获的图像随后会在内置编辑器中打开以供进一步操作。
*   **选区截图 (Region Screenshot)**: 允许用户选择屏幕上的特定矩形区域进行捕捉。所选区域随后会在编辑器中打开。
*   **截图后编辑与标记 (Image Editing & Annotation)**: 截图后，图像会在编辑器中打开，提供以下工具：
    *   绘制形状 (矩形、椭圆、线条、箭头)。
    *   添加文本注释。
    *   裁剪图像。
    *   对选定区域应用模糊或马赛克效果。
    *   自由画笔工具。
    *   保存编辑后的图像或将其复制到剪贴板。
*   **屏幕录制 (Screen Recording)**: 录制主显示器的屏幕活动，并将其保存为视频文件 (MP4 或 AVI 格式，可配置)。
*   **滚动截图 (Scrolling Capture)**: 通过自动滚动并拼接多个截图来捕捉长网页或文档 (长截图)。
*   **OCR 文字识别 (Optical Character Recognition)**: 使用 Tesseract OCR 引擎从图像 (捕获的截图或导入的图像文件) 中提取文本。支持多种语言。
*   **用户自定义设置 (User Customization)**: 允许用户通过设置面板配置默认保存路径、文件名格式、图像/视频输出格式等。配置保存在 `config.json` 文件中。
*   **中英文界面切换 (Multilingual Interface)**: 支持中英文界面语言切换。

### 4. 依赖与安装

#### 4.1. Python 版本
*   推荐使用 Python 3.7 或更高版本。

#### 4.2. Python 包
使用 `requirements.txt` 文件安装所需的 Python 包：
```bash
pip install -r requirements.txt
```
`requirements.txt` 文件包含了如 `mss`, `Pillow`, `pyperclip`, `opencv-python`, `numpy`, `pyautogui`, `pytesseract`, `appdirs` 等库。

#### 4.3. Tesseract OCR 引擎 (OCR 功能关键依赖)
OCR 功能依赖于 **Tesseract OCR 引擎**，该引擎必须独立于此 Python 应用程序进行安装。`pytesseract` 仅仅是 Tesseract 的一个 Python 包装器。

*   **通用安装说明**:
    *   请从 Tesseract 官方资源或可信的软件仓库下载并为您的操作系统安装 Tesseract OCR。详细说明请参阅 [Tesseract 官方文档](https://tesseract-ocr.github.io/tessdoc/)。
    *   **Windows**: 安装程序通常可从 UB Mannheim Tesseract 等项目获取。
    *   **macOS**: 通常通过 Homebrew 安装 (`brew install tesseract`)。
    *   **Linux**: 通常通过您的发行版的包管理器安装 (例如，Debian/Ubuntu 使用 `sudo apt-get install tesseract-ocr`，Fedora 使用 `sudo yum install tesseract`)。

*   **PATH 环境变量配置**:
    *   确保 Tesseract 的安装目录已添加到系统的 PATH 环境变量中。
    *   或者，可以在应用程序代码 (`ocr.py`) 中通过设置 `pytesseract.tesseract_cmd` 来指定 Tesseract 可执行文件的路径 (如果 Tesseract 已正确安装并在 PATH 中，则通常不需要此操作)。

*   **语言包**:
    *   Tesseract 需要语言数据文件 (`.traineddata`) 来进行 OCR。英语 (`eng`) 通常默认包含。
    *   要对其他语言进行 OCR (例如，简体中文 - `chi_sim`)，您必须安装相应的语言包。
    *   **Debian/Ubuntu**: `sudo apt-get install tesseract-ocr-<lang_code>` (例如，简体中文使用 `sudo apt-get install tesseract-ocr-chi-sim`，日语使用 `sudo apt-get install tesseract-ocr-jpn`)。使用 `tesseract-ocr-all` 安装所有可用的语言包。
    *   **Windows**: 语言数据文件通常可以在 Tesseract 安装过程中选择。如果未选择，请从 [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast) 或 [tessdata_best](https://github.com/tesseract-ocr/tessdata_best) 代码库下载所需的 `.traineddata` 文件 (例如 `chi_sim.traineddata`)，并将其放置在 Tesseract 安装目录下的 `tessdata` 子目录中 (例如 `C:\Program Files\Tesseract-OCR\tessdata`)。
    *   **macOS (Homebrew)**: 语言包可通过 `brew install tesseract-lang` 安装，或通过安装特定的语言数据文件来获取。

### 5. 如何运行程序
导航到项目的 `src` 目录并运行：
```bash
python main.py
```
(如果您的项目入口点结构不同，请相应调整命令，例如，如果 `src` 目录未直接添加到 PYTHONPATH，则从项目根目录运行 `python screenshot_tool/src/main.py`)。

### 6. 设置说明
*   用户可通过应用程序的“设置”菜单自定义相关选项。
*   这些设置存储在用户特定的配置目录下的 `config.json` 文件中 (例如，Linux 系统中为 `~/.config/ScreenshotTool/config.json`)。
