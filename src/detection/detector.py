import os
import cv2
import pandas as pd
from ultralytics import YOLO

import logging

logger = logging.getLogger(__name__)


class Detector:
    def __init__(self, video_path, gps_points, model_path, target_class, step_frames=15, conf_threshold=0.3):
        self.video_path = video_path
        self.gps_points = gps_points
        self.model = YOLO(model_path)
        self.target_class = target_class.lower()

        self.step_frames = step_frames
        self.conf_threshold = conf_threshold

        self.detections = []

    # --------------------------------------------------------
    def run(self, frames_folder):
        os.makedirs(frames_folder, exist_ok=True)

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.error("Cannot open video")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        gps_interval = total_frames / len(self.gps_points)

        logger.info(f"Processing {total_frames} frames...")

        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model.track(frame, conf=self.conf_threshold, persist=True, verbose=False)[0]

            if frame_idx % self.step_frames == 0:
                print("frame: ", frame_idx)

                gps_idx = min(int(frame_idx / gps_interval), len(self.gps_points) - 1)
                lat, lon, alt_time = self.gps_points[gps_idx]

                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id].lower()

                    if cls_name != self.target_class:
                        continue

                    track_id = int(box.id[0]) if box.id is not None else -1
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                    self.detections.append({
                        "frame": frame_idx,
                        "track_id": track_id,
                        "class": cls_name,
                        "latitude": lat,
                        "longitude": lon,
                        "alt_or_time": alt_time,
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2
                    })

                    # ------------------------------------
                    # DRAW BOUNDING BOX ON FRAME
                    # ------------------------------------
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{cls_name} {track_id}"
                    cv2.putText(frame, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.imwrite(f"{frames_folder}/frame_{frame_idx}.jpg", frame)

            frame_idx += 1

        cap.release()
        logger.info(f"Total detections: {len(self.detections)}")

    # --------------------------------------------------------
    def save(self, output_csv):
        df = pd.DataFrame(self.detections)
        df.to_csv(output_csv, index=False)
        logger.info(f"Saved detections to {output_csv}")
