import os
import time

def main():
    print("=== Attendance System ===")
    print("📡 Tap your NFC card to log attendance")
    print("(For admin: type 'admin' to enroll a student)")

    while True:
        user_input = input("\nTap card or enter command: ")

        if user_input.lower() == "admin":
            os.system("python enroll.py")
        else:
            # Assume NFC UID is passed here
            nfc_uid = user_input.strip()
            print(f"Detected NFC UID: {nfc_uid}")
            os.system(f"python recognize.py {nfc_uid}")

        time.sleep(1)

if __name__ == "__main__":
    main()
