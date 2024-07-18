import cv2

###################### Purpose of Script ####################################################
'''
This is a script that contains the helper functions to help track objects and identify movement
for various tracking related tasks on the crazyflie additive manufacturing project.
'''
####################### Required Functions ##################################################
def draw_boxes(img, results, model):
    '''
    Definition: Places a bounding box around YOLO identified building block objects.

    Input Params:
    @param: img - The frame in which to put a bounding box over
    @param: results - All locations of blocks being tracked
    @param: model - YOLO model running inference on

    Output Params:
    @param: img - The frame with bounding boxes placed at specified locations containing blocks
    '''
    for box in results:
        xyxy = box.xyxy.flatten()  # Extract bounding box coordinates
        conf = float(box.conf)  # Extract confidence score
        cls = int(box.cls)  # Extract class label
        
        label = f'{model.names[cls]} {conf:.2f}'
        cv2.rectangle(img, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 0, 0), 2)
        cv2.putText(img, label, (int(xyxy[0]), int(xyxy[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return img
