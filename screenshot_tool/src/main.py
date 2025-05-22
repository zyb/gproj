import mss
import mss.tools
import tkinter as tk
from PIL import Image # For converting mss screenshot to Pillow Image
from .editor import open_editor_with_image # Import the editor launcher

def capture_fullscreen(output_path="screenshot.png"): # output_path is no longer directly used for saving here
    """
    Captures the entire screen and opens it in the ImageEditor.
    """
    try:
        with mss.mss() as sct:
            # Grab the primary monitor (monitor 1)
            # sct.monitors[0] is all monitors together, sct.monitors[1] is primary
            monitor = sct.monitors[1] 
            sct_img = sct.grab(monitor)
            
            # Convert to Pillow Image object
            # mss provides BGRA data in sct_img.rgb (despite the name) or sct_img.bgra
            # Pillow's frombytes expects RGB or RGBA, so we might need to reorder color channels
            # Or, ensure mss provides it in a compatible format if possible.
            # For simplicity, let's assume BGRA and convert to RGBA for Pillow
            # img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb, 'raw', 'BGR') - this is one way
            
            # More direct: mss.tools.to_png writes to a BytesIO stream, then Image.open()
            # Or, create from bgra attribute directly:
            if hasattr(sct_img, 'bgra') and sct_img.bgra:
                 pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), sct_img.bgra, "raw", "BGRA")
            else: # Fallback if bgra is not available, try rgb (might need channel swap)
                 # Assuming sct_img.rgb is actually BGRA as is common with mss
                 raw_bgra = sct_img.rgb
                 # Create an RGBA image by swapping B and R channels
                 # This is a bit manual:
                 byte_array = bytearray(raw_bgra)
                 for i in range(0, len(byte_array), 4):
                     b, g, r, a = byte_array[i], byte_array[i+1], byte_array[i+2], byte_array[i+3]
                     byte_array[i], byte_array[i+1], byte_array[i+2] = r, g, b # Swapping B and R
                 pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), bytes(byte_array))


            print(f"Fullscreen screenshot captured. Opening in editor...")
            open_editor_with_image(pil_image)

    except Exception as e:
        print(f"Error capturing fullscreen screenshot or opening editor: {e}")
        import traceback
        traceback.print_exc()


class RegionSelector:
    def __init__(self, master):
        self.master = master
        # Attempt to make the window truly borderless and cover everything.
        # Fullscreen should achieve this on most systems.
        self.master.attributes("-fullscreen", True) 
        self.master.attributes("-alpha", 0.3)  # Semi-transparent for selection visibility
        self.master.attributes("-topmost", True) # Keep on top of other windows
        # For some systems, overrideredirect might be needed for true borderless,
        # but it can also make window management harder. -fullscreen is preferred.
        # self.master.overrideredirect(True) # Use with caution
        
        self.master.bind("<Escape>", self.cancel_selection) # Allow Esc to cancel
        self.master.bind("<ButtonPress-1>", self.on_mouse_press)
        self.master.bind("<B1-Motion>", self.on_mouse_drag)
        self.master.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Use a specific background color that indicates transparency is working.
        # A slightly off-grey or a color not typically part of UIs.
        # highlightthickness=0 removes canvas border.
        self.canvas = tk.Canvas(self.master, cursor="cross", bg="black", highlightthickness=0) 
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = None # Stores the rectangle item drawn on the canvas
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.selection_coordinates = None

    def on_mouse_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                 outline='red', width=2)

    def on_mouse_drag(self, event):
        self.current_x = self.canvas.canvasx(event.x)
        self.current_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.current_x, self.current_y)

    def on_mouse_release(self, event):
        if self.start_x is None or self.start_y is None or self.current_x is None or self.current_y is None:
            print("Selection was not properly made.")
            self.master.destroy()
            return

        # Ensure top-left and bottom-right coordinates
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)
        
        # Check for minimal size to prevent zero-size selections
        if abs(x1 - x2) < 5 or abs(y1 - y2) < 5:
            print("Selected region is too small.")
            self.selection_coordinates = None
        else:
            self.selection_coordinates = {
                "top": int(y1),
                "left": int(x1),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            }
        self.master.destroy()

    def cancel_selection(self, event=None):
        print("Selection cancelled.")
        self.selection_coordinates = None
        self.master.destroy()

def capture_selected_region(output_path="region_capture.png"):
    """
    Allows the user to select a region of the screen and captures it, then opens in editor.

    Args:
        output_path (str, optional): Not directly used for saving here. Kept for signature consistency if needed.
                                     Defaults to "region_capture.png".
    """
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window

        # Create the selection window as a Toplevel
        selector_window = tk.Toplevel(root)
        # selector_window.attributes("-alpha", 0.01) # Make it nearly invisible until canvas is up?
        # selector_window.wait_visibility(selector_window) # Wait for window to be visible before making it transparent
        
        selector = RegionSelector(selector_window)
        selector_window.mainloop()  # This loop finishes when selector_window is destroyed

        # Ensure the hidden root window is also destroyed
        if root.winfo_exists():
            root.destroy()

        if selector.selection_coordinates:
            monitor = selector.selection_coordinates
            if monitor["width"] > 0 and monitor["height"] > 0:
                with mss.mss() as sct:
                    sct_img = sct.grab(monitor) # sct_img is a mss.ScreenShot object
                    
                    # Convert to Pillow Image
                    # Similar to fullscreen, assuming sct_img.bgra or sct_img.rgb (as BGRA)
                    if hasattr(sct_img, 'bgra') and sct_img.bgra:
                         pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), sct_img.bgra, "raw", "BGRA")
                    else: # Fallback for sct_img.rgb (assuming BGRA)
                         raw_bgra = sct_img.rgb
                         byte_array = bytearray(raw_bgra)
                         for i in range(0, len(byte_array), 4):
                             b, g, r, a = byte_array[i], byte_array[i+1], byte_array[i+2], byte_array[i+3]
                             byte_array[i], byte_array[i+1], byte_array[i+2] = r, g, b
                         pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), bytes(byte_array))

                    print(f"Selected region captured (Coordinates: {monitor}). Opening in editor...")
                    open_editor_with_image(pil_image)
            else:
                print("Invalid region selected (zero width or height). Screenshot not taken.")
        else:
            print("No region selected or selection cancelled. Screenshot not taken.")

    except tk.TclError as e:
        print(f"Tkinter error: {e}. This often means no display server is available (e.g., running in a headless SSH session without X11 forwarding).")
    except Exception as e:
        print(f"Error capturing selected region or opening editor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Example: Choose which capture mode to test
    # To test fullscreen:
    # capture_fullscreen()

    # To test region selection:
    capture_selected_region()
