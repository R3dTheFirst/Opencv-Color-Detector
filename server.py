from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CAMERA_URL = "http://10.236.0.22:4747/video"
PAGE = Path(__file__).with_name("index.html")


class ColorDetectorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            page = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return

        if self.path != "/video":
            self.send_error(404)
            return

        request = Request(CAMERA_URL, headers={"User-Agent": "ColorDetector/1.0"})
        try:
            upstream = urlopen(request, timeout=5)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            self.send_error(502, "Could not connect to the camera")
            self.log_message("Camera connection failed: %s", error)
            return

        content_type = upstream.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/"):
            upstream.close()
            self.send_error(502, "Camera did not return a live multipart video stream")
            self.log_message("Unexpected camera content type: %s", content_type or "missing")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                chunk = upstream.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
            pass
        finally:
            upstream.close()

    def log_message(self, format, *args):
        if self.path != "/video":
            super().log_message(format, *args)


def main():
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, ColorDetectorHandler)
    print("Color detector running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping color detector.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()