"""
OCR Module for text extraction from images using Tesseract OCR.

IMPORTANT:
To use this module, Tesseract OCR engine must be installed on your system.
'pytesseract' is a Python wrapper for the Tesseract OCR engine.

Installation Instructions for Tesseract OCR:
-   **Windows**: Download and run the installer from the official Tesseract GitHub repository
    (e.g., from https://github.com/UB-Mannheim/tesseract/wiki).
    Ensure you add the Tesseract installation directory (e.g., C:\\Program Files\\Tesseract-OCR)
    to your system's PATH environment variable during or after installation.
-   **macOS (using Homebrew)**:
    `brew install tesseract`
-   **Linux (Debian/Ubuntu)**:
    `sudo apt-get update`
    `sudo apt-get install tesseract-ocr`
-   **Linux (Fedora)**:
    `sudo yum install tesseract`

After installation, verify Tesseract is in your PATH by opening a terminal/command prompt
and typing `tesseract --version`.

Language Packs:
Tesseract requires language data files to perform OCR for different languages.
-   English (`eng`) is usually included by default.
-   For other languages (e.g., Simplified Chinese - `chi_sim`), you need to install the
    corresponding language pack.
    -   **Debian/Ubuntu**: `sudo apt-get install tesseract-ocr-chi-sim` (for Simplified Chinese)
                         `sudo apt-get install tesseract-ocr-jpn` (for Japanese)
                         `sudo apt-get install tesseract-ocr-kor` (for Korean)
                         `sudo apt-get install tesseract-ocr-fra` (for French)
                         `sudo apt-get install tesseract-ocr-deu` (for German)
                         `sudo apt-get install tesseract-ocr-all` (for all available languages)
    -   **Windows**: Language data files can often be selected during the Tesseract installation process.
                 If not, download the required `.traineddata` files (e.g., `chi_sim.traineddata`)
                 from the Tesseract GitHub data repository (e.g., tessdata_fast or tessdata_best)
                 and place them in your Tesseract installation's 'tessdata' subdirectory.
    -   **macOS (Homebrew)**: Language packs are usually installed with `brew install tesseract-lang`
                         or individually like `brew install tesseract --with-all-languages` (older syntax)
                         or by installing specific language data files into the tessdata directory.

The `lang` parameter in `extract_text_from_image` should match the installed language data files
(e.g., 'eng', 'chi_sim', 'jpn', 'eng+fra' for multiple languages).
"""

import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

# Optional: Specify Tesseract command path if not in system PATH
# Example:
# if os.name == 'nt': # Windows
#     pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# else: # Linux/macOS - typically tesseract is in PATH if installed via package manager
#     pass # Or specify path if needed, e.g., '/usr/local/bin/tesseract'


