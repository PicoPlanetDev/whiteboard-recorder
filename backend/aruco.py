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

def set_video_corners(video_device: str, frame: cv2.typing.MatLike, config: configuration.Configuration):
    boundingBoxes, ids = get_markers(frame)
    if len(ids) != 4: raise Exception(f"Expected 4 markers, found {len(ids)} markers from {video_device}")
    # sort the bounding boxes by id
    boundingBoxes = [boundingBoxes[i] for i in np.argsort(ids.flatten())]
    # sort the ids
    ids = np.sort(ids.flatten())
    # get the corners of the bounding boxes
    corners = [get_bounding_box_corners(box) for box in boundingBoxes]

    # get the outer corners of the markers
    # 0a 0b
    # 0c 0d    we want 0a, 1b, 2c, and 3d
    outer_corners = [corners[0][0], corners[1][1], corners[2][2], corners[3][3]]
    config.config[video_device]['corners'] = outer_corners

    # figure out if the video is left or right for video order based on if the ids contain 0
    if 0 in ids: config.config["stack_order"] = [0, 1]
    else: config.config["stack_order"] = [1, 0]

    config.save_config()


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