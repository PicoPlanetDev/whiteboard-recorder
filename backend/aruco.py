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
    print(f"Setting corners for {video_device}")
    debug_frame = frame.copy()

    boundingBoxes, ids = get_markers(frame)
    print(f"Found {len(ids)} markers from {video_device}")
    if len(ids) != 4: raise Exception(f"Expected 4 markers, found {len(ids)} markers from {video_device}")
    
    boundingBoxes = {ids[i][0]: boundingBoxes[i] for i in range(len(ids))} # create a dictionary of the bounding boxes and ids

    # figure out if the video is left or right for video order based on if the keys include 0,1,2,3  or 4,5,6,7
    if 0 in boundingBoxes and 1 in boundingBoxes and 2 in boundingBoxes and 3 in boundingBoxes: # left
        config.config["stack_order"] = [0, 1]
        corners = [get_bounding_box_corners(boundingBoxes[i]) for i in range(0,4)]
    if 4 in boundingBoxes and 5 in boundingBoxes and 6 in boundingBoxes and 7 in boundingBoxes: # right
        config.config["stack_order"] = [1, 0]
        corners = [get_bounding_box_corners(boundingBoxes[i]) for i in range(4,8)]
    else:
        raise Exception(f"Invalid marker ids for {video_device}")

    # get the outer corners of the markers
    # 0a 0b
    # 0c 0d    we want 0a, 1b, 2c, and 3d
    outer_corners = [corners[0][0], corners[1][1], corners[2][2], corners[3][3]]
    config.config[video_device]['corners'] = outer_corners

    config.save_config()

    # draw the outer corners
    for i, outer_corner in enumerate(outer_corners):
        cv2.circle(debug_frame, outer_corner, 5, (0, 0, 255), -1)
        cv2.putText(debug_frame, str(i), outer_corner, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

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