"""Run the webcam hand gesture to keyboard controller."""

import time

import cv2

from config import CALIBRATION_SECONDS, CONFIDENCE_THRESHOLD, WINDOW_NAME
from gesture_detector import GestureDetector
from hand_tracker import HandTracker
from keyboard_controller import KeyboardController


def draw_status(frame, gesture, action, fps, enabled, cooldown, calibration_text=None):
    color = (60, 220, 60) if enabled else (30, 170, 240)
    lines = [
        f"Gesture: {gesture}",
        f"Action: {action or '--'}",
        f"FPS: {fps:.0f}",
        f"CONTROL: {'ON' if enabled else 'OFF'} (Ctrl+Alt+G)",
        f"Cooldown: {cooldown:.1f}s",
        "ESC: quit | Ctrl+Alt+G: toggle",
    ]
    if calibration_text:
        lines.insert(0, calibration_text)
    for i, text in enumerate(lines):
        cv2.putText(frame, text, (12, 28 + i * 27), cv2.FONT_HERSHEY_SIMPLEX,
                    0.62, color if i == 3 or (calibration_text and i == 0) else (255, 255, 255), 2, cv2.LINE_AA)


def main():
    tracker = controller = None
    try:
        tracker = HandTracker()
        controller = KeyboardController()
        detector = GestureDetector()
        start = time.monotonic()
        previous_frame = start
        fps = 0.0
        calibration_done = False
        current_gesture, current_action = "CALIBRATING", None
        action_status = "--"
        action_status_until = 0.0
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        while not controller.stopped.is_set():
            frame, point, confidence = tracker.read()
            if frame is None:
                print("Webcam frame could not be read; stopping controller.")
                break

            now = time.monotonic()
            delta = now - previous_frame
            if delta > 0:
                fps = 0.9 * fps + 0.1 / delta if fps else 1.0 / delta
            previous_frame = now
            if controller.consume_toggle():
                print(f"Gesture control {'enabled' if controller.enabled else 'disabled'}.")

            calibration_text = None
            if not calibration_done:
                remaining = CALIBRATION_SECONDS - (now - start)
                detector.add_calibration_sample(point)
                calibration_text = f"Calibration: keep hand centered ({max(0, remaining):.1f}s)"
                current_gesture, current_action = "CALIBRATING", None
                if remaining <= 0:
                    calibration_done = detector.finish_calibration()
                    if not calibration_done:
                        # Keep collecting until a hand is present to establish neutral.
                        start = now - CALIBRATION_SECONDS + 0.5
                        calibration_text = "Show your hand near center to calibrate"
                    else:
                        start = now
            else:
                current_gesture, action = detector.update(
                    point, confidence >= CONFIDENCE_THRESHOLD
                )
                if action and controller.enabled:
                    current_action = controller.press_gesture(action)
                    if current_action:
                        action_status = current_action.upper()
                        action_status_until = now + 1.0
                        print(f"Gesture {action} -> sent {current_action.upper()} arrow key")
                elif action:
                    current_action = "CONTROL OFF"
                    action_status = current_action
                    action_status_until = now + 1.0

            if current_action:
                action_status = current_action
                action_status_until = now + 1.0
                current_action = None
            shown_action = action_status if now < action_status_until else "--"

            if point is not None:
                height, width = frame.shape[:2]
                px, py = int(point[0] * width), int(point[1] * height)
                cv2.circle(frame, (px, py), 9, (0, 255, 255), -1)
                cv2.putText(frame, "INDEX", (px + 10, py - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 255), 2, cv2.LINE_AA)

            draw_status(frame, current_gesture, shown_action, fps, controller.enabled,
                        detector.cooldown_remaining(), calibration_text)
            cv2.imshow(WINDOW_NAME, frame)
            # Keep the OpenCV window responsive; global hotkeys are handled by pynput.
            cv2.waitKey(1)
    except KeyboardInterrupt:
        pass
    finally:
        if controller is not None:
            controller.close()
        if tracker is not None:
            tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

