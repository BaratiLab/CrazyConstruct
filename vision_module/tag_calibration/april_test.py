import cv2
import robotpy_apriltag

# Initialize the apriltag detector
def get_apriltag_detector():
    detector = robotpy_apriltag.AprilTagDetector()
    assert detector.addFamily("tag16h5")
    return detector

# Draw detected tags on the frame
def draw_tag(frame, tag):
    cornersBuf = [0] * 8
    corners = tag.getCorners(cornersBuf)
    
    for i in range(4):
        pt1 = (int(corners[2 * i]), int(corners[2 * i + 1]))
        pt2 = (int(corners[2 * ((i + 1) % 4)]), int(corners[2 * ((i + 1) % 4) + 1]))
        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
    
    center = (int(tag.getCenter().x), int(tag.getCenter().y))
    cv2.circle(frame, center, 5, (0, 0, 255), -1)
    cv2.putText(frame, f"ID: {tag.getId()}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Detect and draw apriltags in a frame
def detect_and_draw_apriltag(frame, detector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tag_info = detector.detect(gray)
    for tag in tag_info:
        draw_tag(frame, tag)
    return frame

# Initialize Webcam capture
def get_capture(window_name, video_capture_device_index=0):
    cv2.namedWindow(window_name)
    cap = cv2.VideoCapture(video_capture_device_index)
    return cap

# Capture and process frames in a loop
def show_capture(capture_window_name, capture, detector):
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        frame_with_tags = detect_and_draw_apriltag(frame, detector)
        cv2.imshow(capture_window_name, frame_with_tags)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the capture and close windows
def cleanup_capture(capture):
    capture.release()
    cv2.destroyAllWindows()

# Main function
def main():
    capture_window_name = 'Capture Window'
    capture = get_capture(capture_window_name, 0)
    detector = get_apriltag_detector()
    show_capture(capture_window_name, capture, detector)
    cleanup_capture(capture)

if __name__ == '__main__':
    main()



