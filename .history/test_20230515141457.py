import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        ret, frame = cap.read()
                if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()