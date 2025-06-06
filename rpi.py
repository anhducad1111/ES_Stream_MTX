import subprocess

# Lệnh libcamera-vid
libcamera_cmd = [
    "libcamera-vid",
    "-t", "0",
    "--width", "640",
    "--height", "480",
    "--framerate", "30",
    "--bitrate", "2000000",
    "--codec", "h264",
    "--inline",
    "--profile", "baseline",
    "--level", "4.2",
    "--intra", "15",
    "--vflip",
    "-o", "-"
]

ffmpeg_cmd = [
    "ffmpeg",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-probesize", "32",
    "-analyzeduration", "0",
    "-f", "h264",
    "-i", "-",
    "-c:v", "copy",          # Không encode lại, giữ nguyên stream H.264 từ GPU
    "-f", "rtsp",
    "rtsp://localhost:8554/ES_MTX"
]
# Tạo process libcamera-vid
libcamera_proc = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)

# Tạo process ffmpeg, stdin nhận output libcamera-vid
ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=libcamera_proc.stdout)

print("Streaming tới rtsp://<IP_RPI>:8554/ES_MTX")

try:
    ffmpeg_proc.wait()
except KeyboardInterrupt:
    print("Stopping...")
    libcamera_proc.terminate()
    ffmpeg_proc.terminate()
