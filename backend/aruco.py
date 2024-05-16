import cv2
import numpy as np
import configuration

# ArUco marker layout
# 0               1    4                5
#  ______________        ______________
#  |            |        |            |
#  |    LEFT    |        |   RIGHT    |
#  |____________|        |____________|
# 2               3    6                7

def set_video_corners(video_device: str, frame: cv2.typing.MatLike, config: configuration.Configuration) -> cv2.typing.MatLike:
    """
    Sets the corners of the video device based on the ArUco markers in the frame. Allows for automatic recalibration
    if the cameras have been bumped or moved slightly.

    Args:
        video_device (str): The name of the video device to set the corners for. Either 'video0' or 'video1'.
        frame (numpy.ndarray): The frame to detect the ArUco markers in. Get this from the preview object's capture_frame method.
        config (configuration.Configuration): The configuration object to save the corners to.
    Returns:
        numpy.ndarray: The debug frame with the detected ArUco markers drawn on it. Can be thrown away if not needed.
    """
    # print(f"Setting corners for {video_device}")
    debug_frame = frame.copy()

    boundingBoxes, ids = get_markers(frame)
    # print(f"Found {len(ids)} markers from {video_device}")
    # print(f"Found marker ids: {ids}")

    boundingBoxesDict = {ids[i][0]: boundingBoxes[i] for i in range(len(ids))} # create a dictionary of the bounding boxes and ids

    # iterate through keys and values of the dictionary to draw the bounding boxes
    for key, value in boundingBoxesDict.items():
        # draw the bounding box
        cv2.polylines(debug_frame, [np.int32(value)], True, (0, 255, 0), 2)
        
    # figure out if the video is left or right for video order based on if the keys include 0,1,2,3  or 4,5,6,7
    if 0 in boundingBoxesDict and 1 in boundingBoxesDict and 2 in boundingBoxesDict and 3 in boundingBoxesDict: # left
        # print("Found left whiteboard markers")
        config.config["stack_order"] = [0, 1]
        corners = [get_bounding_box_corners(boundingBoxesDict[i]) for i in range(0,4)]
    elif 4 in boundingBoxesDict and 5 in boundingBoxesDict and 6 in boundingBoxesDict and 7 in boundingBoxesDict: # right
        # print("Found right whiteboard markers")
        config.config["stack_order"] = [1, 0]
        corners = [get_bounding_box_corners(boundingBoxesDict[i]) for i in range(4,8)]
    else:
        # print(f"Invalid marker ids: {ids}")
        raise ValueError(f"Invalid marker ids found for {video_device}: {ids}")

    # get the outer corners of the markers
    # 0a 0b
    # 0c 0d    we want 0a, 1b, 2c, and 3d
    outer_corners = [corners[0][0], corners[1][1], corners[2][3], corners[3][2]]
    config.config[video_device]['corners'] = outer_corners

    config.save_config()

    # draw the outer corners
    for i, outer_corner in enumerate(outer_corners):
        cv2.circle(debug_frame, outer_corner, 5, (0, 0, 255), -1)
        cv2.putText(debug_frame, str(i), outer_corner, cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 3, cv2.LINE_AA)

    return debug_frame

def get_markers(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    boundingBoxes, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict)

    return boundingBoxes, ids

def get_bounding_box_corners(boundingBox):
    corners = []
    for corner in boundingBox[0]:
        corners.append((int(corner[0]), int(corner[1])))
    return corners