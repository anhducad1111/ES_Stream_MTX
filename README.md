# Hệ thống RTSP Streaming với Raspberry Pi và MediaMTX

## Tổng quan hệ thống

Hệ thống này bao gồm 3 thành phần chính:

1. **MediaMTX** - RTSP server chạy trên Raspberry Pi 4
2. **rpi.py** - Script chạy trên Raspberry Pi 4 để capture và stream video
3. **main.py** - Script chạy trên máy client để nhận và hiển thị video stream

## Luồng hoạt động

```
[Camera RPi] → [libcamera-vid] → [ffmpeg] → [MediaMTX Server] → [Network] → [Client main.py] → [Display]
```

---

## 1. MediaMTX Server

**Vị trí**: Raspberry Pi 4  
**Chức năng**: RTSP server nhận video stream từ ffmpeg và phục vụ cho các client

### Cách chạy

```bash
# Cần chạy trước khi chạy rpi.py
./mediamtx
```

MediaMTX sẽ lắng nghe trên port 8554 và chấp nhận stream tại endpoint `/ES_MTX`.

---

## 2. rpi.py - Video Capture và Streaming (Raspberry Pi 4)

### Chức năng chính

Script này capture video từ camera của Raspberry Pi và stream lên RTSP server thông qua MediaMTX.

### Phân tích chi tiết code

#### Cấu hình libcamera-vid

```python
libcamera_cmd = [
    "libcamera-vid",
    "-t", "0",              # Thời gian recording (0 = vô hạn)
    "--width", "640",       # Độ rộng video 640px
    "--height", "480",      # Độ cao video 480px
    "--framerate", "30",    # 30 FPS
    "--bitrate", "2000000", # Bitrate 2Mbps
    "--codec", "h264",      # Sử dụng codec H.264
    "--inline",             # Inline headers cho streaming
    "--profile", "baseline", # H.264 baseline profile (tương thích tốt)
    "--level", "4.2",       # H.264 level 4.2
    "--intra", "15",        # I-frame mỗi 15 frames (GOP size)
    "--vflip",              # Lật video theo chiều dọc
    "-o", "-"               # Output ra stdout
]
```

#### Cấu hình FFmpeg

```python
ffmpeg_cmd = [
    "ffmpeg",
    "-fflags", "nobuffer",      # Không buffer để giảm độ trễ
    "-flags", "low_delay",      # Cờ low delay
    "-probesize", "32",         # Giảm thời gian probe input
    "-analyzeduration", "0",    # Không analyze duration
    "-f", "h264",               # Input format H.264
    "-i", "-",                  # Input từ stdin
    "-c:v", "copy",             # Copy video stream (không encode lại)
    "-f", "rtsp",               # Output format RTSP
    "rtsp://localhost:8554/ES_MTX" # RTSP endpoint
]
```

#### Pipeline xử lý

```python
# Tạo process libcamera-vid
libcamera_proc = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)

# Tạo process ffmpeg, stdin nhận output từ libcamera-vid
ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=libcamera_proc.stdout)
```

**Luồng dữ liệu**: Camera → libcamera-vid → ffmpeg → MediaMTX Server

#### Xử lý tín hiệu và cleanup

```python
try:
    ffmpeg_proc.wait()  # Chờ ffmpeg process
except KeyboardInterrupt:
    print("Stopping...")
    libcamera_proc.terminate()  # Dừng libcamera process
    ffmpeg_proc.terminate()     # Dừng ffmpeg process
```

---

## 3. main.py - RTSP Client (Máy local)

### Chức năng chính

Script này kết nối tới RTSP server, nhận video stream và hiển thị real-time bằng OpenCV.

### Phân tích chi tiết code

#### Cấu hình FFmpeg input

```python
process = (
    ffmpeg
    .input("rtsp://192.168.137.112:8554/ES_MTX",
           rtsp_transport='udp',    # Sử dụng UDP transport (nhanh hơn TCP)
           flags='low_delay',       # Giảm độ trễ
           fflags='nobuffer',       # Không buffer
           probesize='32',          # Giảm probe size
           analyzeduration='0')     # Không analyze duration
    .output('pipe:',
            format='rawvideo',      # Output raw video data
            pix_fmt='bgr24')        # Pixel format BGR 24-bit (OpenCV format)
    .run_async(pipe_stdout=True)    # Chạy async và pipe stdout
)
```

#### Xử lý video frames

```python
width, height = 640, 480  # Kích thước frame khớp với cấu hình RPi

while True:
    # Đọc raw bytes cho 1 frame (640 * 480 * 3 bytes)
    in_bytes = process.stdout.read(width * height * 3)

    if not in_bytes:
        break  # Hết data thì thoát

    # Convert bytes thành numpy array với shape [height, width, 3]
    frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])

    # Hiển thị frame bằng OpenCV
    cv2.imshow("RTSP Stream", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) == ord('q'):
        break

process.stdout.close()  # Đóng stream
```

---

## Cấu hình Network

### IP Address

- **Raspberry Pi IP**: `192.168.137.112`
- **RTSP Port**: `8554`
- **RTSP Endpoint**: `/ES_MTX`

### URL Stream

```
rtsp://192.168.137.112:8554/ES_MTX
```

---

## Thứ tự chạy hệ thống

1. **Trên Raspberry Pi 4**:

   ```bash
   # Bước 1: Chạy MediaMTX server
   ./mediamtx

   # Bước 2: Chạy script streaming (terminal khác)
   python3 rpi.py
   ```

2. **Trên máy client**:
   ```bash
   # Chạy script client để xem stream
   python main.py
   ```

---

## Tối ưu hóa độ trễ (Low Latency)

Hệ thống này được tối ưu cho độ trễ thấp thông qua:

### Trên RPi (rpi.py):

- `--inline`: Inline SPS/PPS headers
- `--profile baseline`: Profile đơn giản, decode nhanh
- `--intra 15`: GOP size nhỏ, ít B-frames
- `-c:v copy`: Không encode lại video
- FFmpeg flags: `nobuffer`, `low_delay`

### Trên Client (main.py):

- `rtsp_transport='udp'`: UDP nhanh hơn TCP
- `flags='low_delay'`, `fflags='nobuffer'`
- `probesize='32'`, `analyzeduration='0'`: Giảm thời gian khởi tạo

---

## Các điểm quan trọng

1. **MediaMTX phải chạy trước** rpi.py
2. **IP address** trong main.py phải khớp với IP của RPi
3. **Kích thước frame** (640x480) phải nhất quán giữa rpi.py và main.py
4. **Camera permission**: RPi cần quyền truy cập camera
5. **Network**: Cả 2 máy phải cùng mạng và có thể kết nối với nhau

---

## Troubleshooting

### Lỗi thường gặp:

- **Connection refused**: MediaMTX chưa chạy hoặc firewall block port 8554
- **No video**: Camera không khả dụng hoặc đang được sử dụng bởi process khác
- **Lag/freeze**: Network không ổn định hoặc bitrate quá cao
- **Format error**: Mismatch giữa codec settings và decoder capabilities

### Debug commands:

```bash
# Test RTSP stream bằng VLC hoặc ffplay
ffplay rtsp://192.168.137.112:8554/ES_MTX

# Check camera trên RPi
libcamera-hello

# Check network connectivity
ping 192.168.137.112
```
