import tkinter as tk
from tkinter import Menu, Button, Label, messagebox, filedialog, scrolledtext
import os

# Assuming other modules are in the same directory or package
from . import i18n 
from .main import capture_fullscreen, capture_selected_region # Assuming these are importable
from .editor import open_editor_with_image # This is used by capture_fullscreen/region indirectly
from .scrolling_capture import capture_scrolling
from .ocr import extract_text_from_image
from .recorder import ScreenRecorder # For placeholder integration

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.recorder_instance = None # For screen recording
        self.is_recording = False
        self._init_ui()

    def _init_ui(self):
        self.title(i18n._("app_title"))
        self.geometry("400x300") # Initial size, can be adjusted

        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar() # Placeholder for status messages

        self._update_ui_text() # Apply initial translations

    def _create_menubar(self):
        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        # File Menu
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=i18n._("menu_file"), menu=self.file_menu)
        
        self.file_menu.add_command(label=i18n._("menu_settings"), command=self._show_settings_placeholder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=i18n._("menu_exit"), command=self.quit)

        # Tools Menu
        self.tools_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=i18n._("menu_tools"), menu=self.tools_menu)

        self.tools_menu.add_command(label=i18n._("menu_fullscreen_shot"), command=self._trigger_fullscreen_shot)
        self.tools_menu.add_command(label=i18n._("menu_region_shot"), command=self._trigger_region_shot)
        self.tools_menu.add_command(label=i18n._("menu_scrolling_capture"), command=self._trigger_scrolling_capture)
        
        self.record_menu_label_id = "menu_screen_recording" # To update text
        self.tools_menu.add_command(label=i18n._(self.record_menu_label_id), command=self._toggle_screen_recording)
        
        self.tools_menu.add_command(label=i18n._("menu_ocr_image_file"), command=self._trigger_ocr_from_file)

        # Language Menu
        self.language_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=i18n._("menu_language"), menu=self.language_menu)
        self.language_menu.add_command(label=i18n._("lang_english"), command=lambda: self._switch_language("en"))
        self.language_menu.add_command(label=i18n._("lang_chinese"), command=lambda: self._switch_language("zh"))
        
    def _create_toolbar(self):
        self.toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        
        self.btn_fullscreen = Button(self.toolbar, text=i18n._("button_fullscreen_shot"), command=self._trigger_fullscreen_shot)
        self.btn_fullscreen.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_region = Button(self.toolbar, text=i18n._("button_region_shot"), command=self._trigger_region_shot)
        self.btn_region.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_scrolling = Button(self.toolbar, text=i18n._("button_scrolling_capture"), command=self._trigger_scrolling_capture)
        self.btn_scrolling.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_record_text_id = "button_screen_recording" # for dynamic text update
        self.btn_record = Button(self.toolbar, text=i18n._(self.btn_record_text_id), command=self._toggle_screen_recording)
        self.btn_record.pack(side=tk.LEFT, padx=2, pady=2)

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def _create_statusbar(self):
        self.status_bar = Label(self, text=i18n._("status_idle"), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_ui_text(self):
        self.title(i18n._("app_title"))
        
        # Menubar
        self.menubar.entryconfig(self.menubar.index(i18n._("menu_file")), label=i18n._("menu_file"))
        self.file_menu.entryconfig(self.file_menu.index(i18n._("menu_settings")), label=i18n._("menu_settings"))
        self.file_menu.entryconfig(self.file_menu.index(i18n._("menu_exit")), label=i18n._("menu_exit"))
        
        self.menubar.entryconfig(self.menubar.index(i18n._("menu_tools")), label=i18n._("menu_tools"))
        self.tools_menu.entryconfig(self.tools_menu.index(i18n._("menu_fullscreen_shot")), label=i18n._("menu_fullscreen_shot"))
        self.tools_menu.entryconfig(self.tools_menu.index(i18n._("menu_region_shot")), label=i18n._("menu_region_shot"))
        self.tools_menu.entryconfig(self.tools_menu.index(i18n._("menu_scrolling_capture")), label=i18n._("menu_scrolling_capture"))
        
        # Dynamic text for recording menu item
        current_record_label = i18n._("menu_screen_recording_stop") if self.is_recording else i18n._("menu_screen_recording_start")
        if not hasattr(self, '_tools_menu_record_item_label_applied') or \
           self._tools_menu_record_item_label_applied != current_record_label:
            try:
                # Find by current label (which might be in old language)
                # This is a bit fragile. Better to store the menu item object if possible.
                # For simplicity now, we assume the label text is unique enough or position is fixed.
                # A more robust way is to store self.tools_menu.index("Screen Recording") at creation.
                # Let's assume it's the 4th item (index 3, after the 3 screenshot types)
                self.tools_menu.entryconfig(3, label=current_record_label) # index for "Screen Recording"
                self._tools_menu_record_item_label_applied = current_record_label
            except tk.TclError: # If index is wrong or item not found by old label
                 # Fallback: try to find by one of the known text_ids if current label is not matching
                 try: self.tools_menu.entryconfig(self.tools_menu.index(i18n.TRANSLATIONS["menu_screen_recording_start"]["en"]), label=current_record_label)
                 except: pass # if all fails, it might not update this time.
                 try: self.tools_menu.entryconfig(self.tools_menu.index(i18n.TRANSLATIONS["menu_screen_recording_start"]["zh"]), label=current_record_label)
                 except: pass


        self.tools_menu.entryconfig(self.tools_menu.index(i18n._("menu_ocr_image_file")), label=i18n._("menu_ocr_image_file"))

        self.menubar.entryconfig(self.menubar.index(i18n._("menu_language")), label=i18n._("menu_language"))
        self.language_menu.entryconfig(self.language_menu.index(i18n._("lang_english")), label=i18n._("lang_english"))
        self.language_menu.entryconfig(self.language_menu.index(i18n._("lang_chinese")), label=i18n._("lang_chinese"))

        # Toolbar buttons
        self.btn_fullscreen.config(text=i18n._("button_fullscreen_shot"))
        self.btn_region.config(text=i18n._("button_region_shot"))
        self.btn_scrolling.config(text=i18n._("button_scrolling_capture"))
        
        # Dynamic text for record button
        record_btn_text = i18n._("button_screen_recording_stop") if self.is_recording else i18n._("button_screen_recording_start")
        self.btn_record.config(text=record_btn_text)

        # Status bar
        self.status_bar.config(text=i18n._("status_idle")) # Reset status on language switch

    def _switch_language(self, lang_code):
        i18n.set_language(lang_code)
        # Add "start/stop" variants to TRANSLATIONS for button/menu record
        # This should be done in i18n.py ideally. For now, quick add:
        if "menu_screen_recording_start" not in i18n.TRANSLATIONS:
            i18n.TRANSLATIONS["menu_screen_recording_start"] = {"en": "Start Screen Recording", "zh": "开始屏幕录制"}
            i18n.TRANSLATIONS["menu_screen_recording_stop"] = {"en": "Stop Screen Recording", "zh": "停止屏幕录制"}
            i18n.TRANSLATIONS["button_screen_recording_start"] = {"en": "Record Screen", "zh": "开始录制"}
            i18n.TRANSLATIONS["button_screen_recording_stop"] = {"en": "Stop Recording", "zh": "停止录制"}
        self._update_ui_text()

    def _show_settings_placeholder(self):
        messagebox.showinfo(i18n._("settings_placeholder_title"), i18n._("settings_placeholder_message"), parent=self)

    def _trigger_fullscreen_shot(self):
        self.status_bar.config(text="Capturing fullscreen...")
        self.update_idletasks() # Ensure status bar updates
        try:
            # Assuming capture_fullscreen now handles opening the editor
            capture_fullscreen() 
            self.status_bar.config(text=i18n._("status_idle"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture fullscreen: {e}", parent=self)
            self.status_bar.config(text=i18n._("status_idle"))


    def _trigger_region_shot(self):
        self.status_bar.config(text="Select region for capture...")
        self.update_idletasks()
        try:
            # Assuming capture_selected_region now handles opening the editor
            # Hide main window during region selection
            self.withdraw() 
            capture_selected_region()
            self.deiconify() # Show main window again
            self.status_bar.config(text=i18n._("status_idle"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture region: {e}", parent=self)
            self.status_bar.config(text=i18n._("status_idle"))
            if not self.winfo_viewable(): self.deiconify()


    def _trigger_scrolling_capture(self):
        self.status_bar.config(text="Starting scrolling capture. Focus target window...")
        self.update_idletasks()
        try:
            # Hide main window during scrolling capture to avoid it being part of capture
            self.withdraw()
            time.sleep(0.5) # Give it a moment to hide
            
            # Define output path for scrolling capture
            captures_dir = "captures"
            if not os.path.exists(captures_dir):
                os.makedirs(captures_dir, exist_ok=True)
            output_file = os.path.join(captures_dir, "gui_scrolling_capture.png")
            
            capture_scrolling(output_filename=output_file) # Uses its own prints for progress
            
            self.deiconify()
            messagebox.showinfo("Scrolling Capture", f"Scrolling capture attempt finished. Saved to {output_file}", parent=self)
            self.status_bar.config(text=i18n._("status_idle"))
            
            # Optional: Open the stitched image in the editor
            if messagebox.askyesno("Open Editor", "Open the scrolling capture in the editor?", parent=self):
                open_editor_with_image(output_file)

        except Exception as e:
            messagebox.showerror("Error", f"Failed scrolling capture: {e}", parent=self)
            self.status_bar.config(text=i18n._("status_idle"))
            if not self.winfo_viewable(): self.deiconify()


    def _toggle_screen_recording(self):
        # Add "start/stop" variants to TRANSLATIONS for button/menu record
        # This is a bit messy here, should be in i18n.py or loaded from a proper resource file.
        if "menu_screen_recording_start" not in i18n.TRANSLATIONS:
            i18n.TRANSLATIONS["menu_screen_recording_start"] = {"en": "Start Screen Recording", "zh": "开始屏幕录制"}
            i18n.TRANSLATIONS["menu_screen_recording_stop"] = {"en": "Stop Screen Recording", "zh": "停止屏幕录制"}
            i18n.TRANSLATIONS["button_screen_recording_start"] = {"en": "Record Screen", "zh": "开始录制"}
            i18n.TRANSLATIONS["button_screen_recording_stop"] = {"en": "Stop Recording", "zh": "停止录制"}


        if not self.is_recording:
            # Start recording
            videos_dir = "videos"
            if not os.path.exists(videos_dir):
                os.makedirs(videos_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(videos_dir, f"recording_{timestamp}.mp4")
            
            # Ask for FPS (optional, could be a setting later)
            fps_str = tk.simpledialog.askstring("FPS", "Enter recording FPS (e.g., 15, 20, 30):", initialvalue="15.0", parent=self)
            try:
                fps = float(fps_str) if fps_str else 15.0
            except ValueError:
                fps = 15.0
            
            self.recorder_instance = ScreenRecorder(output_filename=output_filename, fps=fps)
            try:
                self.recorder_instance.start_recording()
                if self.recorder_instance.get_status()["is_recording"]:
                    self.is_recording = True
                    self.status_bar.config(text=f"Recording to {output_filename}...")
                    messagebox.showinfo("Screen Recording", f"Recording started: {output_filename}", parent=self)
                else: # Failed to start (e.g. VideoWriter error)
                    self.is_recording = False
                    self.recorder_instance = None # Clear instance
                    messagebox.showerror("Recording Error", "Could not start screen recording. Check console for errors.", parent=self)
                    self.status_bar.config(text=i18n._("status_idle"))
            except Exception as e:
                 messagebox.showerror("Recording Error", f"Failed to start recording: {e}", parent=self)
                 self.is_recording = False
                 self.recorder_instance = None
                 self.status_bar.config(text=i18n._("status_idle"))
        else:
            # Stop recording
            if self.recorder_instance:
                self.recorder_instance.stop_recording()
                saved_file = self.recorder_instance.output_filename
                self.is_recording = False
                self.recorder_instance = None
                self.status_bar.config(text=f"Recording stopped. Saved to {saved_file}")
                messagebox.showinfo("Screen Recording", f"Recording stopped. Saved to {saved_file}", parent=self)
            else: # Should not happen if is_recording is true
                self.is_recording = False 
                self.status_bar.config(text="Error: Recorder instance not found.")
        
        self._update_ui_text() # Update button/menu text to "Start/Stop Recording"


    def _trigger_ocr_from_file(self):
        filepath = filedialog.askopenfilename(
            title=i18n._("ocr_select_image_title"),
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")],
            parent=self)
        
        if not filepath:
            return

        self.status_bar.config(text=f"Performing OCR on {os.path.basename(filepath)}...")
        self.update_idletasks()
        
        # Ask for language (can be a setting later)
        # Example: 'eng', 'chi_sim', 'jpn', 'deu', 'fra'
        # For multiple languages: 'eng+fra'
        lang_code = tk.simpledialog.askstring("OCR Language", 
                                              "Enter language code(s) for OCR (e.g., 'eng', 'chi_sim', 'eng+fra'):", 
                                              initialvalue=i18n.get_language(), # Default to current UI lang if suitable or 'eng'
                                              parent=self)
        if not lang_code: # User cancelled or entered empty
            lang_code = 'eng' # Default to English if nothing provided

        extracted_text = extract_text_from_image(filepath, lang=lang_code)
        
        result_display_window = tk.Toplevel(self)
        result_display_window.title(i18n._("ocr_result_title"))
        result_display_window.geometry("500x400")
        
        text_area = scrolledtext.ScrolledText(result_display_window, wrap=tk.WORD, width=60, height=20)
        if extracted_text:
            text_area.insert(tk.INSERT, extracted_text)
        else:
            text_area.insert(tk.INSERT, i18n._("ocr_no_text_found"))
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.configure(state='disabled') # Make it read-only

        self.status_bar.config(text=i18n._("status_idle"))

if __name__ == '__main__':
    # This allows testing gui.py directly if needed,
    # but the main entry point will be from main.py
    app = MainApplication()
    app.mainloop()
