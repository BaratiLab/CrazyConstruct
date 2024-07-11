import cv2
import numpy as np
###################### Purpose of Script ####################################################
'''
This tracks the position of every block after it has been placed. Once it has been placed, it checks if the block is in the position
it is supposed to be in. If so, it remains silent. If not the landing detector finds the location of the block
and sends the updated info back to main flying module.
'''
####################### Required Classes ##################################################
class PadDetector:
    def __init__(self, template_path, frame_size):
        self.template = cv2.imread(template_path, 0)
        self.template = self.resize_template(self.template, frame_size)
        self.orb = cv2.ORB_create()
        self.kp_template, self.des_template = self.orb.detectAndCompute(self.template, None)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.pad_corners = None

    def detect_pad(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_frame, 50, 150, apertureSize=3)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Look for the largest rectangular contour
        max_area = 0
        best_approx = None
        for contour in contours:
            epsilon = 0.1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 4 and cv2.contourArea(approx) > max_area:
                max_area = cv2.contourArea(approx)
                best_approx = approx

        if best_approx is not None:
            self.pad_corners = best_approx
            cv2.drawContours(frame, [self.pad_corners], -1, (0, 255, 0), 3)

        return frame

    def get_pad_corners(self):
        return self.pad_corners
    
    def resize_template(self, template, frame_size):
        height, width = frame_size
        return cv2.resize(template, (width, height))
    
class BlockToPadMapping:
    def __init__(self):
        self.pad_corners = None

    def set_pad_corners(self, pad_corners):
        self.pad_corners = pad_corners

    def compute_block_position(self, block_center):
        if self.pad_corners is None:
            return None

        # Find the center of the pad
        pad_center = np.mean(self.pad_corners, axis=0).flatten()

        # Calculate the relative position of the block with respect to the pad center
        relative_position = (block_center[0] - pad_center[0], block_center[1] - pad_center[1])

        return relative_position
    

if __name__ == '__main__':
    template_path = 'pad_template.JPG'
    pad_detector = PadDetector(template_path, (480,640))
    block_to_pad_mapping = BlockToPadMapping()
    cap = cv2.VideoCapture(0)
    key = True
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = pad_detector.detect_pad(frame)
        pad_corners = pad_detector.get_pad_corners()
        if pad_corners is not None:
            block_to_pad_mapping.set_pad_corners(pad_corners)
            print(f"Pad corners detected: {pad_corners}")
        cv2.imshow('Pad Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()