# Hand Gesture Keyboard Controller

A webcam-to-keyboard controller for an existing PC game. It does not include,
modify, or recreate a game. It detects the index fingertip with MediaPipe and
sends short arrow-key taps to whichever application currently has focus.

## Requirements

- Python version supported by the installed MediaPipe package
- A webcam
- Windows, macOS, or Linux desktop session with permission for webcam and
  keyboard automation

## Use in VS Code

Open the project folder in VS Code. Select the Python interpreter where the
requirements were installed. In **Terminal → New Terminal**, run:

```powershell
python -m pip install -r requirements.txt
```

Use **Run → Start Debugging** or press **F5**, then choose **Hand Gesture
Controller** if prompted. The included `.vscode/launch.json` starts `main.py`
with the project folder as its working directory.

## Install from a terminal

Open a terminal in this `gesture_controller` folder and run:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux, use `source .venv/bin/activate` instead. Then install packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Play

1. Start with **F5** in VS Code, or run `python main.py` from this folder.
2. Allow webcam access if your operating system asks.
   On first run, the controller downloads MediaPipe's hand landmark model
   (`hand_landmarker.task`) into this project folder. Internet is needed once.
3. During the brief calibration, hold your index fingertip near the center of
   the webcam image. The controller waits for a visible hand if needed.
4. Start the existing game and click its window so it has keyboard focus.
5. Press **Ctrl+Alt+G** anywhere to turn control on. The webcam window shows `CONTROL:
   ON` or `CONTROL: OFF`.
6. Move your hand/finger left, right, up to jump, or down to slide. Press **Ctrl+Alt+G**
   again to stop sending game input while keeping video detection active.
7. Press **Escape** anywhere to stop immediately and close the webcam window.

Global Ctrl+Alt+G and Escape hotkeys work while the game has focus. The OpenCV preview
does not need to remain the focused window. Arrow inputs are taps, not held
keys. On macOS, grant Accessibility/Input Monitoring permission to the terminal
or Python; on Linux, use a desktop session that supports `pynput` global keys.

## Configuration

Edit `config.py` to adjust:

- `CAMERA_INDEX`, `FRAME_WIDTH`, `FRAME_HEIGHT`
- `MOVEMENT_THRESHOLD`: relative movement needed to recognize a direction
- `GESTURE_COOLDOWN`: minimum time between actions
- `CONFIDENCE_THRESHOLD`: MediaPipe hand detection/tracking confidence
- `CALIBRATION_SECONDS`, `SMOOTHING_WINDOW`, and confirmation frames

The detector requires a directional movement to persist across multiple
smoothed frames, then will not retrigger until the hand returns close to neutral.
This prevents small camera jitter from producing repeated key presses. The
cooldown also gates triggers. If your hand drifts after calibration, restart the
program to recalibrate.

## Troubleshooting

- If the wrong camera opens, change `CAMERA_INDEX` in `config.py`.
- If camera startup is slow on Windows, set `CAMERA_BACKEND` in `config.py` to
  the integer value of OpenCV's `CAP_DSHOW` backend (700 on standard OpenCV
  builds); otherwise leave the default alone.
- If gestures do not trigger, lower `MOVEMENT_THRESHOLD` slightly or improve
  lighting. Raise it if camera noise triggers gestures.
- Keep the controller's Python process running while the game is active.
- Avoid running another app that also sends keyboard inputs.
