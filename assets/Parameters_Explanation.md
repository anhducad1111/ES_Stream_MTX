# Giải thích chi tiết các thông số RTSP Streaming

## 1. LIBCAMERA-VID Parameters (rpi.py)

### Thông số hiện tại:

#### [`-t "0"`](rpi.py:6)

- **Ý nghĩa**: Thời gian recording (milliseconds)
- **Giá trị**: `0` = vô thời hạn
- **Nếu có**: Stream sẽ chạy trong thời gian chỉ định rồi tự dừng
- **Nếu không**: Mặc định là 5000ms (5 giây)
- **Có thể thay đổi**: `10000` (10s), `30000` (30s), `-1` (vô hạn)

#### [`--width "640"`](rpi.py:7) & [`--height "480"`](rpi.py:8)

- **Ý nghĩa**: Độ phân giải video
- **Giá trị hiện tại**: 640x480 (VGA)
- **Nếu có**: Chỉ định độ phân giải cụ thể
- **Nếu không**: Sử dụng độ phân giải mặc định của camera
- **Các tùy chọn khác**:
  - `320x240` (QVGA) - ít bandwidth
  - `1280x720` (HD) - chất lượng cao hơn
  - `1920x1080` (Full HD) - chất lượng cao nhất
  - `800x600` (SVGA)

#### [`--framerate "30"`](rpi.py:9)

- **Ý nghĩa**: Số khung hình trên giây (FPS)
- **Giá trị**: 30 FPS
- **Nếu có**: Kiểm soát tốc độ khung hình
- **Nếu không**: Sử dụng FPS mặc định (thường 30)
- **Tác động**:
  - **Cao (60 FPS)**: Mượt mà hơn, tốn bandwidth
  - **Trung bình (30 FPS)**: Cân bằng tốt
  - **Thấp (15-20 FPS)**: Tiết kiệm bandwidth, có thể giật
- **Có thể điều chỉnh**: `15`, `20`, `25`, `30`, `60`

#### [`--bitrate "2000000"`](rpi.py:10)

- **Ý nghĩa**: Tốc độ bit (bits/giây)
- **Giá trị**: 2,000,000 bits/s = 2 Mbps
- **Nếu có**: Kiểm soát chất lượng và kích thước file
- **Nếu không**: Sử dụng bitrate mặc định
- **Tác động**:
  - **Cao (5-10 Mbps)**: Chất lượng cao, tốn bandwidth
  - **Trung bình (1-3 Mbps)**: Cân bằng
  - **Thấp (500k-1M)**: Tiết kiệm, chất lượng thấp
- **Gợi ý theo độ phân giải**:
  - 320x240: 500k-1M
  - 640x480: 1-2M
  - 1280x720: 2-4M
  - 1920x1080: 4-8M

#### [`--codec "h264"`](rpi.py:11)

- **Ý nghĩa**: Codec nén video
- **Giá trị**: H.264 (AVC)
- **Nếu có**: Sử dụng codec chỉ định
- **Nếu không**: Sử dụng codec mặc định
- **Các tùy chọn khác**:
  - `h265` (HEVC) - nén tốt hơn nhưng tốn CPU
  - `mjpeg` - ít nén, chất lượng cao
  - `yuv420` - raw format

#### [`--inline`](rpi.py:12)

- **Ý nghĩa**: Đưa SPS/PPS headers vào mỗi keyframe
- **Nếu có**: Streaming real-time tốt hơn
- **Nếu không**: Headers riêng biệt, có thể gây vấn đề streaming
- **Quan trọng**: **BẮT BUỘC** cho RTSP streaming

#### [`--profile "baseline"`](rpi.py:13)

- **Ý nghĩa**: H.264 profile
- **Giá trị**: Baseline profile
- **Nếu có**: Kiểm soát tính năng codec
- **Nếu không**: Sử dụng profile mặc định
- **Các tùy chọn**:
  - `baseline` - tương thích tốt nhất, ít tính năng
  - `main` - cân bằng
  - `high` - nhiều tính năng, yêu cầu decoder mạnh

#### [`--level "4.2"`](rpi.py:14)

- **Ý nghĩa**: H.264 level (giới hạn độ phân giải/bitrate)
- **Giá trị**: Level 4.2
- **Nếu có**: Đảm bảo tương thích với decoder
- **Nếu không**: Tự động detect
- **Các level phổ biến**:
  - `3.1` - 720p@30fps
  - `4.0` - 1080p@30fps
  - `4.2` - 1080p@60fps

#### [`--intra "15"`](rpi.py:15)

