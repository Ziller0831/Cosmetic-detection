import cv2
import numpy as np

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
    
## Laplacian()
