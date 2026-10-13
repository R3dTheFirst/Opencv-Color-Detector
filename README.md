# Camera Color Detector

Run the local viewer with:

```sh
python3 server.py
```

Then open http://127.0.0.1:8000. The viewer connects to the configured DroidCam feed at `http://10.236.0.22:4747/video`. Click the live image to average the pixels inside a 30-pixel-diameter circle centered on that source-frame point. The resulting HEX and RGB values are shown alongside the sample location.

The camera must be reachable from this computer and available to the viewer. If DroidCam reports that it is busy, close other apps using the camera and reload the page.