- **Ý nghĩa**: Khoảng cách giữa các I-frame (GOP size)
- **Giá trị**: 15 frames
- **Nếu có**: Kiểm soát chất lượng và khả năng tìm kiếm
- **Nếu không**: Mặc định thường là 30
- **Tác động**:
  - **Nhỏ (5-10)**: Chất lượng cao, tìm kiếm nhanh, file lớn
  - **Vừa (15-30)**: Cân bằng
  - **Lớn (60+)**: File nhỏ, chất lượng có thể giảm

#### [`--vflip`](rpi.py:16)

- **Ý nghĩa**: Lật video theo chiều dọc
- **Nếu có**: Video bị lật 180°
- **Nếu không**: Video hướng bình thường
- **Tùy chọn khác**: `--hflip` (lật ngang), `--rotation 180`

#### [`-o "-"`](rpi.py:17)

- **Ý nghĩa**: Output destination
- **Giá trị**: `-` = stdout (pipe to other process)
- **Nếu có**: Xuất ra file hoặc pipe
- **Nếu không**: Không có output
- **Các tùy chọn**: `output.h264`, `/dev/null`, `-`

---

## 2. FFMPEG Parameters (rpi.py)

### Input Parameters:

#### [`-fflags "nobuffer"`](rpi.py:22)

- **Ý nghĩa**: Tắt buffering
- **Nếu có**: Giảm latency, real-time streaming
- **Nếu không**: Có buffer, tăng latency
- **Quan trọng**: **QUAN TRỌNG** cho streaming real-time

#### [`-flags "low_delay"`](rpi.py:23)

- **Ý nghĩa**: Chế độ low delay
- **Nếu có**: Tối ưu cho streaming real-time
- **Nếu không**: Tối ưu cho quality thay vì latency

#### [`-probesize "32"`](rpi.py:24)

- **Ý nghĩa**: Kích thước dữ liệu để analyze input (bytes)
- **Giá trị**: 32 bytes (rất nhỏ)
- **Nếu có**: Khởi động nhanh
- **Nếu không**: Mặc định 5MB, chậm hơn
- **Gợi ý**:
  - **Streaming**: 32-1024
  - **File analysis**: 1M-10M

#### [`-analyzeduration "0"`](rpi.py:25)

- **Ý nghĩa**: Thời gian analyze input (microseconds)
- **Giá trị**: 0 = không analyze
- **Nếu có**: Khởi động ngay lập tức
- **Nếu không**: Mặc định 5 giây

#### [`-f "h264"`](rpi.py:26)

- **Ý nghĩa**: Format của input stream
- **Giá trị**: H.264 elementary stream
- **Nếu có**: FFmpeg biết cách parse
- **Nếu không**: Auto-detect (có thể sai)

#### [`-i "-"`](rpi.py:27)

- **Ý nghĩa**: Input source
- **Giá trị**: stdin (từ libcamera-vid)
- **Các tùy chọn**: file path, URL, device

### Output Parameters:

#### [`-c:v "copy"`](rpi.py:28)

- **Ý nghĩa**: Video codec cho output
- **Giá trị**: copy = không encode lại
- **Nếu có**: Giữ nguyên codec, nhanh
- **Nếu không**: Re-encode, chậm, tốn CPU
- **Các tùy chọn**: `libx264`, `h264_nvenc`, `copy`

#### [`-f "rtsp"`](rpi.py:29)

- **Ý nghĩa**: Output format
- **Giá trị**: RTSP protocol
- **Nếu có**: Stream qua RTSP
- **Nếu không**: Xuất ra file
- **Các tùy chọn**: `mp4`, `flv`, `hls`, `rtsp`

---

## 3. FFMPEG Parameters (main.py)

### Input Parameters:

#### [`rtsp_transport='udp'`](main.py:7)

- **Ý nghĩa**: Giao thức transport cho RTSP
- **Giá trị**: UDP
- **Nếu có UDP**: Nhanh nhưng có thể mất packet
- **Nếu TCP**: Đáng tin cậy nhưng chậm hơn
- **Gợi ý**:
  - **LAN tốt**: UDP
  - **Mạng không ổn định**: TCP

#### [`flags='low_delay'`](main.py:7)

- **Ý nghĩa**: Tối ưu cho latency thấp
- **Tương tự như phía server**

#### [`fflags='nobuffer'`](main.py:7)

- **Ý nghĩa**: Tắt buffering
- **Tương tự như phía server**

#### [`probesize='32'`](main.py:7)

- **Ý nghĩa**: Kích thước probe
- **Giá trị**: 32 bytes
- **Tác động**: Khởi động nhanh nhưng có thể miss metadata

#### [`analyzeduration='0'`](main.py:7)

- **Ý nghĩa**: Thời gian analyze
- **Giá trị**: 0 = không analyze
- **Tác động**: Khởi động ngay nhưng có thể thiếu info

### Output Parameters:

