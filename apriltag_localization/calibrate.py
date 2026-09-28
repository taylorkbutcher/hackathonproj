"""Chessboard calibration for MacBook camera. Saves calibration.npz."""
import cv2
import numpy as np
import glob

PATTERN = (9, 6)  # inner corners: adjust to your board
SQUARE_M = 0.025  # 25mm squares

objp = np.zeros((PATTERN[0] * PATTERN[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:PATTERN[0], 0:PATTERN[1]].T.reshape(-1, 2) * SQUARE_M

objpoints, imgpoints = [], []
cap = cv2.VideoCapture(0)
print("Show chessboard. Press 'c' to capture, 'q' when done (>=10 views).")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, PATTERN)
    cv2.drawChessboardCorners(frame, PATTERN, corners, found)
    cv2.imshow("calib", frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord("c") and found:
        objpoints.append(objp)
        imgpoints.append(corners)
        print(f"captured {len(objpoints)}")
    elif k == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

if len(objpoints) < 8:
    print("Need >=8 views. Exiting.")
    raise SystemExit(1)

ret, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("camera_matrix:\n", mtx)
print("dist:", dist.ravel())
np.savez("calibration.npz", camera_matrix=mtx, dist_coeffs=dist)
print("Saved calibration.npz - paste values into detect.py")
