# i18n.py

TRANSLATIONS = {
    "app_title": {"en": "Screenshot Tool", "zh": "截图工具"},
    "menu_file": {"en": "File", "zh": "文件"},
    "menu_settings": {"en": "Settings", "zh": "设置"},
    "menu_exit": {"en": "Exit", "zh": "退出"},
    "menu_tools": {"en": "Tools", "zh": "工具"},
    "menu_fullscreen_shot": {"en": "Fullscreen Screenshot", "zh": "全屏截图"},
    "menu_region_shot": {"en": "Region Screenshot", "zh": "选区截图"},
    "menu_scrolling_capture": {"en": "Scrolling Capture", "zh": "长截图"},
    "menu_screen_recording": {"en": "Screen Recording", "zh": "屏幕录制"},
    "menu_ocr_image_file": {"en": "OCR from Image File", "zh": "OCR识别图像文件"},
    "menu_language": {"en": "Language", "zh": "语言"},
    "lang_english": {"en": "English", "zh": "English"}, # Keep "English" as English for clarity
    "lang_chinese": {"en": "Chinese", "zh": "中文"},

    "button_fullscreen_shot": {"en": "Fullscreen", "zh": "全屏截图"},
    "button_region_shot": {"en": "Select Region", "zh": "选区截图"},
    "button_scrolling_capture": {"en": "Scrolling", "zh": "长截图"},
    "button_screen_recording": {"en": "Record Screen", "zh": "录屏"},
    "button_select_color": {"en": "Color", "zh": "颜色"},
    
    "status_idle": {"en": "Idle", "zh": "空闲"},
    "status_recording_start_prompt": {"en": "Screen recording started (placeholder).", "zh": "屏幕录制已开始（占位符）。"},
    "status_recording_stop_prompt": {"en": "Screen recording stopped (placeholder).", "zh": "屏幕录制已停止（占位符）。"},
    "ocr_select_image_title": {"en": "Select Image for OCR", "zh": "选择图像进行OCR"},
    "ocr_result_title": {"en": "OCR Result", "zh": "OCR识别结果"},
    "ocr_no_text_found": {"en": "No text found or OCR failed.", "zh": "未找到文本或OCR失败。"},
    "settings_placeholder_title": {"en": "Settings", "zh": "设置"},
    "settings_placeholder_message": {"en": "Settings dialog will be implemented here.", "zh": "设置对话框将在此实现。"},
}

# Default language
current_language = "en"

def set_language(lang_code):
    """Sets the current language for translations."""
    global current_language
    if lang_code in ["en", "zh"]: # Add more supported languages here
        current_language = lang_code
    else:
        print(f"Warning: Language code '{lang_code}' not explicitly supported. Defaulting to 'en'.")
        current_language = "en"

def get_language():
    """Gets the current language code."""
    return current_language

def _(text_id):
    """
    Returns the translation for the given text_id in the current_language.
    Falls back to English if the translation is missing, then to a placeholder.
    """
    translation = TRANSLATIONS.get(text_id, {}).get(current_language)
    if translation is None: # Fallback to English if current language translation is missing
        translation = TRANSLATIONS.get(text_id, {}).get("en", f"Missing: {text_id} ({current_language})")
    return translation

if __name__ == '__main__':
    # Test translations
    print(f"Current language: {current_language}")
    print(f"App Title: {_('app_title')}")
    print(f"Exit Menu: {_('menu_exit')}")

    set_language("zh")
    print(f"\nCurrent language: {current_language}")
    print(f"App Title: {_('app_title')}")
    print(f"Exit Menu: {_('menu_exit')}")
    
    print(f"\nMissing key test: {_('non_existent_key')}")
    
    set_language("fr") # Test unsupported language
    print(f"\nCurrent language: {current_language}")
    print(f"App Title: {_('app_title')}") # Should fallback to English
    print(f"Missing key test with fallback: {_('non_existent_key_fr')}") # Should show placeholder
