import cv2
from track_YOLO import InFrameBlockTracker
from pickup_detector import PickupDetector

class VisionInterface:
    def __init__(self, model_path, video_source=0):
        self.cap = cv2.VideoCapture(video_source)
        self.scene_processor = InFrameBlockTracker(self.cap, model_path)
        self.pickup_detector = PickupDetector()

    def process_scene(self):
        self.scene_processor.track_scene()

    def check_pickups(self):
        trackers = self.scene_processor.get_trackers()
        frame = self.scene_processor.get_frame()
        
        for obj_id, tracker in trackers.items():
            if self.pickup_detector.detect(tracker):
                print(f"Block {obj_id} picked up!")
                self.pickup_detector.block_picked()
                return self.pickup_detector.pickup_status()
        return self.pickup_detector.pickup_status()

    def get_pickup_status(self):
        return self.pickup_detector.pickup_status()
    
    def reset_block_picked(self):
        self.pickup_detector.reset_block_picked()