import cv2
import mss
import numpy as np
import threading
import time
import os

class ScreenRecorder:
    def __init__(self, output_filename="recording.mp4", fps=15.0):
        self.output_filename = output_filename
        self.fps = float(fps)
        self.is_recording = False
        self.recording_thread = None
        self.writer = None
        
        # Get screen dimensions using mss for the primary monitor
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            self.screen_width = monitor["width"]
            self.screen_height = monitor["height"]
            # Define the capture area for mss (same as primary monitor)
            self.monitor_capture_details = {"top": monitor["top"], "left": monitor["left"], 
                                            "width": self.screen_width, "height": self.screen_height}

        self._video_codec = 'mp4v' # Common for .mp4
        self._file_extension = ".mp4"
        
        # Ensure output directory exists if a path is specified
        output_dir = os.path.dirname(self.output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)


    def _get_fourcc(self, filename):
        """Determines FourCC and extension based on filename."""
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == ".mp4":
            return 'mp4v', ext
        elif ext == ".avi":
            return 'XVID', ext
        # Add more formats if needed
        else: # Default to mp4
            print(f"Warning: Unsupported file extension {ext}. Defaulting to .mp4 with mp4v codec.")
            self.output_filename = name + ".mp4" # Correct filename if default is used
            return 'mp4v', ".mp4"


    def _recording_loop(self):
        # Initialize VideoWriter here, within the thread, after start_recording sets it up
        if not self.writer:
            print("Error: VideoWriter not initialized before starting recording loop.")
            return

        frame_time = 1.0 / self.fps  # Time per frame in seconds

        with mss.mss() as sct:
            while self.is_recording:
                start_time = time.time()

                # Capture screen frame
                sct_img = sct.grab(self.monitor_capture_details) # mss.ScreenShot object

                # Convert BGRA (from mss) to BGR (for OpenCV)
                # sct_img.rgb is the BGRA data, sct_img.size is (width, height)
                frame = np.array(sct_img, dtype=np.uint8) # Convert to numpy array
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Write frame to video
                try:
                    self.writer.write(frame_bgr)
                except Exception as e:
                    print(f"Error writing frame: {e}")
                    self.is_recording = False # Stop recording on error
                    break
                
                # Ensure consistent frame rate
                elapsed_time = time.time() - start_time
                sleep_time = frame_time - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
        print("Recording loop stopped.")


    def start_recording(self):
        if self.is_recording:
            print("Recording is already in progress.")
            return

        # Determine codec and update filename if extension changed
        self._video_codec, actual_ext = self._get_fourcc(self.output_filename)
        if actual_ext != os.path.splitext(self.output_filename)[1].lower():
             self.output_filename = os.path.splitext(self.output_filename)[0] + actual_ext
             print(f"Output filename updated to: {self.output_filename}")

        fourcc = cv2.VideoWriter_fourcc(*self._video_codec)
        try:
            self.writer = cv2.VideoWriter(self.output_filename, fourcc, self.fps, 
                                          (self.screen_width, self.screen_height))
            if not self.writer.isOpened():
                print(f"Error: Could not open VideoWriter. Check codec ({self._video_codec}) and permissions for {self.output_filename}.")
                self.writer = None
                return
        except Exception as e:
            print(f"Failed to initialize VideoWriter: {e}")
            self.writer = None
            return

        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.start()
        print(f"Recording started. Output to: {self.output_filename}")

    def stop_recording(self):
        if not self.is_recording:
            print("Recording is not in progress.")
            return

        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join() # Wait for the thread to finish
        
        if self.writer:
            self.writer.release()
            self.writer = None
            print("Recording stopped and file saved.")
        else:
            print("Recording stopped, but writer was not available or already released.")
        
        self.recording_thread = None

    def get_status(self):
        return {"is_recording": self.is_recording, "filename": self.output_filename if self.is_recording else None}

if __name__ == '__main__':
    # Simple test: Start recording, wait a few seconds, then stop.
    print("Screen Recorder Test")
    
    # Create a 'videos' directory for output if it doesn't exist
    if not os.path.exists("videos"):
        os.makedirs("videos")
    
    output_file = os.path.join("videos", "test_recording.mp4") 
    # output_file_avi = os.path.join("videos", "test_recording.avi") 

    recorder = ScreenRecorder(output_filename=output_file, fps=20)
    # recorder_avi = ScreenRecorder(output_filename=output_file_avi, fps=20)

    print("Press 's' to start, 'p' to stop, 'q' to quit.")

    while True:
        cmd = input("> ").strip().lower()
        if cmd == 's':
            if not recorder.get_status()["is_recording"]:
                recorder.start_recording()
            else:
                print("Already recording.")
        elif cmd == 'p':
            if recorder.get_status()["is_recording"]:
                recorder.stop_recording()
            else:
                print("Not recording.")
        elif cmd == 'q':
            if recorder.get_status()["is_recording"]:
                print("Stopping recording before quitting...")
                recorder.stop_recording()
            print("Quitting test.")
            break
        else:
            status = recorder.get_status()
            print(f"Current status: {'Recording to ' + status['filename'] if status['is_recording'] else 'Not recording'}. Commands: s (start), p (stop), q (quit)")

    print("Test finished. Check the video file:", output_file)
    # print("Test finished. Check the video file:", output_file_avi)
