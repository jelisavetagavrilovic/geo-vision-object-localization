import os
import folium
import pandas as pd
import base64
from src.gps.gps_utils import calculate_bearing

import logging
logger = logging.getLogger(__name__)


class MapBuilder:
    def __init__(self, gps_points):
        self.gps_points = gps_points

    def img_to_base64(self, path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # ------------------------------------------------------
    def build_map(self, output_html, detections_csv, frames_folder):
        coords = [(lat, lon) for (lat, lon, _) in self.gps_points]

        m = folium.Map(location=coords[0], zoom_start=17, max_zoom=22)

        # Draw GPS route + arrows
        for i in range(len(coords) - 1):
            lat1, lon1 = coords[i]
            lat2, lon2 = coords[i + 1]

            bearing = calculate_bearing(lat1, lon1, lat2, lon2)

            folium.PolyLine([(lat1, lon1), (lat2, lon2)], color="blue", weight=3).add_to(m)

            mid_lat = (lat1 + lat2) / 2
            mid_lon = (lon1 + lon2) / 2

            arrow = folium.DivIcon(html=f"""
                <div style="
                    transform: rotate({bearing - 90}deg);
                    color: red;
                    font-size: 15px;
                    line-height: 0.5;">
                    ➤
                </div>
            """)

            folium.Marker([mid_lat, mid_lon], icon=arrow).add_to(m)

        # Start/end markers
        folium.Marker(coords[0], icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(coords[-1], icon=folium.Icon(color="darkgreen")).add_to(m)

        # ------------------------------------------------------
        # LOAD DETECTIONS
        try:
            df = pd.read_csv(detections_csv)
            df = df.dropna(subset=["latitude", "longitude"])

            last = df.groupby("track_id").last().reset_index()
            groups = last.groupby(["latitude", "longitude"])

            for (lat, lon), group in groups:

                group = group.sort_values("frame")

                # BUILD IMAGES
                img_tags = ""

                for i, row in enumerate(group.itertuples(), 1):

                    img_path = os.path.join(frames_folder, f"frame_{row.frame}.jpg")

                    try:
                        encoded = self.img_to_base64(img_path)
                    except Exception as e:
                        logger.error(f"Cannot load frame {img_path}: {e}")
                        continue

                    # First image visible, others hidden
                    display_state = "block" if i == 1 else "none"

                    img_tags += f"""
                        <div class="slide" style="display:{display_state}">
                            <img src="data:image/jpeg;base64,{encoded}" style="max-width:700px;">
                            <br><b>ID:</b> {row.track_id} | <b>Frame:</b> {row.frame}
                        </div>
                    """


                # SLIDER POPUP
                slider_html = f"""
                <div>
                    <h4>Detections on this location: {len(group)}</h4>
                    <div id="slider" style="text-align:center;">
                        {img_tags}
                        <br>
                        <input type="range" min="1" max="{len(group)}" value="1"
                            oninput="this.parentElement.querySelectorAll('.slide')
                            .forEach((div,i)=>div.style.display=(i==this.value-1)?'block':'none');">
                    </div>
                    <b>Lat:</b> {lat}, <b>Lon:</b> {lon}
                </div>
                """

                popup = folium.Popup(slider_html, max_width=1000)

                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html="""
                        <div style="font-size: 30px; transform: translate(-50%, -50%);">🚗</div>
                    """),
                    tooltip=f"{len(group)} object(s) here",
                    popup=popup
                ).add_to(m)

        except Exception as e:
            logger.error(f"Error loading detections: {e}")

        m.save(output_html)
        logger.info(f"Map saved to {output_html}")

