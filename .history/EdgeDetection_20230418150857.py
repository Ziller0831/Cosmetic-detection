import cv2
import numpy as np

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
ret, frame = cap.read()
img = cv2.cvtColor(frame, )

## Laplacian()