#### [`format='rawvideo'`](main.py:8)

- **Ý nghĩa**: Format output
- **Giá trị**: Raw video data
- **Nếu có**: Dữ liệu thô, dễ xử lý
- **Nếu không**: Encoded format

#### [`pix_fmt='bgr24'`](main.py:8)

- **Ý nghĩa**: Pixel format
- **Giá trị**: BGR 24-bit (OpenCV format)
- **Nếu có**: Tương thích với OpenCV
- **Nếu không**: Cần convert format
- **Các tùy chọn**: `rgb24`, `yuv420p`, `gray`

---

## 4. Thông số có thể THÊM VÀO

### Cho libcamera-vid:

```bash
# Điều khiển exposure
--shutter 33333        # 1/30s exposure
--gain 2.0             # ISO gain

# Điều khiển white balance
--awb auto             # Auto white balance
--awbgains 1.5,1.3     # Manual white balance

# Điều khiển image
--brightness 0.1       # Độ sáng (-1.0 to 1.0)
--contrast 1.1         # Độ tương phản (0.0 to 2.0)
--saturation 1.0       # Độ bão hòa màu

# Preview (không cần cho streaming)
--nopreview           # Tắt preview window

# Advanced encoding
--flush               # Flush encoder
--split               # Split output files
--circular            # Circular buffer

# Quality control
--qp 25               # Quantization parameter (thay cho bitrate)
--memlimit 0          # Memory limit for encoder
```

### Cho FFmpeg (rpi.py):

```bash
# Buffer control
-bufsize 2M           # Encoder buffer size
-maxrate 2M           # Maximum bitrate
-minrate 1M           # Minimum bitrate

# GOP control
-g 30                 # GOP size
-keyint_min 15        # Minimum keyframe interval

# Transport
-rtsp_transport tcp   # Force TCP transport
-rtsp_flags prefer_tcp # Prefer TCP

# Timeouts
-timeout 5000000      # Connection timeout (microseconds)
-reconnect 1          # Auto reconnect on failure

# Advanced
-tune zerolatency     # Zero latency tuning
-preset ultrafast     # Encoding preset
-profile:v baseline   # Video profile
```

### Cho FFmpeg (main.py):

```bash
# Buffer control
-buffer_size 1024000  # Input buffer size
-max_delay 500000     # Maximum delay (microseconds)

# Decoding
-threads 2            # Decoder threads
-thread_type slice    # Threading type

# Error handling
-err_detect aggressive # Error detection level
-fflags +discardcorrupt # Discard corrupt packets

# Sync
-sync ext             # External sync
-drop_pkts_on_overflow 1 # Drop packets on overflow

# Advanced
-reorder_queue_size 1 # Reorder queue size
-protocol_whitelist file,udp,rtp,rtsp # Protocol whitelist
```

---

## 5. Thông số có thể BỚT ĐI

### Có thể bỏ nếu không cần:

#### libcamera-vid:

- `--level` - tự động detect
- `--profile` - dùng mặc định
- `--vflip` - nếu camera đặt đúng hướng

#### FFmpeg:

- `-flags low_delay` - nếu không cần latency thấp
- `-probesize` và `-analyzeduration` - nếu chấp nhận khởi động chậm
- `-fflags nobuffer` - nếu chấp nhận latency cao

---

## 6. Tối ưu hóa theo USE CASE

### Chất lượng cao (LAN):

```bash
# libcamera-vid
--width 1920 --height 1080
--framerate 30
--bitrate 8000000
--profile high
--intra 30

# ffmpeg
-c:v libx264 -preset medium -crf 18
```

### Latency thấp (Gaming):

```bash
# libcamera-vid
--width 1280 --height 720
--framerate 60
--bitrate 4000000
--intra 1
--inline

# ffmpeg
-tune zerolatency -preset ultrafast
-fflags nobuffer -flags low_delay
```

### Tiết kiệm bandwidth:

```bash
# libcamera-vid
--width 640 --height 480
--framerate 15
--bitrate 500000
--intra 60

# ffmpeg
-maxrate 500k -bufsize 1M
```

### Ổn định mạng:

```bash
# ffmpeg (cả 2 phía)
-rtsp_transport tcp
-timeout 10000000
-reconnect 1
```

---

## 7. Troubleshooting Parameters

### Khi gặp packet loss:

```bash
# main.py
rtsp_transport='tcp'  # Thay vì UDP
max_delay='1000000'   # Tăng delay tolerance
```

### Khi video lag:

```bash
# rpi.py - giảm bitrate
--bitrate 1000000

# rpi.py - tăng GOP
--intra 5
```

### Khi không connect được:

```bash
# main.py - tăng timeout
analyzeduration='1000000'
probesize='1048576'
```
