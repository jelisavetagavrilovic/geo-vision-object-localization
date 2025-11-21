import os
import logging

from src.gps.gps_parser import GPSParser
from src.detection.detector import Detector
from src.visualization.map_builder import MapBuilder

logger = logging.getLogger(__name__)


class ObjectMappingPipeline:
    def __init__(self, config):
        self.config = config

    def run(self):
        video_path = self.config["video_path"]
        output_folder = self.config["output"]["folder"]

        os.makedirs(output_folder, exist_ok=True)

        # --------------------------------------------------------
        # GPS Parsing
        # --------------------------------------------------------
        gps = GPSParser(video_path, output_folder)
        if gps.extract_gps_from_video():
            gps.detect_source_type()
            gps.parse_gps_data()

            gps_csv = os.path.join(output_folder, "gps_points.csv")
            gps.save_gps_to_csv(gps_csv)

            # --------------------------------------------------------
            # Object Detection
            # --------------------------------------------------------
            frames_folder = os.path.join(output_folder, "frames")
            detections_csv = os.path.join(output_folder, "detections.csv")

            detector = Detector(
                video_path=video_path,
                gps_points=gps.gps_points,
                model_path=self.config["model"]["path"],
                target_class=self.config["model"]["target_class"],
                step_frames=self.config["processing"]["step_frames"],
                conf_threshold=self.config["model"]["conf_threshold"]
            )

            detector.run(frames_folder=frames_folder)
            detector.save(detections_csv)

            # --------------------------------------------------------
            # Map Building
            # --------------------------------------------------------
            map_file = os.path.join(output_folder, "map.html")
            mb = MapBuilder(gps_points=gps.gps_points)
            mb.build_map(map_file, detections_csv, frames_folder)

            logger.info("Pipeline completed successfully")
