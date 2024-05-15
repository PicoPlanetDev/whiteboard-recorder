import numpy as np
import cv2
import os

def generate_marker(id: int, size: int = 4, borderBits: int = 1, whiteBorderBits: int = 0):
    """
    Generate an ArUco marker, optionally with a white border around the marker.

    Args:
        id (int): The ArUco marker id.
        size (int, optional): The size of the marker. Defaults to 4 pixels.
        borderBits (int, optional): The number of border bits. Defaults to 1.
        whiteBorderBits (int, optional): The number of white border bits, around the black border. Defaults to 0.
    """
    total_size = size + (2*borderBits) + (2*whiteBorderBits)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = np.zeros((total_size, total_size, 1), dtype="uint8")
    cv2.aruco.generateImageMarker(aruco_dict, id, total_size, marker, borderBits=borderBits+whiteBorderBits)

    # make the extra border white
    if whiteBorderBits > 0:
        whiteBorderPixels = int((whiteBorderBits * (size / 4)) / 2)
        marker[0:whiteBorderPixels, :] = 255
        marker[:, 0:whiteBorderPixels] = 255
        marker[-whiteBorderPixels:, :] = 255
        marker[:, -whiteBorderPixels:] = 255

    file_path = f"markers\\ArUco_4x4_50_{id}.png"
    if not os.path.exists("markers"):
        os.makedirs("markers")

    cv2.imwrite(file_path, marker)
    cv2.imshow("ArUco marker", marker)
    cv2.waitKey(0)

if __name__ == "__main__":
    print("Generating ArUco markers. Press any key to generate the next marker.")
    for i in range(0,8): # generate markers 0-7 for two whiteboards
        generate_marker(i,1024,1,1) # generate a 1024x1024 marker with a 1 bit wide black border and 1 bit wide white border