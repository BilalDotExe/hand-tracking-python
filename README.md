# Hand Gesture Finger Counter

A real-time hand-tracking demo that uses your webcam to detect hands, draw the hand skeleton, and count how many fingers are raised on each hand.

## Features

- Live webcam feed with hand landmark detection (up to 2 hands at once)
- Skeleton overlay showing all 21 landmarks per hand, connected by lines
- Per-hand finger count, displayed next to the wrist
- Left/right hand labeling (corrected for the mirrored webcam view)
- Landmark ID labels on fingertips for debugging

## Tech Stack

- **OpenCV** — webcam capture, drawing, and display
- **MediaPipe Tasks (Hand Landmarker)** — hand detection and landmark tracking, running in live-stream/async mode

## Requirements

- Python 3.9+
- A webcam
- The MediaPipe hand landmark model file

## Setup

Install dependencies:

```bash
pip install opencv-python mediapipe
```

Download the hand landmark model and place it at `models/hand_landmarker.task`:

```bash
mkdir -p models
curl -L -o models/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

## Usage

Run the script:

```bash
python main.py
```

A window titled "Hand Detection" will open showing your webcam feed with hand tracking overlaid. Press **Q** to quit.

## How It Works

1. Each frame is flipped horizontally for a natural mirror view and converted into a MediaPipe `Image`.
2. The frame is sent to the `HandLandmarker` asynchronously (`detect_async`), with results delivered via a callback into `latest_result`.
3. For each detected hand, the script draws the connections and landmark points, then checks whether each fingertip landmark sits above its corresponding joint landmark (lower `y` = higher on screen) to determine if that finger is raised.
4. The thumb is handled separately since it moves sideways rather than up/down, using the hand's left/right label to pick the correct direction.
5. The total raised-finger count is displayed near the wrist for each hand.

## Notes

- Detection confidence thresholds (`min_hand_detection_confidence`, `min_hand_presence_confidence`, `min_tracking_confidence`) can be tuned in the `HandLandmarkerOptions` block if tracking feels too jumpy or unresponsive.
- Resolution is set to 1200x720 by default via `cap.set(...)`; adjust if your webcam doesn't support it.
- There's a little extra logic tucked into the finger-detection loop that goes beyond just counting. We won't spoil it — but you may want to think twice before casually flashing certain hand gestures at your webcam while this is running. Consider yourself warned. 👀
