import os
import re
import csv
import base64
import subprocess
import xml.etree.ElementTree as ET

from src.gps.gps_utils import dms_to_decimal
import logging

logger = logging.getLogger(__name__)


class GPSParser:
    def __init__(self, video_path, output_folder: str):
        self.video_path = video_path
        # self.xml_path = "gps_data.xml"
        self.xml_path = os.path.join(output_folder, "gps_points.xml")

        # drone -> (lat, lon, alt)
        # car -> (lat, lon, timestamp)
        self.gps_points = []

        self.source_type = None  # 'dji', 'car', 'unknown'

    # -----------------------------------------
    #  Extract GPS via Exiftool
    # -----------------------------------------
    def extract_gps_from_video(self) -> bool:
        logger.info(f"Extracting GPS from {self.video_path}")

        result = subprocess.run(
            ["exiftool", "-G", "-ee", "-X", self.video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Exiftool error: {result.stderr}")
            return False

        with open(self.xml_path, "w") as f:
            f.write(result.stdout)

        logger.info("GPS XML extracted successfully")
        return True

    # -----------------------------------------
    #  Determine source type (drone vs car)
    # -----------------------------------------
    def detect_source_type(self):
        with open(self.xml_path, "r") as f:
            xml_content = f.read()

            if "QuickTime/Track3" in xml_content:
                self.source_type = "dji"
            elif "QuickTime/LIGO" in xml_content:
                self.source_type = "car"
            else:
                self.source_type = "unknown"

        logger.info(f"Detected source type: {self.source_type}")

    # -----------------------------------------
    #  Parse GPS data depending on source
    # -----------------------------------------
    def parse_gps_data(self):
        if self.source_type == "dji":
            self._parse_dji_gps()

        elif self.source_type == "car":
            self._parse_car_gps()

        else:
            logger.error("Unknown GPS format")

    # -----------------------------------------
    #  Car GPS parser
    # -----------------------------------------
    def _parse_car_gps(self):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        ns = {"LIGO": "http://ns.exiftool.org/QuickTime/LIGO/1.0/"}

        lat_tags = root.findall(".//LIGO:GPSLatitude", ns)
        lon_tags = root.findall(".//LIGO:GPSLongitude", ns)
        time_tags = root.findall(".//LIGO:GPSDateTime", ns)

        self.gps_points = []

        for lat, lon, t in zip(lat_tags, lon_tags, time_tags):
            lat_dec = dms_to_decimal(lat.text)
            lon_dec = dms_to_decimal(lon.text)
            self.gps_points.append((lat_dec, lon_dec, t.text))

        logger.info(f"Loaded {len(self.gps_points)} car GPS points")

    # -----------------------------------------
    #  Drone GPS parser
    # -----------------------------------------
    def _parse_dji_gps(self):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        ns = {"Track3": "http://ns.exiftool.org/QuickTime/Track3/1.0/"}

        points = []

        for text_tag in root.findall(".//Track3:Text", ns):
            b64 = text_tag.text
            if not b64:
                continue

            try:
                decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")

                match = re.search(
                    r"GPS\s*\(([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)", decoded
                )
                if match:
                    lon = float(match.group(1))
                    lat = float(match.group(2))
                    alt = float(match.group(3))
                    points.append((lat, lon, alt))

            except Exception:
                continue

        self.gps_points = points
        logger.info(f"Loaded {len(points)} drone GPS points")

    # -----------------------------------------
    #  Save to CSV
    # -----------------------------------------
    def save_gps_to_csv(self, path="gps_points.csv"):
        if not self.gps_points:
            logger.error("No GPS points to save")
            return

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["latitude", "longitude", "alt_or_time"])

            for row in self.gps_points:
                writer.writerow(row)

        logger.info(f"Saved GPS points to {path}")
