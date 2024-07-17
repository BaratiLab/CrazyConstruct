import cv2
import numpy as np
import apriltag
###################### Purpose of Script ####################################################
'''
This tracks the position of every block after it has been placed. Once it has been placed, it checks if the block is in the position
it is supposed to be in. If so, it remains silent. If not the landing detector finds the location of the block
and sends the updated info back to main flying module.
'''
####################### Required Classes ##################################################
class PadDetector:
    def __init__(self, frame_size):
        self.detector = self.get_apriltag_detector()
        self.pad_corners = None
        self.frame_size = frame_size
        self.pad_size = (7.9, 7.9)  # Assuming the pad is 20cm x 20cm

    def get_apriltag_detector(self):
        options = apriltag.DetectorOptions(families="tag36h11")
        detector = apriltag.Detector(options)
        return detector

    def detect_pad(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = self.detector.detect(gray_frame)

        corners = {}
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

            cv2.putText(frame, f"{tagFamily}:{tagID}", 
                        (ptA[0], ptA[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2)

            corners[tagID] = r.center

        if len(corners) >= 2:
            self.pad_corners = self.estimate_missing_corners(corners)
            if self.pad_corners is not None:
                cv2.polylines(frame, [self.pad_corners.astype(np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        return frame

    def estimate_missing_corners(self, corners):
        # Use the known tag IDs and their positions to estimate the pad corners
        tag_positions = list(corners.values())
        tag_positions = np.array(tag_positions, dtype=np.float32)

        if len(tag_positions) < 2:
            return None

        # Estimate pad corners based on the detected tags
        pad_corners = []

        # Assuming the first detected tag is the top-left corner
        top_left = tag_positions[0]
        pad_corners.append(top_left)

        # Estimate other corners based on the known pad size
        if len(tag_positions) > 1:
            for pos in tag_positions[1:]:
                dx, dy = pos - top_left
                if abs(dx) > abs(dy):
                    top_right = pos
                    bottom_left = top_left + np.array([0, dy])
                else:
                    bottom_left = pos
                    top_right = top_left + np.array([dx, 0])
                bottom_right = top_right + (bottom_left - top_left)
                pad_corners.extend([top_right, bottom_left, bottom_right])
                break

        return np.array(pad_corners, dtype=np.float32)


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
    pad_detector = PadDetector((480,640))
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