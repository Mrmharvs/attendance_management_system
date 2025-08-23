from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch
import numpy as np
import cv2
from database import get_connection
import sys

# Initialize FaceNet models
mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def enroll_student(last, first, middle, course, year, subject, room, nfc_uid, image_path=None):
    # If no image_path, open webcam
    if image_path is None:
        cap = cv2.VideoCapture(0)
        print("📸 Press SPACE to capture face, ESC to exit")
        while True:
            ret, frame = cap.read()
            cv2.imshow("Enrollment - Capture Face", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("❌ Enrollment cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return
            elif key == 32:  # SPACE
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        img = Image.open(image_path)

    face = mtcnn(img)
    if face is None:
        print("❌ No face detected.")
        return

    # Generate embedding
    embedding = resnet(face.unsqueeze(0)).detach().numpy().flatten()
    print(f"✅ Embedding shape: {embedding.shape}")   # should be (512,)

    # Convert to bytes for DB storage
    embedding_bytes = embedding.tobytes()

    # Save to DB
    conn = get_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO students
             (last_name, first_name, mi, course, year, subject, room, nfc_uid, embedding)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (last, first, middle, course, year, subject, room, nfc_uid, embedding_bytes)

    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"✅ Enrolled {first} {last} with NFC {nfc_uid}")
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 9:
        print("⚠ Usage: python enroll.py <nfc_uid> <first> <middle> <last> <course> <year> <subject> <room> [image_path]")
        print("👉 If no image_path is given, webcam will be used.")
    else:
        image_path = sys.argv[9] if len(sys.argv) > 9 else None
        enroll_student(
            nfc_uid=sys.argv[1],
            first=sys.argv[2],
            middle=sys.argv[3],
            last=sys.argv[4],
            course=sys.argv[5],
            year=sys.argv[6],
            subject=sys.argv[7],
            room=sys.argv[8],
            image_path=image_path
        )