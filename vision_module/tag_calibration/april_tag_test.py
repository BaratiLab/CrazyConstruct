import cv2
import apriltag
import numpy as np

def detect_apriltags_from_video():
    # Open the video stream from the USB camera
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # Define camera parameters (you need to calibrate your camera to get these values)
    calibration_data = np.load("calibration_data.npy", allow_pickle=True).item()
    camera_matrix = np.array(calibration_data["camera_matrix"])
    dist_coeffs = np.array(calibration_data["dist_coeffs"])

    # Define the size of the AprilTag (in meters)
    tag_size = 0.017  # Example: 10 cm

    # Create the AprilTag detector
    options = apriltag.DetectorOptions(families="tag36h11,tag25h9,tag16h5")
    detector = apriltag.Detector(options)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame reading was unsuccessful, break the loop
        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect tags
        results = detector.detect(gray_frame)

        # Print detections to the terminal and draw on the frame
        for r in results:
            (ptA, ptB, ptC, ptD) = r.corners
            ptA = (int(ptA[0]), int(ptA[1]))
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))

            cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
            cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
            cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
            cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

            (cX, cY) = (int(r.center[0]), int(r.center[1]))
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

            tagFamily = r.tag_family.decode("utf-8")
            tagID = r.tag_id

            # Define the 3D points of the tag in its own coordinate system
            object_points = np.array([
                [-tag_size/2, -tag_size/2, 0],
                [ tag_size/2, -tag_size/2, 0],
                [ tag_size/2,  tag_size/2, 0],
                [-tag_size/2,  tag_size/2, 0]
            ], dtype="double")

            # Define the 2D image points of the detected corners
            image_points = np.array([ptA, ptB, ptC, ptD], dtype="double")

            # Estimate the pose of the tag
            _, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rvec)

            # Display position and orientation
            position = tvec.flatten()
            orientation = rotation_matrix.flatten()
            yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) * 180 / np.pi

            print(f"Tag Family: {tagFamily}, Tag ID: {tagID}")
            print(f"Position: {position}")
            print(f"Orientation: {orientation}")
            print(f"Yaw: {yaw}")
            print("----------------------------------------------------")

            # Display position and orientation on the frame
            pos_text = f"Pos: {position}"
            ori_text = f"Ori: {orientation}"

            cv2.putText(frame, f"{tagFamily}:{tagID}", 
                        (ptA[0], ptA[1] - 60), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2)

        # Display the frame with detections
        cv2.imshow("AprilTags Detected", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close display windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_apriltags_from_video()
