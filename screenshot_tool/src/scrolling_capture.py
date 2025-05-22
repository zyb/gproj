import mss
import pyautogui
from PIL import Image, ImageChops
import time
import os
import numpy as np

def find_overlap_and_stitch(img1, img2, scroll_direction="vertical"):
    """
    Finds the overlap between two images and stitches them.
    Assumes vertical scrolling for now. img1 is above img2.
    """
    if not img1:
        return img2

    w1, h1 = img1.size
    w2, h2 = img2.size

    # For vertical scroll, width should be the same or very similar
    # We are comparing bottom of img1 with top of img2

    # Determine a strip height for comparison (e.g., 20% of the smaller height, min 50px)
    strip_h = min(max(50, int(min(h1, h2) * 0.2)), h1, h2)
    
    best_match_y_offset = h1 # Default to no overlap (append)
    min_diff = float('inf')

    # Iterate from a potential full overlap down to a minimal overlap
    # Search for img2's top strip within img1's bottom part
    # y_offset is how many pixels from the bottom of img1 the overlap starts
    for y_offset_in_img1_bottom in range(strip_h, min(h1, h2) + 1):
        
        # Region from img1: bottom part, height = y_offset_in_img1_bottom
        # Its top edge is at h1 - y_offset_in_img1_bottom
        img1_strip = img1.crop((0, h1 - y_offset_in_img1_bottom, w1, h1))
        
        # Region from img2: top part, height = y_offset_in_img1_bottom
        img2_strip = img2.crop((0, 0, w2, y_offset_in_img1_bottom))

        if img1_strip.size != img2_strip.size:
            # This can happen if overlap is larger than one of the images, skip.
            # Or if widths are different, which they shouldn't be for simple vertical scroll.
            continue

        # Compare these two strips
        try:
            # diff_img = ImageChops.difference(img1_strip.convert("RGB"), img2_strip.convert("RGB"))
            # diff_stat = np.array(diff_img).sum() # Sum of differences
            
            # Using RMS difference for better sensitivity
            diff = ImageChops.difference(img1_strip.convert("RGB"), img2_strip.convert("RGB"))
            stat = np.array(diff.getdata()).sum(axis=1) # sum of R,G,B differences for each pixel
            rms = np.sqrt(np.mean(stat**2))


            if rms < min_diff:
                min_diff = rms
                # This y_offset_in_img1_bottom is the height of the overlap
                # The stitching point in img1 is (h1 - y_offset_in_img1_bottom)
                # The amount to crop from img2 is y_offset_in_img1_bottom from its top
                best_match_y_offset = h1 - y_offset_in_img1_bottom
                # print(f"Potential overlap found: height {y_offset_in_img1_bottom}, rms_diff: {rms}, stitch_at_img1_y: {best_match_y_offset}")

        except ValueError as e:
            # print(f"ValueError during image comparison: {e}")
            continue # Skip if strips can't be compared

    # Heuristic: if min_diff is too high, assume no good overlap or very different images
    # This threshold needs tuning. For now, let's be somewhat lenient.
    # Max possible RMS for 8-bit RGB is sqrt( (255^2 * 3) / 3 ) = 255.
    # A "good" match might be < 10-30. If it's > 50, maybe no overlap.
    overlap_threshold_rms = 50 
    
    # The actual height of the overlap found is (h1 - best_match_y_offset)
    overlap_height = h1 - best_match_y_offset
    
    # print(f"Final decision: Stitch at img1_y={best_match_y_offset}, Overlap height={overlap_height}, Min RMS diff={min_diff}")

    if min_diff > overlap_threshold_rms or overlap_height <= 10: # Minimal overlap of 10px
        # print("No significant overlap found or diff too high, appending.")
        # Append img2 below img1 (assuming they have same width)
        stitched_width = max(w1, w2) # Should be same for vertical scroll
        stitched_img = Image.new("RGBA", (stitched_width, h1 + h2))
        stitched_img.paste(img1, (0, 0))
        stitched_img.paste(img2, (0, h1))
        return stitched_img, h1 # The y-coordinate where img2 was pasted (height of img1)
    else:
        # Stitch by pasting the non-overlapping part of img2
        non_overlap_h2 = h2 - overlap_height
        stitched_width = max(w1, w2) # Should be same ideally
        
        # New image height: original h1 + non-overlapping part of h2
        new_height = h1 + non_overlap_h2
        stitched_img = Image.new("RGBA", (stitched_width, new_height))
        
        # Paste img1
        stitched_img.paste(img1, (0, 0))
        
        # Crop the non-overlapping part of img2 and paste it
        img2_to_paste = img2.crop((0, overlap_height, w2, h2))
        stitched_img.paste(img2_to_paste, (0, h1)) # Paste at the bottom of original img1
        
        return stitched_img, h1 # The y-coordinate where the new part of img2 effectively starts


