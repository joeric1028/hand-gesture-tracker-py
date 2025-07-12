

import cv2
import mediapipe as mp
import sys
import time
import platform
if platform.system() == "Windows":
    try:
        import win32com.client
    except ImportError:
        print("pywin32 is required for camera name detection on Windows. Run 'pip install pywin32'.")


def select_camera():
    """Interactively select a camera index."""
    print("\nAvailable camera indices (try 0, 1, 2, ...):")
    camera_names = {}
    if platform.system() == "Windows":
        try:
            dshow = win32com.client.Dispatch("WIA.DeviceManager")
            for info in dshow.DeviceInfos:
                if info.Type == 2:  # 2 = Video
                    name = info.Properties["Name"].Value
                    # Try to match index by order
                    idx = len(camera_names)
                    camera_names[idx] = name
        except Exception as e:
            print(f"Could not get camera names: {e}")
    for idx in range(5):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            cam_name = camera_names.get(idx, "Unknown Camera")
            print(f"  Camera {idx}: Available - {cam_name}")
            cap.release()
        else:
            print(f"  Camera {idx}: Not available")
    while True:
        try:
            user_input = input("Enter camera index to use (default 0): ").strip()
            if user_input == "":
                return 0
            idx = int(user_input)
            return idx
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    # Camera selection
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print("Invalid camera index. Using default camera 0.")
    else:
        # Optionally allow interactive selection
        print("No camera index provided as argument.")
        camera_index = select_camera()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Camera {camera_index} is not open")
        return

    print(f"Initialized Camera {camera_index}")

    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils

    prev_time = time.time()
    frame_count = 0
    last_fps = None
    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success or image is None:
                print("Failed to read from camera. Exiting loop.")
                break
            # Convert and flip image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)  # Flip horizontally
            results = hands.process(image)

            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = image.shape
                        cx, cy = int(lm.x*w), int(lm.y * h)
                        if id == 20:
                            cv2.circle(image, (cx, cy), 25, (255, 0, 255), cv2.FILLED)
                    mpDraw.draw_landmarks(image, handLms, mpHands.HAND_CONNECTIONS)

            # FPS calculation
            frame_count += 1
            curr_time = time.time()
            elapsed = curr_time - prev_time
            if elapsed >= 1.0:
                last_fps = frame_count / elapsed
                prev_time = curr_time
                frame_count = 0

            # Always display the last FPS value if available
            if last_fps is not None:
                cv2.putText(image, f"FPS: {last_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # Show image
            cv2.imshow("Video", image)
            key = cv2.waitKey(1)
            if key == 27 or key & 0xFF == ord('q'):  # ESC or 'q'
                break
            if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Exited main loop and closed window.")

if __name__ == "__main__":
    main()
