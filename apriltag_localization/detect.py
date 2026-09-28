"""AprilTag localization: tag pose in camera frame.
Setup: MacBook camera, 100mm tags (tag36h11), Python + OpenCV.
"""
import cv2
import numpy as np
from pupil_apriltags import Detector

TAG_SIZE_M = 0.100  # 100mm
TAG_FAMILY = "tag36h11"

# TODO: replace with your calibrated values.
# Run calibrate.py to fill these in.
# MacBook Pro 720p defaults are a starting guess only.
CAMERA_MATRIX = np.array([
    [900.0, 0.0, 640.0],
    [0.0, 900.0, 360.0],
    [0.0, 0.0, 1.0],
], dtype=float)
DIST_COEFFS = np.zeros((4, 1))  # k1,k2,p1,p2


def get_detector():
    return Detector(
        families=TAG_FAMILY,
        nthreads=4,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0,
    )


def estimate_pose(det, camera_matrix, dist_coeffs):
    # 3D corners in tag frame: x right, y down, z out (toward camera)
    s = TAG_SIZE_M / 2.0
    obj_pts = np.array([
        [-s, -s, 0],
        [ s, -s, 0],
        [ s,  s, 0],
        [-s,  s, 0],
    ], dtype=np.float64)
    img_pts = np.array(det.corners, dtype=np.float64)
    ok, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, camera_matrix, dist_coeffs)
    if not ok:
        return None, None
    return rvec.flatten(), tvec.flatten()


def main():
    detector = get_detector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open MacBook camera (index 0).")
        return

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets = detector.detect(gray, estimate_tag_pose=False)

        for det in dets:
            rvec, tvec = estimate_pose(det, CAMERA_MATRIX, DIST_COEFFS)
            dist = float(np.linalg.norm(tvec)) if tvec is not None else -1

            # draw outline + id
            pts = det.corners.astype(int)
            for i in range(4):
                cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % 4]), (0, 255, 0), 2)
            cv2.putText(frame, f"id:{det.tag_id} d:{dist:.2f}m",
                        tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # axes for pose
            if rvec is not None:
                cv2.drawFrameAxes(frame, CAMERA_MATRIX, DIST_COEFFS, rvec, tvec, TAG_SIZE_M * 0.5)
                print(f"tag {det.tag_id}: t={tvec.round(3)} m rvec={rvec.round(3)} dist={dist:.3f}m")

        cv2.imshow("apriltag", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
