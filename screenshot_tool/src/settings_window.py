import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from . import i18n
from . import config_manager
import os

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent # MainApplication instance
        self.transient(parent) # Keep window on top of parent
        self.grab_set() # Modal behavior

        self.title(i18n._("settings_window_title"))
        self.geometry("550x450") # Adjusted size

        self.config_vars = {} # To store tk.StringVar, tk.IntVar, etc. for UI elements

        self._create_widgets()
        self._load_settings_to_ui()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel) # Handle window close button

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill=tk.BOTH, pady=5)

        # Create tabs
        self.tab_general = ttk.Frame(self.notebook, padding="10")
        self.tab_output = ttk.Frame(self.notebook, padding="10")
        self.tab_interface = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.tab_general, text=i18n._("settings_tab_general"))
        self.notebook.add(self.tab_output, text=i18n._("settings_tab_output"))
        self.notebook.add(self.tab_interface, text=i18n._("settings_tab_interface"))

        self._create_general_tab(self.tab_general)
        self._create_output_tab(self.tab_output)
        self._create_interface_tab(self.tab_interface)

        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        self.btn_restore = ttk.Button(button_frame, text=i18n._("settings_btn_restore_defaults"), command=self._restore_defaults)
        self.btn_restore.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = ttk.Button(button_frame, text=i18n._("settings_btn_cancel"), command=self._on_cancel)
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)
        
        self.btn_save = ttk.Button(button_frame, text=i18n._("settings_btn_save_apply"), command=self._on_save_apply)
        self.btn_save.pack(side=tk.RIGHT, padx=5)


    def _create_general_tab(self, tab):
        frame = ttk.LabelFrame(tab, text=i18n._("settings_group_general_options"), padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Default Save Path
        ttk.Label(frame, text=i18n._("settings_label_default_save_path")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_vars["general_default_save_path"] = tk.StringVar()
        entry_save_path = ttk.Entry(frame, textvariable=self.config_vars["general_default_save_path"], width=40)
        entry_save_path.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        btn_browse_save_path = ttk.Button(frame, text=i18n._("settings_btn_browse"), command=self._browse_save_path)
        btn_browse_save_path.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        # Filename Format
        ttk.Label(frame, text=i18n._("settings_label_filename_format")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.config_vars["general_screenshot_filename_format"] = tk.StringVar()
        entry_filename_format = ttk.Entry(frame, textvariable=self.config_vars["general_screenshot_filename_format"], width=40)
        entry_filename_format.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        # Add tooltip or small help text for format codes later

        # Auto Copy to Clipboard
        self.config_vars["general_auto_copy_to_clipboard"] = tk.BooleanVar()
        chk_auto_copy = ttk.Checkbutton(frame, text=i18n._("settings_chk_auto_copy_clipboard"), variable=self.config_vars["general_auto_copy_to_clipboard"])
        chk_auto_copy.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Auto Start on Boot (Placeholder)
        self.config_vars["general_auto_start_on_boot"] = tk.BooleanVar()
        chk_auto_start = ttk.Checkbutton(frame, text=i18n._("settings_chk_auto_start_boot") + i18n._("settings_label_placeholder"), variable=self.config_vars["general_auto_start_on_boot"], state=tk.DISABLED)
        chk_auto_start.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        frame.columnconfigure(1, weight=1) # Make entry expand

    def _browse_save_path(self):
        path = filedialog.askdirectory(parent=self, initialdir=self.config_vars["general_default_save_path"].get())
        if path:
            self.config_vars["general_default_save_path"].set(path)

    def _create_output_tab(self, tab):
        frame = ttk.LabelFrame(tab, text=i18n._("settings_group_output_options"), padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Image Format
        ttk.Label(frame, text=i18n._("settings_label_image_format")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_vars["output_image_format"] = tk.StringVar()
        combo_img_format = ttk.Combobox(frame, textvariable=self.config_vars["output_image_format"], values=["PNG", "JPG", "BMP"], state="readonly", width=10)
        combo_img_format.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        combo_img_format.bind("<<ComboboxSelected>>", self._on_image_format_change)

        # Image Quality (JPG)
        self.lbl_jpg_quality = ttk.Label(frame, text=i18n._("settings_label_jpg_quality"))
        self.lbl_jpg_quality.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.config_vars["output_image_quality_jpg"] = tk.IntVar()
        self.scale_jpg_quality = ttk.Scale(frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.config_vars["output_image_quality_jpg"], length=200)
        self.scale_jpg_quality.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.val_jpg_quality_label = ttk.Label(frame, text="") # To display current scale value
        self.val_jpg_quality_label.grid(row=1, column=2, sticky=tk.W, padx=5)
        self.config_vars["output_image_quality_jpg"].trace_add("write", self._update_jpg_quality_label)


        # Video Format
        ttk.Label(frame, text=i18n._("settings_label_video_format")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.config_vars["output_video_format"] = tk.StringVar()
        combo_vid_format = ttk.Combobox(frame, textvariable=self.config_vars["output_video_format"], values=["MP4", "AVI"], state="readonly", width=10) # Add more later if needed
        combo_vid_format.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Video FPS
        ttk.Label(frame, text=i18n._("settings_label_video_fps")).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.config_vars["output_video_fps"] = tk.DoubleVar()
        entry_vid_fps = ttk.Entry(frame, textvariable=self.config_vars["output_video_fps"], width=12)
        entry_vid_fps.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        frame.columnconfigure(1, weight=1)
        self._on_image_format_change() # Initial state update for JPG quality controls

    def _on_image_format_change(self, event=None):
        is_jpg = self.config_vars["output_image_format"].get() == "JPG"
        state = tk.NORMAL if is_jpg else tk.DISABLED
        self.lbl_jpg_quality.config(state=state)
        self.scale_jpg_quality.config(state=state)
        self.val_jpg_quality_label.config(state=state)
        if is_jpg:
            self._update_jpg_quality_label()


    def _update_jpg_quality_label(self, *args):
        self.val_jpg_quality_label.config(text=str(self.config_vars["output_image_quality_jpg"].get()))


    def _create_interface_tab(self, tab):
        frame = ttk.LabelFrame(tab, text=i18n._("settings_group_interface_options"), padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Theme (Placeholder)
        ttk.Label(frame, text=i18n._("settings_label_theme")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_vars["interface_theme"] = tk.StringVar()
        combo_theme = ttk.Combobox(frame, textvariable=self.config_vars["interface_theme"], values=[i18n._("theme_light"), i18n._("theme_dark")], state="disabled", width=15) # Disabled for now
        combo_theme.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text=i18n._("settings_label_placeholder")).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language (already handled by main app's menu, but can be shown here)
        ttk.Label(frame, text=i18n._("settings_label_language")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.config_vars["interface_language"] = tk.StringVar()
        # This combobox is for display/consistency, actual change is via main menu or needs restart
        combo_lang = ttk.Combobox(frame, textvariable=self.config_vars["interface_language"], values=["en", "zh"], state="readonly", width=15)
        combo_lang.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text=i18n._("settings_label_restart_required")).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)


    def _load_settings_to_ui(self):
        config = config_manager.load_config()
        for section, settings in config.items():
            for key, value in settings.items():
                var_key = f"{section}_{key}"
                if var_key in self.config_vars:
                    if isinstance(self.config_vars[var_key], tk.BooleanVar):
                        self.config_vars[var_key].set(bool(value))
                    elif isinstance(self.config_vars[var_key], tk.IntVar):
                         try: self.config_vars[var_key].set(int(value))
                         except ValueError: self.config_vars[var_key].set(0) # Default if parse error
                    elif isinstance(self.config_vars[var_key], tk.DoubleVar):
                         try: self.config_vars[var_key].set(float(value))
                         except ValueError: self.config_vars[var_key].set(0.0)
                    else: # tk.StringVar
                        self.config_vars[var_key].set(str(value))
        
        self._on_image_format_change() # Ensure JPG quality state is correct after load
        self._update_jpg_quality_label() # Update label for JPG quality

    def _collect_ui_settings_to_dict(self):
        new_config = {}
        for var_key, tk_var in self.config_vars.items():
            section, key = var_key.split("_", 1)
            if section not in new_config:
                new_config[section] = {}
            new_config[section][key] = tk_var.get()
        return new_config

    def _on_save_apply(self):
        new_settings = self._collect_ui_settings_to_dict()
        if config_manager.save_config(new_settings):
            messagebox.showinfo(i18n._("settings_save_success_title"), i18n._("settings_save_success_message"), parent=self)
            # Notify parent (MainApplication) about changes
            if hasattr(self.parent, 'on_settings_changed'):
                self.parent.on_settings_changed(new_settings)
            self.destroy()
        else:
            messagebox.showerror(i18n._("settings_save_error_title"), i18n._("settings_save_error_message"), parent=self)

    def _on_cancel(self):
        # Optionally, check for unsaved changes here if desired
        self.destroy()

    def _restore_defaults(self):
        # Create dummy i18n entries for themes if not present
        if "theme_light" not in i18n.TRANSLATIONS: i18n.TRANSLATIONS["theme_light"] = {"en": "Light", "zh": "亮色"}
        if "theme_dark" not in i18n.TRANSLATIONS: i18n.TRANSLATIONS["theme_dark"] = {"en": "Dark", "zh": "暗色"}
            
        current_lang_temp = self.config_vars.get("interface_language", tk.StringVar(value="en")).get()
        
        # Load default config into UI elements
        default_config = config_manager.DEFAULT_CONFIG.copy()
        for section, settings in default_config.items():
            for key, value in settings.items():
                var_key = f"{section}_{key}"
                if var_key in self.config_vars:
                    if isinstance(self.config_vars[var_key], tk.BooleanVar):
                        self.config_vars[var_key].set(bool(value))
                    elif isinstance(self.config_vars[var_key], tk.IntVar):
                         self.config_vars[var_key].set(int(value))
                    elif isinstance(self.config_vars[var_key], tk.DoubleVar):
                         self.config_vars[var_key].set(float(value))
                    else: # tk.StringVar
                        self.config_vars[var_key].set(str(value))
        
        # Ensure the language setting in UI doesn't change due to this restore,
        # as language is typically managed outside default config restore for the UI itself.
        if "interface_language" in self.config_vars:
             self.config_vars["interface_language"].set(current_lang_temp)

        self._on_image_format_change() # Update dependent UI like JPG quality
        self._update_jpg_quality_label()
        messagebox.showinfo(i18n._("settings_restore_confirm_title"), i18n._("settings_restore_confirm_message"), parent=self)


if __name__ == '__main__':
    # This is for testing the SettingsWindow directly
    # Add dummy i18n entries for testing if not running through main app
    if "settings_window_title" not in i18n.TRANSLATIONS: # Check if loaded
        i18n.TRANSLATIONS.update({
            "settings_window_title": {"en": "Settings (Test)", "zh": "设置 (测试)"},
            "settings_tab_general": {"en": "General", "zh": "常规"},
            "settings_tab_output": {"en": "Output", "zh": "输出"},
            "settings_tab_interface": {"en": "Interface", "zh": "界面"},
            "settings_group_general_options": {"en": "General Options", "zh": "常规选项"},
            "settings_label_default_save_path": {"en": "Default Save Path:", "zh": "默认保存路径:"},
            "settings_btn_browse": {"en": "Browse...", "zh": "浏览..."},
            "settings_label_filename_format": {"en": "Filename Format:", "zh": "文件名格式:"},
            "settings_chk_auto_copy_clipboard": {"en": "Auto-copy to Clipboard after capture", "zh": "截图后自动复制到剪افظ板"},
            "settings_chk_auto_start_boot": {"en": "Auto-start on Boot", "zh": "开机自启"},
            "settings_label_placeholder": {"en": " (Placeholder)", "zh": " (占位符)"},
            "settings_group_output_options": {"en": "Output Options", "zh": "输出选项"},
            "settings_label_image_format": {"en": "Image Format (Screenshots):", "zh": "图片格式 (截图):"},
            "settings_label_jpg_quality": {"en": "JPG Quality (1-100):", "zh": "JPG 质量 (1-100):"},
            "settings_label_video_format": {"en": "Video Format (Recording):", "zh": "视频格式 (录屏):"},
            "settings_label_video_fps": {"en": "Video FPS:", "zh": "视频帧率:"},
            "settings_group_interface_options": {"en": "Interface Options", "zh": "界面选项"},
            "settings_label_theme": {"en": "Theme:", "zh": "主题:"},
            "theme_light": {"en": "Light", "zh": "亮色"},
            "theme_dark": {"en": "Dark", "zh": "暗色"},
            "settings_label_language": {"en": "Language:", "zh": "语言:"},
            "settings_label_restart_required": {"en": " (Restart may be required)", "zh": " (可能需要重启生效)"},
            "settings_btn_save_apply": {"en": "Save & Apply", "zh": "保存并应用"},
            "settings_btn_cancel": {"en": "Cancel", "zh": "取消"},
            "settings_btn_restore_defaults": {"en": "Restore Defaults", "zh": "恢复默认"},
            "settings_save_success_title": {"en": "Settings Saved", "zh": "设置已保存"},
            "settings_save_success_message": {"en": "Settings have been saved successfully.", "zh": "设置已成功保存。"},
            "settings_save_error_title": {"en": "Save Error", "zh": "保存错误"},
            "settings_save_error_message": {"en": "Could not save settings.", "zh": "无法保存设置。"},
            "settings_restore_confirm_title": {"en": "Defaults Restored", "zh": "已恢复默认"},
            "settings_restore_confirm_message": {"en": "Settings in the UI have been restored to default values. Click 'Save & Apply' to keep these changes.", "zh": "界面中的设置已恢复为默认值。点击“保存并应用”以保留这些更改。"}
        })

    # Ensure a root window exists for the Toplevel window
    root = tk.Tk()
    root.withdraw() # Hide the root window, only show settings

    # Initialize config manager (loads or creates default config)
    config_manager.load_config() 

    settings_app = SettingsWindow(parent=root)
    settings_app.mainloop()
    
    # Clean up dummy root window
    if root.winfo_exists():
        root.destroy()
