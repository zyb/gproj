import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter

class ImageEditor:
    def __init__(self, master, image_path_or_object):
        self.master = master
        self.master.title("Image Editor")

        if isinstance(image_path_or_object, str):
            try:
                self.image_original = Image.open(image_path_or_object).convert("RGBA")
            except FileNotFoundError:
                messagebox.showerror("Error", f"Image file not found: {image_path_or_object}")
                self.master.destroy()
                return
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")
                self.master.destroy()
                return
        elif isinstance(image_path_or_object, Image.Image):
            self.image_original = image_path_or_object.convert("RGBA")
        else:
            messagebox.showerror("Error", "Invalid image input. Must be a file path or PIL.Image object.")
            self.master.destroy()
            return

        self.image_display = self.image_original.copy() # Image for display and temporary edits
        self.tk_image = None # For tkinter display

        # History for undo/redo
        self.history = [self.image_original.copy()]
        self.history_index = 0

        # Drawing defaults
        self.current_color = "red" # Renamed from draw_color
        self.line_width = 3
        self.font_size = 20
        self.font_family = "Arial" # A common default

        # Current tool
        self.current_tool = None # e.g., "rectangle", "line", "text", "crop"
        self.start_x = None
        self.start_y = None
        self.temp_drawing_item = None # For previewing shapes during drag

        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        toolbar = tk.Frame(main_frame, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # --- Placeholder for toolbar buttons ---
        tk.Label(toolbar, text="Tools", font=("Arial", 12, "bold")).pack(pady=5)
        
        btn_rect = tk.Button(toolbar, text="Rect", command=lambda: self.set_tool("rectangle"))
        btn_rect.pack(fill=tk.X, pady=2)

        btn_ellipse = tk.Button(toolbar, text="Ellipse", command=lambda: self.set_tool("ellipse"))
        btn_ellipse.pack(fill=tk.X, pady=2)

        btn_line = tk.Button(toolbar, text="Line", command=lambda: self.set_tool("line"))
        btn_line.pack(fill=tk.X, pady=2)
        
        btn_arrow = tk.Button(toolbar, text="Arrow", command=lambda: self.set_tool("arrow"))
        btn_arrow.pack(fill=tk.X, pady=2)

        btn_text = tk.Button(toolbar, text="Text", command=lambda: self.set_tool("text"))
        btn_text.pack(fill=tk.X, pady=2)

        btn_pen = tk.Button(toolbar, text="Pen", command=lambda: self.set_tool("pen"))
        btn_pen.pack(fill=tk.X, pady=2)

        btn_crop = tk.Button(toolbar, text="Crop", command=lambda: self.set_tool("crop"))
        btn_crop.pack(fill=tk.X, pady=2)

        btn_blur = tk.Button(toolbar, text="Blur", command=lambda: self.set_tool("blur_region"))
        btn_blur.pack(fill=tk.X, pady=2)
        
        btn_mosaic = tk.Button(toolbar, text="Mosaic", command=lambda: self.set_tool("mosaic_region"))
        btn_mosaic.pack(fill=tk.X, pady=2)
        
        tk.Label(toolbar, text="Options", font=("Arial", 10, "bold")).pack(pady=(10,0)) # This label might need i18n if not already
        
        # Updated button text to use i18n key and command to renamed method
        self.btn_select_color = tk.Button(toolbar, text=i18n._("button_select_color"), command=self._select_pen_color)
        self.btn_select_color.pack(fill=tk.X, pady=2)

        btn_line_width = tk.Button(toolbar, text="Line Width", command=self.choose_line_width) # Assuming "Line Width" has i18n key or is fine
        btn_line_width.pack(fill=tk.X, pady=2)

        btn_font_size = tk.Button(toolbar, text="Font Size", command=self.choose_font_size)
        btn_font_size.pack(fill=tk.X, pady=2)

        tk.Label(toolbar, text="Actions", font=("Arial", 10, "bold")).pack(pady=(10,0))
        btn_copy_clipboard = tk.Button(toolbar, text="Copy", command=self.copy_to_clipboard)
        btn_copy_clipboard.pack(fill=tk.X, pady=2)

        btn_save = tk.Button(toolbar, text="Save", command=self.save_image)
        btn_save.pack(fill=tk.X, pady=2)
        
        btn_save_as = tk.Button(toolbar, text="Save As", command=self.save_as_image)
        btn_save_as.pack(fill=tk.X, pady=2)


        # Canvas for image
        self.canvas = tk.Canvas(main_frame, bg="lightgrey", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.display_image_on_canvas()

        # Bind mouse events to canvas
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Bind keyboard shortcuts for undo/redo
        self.master.bind_all("<Control-z>", self.undo)
        self.master.bind_all("<Control-y>", self.redo) # Or <Control-Shift-Z> on some systems

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.saved_once = False # To track if initial save has happened for "Save" vs "Save As" logic
        self.current_file_path = None
        if isinstance(image_path_or_object, str):
            self.current_file_path = image_path_or_object


    def display_image_on_canvas(self):
        if self.image_display:
            # Resize image to fit canvas if it's too large, maintaining aspect ratio
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width < 50 or canvas_height < 50: # Canvas not yet sized
                self.master.after(50, self.display_image_on_canvas) # Retry after a short delay
                return

            img_w, img_h = self.image_display.size
            
            # Maintain aspect ratio
            ratio = min(canvas_width / img_w, canvas_height / img_h)
            
            if ratio < 1.0: # Only scale down if image is larger than canvas
                new_width = int(img_w * ratio)
                new_height = int(img_h * ratio)
                img_to_show = self.image_display.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                img_to_show = self.image_display

            self.tk_image = ImageTk.PhotoImage(img_to_show)
            self.canvas.delete("all") # Clear previous image
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                     anchor=tk.CENTER, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))


    def set_tool(self, tool_name):
        self.current_tool = tool_name
        print(f"Tool set to: {self.current_tool}")
        if self.current_tool not in ["crop", "blur_region", "mosaic_region"]: # These tools don't need a temp drawing item
            self.canvas.config(cursor="cross")
        else:
            self.canvas.config(cursor="plus") # Cursor for selection type tools


    def _select_pen_color(self): # Renamed from choose_color
        # Use self.current_color as the initial color for the dialog
        color_code = colorchooser.askcolor(initialcolor=self.current_color, title="Choose Pen Color", parent=self.master)
        if color_code and color_code[1]: # Check if a color was selected and hex string is available
            self.current_color = color_code[1]
            print(f"Pen color set to: {self.current_color}")
            # Optional: Update a UI element to show the new color, e.g., self.color_preview.config(bg=self.current_color)

    def choose_line_width(self):
        width = simpledialog.askinteger("Line Width", "Enter line width (e.g., 1-10):",
                                        parent=self.master, minvalue=1, maxvalue=50, initialvalue=self.line_width)
        if width:
            self.line_width = width
            print(f"Line width set to: {self.line_width}")

    def choose_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter font size (e.g., 10-48):",
                                       parent=self.master, minvalue=8, maxvalue=100, initialvalue=self.font_size)
        if size:
            self.font_size = size
            print(f"Font size set to: {self.font_size}")

    def on_canvas_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # For tools that draw temporary shapes on canvas (not directly on Pillow image yet)
        if self.current_tool in ["rectangle", "ellipse", "line", "arrow", "crop", "blur_region", "mosaic_region"]:
            if self.temp_drawing_item:
                self.canvas.delete(self.temp_drawing_item)
            if self.current_tool == "rectangle" or self.current_tool == "crop" or self.current_tool == "blur_region" or self.current_tool == "mosaic_region":
                self.temp_drawing_item = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                                    outline=self.current_color, width=self.line_width)
            elif self.current_tool == "ellipse":
                 self.temp_drawing_item = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y,
                                                                    outline=self.current_color, width=self.line_width)
            elif self.current_tool == "line":
                self.temp_drawing_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y,
                                                                 fill=self.current_color, width=self.line_width)
            elif self.current_tool == "arrow":
                 self.temp_drawing_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y,
                                                                 fill=self.current_color, width=self.line_width, arrow=tk.LAST)
        elif self.current_tool == "pen":
            self.image_draw = ImageDraw.Draw(self.image_display) # Prepare to draw on Pillow image

    def on_canvas_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.temp_drawing_item and self.current_tool in ["rectangle", "ellipse", "line", "arrow", "crop", "blur_region", "mosaic_region"]:
            self.canvas.coords(self.temp_drawing_item, self.start_x, self.start_y, cur_x, cur_y)
        elif self.current_tool == "pen" and self.start_x is not None and self.start_y is not None:
            # Map canvas coordinates to image coordinates for pen tool
            img_cur_x, img_cur_y = self._get_image_coords(cur_x, cur_y)
            img_start_x, img_start_y = self._get_image_coords(self.start_x, self.start_y)

            self.image_draw.line([(img_start_x, img_start_y), (img_cur_x, img_cur_y)],
                                 fill=self.current_color, width=self.line_width, capstyle="round", joinstyle="round")
            
            # Update start_x, start_y with the original canvas coordinates for the next segment of this drag
            self.start_x, self.start_y = cur_x, cur_y 
            self.display_image_on_canvas() # Update display

    def on_canvas_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        # Ensure coordinates are relative to original image if scaled
        # This requires mapping canvas coords back to original image coords
        # For simplicity here, we'll assume 1:1 or handle scaling during actual drawing
        # A more robust solution maps these coordinates back to the original image space.
        
        # For now, let's assume drawing coordinates are directly applicable to self.image_display
        # This will be accurate if the image is smaller than or fits the canvas without scaling down.
        # If scaled down, coordinates need adjustment.
        # Let's add a helper for coordinate mapping
        
        # For text tool, we use the start_x, start_y directly for placement.
        if self.current_tool == "text":
            # Text tool uses a single click for position, not drag.
            # So, sx, sy are the click point for text placement.
            sx_text, sy_text = self._get_image_coords(self.start_x, self.start_y)
            text_to_add = simpledialog.askstring("Input", "Enter text:", parent=self.master)
            if text_to_add:
                try:
                    # Attempt to load a common font, otherwise default
                    font = ImageFont.truetype(f"{self.font_family.lower()}.ttf", self.font_size)
                except IOError:
                    try:
                        font = ImageFont.truetype("arial.ttf", self.font_size) # Common fallback
                    except IOError:
                        font = ImageFont.load_default() # Absolute fallback
                
                self.image_draw = ImageDraw.Draw(self.image_display)
                self.image_draw.text((sx_text, sy_text), text_to_add, font=font, fill=self.current_color)
                self.add_history_state()
                self.display_image_on_canvas()
            self.start_x, self.start_y = None, None # Reset after text is placed
            return # Text tool action is complete on press for this implementation

        # For other tools that use drag:
        sx, sy = self._get_image_coords(self.start_x, self.start_y)
        ex, ey = self._get_image_coords(end_x, end_y)


        if self.current_tool in ["rectangle", "ellipse", "line", "arrow"]:
            # Ensure sx < ex and sy < ey for rects/ovals for consistent drawing
            # However, for lines/arrows, the original start/end points matter for direction
            self.image_draw = ImageDraw.Draw(self.image_display)
            if self.current_tool == "rectangle":
                self.image_draw.rectangle([min(sx,ex), min(sy,ey), max(sx,ex), max(sy,ey)], outline=self.current_color, width=self.line_width)
            elif self.current_tool == "ellipse":
                self.image_draw.ellipse([min(sx,ex), min(sy,ey), max(sx,ex), max(sy,ey)], outline=self.current_color, width=self.line_width)
            elif self.current_tool == "line":
                 # Use original mapped start/end for lines to preserve direction
                sx_orig, sy_orig = self._get_image_coords(self.start_x, self.start_y)
                ex_orig, ey_orig = self._get_image_coords(end_x, end_y)
                self.image_draw.line([sx_orig, sy_orig, ex_orig, ey_orig], fill=self.current_color, width=self.line_width)
            elif self.current_tool == "arrow":
                sx_orig, sy_orig = self._get_image_coords(self.start_x, self.start_y)
                ex_orig, ey_orig = self._get_image_coords(end_x, end_y)
                self.image_draw.line([sx_orig, sy_orig, ex_orig, ey_orig], fill=self.current_color, width=self.line_width)
                self._draw_arrowhead(self.image_draw, sx_orig, sy_orig, ex_orig, ey_orig, self.current_color, self.line_width)

            if self.temp_drawing_item:
                self.canvas.delete(self.temp_drawing_item)
                self.temp_drawing_item = None
            self.add_history_state()
            self.display_image_on_canvas()
        
        elif self.current_tool == "pen":
            # Pen drawing happens in on_canvas_drag, just finalize history
            # Need to ensure sx, sy, ex, ey are mapped for pen as well if we want to use the _get_image_coords
            # The current pen tool draws directly using canvas coords scaled in on_canvas_drag.
            # For consistency, pen should also use _get_image_coords.
            # However, pen draws segments, so this release might just be finalization.
            if hasattr(self, 'image_draw'): # Ensure drawing was initiated by pen tool
                del self.image_draw # Finalize drawing object for this continuous stroke
                self.add_history_state()
                # display_image_on_canvas() was called during drag

        elif self.current_tool == "crop":
            if self.temp_drawing_item:
                self.canvas.delete(self.temp_drawing_item)
                self.temp_drawing_item = None
            # Use min/max for crop box to ensure correct coordinates
            crop_x1, crop_y1 = min(sx, ex), min(sy, ey)
            crop_x2, crop_y2 = max(sx, ex), max(sy, ey)

            if crop_x1 < crop_x2 and crop_y1 < crop_y2: # Valid crop area
                self.image_display = self.image_display.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                self.add_history_state()
                self.display_image_on_canvas()

        elif self.current_tool == "blur_region" or self.current_tool == "mosaic_region":
            if self.temp_drawing_item:
                self.canvas.delete(self.temp_drawing_item)
                self.temp_drawing_item = None
            
            # Use min/max for region box
            reg_x1, reg_y1 = min(sx, ex), min(sy, ey)
            reg_x2, reg_y2 = max(sx, ex), max(sy, ey)

            if reg_x1 < reg_x2 and reg_y1 < reg_y2:
                region_coords = (reg_x1, reg_y1, reg_x2, reg_y2)
                
                # Ensure region coords are within image bounds
                img_w, img_h = self.image_display.size
                region_coords = (max(0, region_coords[0]), max(0, region_coords[1]),
                                 min(img_w, region_coords[2]), min(img_h, region_coords[3]))

                if region_coords[0] < region_coords[2] and region_coords[1] < region_coords[3]: # Check again after clamping
                    crop_region = self.image_display.crop(region_coords)
                    
                    if self.current_tool == "blur_region":
                        processed_region = crop_region.filter(ImageFilter.GaussianBlur(radius=5))
                    else: # mosaic_region
                        pixel_size = max(5, int(min(crop_region.width, crop_region.height) * 0.1)) # Mosaic pixel size relative to region
                        if crop_region.width < pixel_size or crop_region.height < pixel_size : # region too small for mosaic
                             processed_region = crop_region.filter(ImageFilter.GaussianBlur(radius=2)) # fallback to blur
                        else:
                            small = crop_region.resize(
                                (max(1, crop_region.width // pixel_size), max(1, crop_region.height // pixel_size)), 
                                Image.Resampling.BILINEAR
                            )
                            processed_region = small.resize(crop_region.size, Image.Resampling.NEAREST)
                    
                    self.image_display.paste(processed_region, region_coords)
                    self.add_history_state()
                    self.display_image_on_canvas()
                else:
                    print("Selected region for effect is outside image bounds or too small after clamping.")
            else:
                print("Selected region for effect has zero width or height.")
        
        self.start_x, self.start_y = None, None # Reset for next action

    def _get_image_coords(self, canvas_x, canvas_y):
        """Converts canvas coordinates to image_display coordinates."""
        if not self.image_display or not self.tk_image or self.canvas.winfo_width() < 1 or self.canvas.winfo_height() < 1:
            # Canvas not ready or no image
            return int(canvas_x), int(canvas_y)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_disp_w, img_disp_h = self.image_display.size # Current dimensions of the image being edited
        
        # Calculate the scaling ratio used for display
        ratio = 1.0
        if img_disp_w > 0 and img_disp_h > 0 : # Avoid division by zero
             ratio = min(canvas_width / img_disp_w, canvas_height / img_disp_h)
        
        displayed_img_w_on_canvas = img_disp_w
        displayed_img_h_on_canvas = img_disp_h

        if ratio < 1.0: # Image was scaled down to fit canvas
            displayed_img_w_on_canvas = int(img_disp_w * ratio)
            displayed_img_h_on_canvas = int(img_disp_h * ratio)
        # If ratio >= 1.0, image is displayed at its actual size or smaller than canvas, so no scaling down of image,
        # but it's still centered.

        # Top-left corner of the (potentially scaled) image on the canvas (it's centered)
        img_canvas_origin_x = (canvas_width - displayed_img_w_on_canvas) // 2
        img_canvas_origin_y = (canvas_height - displayed_img_h_on_canvas) // 2

        # Click position relative to the top-left of the image *as displayed on canvas*
        relative_x_on_canvas = canvas_x - img_canvas_origin_x
        relative_y_on_canvas = canvas_y - img_canvas_origin_y
        
        # Convert these relative canvas coordinates to actual image_display coordinates
        if ratio < 1.0: # Scaled down
            actual_x = relative_x_on_canvas / ratio
            actual_y = relative_y_on_canvas / ratio
        else: # Displayed at original size (or canvas is larger)
            actual_x = relative_x_on_canvas
            actual_y = relative_y
            
        # Clamp to the boundaries of self.image_display
        actual_x = max(0, min(actual_x, img_disp_w - 1))
        actual_y = max(0, min(actual_y, img_disp_h - 1))

        return int(actual_x), int(actual_y)


    def _draw_arrowhead(self, draw, x1, y1, x2, y2, color, width):
        """Draws an arrowhead on the line from (x1,y1) to (x2,y2)."""
        # Calculate angle of the line
        import math
        # Ensure x1, y1 is start, x2, y2 is end for correct arrowhead direction
        angle = math.atan2(y2 - y1, x2 - x1) # Note: y is often inverted in graphics vs math
        
        # Arrowhead properties
        arrow_length = 8 + self.line_width * 2.5 # Adjusted for better proportion
        arrow_degrees = 0.4 # Radians, approx 22.5 degrees for each wing

        # Arrowhead wing points
        # Point 1
        px1 = x2 - arrow_length * math.cos(angle - arrow_degrees)
        py1 = y2 - arrow_length * math.sin(angle - arrow_degrees)
        # Point 2
        px2 = x2 - arrow_length * math.cos(angle + arrow_degrees)
        py2 = y2 - arrow_length * math.sin(angle + arrow_degrees)
        
        # Draw filled polygon for arrowhead
        draw.polygon([(x2, y2), (px1, py1), (px2, py2)], fill=self.current_color) # Use self.current_color if 'color' param is not specific


    def add_history_state(self):
        # If we undo and then make a new change, clear the "redo" history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Deep copy the current state of image_display for history
        current_image_state = self.image_display.copy()
        self.history.append(current_image_state)
        self.history_index += 1
        
        # Optional: Limit history size to prevent excessive memory usage
        # if len(self.history) > 20:
        #     self.history = self.history[-20:]
        #     if self.history_index > 19: # Adjust index if truncated from beginning
        #         self.history_index = 19 


    def undo(self, event=None):
        if self.history_index > 0:
            self.history_index -= 1
            self.image_display = self.history[self.history_index].copy()
            self.display_image_on_canvas()
            print(f"Undo performed. History index: {self.history_index}")
        else:
            print("Nothing to undo.")
            messagebox.showinfo("Undo", "Nothing further to undo.", parent=self.master)


    def redo(self, event=None):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image_display = self.history[self.history_index].copy()
            self.display_image_on_canvas()
            print(f"Redo performed. History index: {self.history_index}")
        else:
            print("Nothing to redo.")
            messagebox.showinfo("Redo", "Nothing further to redo.", parent=self.master)


    def copy_to_clipboard(self):
        # This is a simplified version. True image clipboard support is complex.
        # Option 1: Use a library that supports images (e.g., specific Qt bindings if using PyQt/PySide)
        # Option 2: Save to a temp file and copy file path (not ideal)
        # Option 3: For Tkinter, try to use its clipboard capabilities for images if possible.
        # For now, a message or a very basic attempt.
        try:
            import io
            import pyperclip # Added to requirements

            # Convert Pillow image to bytes in PNG format
            image_bytes = io.BytesIO()
            self.image_display.save(image_bytes, format="PNG")
            image_data = image_bytes.getvalue() # This is raw PNG data

            # Pyperclip is primarily for text.
            # For cross-platform image clipboard, it's non-trivial.
            # A common workaround is to inform the user the image is "copied"
            # and have a mechanism for pasting if the app also controlled that.
            # Or use platform specific tools.
            
            # Let's try Tkinter's clipboard for image data if possible.
            # This is not universally supported for images across all OS versions / Tk versions.
            # Tkinter's clipboard append/clear expects string data.
            # A more robust way involves platform specific APIs or larger libraries like Kivy, Qt.

            # Fallback: Inform user, or copy a representation.
            # For this exercise, let's try to use pyperclip to copy a message
            # as direct image copy is too complex for a single tool call update.
            
            # A more advanced Tkinter approach might involve:
            # self.master.clipboard_clear()
            # self.master.clipboard_append(image_data, type='IMAGE') # This is hypothetical, type='IMAGE' is not standard
            # A common way is to base64 encode the image and put that on clipboard,
            # then the receiving app decodes it.

            # For now, let's save to a temporary file and copy the path as a placeholder for a more robust solution.
            import tempfile
            import os
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            self.image_display.save(temp_file.name)
            temp_file.close() # Close it so pyperclip can access if needed, path still valid
            
            pyperclip.copy(temp_file.name) # Copies the file path to clipboard
            messagebox.showinfo("Copied to Clipboard", f"Image saved to temporary path and path copied to clipboard: {temp_file.name}\n(Note: This is a file path, not the image data itself for universal pasting)", parent=self.master)
            # Ideally, the temp file should be cleaned up later.

        except ImportError:
            messagebox.showwarning("Clipboard Error", "Pyperclip library not found. Please install it (`pip install pyperclip`) to use clipboard functions.", parent=self.master)
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}", parent=self.master)


    def save_image(self):
        if self.current_file_path and self.saved_once: # If previously saved and path known
            try:
                # Ensure RGB if saving as JPEG (common requirement)
                image_to_save = self.image_display
                if self.current_file_path.lower().endswith(('.jpg', '.jpeg')):
                    if image_to_save.mode == 'RGBA' or image_to_save.mode == 'P':
                        image_to_save = image_to_save.convert('RGB')
                image_to_save.save(self.current_file_path)
                messagebox.showinfo("Saved", f"Image saved to {self.current_file_path}", parent=self.master)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}", parent=self.master)
        else:
            # If not saved before, or path not known, trigger "Save As"
            self.save_as_image()

    def save_as_image(self):
        # Suggest a filename based on current if available, else default
        initial_filename = os.path.basename(self.current_file_path) if self.current_file_path else "edited_image.png"
        initial_dir = os.path.dirname(self.current_file_path) if self.current_file_path else os.getcwd()

        file_path = filedialog.asksaveasfilename(
            initialfile=initial_filename,
            initialdir=initial_dir,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), 
                       ("JPEG files", "*.jpg;*.jpeg"), 
                       ("Bitmap files", "*.bmp"),
                       ("GIF files", "*.gif"),
                       ("All files", "*.*")],
            parent=self.master
        )
        if file_path:
            try:
                image_to_save = self.image_display
                # Handle transparency for formats that don't support alpha (e.g., JPEG, BMP)
                file_ext = file_path.lower().split('.')[-1]
                if file_ext in ['jpg', 'jpeg', 'bmp']:
                    if image_to_save.mode == 'RGBA' or image_to_save.mode == 'P':
                        # Create a white background image
                        background = Image.new('RGB', image_to_save.size, (255, 255, 255))
                        background.paste(image_to_save, mask=image_to_save.split()[3] if image_to_save.mode == 'RGBA' else None) # Paste using alpha channel as mask
                        image_to_save = background
                    elif image_to_save.mode == 'LA': # Luminance + Alpha
                        background = Image.new('L', image_to_save.size, 255) # White background for grayscale
                        background.paste(image_to_save, mask=image_to_save.split()[1])
                        image_to_save = background.convert('RGB') # JPEGs are typically RGB
                
                image_to_save.save(file_path)
                self.current_file_path = file_path # Update current path
                self.saved_once = True # Mark as saved
                self.master.title(f"Image Editor - {os.path.basename(file_path)}")
                messagebox.showinfo("Saved", f"Image saved as {file_path}", parent=self.master)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}", parent=self.master)
    
    def on_close(self):
        # Check if the current image_display state is different from the last saved state in history
        # or if it's different from the initial state and never saved.
        
        is_modified_since_last_save = True # Assume modified unless proven otherwise
        if self.saved_once and self.history_index < len(self.history):
            # Compare current image_display with the version that was last explicitly saved.
            # This is tricky because "Save" updates current_file_path but doesn't necessarily mean
            # the current history[history_index] is that saved state if user undid after save.
            # A simpler check: is image_display different from history[history_index]?
            # And was it saved at least once?
            # A more robust check would involve comparing self.image_display to the actual file content
            # or a copy made at the time of saving.

            # Simpler: If history_index points to a state that is different from image_display, it's "dirty".
            # Or if (self.history_index == len(self.history) -1) means no undo since last change.
            
            # If saved_once is true, we can assume the current file_path holds a saved version.
            # The question is whether self.image_display is *that* version.
            # For simplicity: if there are changes (history_index > 0 for initial load, or more states)
            # and the current image is not identical to the last state in history (if any undos happened)
            # or not identical to the original image if no saves occurred.

        # Simplified check: if current image is different from the one at history_index, it means changes were made
        # and potentially not saved in their current state.
        # Or, if current image is different from the original image and we haven't saved at all.
        
        # Let's check against the *latest* state in history (self.history[-1])
        # If self.image_display is not self.history[self.history_index], it means user has undone to a previous state.
        # If self.image_display *is* self.history[self.history_index] but this is different from self.history[0] (original)
        # and not self.saved_once, then it's unsaved.
        
        # A practical approach:
        # If the image_display is different from what's at self.current_file_path (if it exists and saved_once)
        # Or if not saved_once and image_display is different from initial image (history[0])
        
        # Current check:
        # 1. Has more than the initial state in history? (len(self.history) > 1)
        # 2. Is the current self.image_display different from the very first image loaded (self.history[0])?
        # This covers "made any change at all".
        made_any_change = False
        if len(self.history) > 0: # Should always be true after init
             if self.image_display.tobytes() != self.history[0].tobytes():
                 made_any_change = True

        if made_any_change:
            # Now, are these changes saved?
            # If not saved_once, then definitely unsaved changes.
            # If saved_once, are the current changes *the ones* that were saved?
            # This is hard to track perfectly without storing a pristine copy of the last saved version.
            # A common heuristic: if made_any_change and current_file_path exists,
            # assume changes after the last save might exist.
            
            # Let's use a flag: self.is_dirty
            # Set self.is_dirty = True after any modification.
            # Set self.is_dirty = False after save/save_as.
            # (This needs adding self.is_dirty logic throughout)

            # For now, using existing logic:
            # If (there are changes from original) AND ( (never saved) OR (current display is not the latest history item, implying undo after last op) )
            # The original logic is:
            # (len(self.history) > 1 AND self.image_display.tobytes() != self.history[0].tobytes()) : This means "modified from original"
            # AND
            # (not self.saved_once OR self.image_display.tobytes() != self.history[self.history_index].tobytes()):
            #    If not saved_once, it's true.
            #    If saved_once, it's true if current display is not what current history index points to (e.g. undo after change).
            # This logic seems mostly fine for prompting.

            prompt_needed = False
            if made_any_change: # Modified from original
                if not self.saved_once:
                    prompt_needed = True
                else:
                    # If saved, are the current changes committed to file?
                    # This requires comparing self.image_display to the file at self.current_file_path
                    # which is too slow for on_close.
                    # A simpler proxy: if the current image_display is not the *latest* possible state in history,
                    # it implies an undo or some operation made it different from the tip of history.
                    # Or, if any operation happened since the last save.
                    # The current logic `self.image_display.tobytes() != self.history[self.history_index].tobytes()`
                    # is problematic because image_display *is* usually history[history_index].
                    # We need a flag like `changes_since_last_save`.

                    # Let's assume if made_any_change and saved_once, we should still ask,
                    # unless we are certain the current state IS the saved state.
                    # The safest is to ask if any changes were made since the last save.
                    # For now, if `made_any_change` is true, we'll ask if not sure.
                    # This might lead to asking even if saved and no new changes.
                    # To improve: add `self.dirty = True` on edits, `self.dirty = False` on save.
                    prompt_needed = True # Over-prompting is safer than data loss.

            if prompt_needed:
                if messagebox.askyesno("Quit", "You have unsaved changes. Do you want to save before quitting?", parent=self.master):
                    self.save_image() # This will trigger save_as if not saved before or path unknown
            
        self.master.destroy()

