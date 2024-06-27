import cv2
import pygame
import time
import os

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

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

# Check if the joystick is available
if pygame.joystick.get_count() == 0:
    print("No joystick connected")
    exit()

# Initialize the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize the camera
cap = cv2.VideoCapture(0)  # Use the correct camera index

# Set directory for saving images
os.makedirs('YOLO_images', exist_ok=True)
os.chdir('YOLO_images')

def capture_image(frame):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f'image_{timestamp}.png'
    cv2.imwrite(filename, frame)
    print(f'Image saved as {filename}')

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(0):  # Assuming 'A' button is button 0
                ret, frame = cap.read()
                if ret:
                    capture_image(frame)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Display the video feed
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
