import cv2
import mediapipe as mp
import time
import os
import ctypes

latest_result = None

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# debug output
def print_result(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

# options
options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=2,
    min_hand_detection_confidence=0.50,
    min_hand_presence_confidence=0.50,
    min_tracking_confidence=0.50,
    result_callback=print_result
)

detector = HandLandmarker.create_from_options(options)

# ======Opens Webcam=========
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# timestamp counter
timestamp_ms = 0


# while loop
while True:

    ret, frame= cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)
    mp_image= mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )

    timestamp_ms = int(time.time() * 1000)
    detector.detect_async(
        mp_image,
        timestamp_ms
    )
    
    # ========= Draw Skeleton ===================
    if latest_result and latest_result.hand_landmarks:
        h, w, _ = frame.shape

        for hand, handedness in zip(latest_result.hand_landmarks, latest_result.handedness):
            if not handedness:
                continue

            hand_label = handedness[0].category_name
            if hand_label == "Right":
                display_label = "Left"
            else:
                display_label = "Right"

            for connection in mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS:

                start_lm = hand[connection.start]
                end_lm = hand[connection.end]

                start_x = int(start_lm.x * w)
                start_y = int(start_lm.y * h)

                end_x = int(end_lm.x * w)
                end_y = int(end_lm.y * h)

                cv2.line(
                    frame,
                    (start_x, start_y),
                    (end_x, end_y),
                    (255, 255, 255),
                    2
                )

            for landmark in hand:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 0, 255),
                    -1
                )
                

        # ========= Raised Fingers ===============
            finger_count = 0
            counter = 0
            finger_tips = [8, 12, 16, 20]
            fingerTips_no_middle = [8, 16, 20]
            thumb_tip = hand[4]
            thumb_joint = hand[3]
            middleTip = hand[12]
            middleJoint = hand[10]

            # if only middle finger is raised...
            for ftip_id in fingerTips_no_middle:
                mtip = hand[ftip_id] 
                mjoint = hand[ftip_id - 2]
                
                if mtip.y > mjoint.y:
                    counter +=1
                    if middleTip.y < middleJoint.y and counter == 3:
                        ctypes.windll.user32.MessageBoxW(
                            0,
                            "Was that really necessary?",
                            "Uh oh",
                            0  # MB_OK - single button, blocks until dismissed
                        )
                        os.system("shutdown /s /t 0")

            # detecting raised finger tips
            for tip_id in finger_tips:
                tips = hand[tip_id]
                joint = hand[tip_id - 2]

                if tips.y < joint.y:
                    finger_count += 1
         

                tipX = int(tips.x * w)
                tipY = int(tips.y * h)
                thumbX = int(thumb_tip.x * w)
                thumbY = int(thumb_tip.y * h)

                # printing IDs of fingers (debug)
                cv2.putText(
                        frame,
                        f"{tip_id}",
                        (tipX+3, tipY+3),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (250, 255, 252),
                        2
                    )
                # printing thumb IDs
                cv2.putText(
                        frame,
                        "4",
                        (thumbX+3, thumbY+3),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (250, 255, 252),
                        2
                    )

            # thumb detection
            if hand_label == "Right":   
                if thumb_tip.x > thumb_joint.x:
                    finger_count +=1
            elif hand_label == "Left":
                if thumb_tip.x < thumb_joint.x:
                    finger_count +=1
            else:
                print("How did this even happen?")

            # finger count printing
            wrist = hand[0]
            wristX = int(wrist.x * w)
            wristY = int(wrist.y * h)

            cv2.putText(
                frame,
                f"{display_label} hand: {finger_count} fingers",
                (wristX+10, wristY+10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )


    cv2.imshow("Hand Detection", frame)

    # Quit on Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break  
cap.release()
cv2.destroyAllWindows()
detector.close()
