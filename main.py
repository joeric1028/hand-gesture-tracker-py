import cv2
import mediapipe as mp

# USB WebCam 
cap = cv2.VideoCapture(2)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

if cap.isOpened() == False:
    print("Camera is not open")
    exit(1)

print("Initialized Camera 0")

while cap.isOpened():
    success, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x*w), int(lm.y * h)
                if id == 20:
                    cv2.circle(image, (cx, cy), 25, (255, 0, 255), cv2.FILLED)
            mpDraw.draw_landmarks(image, handLms, mpHands.HAND_CONNECTIONS)
    if success == True:
        cv2.imshow("Video", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
