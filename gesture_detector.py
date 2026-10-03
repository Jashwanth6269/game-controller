"""Calibrated, smoothed, debounced directional gesture detection."""

from collections import deque
from statistics import mean
import time

from config import (
    GESTURE_CONFIRM_FRAMES,
    GESTURE_COOLDOWN,
    MOVEMENT_THRESHOLD,
    NEUTRAL_RETURN_RATIO,
    SMOOTHING_WINDOW,
)


class GestureDetector:
    def __init__(self):
        self.positions = deque(maxlen=SMOOTHING_WINDOW)
        self.neutral = None
        self.candidate = None
        self.candidate_frames = 0
        self.armed = True
        self.last_action_time = 0.0

    def add_calibration_sample(self, point):
        if point is not None:
            self.positions.append(point)

    def finish_calibration(self):
        if not self.positions:
            return False
        self.neutral = (mean(p[0] for p in self.positions), mean(p[1] for p in self.positions))
        self.positions.clear()
        return True

    def update(self, point, confidence_ok=True):
        """Return (current gesture label, newly triggered action or None)."""
        if point is None or not confidence_ok or self.neutral is None:
            self.candidate, self.candidate_frames = None, 0
            return "NO HAND" if point is None else "LOW CONFIDENCE", None

        self.positions.append(point)
        smooth_x = mean(p[0] for p in self.positions)
        smooth_y = mean(p[1] for p in self.positions)
        dx, dy = smooth_x - self.neutral[0], smooth_y - self.neutral[1]
        distance = max(abs(dx), abs(dy))

        if distance < MOVEMENT_THRESHOLD * NEUTRAL_RETURN_RATIO:
            self.armed = True
            self.candidate, self.candidate_frames = None, 0
            return "NEUTRAL", None

        gesture = None
        # Choose the strongest axis so diagonal movements do not issue two keys.
        if distance >= MOVEMENT_THRESHOLD:
            if abs(dx) >= abs(dy):
                gesture = "LEFT" if dx < 0 else "RIGHT"
            else:
                gesture = "UP" if dy < 0 else "DOWN"

        if gesture is None:
            return "MOVING", None
        if gesture == self.candidate:
            self.candidate_frames += 1
        else:
            self.candidate, self.candidate_frames = gesture, 1

        now = time.monotonic()
        if (self.armed and self.candidate_frames >= GESTURE_CONFIRM_FRAMES
                and now - self.last_action_time >= GESTURE_COOLDOWN):
            self.armed = False
            self.last_action_time = now
            return gesture, gesture
        return gesture, None

    def cooldown_remaining(self):
        return max(0.0, GESTURE_COOLDOWN - (time.monotonic() - self.last_action_time))

