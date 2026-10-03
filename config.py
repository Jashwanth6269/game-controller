"""User-adjustable camera and gesture settings."""

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Relative displacement from the calibrated neutral position, in normalized
# image coordinates (0.10 means 10% of the image width or height).
MOVEMENT_THRESHOLD = 0.12
GESTURE_COOLDOWN = 0.65  # seconds
CONFIDENCE_THRESHOLD = 0.65

CALIBRATION_SECONDS = 3.0
SMOOTHING_WINDOW = 3
GESTURE_CONFIRM_FRAMES = 2
NEUTRAL_RETURN_RATIO = 0.55
CAMERA_BACKEND = None  # Set to cv2.CAP_DSHOW on Windows if camera startup is slow.
WINDOW_NAME = "Hand Gesture Controller"

