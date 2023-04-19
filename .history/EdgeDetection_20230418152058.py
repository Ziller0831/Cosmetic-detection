import cv2
import numpy as np

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break
    
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ## Laplacian()
    Laplace_output = cv2.Laplacian(img, -1, 1, 5)
    cv2.imshow("Laplacian", Laplace_output)



    ## Contours process
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))





    if cv2.waitKey(1) == ord('q'):
        break  

cap.release()
cv2.destroyAllWindows()