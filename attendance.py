from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch
import numpy as np
import cv2
import sys
from database import get_connection
import datetime

mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def recognize(nfc_uid):
    conn = get_connection()
    cursor = conn.cursor()

    # 1️⃣ Check if NFC UID exists
    cursor.execute("SELECT id, first_name, last_name, course, year, subject, room, embedding FROM students WHERE nfc_uid=%s", (nfc_uid,))
    student = cursor.fetchone()

    if not student:
        print("❌ NFC UID not registered.")
        cursor.close()
        conn.close()
        return

    sid, fname, lname, course, year, subject, room, db_emb = student

    print(f"\n👤 Student Found:")
    print(f"   Name    : {fname} {lname}")
    print(f"   Course  : {course} - Year {year}")
    print(f"   Subject : {subject} | Room {room}")
    print("\n📸 Opening camera for facial recognition...")

    # Convert DB embedding back to numpy
    db_emb = np.frombuffer(db_emb, dtype=np.float32).reshape(1, -1)

    # Hard-set status_id for now
    PRESENT_STATUS_ID = 1
    FAILED_STATUS_ID = 3

    # 2️⃣ Open webcam for face capture
    cap = cv2.VideoCapture(0)
    matched = False
    attempts = 0
    MAX_ATTEMPTS = 3

    while attempts < MAX_ATTEMPTS:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame from camera.")
            break

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        face = mtcnn(img)

        if face is not None:
            embedding = resnet(face.unsqueeze(0)).detach().numpy()
            dist = np.linalg.norm(embedding - db_emb)

            if dist < 0.9:  # threshold for 1:1 verification
                print(f"✅ Face matched. Attendance logged for {fname} {lname}.")
                now = datetime.datetime.now()
                cursor.execute(
                    "INSERT INTO attendance (student_id, timestamp, status_id) VALUES (%s, %s, %s)", 
                    (sid, now, PRESENT_STATUS_ID)
                )
                conn.commit()
                matched = True
                break
            else:
                attempts += 1
                print(f"❌ Face did not match. Attempt {attempts}/{MAX_ATTEMPTS}")

            cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("⚠ Exiting without logging attendance.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if not matched:
        now = datetime.datetime.now()
        if attempts >= MAX_ATTEMPTS:
            print("❌ Face did not match after 3 tries. Please go to your professor.")
            # Log failed attempts in attendance with "Failed" status
            cursor.execute(
                "INSERT INTO attendance (student_id, timestamp, status_id, status_message) VALUES (%s, %s, %s)", 
                (sid, now, FAILED_STATUS_ID, "Failed - Notify Professor")
            )
            conn.commit()
        else:
            print("⚠ No valid face match recorded.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        recognize(sys.argv[1])
    else:
        print("⚠ Please provide NFC UID")