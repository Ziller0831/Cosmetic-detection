import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
if not cap.isOpened():
    print("Cannot open camera")
    exit()
ret, frame = cap.read()
img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

## Laplacian()
Laplace_output = cv2.Laplacian(img, -1, 1, 5)
