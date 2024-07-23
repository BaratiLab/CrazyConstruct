import cv2
import numpy as np
import apriltag

# Define camera parameters (you need to calibrate your camera to get these values)
calibration_data = np.load("calibration_data.npy", allow_pickle=True).item()
mtx = np.array(calibration_data["camera_matrix"])
dist = np.array(calibration_data["dist_coeffs"])

# Function to undistort images
def undistort_image(image, mtx, dist, new_camera_mtx, roi):
    undistorted_img = cv2.undistort(image, mtx, dist, None, new_camera_mtx)
    x, y, w, h = roi
    return undistorted_img[y:y+h, x:x+w]

# Function to detect AprilTags and identify the origin and build plate corners
def detect_tags(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray)
    
    tags = {}
    for r in results:
        tags[r.tag_id] = r
    return tags

# Function to calculate distance and angle between two tags
def calculate_distance_angle(tag1, tag2):
    dx = tag2.center[0] - tag1.center[0]
    dy = tag2.center[1] - tag1.center[1]
    distance = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx)
    return distance, angle

# Function to estimate the pose of a tag
def estimate_tag_pose(tag, tag_size, mtx, dist):
    # Define the 3D coordinates of the tag corners in the world coordinate system
    object_points = np.array([
        [-tag_size / 2, -tag_size / 2, 0],
        [ tag_size / 2, -tag_size / 2, 0],
        [ tag_size / 2,  tag_size / 2, 0],
        [-tag_size / 2,  tag_size / 2, 0]
    ])
    
    # Get the 2D coordinates of the tag corners in the image
    image_points = tag.corners.astype(np.float32)
    
    # Estimate the pose of the tag
    success, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx, dist)
    
    return rvec, tvec

# Function to find the bottom-left coordinate and orientation of the build plate
def find_build_plate(tags, origin_id, bottom_left_id, origin_tag_size, build_plate_tag_size, mtx, dist):
    if origin_id in tags and bottom_left_id in tags:
        origin_tag = tags[origin_id]
        bottom_left_tag = tags[bottom_left_id]
        
        # Estimate the poses of the origin and bottom-left tags
        rvec_origin, tvec_origin = estimate_tag_pose(origin_tag, origin_tag_size, mtx, dist)
        rvec_bl, tvec_bl = estimate_tag_pose(bottom_left_tag, build_plate_tag_size, mtx, dist)
        
        # Calculate the relative position
        relative_position = tvec_bl - tvec_origin
        relative_position = relative_position*100
        
        return relative_position, rvec_bl
    else:
        raise ValueError("Required tags not found in the image")

# Main function to process the image and find the build plate position
def main():
    # Open the video stream from the USB camera
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    # Get the width and height of the frames
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        exit()
    
    h, w = frame.shape[:2]
    new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    # Define the IDs of the origin and bottom-left tags
    origin_id = 1
    bottom_left_id = 8
    origin_tag_size = 0.043
    build_plate_tag_size = 0.029

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame reading was unsuccessful, break the loop
        if not ret:
            print("Error: Could not read frame.")
            break
        undistorted_image = undistort_image(frame, mtx, dist, new_camera_mtx, roi)
        # Detect AprilTags
        tags = detect_tags(undistorted_image)
    
    
        # Find the build plate position and orientation
        try:
            relative_position, rvec_bl = find_build_plate(tags, origin_id, bottom_left_id, origin_tag_size, build_plate_tag_size, mtx, dist)
            print(f"Build Plate Position (relative to origin): {relative_position}")
            rotation_matrix, _ = cv2.Rodrigues(rvec_bl)
            print(f"Rotation Matrix of Bottom Left Tag: \n{rotation_matrix}")
        except ValueError as e:
            print(e)

        # Visualize the detected tags and positions
        for tag_id, tag in tags.items():
            cv2.polylines(undistorted_image, [tag.corners.astype(np.int32)], True, (0, 255, 0), 2)
            cv2.putText(undistorted_image, str(tag_id), (tag.center[0].astype(int), tag.center[1].astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if bottom_left_id in tags:
            cv2.circle(undistorted_image, tuple(tags[bottom_left_id].center.astype(int)), 5, (0, 0, 255), -1)
        # Display the frame with detections
        cv2.imshow("Undistorted Video Stream", undistorted_image)
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close display windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create the AprilTag detector
    options = apriltag.DetectorOptions(families="tag36h11")
    detector = apriltag.Detector(options)
    main()