class ScrollingCapture:
    def __init__(self, output_filename="scrolling_capture.png", scroll_delay=2, max_scrolls=10, scroll_amount=-120):
        self.output_filename = output_filename
        self.scroll_delay = scroll_delay
        self.max_scrolls = max_scrolls
        self.scroll_amount = scroll_amount # Negative for scrolling down
        
        self.stitched_image = None
        self.last_captured_image = None
        self.monitor_details = None

        with mss.mss() as sct:
            self.monitor_details = sct.monitors[1] # Primary monitor

    def _capture_screen_part(self):
        # For now, captures the full primary monitor.
        # Could be adapted to capture a specific region if initial_region is provided.
        with mss.mss() as sct:
            sct_img = sct.grab(self.monitor_details)
            if hasattr(sct_img, 'bgra') and sct_img.bgra:
                 pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), sct_img.bgra, "raw", "BGRA")
            else:
                 raw_bgra = sct_img.rgb
                 byte_array = bytearray(raw_bgra)
                 for i in range(0, len(byte_array), 4):
                     b, g, r, a = byte_array[i], byte_array[i+1], byte_array[i+2], byte_array[i+3]
                     byte_array[i], byte_array[i+1], byte_array[i+2] = r, g, b
                 pil_image = Image.frombytes("RGBA", (sct_img.width, sct_img.height), bytes(byte_array))
            return pil_image

    def _are_images_identical(self, img1, img2, tolerance=5):
        if img1 is None or img2 is None:
            return False
        if img1.size != img2.size:
            return False
        
        diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
        stat = np.array(diff.getdata()).sum(axis=1)
        rms = np.sqrt(np.mean(stat**2))
        # print(f"RMS diff for identical check: {rms}")
        return rms < tolerance


    def start(self):
        print("Starting scrolling capture...")
        print(f"Ensure the target window is focused and has a scrollbar.")
        print(f"Will scroll {self.max_scrolls} times, with a {self.scroll_delay}s delay between scrolls.")
        print("Waiting 3 seconds before starting to allow you to focus the window...")
        time.sleep(3)

        # 1. Initial capture
        current_capture = self._capture_screen_part()
        self.stitched_image = current_capture
        self.last_captured_image = current_capture
        
        if not os.path.exists(os.path.dirname(self.output_filename)) and os.path.dirname(self.output_filename):
            os.makedirs(os.path.dirname(self.output_filename), exist_ok=True)
        
        # Save initial part for debugging
        # self.stitched_image.save(os.path.join(os.path.dirname(self.output_filename), f"scroll_part_0.png"))

        for i in range(self.max_scrolls):
            print(f"Scroll attempt {i + 1}/{self.max_scrolls}...")

            # 2. Scroll
            pyautogui.scroll(self.scroll_amount) # Scroll down
            time.sleep(self.scroll_delay)

            # 3. Capture new screen part
            new_capture = self._capture_screen_part()

            # 4. Check if new capture is same as last (indicates end of scroll)
            if self._are_images_identical(self.last_captured_image, new_capture):
                print("Reached end of scroll (images are identical).")
                break
            
            # 5. Stitch
            # For simplicity, the find_overlap_and_stitch will handle None for the first self.stitched_image
            # However, we initialized self.stitched_image with the first capture.
            self.stitched_image, _ = find_overlap_and_stitch(self.stitched_image, new_capture)
            
            self.last_captured_image = new_capture # Update last_captured_image for next iteration's check
            
            # Save intermediate stitch for debugging
            # self.stitched_image.save(os.path.join(os.path.dirname(self.output_filename), f"scroll_part_{i+1}.png"))
            print(f"Stitched. Current dimensions: {self.stitched_image.size}")


            # Alternative stop condition: if overlap is almost full image height (less robust)
            # This is somewhat handled by _are_images_identical if the scroll does nothing.

        # 6. Save final image
        if self.stitched_image:
            self.stitched_image.save(self.output_filename)
            print(f"Scrolling capture finished. Saved to {self.output_filename}")
        else:
            print("No image was captured or stitched.")

def capture_scrolling(output_filename="scrolling_capture.png", scroll_delay=2, max_scrolls=10, scroll_amount=-120):
    """
    Functional interface to initiate a scrolling capture.
    """
    capturer = ScrollingCapture(
        output_filename=output_filename,
        scroll_delay=scroll_delay,
        max_scrolls=max_scrolls,
        scroll_amount=scroll_amount
    )
    capturer.start()


if __name__ == "__main__":
    # Create a 'captures' directory for output if it doesn't exist
    captures_dir = "captures"
    if not os.path.exists(captures_dir):
        os.makedirs(captures_dir)
    
    output_file = os.path.join(captures_dir, "long_screenshot.png")
    
    print("Preparing for scrolling capture. Please focus the window you want to capture.")
    print("The capture will start in a few seconds.")
    
    # Parameters for the scrolling capture
    # scroll_delay: Time in seconds to wait after each scroll for content to load.
    # max_scrolls: Maximum number of times to scroll. Prevents infinite loops.
    # scroll_amount: The amount to scroll each time (negative for down, positive for up).
    #                This value might need tuning based on your system's scroll sensitivity.
    capture_scrolling(
        output_filename=output_file,
        scroll_delay=1.5,  # Adjust as needed, larger for web pages with lazy loading
        max_scrolls=5,     # Adjust based on expected page length
        scroll_amount=-100 # Adjust scroll step; smaller steps can be more accurate but slower
    )

    print(f"Test finished. Check the image file: {output_file}")
