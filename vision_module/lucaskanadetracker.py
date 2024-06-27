import cv2
import numpy as np
###################### Purpose of Script ####################################################
'''
Track a single block and its movements. This class contains the framework for Lucas Kanade tracking
per identified block.
'''
####################### Required Classes ##################################################
class LucasKanadeTracker:
    def __init__(self, lk_params=None, feature_params=None):
        self.lk_params = lk_params if lk_params else dict(winSize=(15, 15),
                                                          maxLevel=2,
                                                          criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.feature_params = feature_params if feature_params else dict(maxCorners=100,
                                                                         qualityLevel=0.3,
                                                                         minDistance=7,
                                                                         blockSize=7)
        self.mask = None
        self.old_gray = None
        self.p0 = None
        self.movements = []

    def initialize(self, frame, bounding_box):
        '''
        Definition: Initializes the filter algorithm by finding good features to track. It then
        places a mask over the region of the bounding box as well.
        Input Params:
        @param: frame - The frame in which to put a bounding box over
        @param: bounding box - box.xyxy from YOLO model outlining the location of the bounding box
        within the frame

        Output Params:
        N/A
        '''
        self.mask = np.zeros_like(frame)
        self.old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Create a mask for the bounding box
        bbox_mask = np.zeros_like(self.old_gray)
        x1, y1, x2, y2 = map(int, bounding_box)
        bbox_mask[y1:y2, x1:x2] = 1

        # Detect initial points to track within the bounding box
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=bbox_mask, **self.feature_params)

    def track(self, frame):
        '''
        This uses LK to keep track of the important features for calculation use.

        Input Params:
        @param: frame - The frame being analyzed

        Output Params:
        @param: The tracked frame with the lines from change in position from start
        '''
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.p0 is None:
            return frame

        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)

        # Select good points
        if p1 is not None:
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]

            # Draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = map(int, new.ravel())
                c, d = map(int, old.ravel())
                self.mask = cv2.line(self.mask, (a, b), (c, d), (0, 255, 0), 2)
                frame = cv2.circle(frame, (a, b), 5, (0, 255, 0), -1)
                self.movements.append((c,d,a,b))

            self.old_gray = frame_gray.copy()
            self.p0 = good_new.reshape(-1, 1, 2)

        return cv2.add(frame, self.mask)
    
    def get_movements(self):
        movements = self.movements
        self.movements = []
        return movements
    
    def get_total_displacement(self):
        total_horizontal = 0
        total_vertical = 0
        for (c, d, a, b) in self.movements:
            total_horizontal += (a - c)
            total_vertical += (b - d)
        return total_horizontal, total_vertical