def open_editor_with_image(image_path_or_object):
    """Helper function to create a root window and launch the editor."""
    root = tk.Tk()
    editor_app = ImageEditor(root, image_path_or_object)
    # Determine initial window size based on image, but with limits
    img_w, img_h = editor_app.image_original.size
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    # Max initial window size (e.g., 80% of screen)
    max_win_w = int(screen_w * 0.8)
    max_win_h = int(screen_h * 0.8)

    # Toolbar width approx 100-150px
    toolbar_width_approx = 120 
    canvas_w = min(img_w, max_win_w - toolbar_width_approx)
    canvas_h = min(img_h, max_win_h - 50) # -50 for title bar etc.
    
    window_w = canvas_w + toolbar_width_approx
    window_h = canvas_h + 50

    root.geometry(f"{window_w}x{window_h}")
    root.mainloop()

if __name__ == '__main__':
    # This is for testing the editor directly
    # Create a dummy image or load one for testing
    try:
        # Try to load a test image if available, otherwise create one
        # For testing, you might need to place an image as 'test_image.png' in the same directory
        # or provide a full path.
        img_path = "test_image.png" 
        if not os.path.exists(img_path):
            # Create a dummy if test_image.png not found
            print(f"Test image '{img_path}' not found. Creating a dummy image.")
            img = Image.new("RGBA", (800, 600), "lightcyan")
            draw = ImageDraw.Draw(img)
            draw.text((50,50), "Sample Text", fill="blue", font=ImageFont.truetype("arial.ttf", 30))
            draw.rectangle((100,100, 300,200), outline="red", width=5)
            img.save(img_path) # Save the dummy for next time if desired
        else:
            img = Image.open(img_path)
            
    except Exception as e: # Broad exception for font loading or other Pillow issues
        print(f"Error preparing test image: {e}. Creating a simple fallback.")
        img = Image.new("RGBA", (600, 400), "grey")
        draw = ImageDraw.Draw(img)
        draw.text((10,10), "Fallback Image", fill="white")

    open_editor_with_image(img)
