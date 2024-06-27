class PickupDetector:
    def __init__(self, vertical_threshold=200, horizontal_threshold=200):
        self.vertical_threshold = vertical_threshold  # Threshold for detecting vertical movement
        self.horizontal_threshold = horizontal_threshold  # Threshold for detecting horizontal movement

    def is_picked_up(self, vertical_displacement, horizontal_displacement):
        print(f"Total vertical displacement: {vertical_displacement}, Total horizontal displacement: {horizontal_displacement}")
        return abs(vertical_displacement) > self.vertical_threshold