def extract_text_from_image(image_input, lang='eng'):
    """
    Extracts text from an image using Tesseract OCR.

    Args:
        image_input (str or PIL.Image.Image): Path to an image file or a Pillow Image object.
                                              The image can be in formats like PNG, JPEG, TIFF, BMP, etc.
                                              RGBA images (like those from mss captures) are handled well
                                              by Tesseract via Pillow.
        lang (str, optional): Language code(s) for OCR (e.g., 'eng', 'chi_sim', 'eng+fra').
                              Defaults to 'eng'. Ensure the corresponding language data
                              (traineddata file) is installed in Tesseract's 'tessdata' directory.

    Returns:
        str: The extracted text.
        None: If an error occurred during OCR (e.g., Tesseract not found, invalid image).
              An error message will be printed to stderr.
    """
    try:
        # pytesseract.image_to_string can directly handle both file paths and Pillow Image objects.
        text = pytesseract.image_to_string(image_input, lang=lang)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        print("OCR Error: Tesseract OCR engine not found or not in PATH.")
        print("Please ensure Tesseract is installed and its path is configured correctly.")
        print("See module documentation for installation details.")
        return None
    except pytesseract.TesseractError as e: # Catches other Tesseract-specific errors
        print(f"OCR Error: Tesseract failed to process the image. Message: {e}")
        print(f"This could be due to an unsupported image format, corrupted image, missing language data for '{lang}', or other Tesseract issues.")
        return None
    except FileNotFoundError: # If image_input is a path and the file doesn't exist
        print(f"OCR Error: Image file not found at path: {image_input}")
        return None
    except Exception as e:
        print(f"OCR Error: An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    print("Testing OCR functionality...")

    # --- Test Case 1: Using a generated Pillow Image object ---
    print("\n--- Test Case 1: Generated Pillow Image ---")
    try:
        # Create a simple Pillow image with text
        img_width, img_height = 400, 150
        generated_image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(generated_image)
        
        text_to_draw = "Hello World!\nLine 2: OCR Test\n12345"
        
        try:
            # Try to use a common font, fallback if not found
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            print("(Arial font not found, using default font for test image)")
            font = ImageFont.load_default()
            # Adjust text position if default font is much smaller/larger
            # For default font, we might need to draw line by line.
            # This is a simplified text drawing for the test.
            
        # Simple text drawing (may need adjustment based on font metrics for perfection)
        draw.text((10, 10), text_to_draw, fill="black", font=font)

        print(f"Attempting OCR on generated image with text: \"{text_to_draw.replace('\\n', ' ')}\"")
        extracted_text_generated = extract_text_from_image(generated_image, lang='eng')

        if extracted_text_generated is not None:
            print(f"Extracted Text (Generated Image):\n---\n{extracted_text_generated}\n---")
            # Basic check for correctness (Tesseract might not be perfect)
            if "Hello" in extracted_text_generated and "OCR Test" in extracted_text_generated:
                print("OCR on generated image seems to be working.")
            else:
                print("OCR on generated image might have inaccuracies or failed to pick up all text.")
        else:
            print("OCR failed for the generated image.")

    except Exception as e:
        print(f"Error during Test Case 1 (Generated Image): {e}")


    # --- Test Case 2: Using an image file path ---
    print("\n--- Test Case 2: Image File Path ---")
    test_image_path = "test_ocr_image.png" # Create this image or use an existing one

    # Create a test image file if it doesn't exist
    if not os.path.exists(test_image_path):
        print(f"'{test_image_path}' not found. Creating a dummy image for testing...")
        try:
            dummy_img = Image.new("RGB", (300, 100), "lightgray")
            draw_dummy = ImageDraw.Draw(dummy_img)
            try:
                font_dummy = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font_dummy = ImageFont.load_default()
            draw_dummy.text((10, 30), "Test OCR File 123", fill="darkblue", font=font_dummy)
            dummy_img.save(test_image_path)
            print(f"Dummy image '{test_image_path}' created.")
        except Exception as e:
            print(f"Could not create dummy test image: {e}")
            test_image_path = None # Prevent trying to load if creation failed

    if test_image_path and os.path.exists(test_image_path):
        print(f"Attempting OCR on image file: '{test_image_path}'")
        extracted_text_file = extract_text_from_image(test_image_path, lang='eng')
        if extracted_text_file is not None:
            print(f"Extracted Text (File Image):\n---\n{extracted_text_file}\n---")
        else:
            print(f"OCR failed for the image file '{test_image_path}'.")
    elif test_image_path: # Path exists but file doesn't (should be caught by extract_text)
        print(f"Test image file '{test_image_path}' was specified but could not be found/created. Skipping file test.")
    else:
        print("Skipping image file test as no test image path was available.")

    print("\nOCR Test finished.")
    print("If you see 'Tesseract OCR engine not found' errors, please ensure Tesseract is installed and in your PATH.")
    print("For language-specific errors, ensure the necessary .traineddata files are in Tesseract's tessdata directory.")
    print("For example, for English (eng), 'eng.traineddata' must be present.")

    # --- Test Case 3: Example with a non-English language (e.g., German - deu) ---
    # This test will likely fail unless the user has the 'deu.traineddata' file.
    # It serves as a demonstration for language pack requirements.
    print("\n--- Test Case 3: Non-English Language Example (German - 'deu') ---")
    german_text_image_path = "test_ocr_german.png"
    if not os.path.exists(german_text_image_path):
        print(f"'{german_text_image_path}' not found. Creating a dummy German text image...")
        try:
            img_de = Image.new("RGB", (400,100), "white")
            draw_de = ImageDraw.Draw(img_de)
            try: font_de = ImageFont.truetype("arial.ttf", 20)
            except: font_de = ImageFont.load_default()
            draw_de.text((10,10), "Hallo Welt, dies ist ein Test.", fill="black", font=font_de)
            img_de.save(german_text_image_path)
            print(f"Dummy German image '{german_text_image_path}' created.")
        except Exception as e:
            print(f"Could not create dummy German test image: {e}")
            german_text_image_path = None
            
    if german_text_image_path and os.path.exists(german_text_image_path):
        print(f"Attempting OCR with lang='deu' on '{german_text_image_path}'.")
        print("This will likely fail if 'deu.traineddata' is not installed in Tesseract's tessdata folder.")
        extracted_text_german = extract_text_from_image(german_text_image_path, lang='deu')
        if extracted_text_german is not None:
            print(f"Extracted German Text:\n---\n{extracted_text_german}\n---")
        else:
            print("OCR for German text failed. This is expected if the 'deu' language pack is missing.")
    else:
        print("Skipping German language test as the test image could not be created/found.")

    print("\nReminder: For OCR to work, Tesseract engine must be installed and configured, along with any necessary language packs.")
