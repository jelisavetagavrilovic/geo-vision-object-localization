# Geo Vision Object Localization

## Project Overview

**Geo Vision Object Localization** is a system for detecting and geolocating objects in videos recorded by moving cameras such as dashcams or drones. Powered by **YOLOv8**, the pipeline analyzes each video frame, identifies selected object classes (e.g., cars, people, bicycles), and pairs every detection with the **GPS position** of the camera at that moment.

The detections are displayed on an interactive HTML map that includes:
- the full route of the camera,
- markers for each detected object,
- each object is placed using its last detected frame, which provides the closest available camera position relative to the object.

At this stage, the recorded location reflects the camera’s position when the object was detected, rather than the object’s precise location. Future improvements aim to calculate **accurate object geolocation** by considering camera angles, device orientation, lens properties, scene depth, and other factors.  



## Project Structure

```bash
geo-vision-object-localization/
├── data/
│   ├── raw_videos/        # Optional: user-provided videos (not included by default)
│   └── outputs/           # Generated frames, CSVs files
├── models/                # Optional: place your YOLOv8 model (.pt) here
├── src/
│   ├── detection/         # Object detection scripts
│   ├── gps/               # GPS parsing and utilities
│   ├── visualization/     # Map generation scripts
│   ├── config.yaml        # Configuration file: model, video, processing settings
│   └── pipeline.py        # Core processing pipeline
└── main.py                # Entry point to run the full pipeline
```


## Installation

### Requirements
- **Python 3.10**  
  > Some libraries used in this project are not yet tested with newer Python versions.
- **Pip** (Python package manager)

### Libraries
Recommended versions:
- `numpy < 2.0`
- `pandas`
- `opencv-python`
- `ultralytics` (YOLOv8)
- `folium`
- `pyyaml` (for configuration files)

Install required Python libraries via pip:

```bash
pip install "numpy<2" pandas opencv-python ultralytics folium pyyaml
```

### External Tools

The project requires **ExifTool** to extract GPS data from video files.  

Install instructions:

- **macOS**:  
```bash
brew install exiftool
```

- **Linux (Debian/Ubuntu)**:
```bash
sudo apt install libimage-exiftool-perl
```

- **Windows**:  
Download and install from the [ExifTool official website](https://exiftool.org/).


## Project Setup 

### Clone the Repository

```bash
git clone https://github.com/jelisavetagavrilovic/geo-vision-object-localization
cd geo-vision-object-localization
```

### Download YOLOv8 Model

This project uses a YOLOv8 model (`.pt`) for object detection. Before running the pipeline, download the YOLOv8 nano model:

```bash
mkdir -p models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -O models/yolov8n.pt
```
Alternatively, you can download a different YOLOv8 model version from [Ultralytics releases](https://github.com/ultralytics/ultralytics/releases).


#### Configuring the Model

Edit `src/config.yaml` to define the model path, target class, and confidence threshold:
```yaml
model:
  path: "models/yolov8n.pt"
  target_class: "car"        
  conf_threshold: 0.5        
```
> The model must be downloaded and placed correctly before running the pipeline.


### Video File

Supported video formats: `.mp4`, `.MOV`, `.avi`, `.mkv`.

Currently, the project supports videos with GPS data from:
- **Car dashcams** using the QuickTime LIGO format.  
- **DJI drones** using the QuickTime Track3 format.  

#### Configuring the Video Path

Update the `src/config.yaml` file to point to your video, example:

```yaml
video_path: "data/raw_videos/video.MP4"
```

## Running the Pipeline

After placing the model and video file, execute:
```bash
python3 main.py
```
The script will:
- Perform object detection frame by frame
- Save detections to a CSV file
- Generate an interactive HTML map

Extracted frames and detection snapshots will be stored in `data/outputs/frames/`.

Open the HTML map using a browser or with a Live Server extension to explore the results interactively.

You can check the example interactive map: `data/outputs/map.html`.