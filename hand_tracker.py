"""Webcam capture and MediaPipe Tasks hand landmark tracking."""

from pathlib import Path
import time
from urllib.request import urlopen

import cv2
import mediapipe as mp

from config import CAMERA_BACKEND, CAMERA_INDEX, FRAME_HEIGHT, FRAME_WIDTH, CONFIDENCE_THRESHOLD


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")

# Connections between the standard 21 hand landmarks, used to draw the skeleton.
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
)


class HandTracker:
    def __init__(self):
        self.camera = (
            cv2.VideoCapture(CAMERA_INDEX, CAMERA_BACKEND)
            if CAMERA_BACKEND is not None
            else cv2.VideoCapture(CAMERA_INDEX)
        )
        if not self.camera.isOpened():
            raise RuntimeError(f"Could not open webcam (camera index {CAMERA_INDEX}).")
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if not MODEL_PATH.exists():
            try:
                temporary_model = MODEL_PATH.with_suffix(".task.download")
                with urlopen(MODEL_URL, timeout=30) as response:
                    temporary_model.write_bytes(response.read())
                temporary_model.replace(MODEL_PATH)
            except Exception as exc:
                if "temporary_model" in locals() and temporary_model.exists():
                    temporary_model.unlink()
                self.camera.release()
                raise RuntimeError(
                    "Could not download MediaPipe's hand model. Check your internet "
                    "connection, then run main.py again."
                ) from exc

        try:
            options = mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=CONFIDENCE_THRESHOLD,
                min_hand_presence_confidence=CONFIDENCE_THRESHOLD,
                min_tracking_confidence=CONFIDENCE_THRESHOLD,
            )
            self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        except Exception:
            self.camera.release()
            raise
        self.started_at = time.monotonic()
        self.last_timestamp_ms = -1

    def read(self):
        """Return (BGR frame, normalized index-finger tip, confidence)."""
        ok, frame = self.camera.read()
        if not ok:
            return None, None, 0.0
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - self.started_at) * 1000)
        timestamp_ms = max(timestamp_ms, self.last_timestamp_ms + 1)
        self.last_timestamp_ms = timestamp_ms
        result = self.landmarker.detect_for_video(image, timestamp_ms)

        point, confidence = None, 0.0
        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            height, width = frame.shape[:2]
            for start, end in HAND_CONNECTIONS:
                a = (int(landmarks[start].x * width), int(landmarks[start].y * height))
                b = (int(landmarks[end].x * width), int(landmarks[end].y * height))
                cv2.line(frame, a, b, (80, 220, 80), 2, cv2.LINE_AA)
            for landmark in landmarks:
                xy = (int(landmark.x * width), int(landmark.y * height))
                cv2.circle(frame, xy, 3, (255, 100, 80), -1, cv2.LINE_AA)
            tip = landmarks[8]  # index fingertip
            point = (float(tip.x), float(tip.y))
            # A returned hand has already passed MediaPipe's configured confidence thresholds.
            confidence = 1.0
        return frame, point, confidence

    def close(self):
        self.landmarker.close()
        self.camera.release()

