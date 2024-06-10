import cv2
import numpy as np

# Try indices to find the USB camera
index = 1
found = False

# Check indices from 0 to 10
for i in range(1,10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            index = i
            found = True
            break
        cap.release()

if not found:
    print("Error: Could not find any camera.")
    exit()

print(f"Using camera index: {index}")

# Open a connection to the USB camera (replace 1 with the correct index for your USB camera)
cap = cv2.VideoCapture(1)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Error: Could not read frame.")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to get a binary image
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through the contours and draw bounding boxes around the white block
    for contour in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(contour)

        # Ignore small contours that may be noise
        if area > 1000:
            # Get the bounding box coordinates
            x, y, w, h = cv2.boundingRect(contour)

            # Draw the bounding box on the original frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with the bounding boxes
    cv2.imshow('Video Stream', frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
