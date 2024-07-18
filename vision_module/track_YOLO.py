import cv2
from ultralytics import YOLO

from lucaskanadetracker import LucasKanadeTracker
import vision_tracking_utils
from pickup_detector import PickupDetector

###################### Purpose of Script ####################################################
'''
This main class controls visualizing and tracking each block as they appear on frame and leave frame.
This tracks each block and calls helper functions class to track each block and its type of movements. 
'''
####################### Required Classes ##################################################
class InFrameBlockTracker:
    def __init__(self, cap, model_path):
        self.cap = cap
        self.model = YOLO(model_path)
        # Initialize the dictionary to hold trackers for each block
        self.trackers = {}
        self.frame_count = 0
        self.initialized = False
        self.pickup_detector = PickupDetector()
        self.frame = None

    def initialize_trackers(self, frame, boxes):
        '''
        Definition: Initialiizes all blocks not being tracked to track position and refreshes if a 
        new block enters or leaves the frame. 

        Input Params:
        @param: frame - The frame area in which being tracked over
        @param: boxes - The number of blocks being tracked and its attributes

        Output Params:
        N/A
        '''
        ids = boxes.id
        # Check if all IDs are reassigned
        if set(self.trackers.keys()) != set(ids):
            self.trackers = {}
            for box, obj_id in zip(boxes, ids):
                tracker = LucasKanadeTracker()
                tracker.initialize(frame, box.xyxy.flatten())
                self.trackers[obj_id] = tracker
        else:
            # Update existing trackers
            for box, obj_id in zip(boxes, ids):
                if obj_id not in self.trackers:
                    tracker = LucasKanadeTracker()
                    tracker.initialize(frame, box.xyxy.flatten())
                    self.trackers[obj_id] = tracker

    def track_scene(self):
        '''
        Definition: Tracks the scene of the frame

        Input Params:
        N/A

        Output Params:
        N/A
        '''
        while self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if not ret:
                break

            # Perform inference
            results = self.model.track(self.frame)[0]

            # Extract bounding boxes
            if results.boxes is not None:
                boxes = results.boxes.cpu().numpy()
                #ids = results.boxes.id
            else:
                boxes = []
                #ids = []
            if boxes.id is not None:
                self.initialize_trackers(self.frame, boxes)
                # Track and mask the movement within each bounding box
                for obj_id, tracker in self.trackers.items():
                    self.frame = tracker.track(self.frame)
            # Draw bounding boxes and labels on the frame if there are any boxes
            if len(boxes) > 0:
                self.frame = vision_tracking_utils.draw_boxes(self.frame, boxes, self.model)

            # Display the frame
            cv2.imshow('YOLOv5 Detection', self.frame)
            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
    
    def get_trackers(self):
        return self.trackers

    def get_frame(self):
        return self.frame


def main():
    # Load the YOLOv5 model
    model_path = 'best.pt'  # Update this to your trained model path
    # Set the video capture
    cap = cv2.VideoCapture(0)  # Use 0 for the built-in webcam or the index for USB camera
    scene_processor = InFrameBlockTracker(cap, model_path)
    scene_processor.track_scene()

################################ Run Main #############################################
if __name__ == "__main__":
    main()