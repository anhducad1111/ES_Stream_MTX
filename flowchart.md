# Flowchart & Hướng dẫn hệ thống truyền dữ liệu qua RTSP (metadata + hình ảnh) và TCP song song

## 1. Tổng quan hệ thống

- **Raspberry Pi (RPI)**: Đóng vai trò là thiết bị thu hình ảnh từ camera, xử lý dữ liệu, gửi hình ảnh qua RTSP stream, đồng thời truyền/nhận dữ liệu lệnh, trạng thái qua TCP.
- **PC (App)**: Nhận stream RTSP, giải mã hình ảnh, đồng thời kết nối TCP để gửi/nhận lệnh, trạng thái, dữ liệu xử lý.

## 2. Luồng dữ liệu

1. **RPI**
    - Thu hình ảnh từ camera.
    - Xử lý dữ liệu (nếu có: ví dụ nhận diện, đo đạc, v.v.).
    - Gửi stream RTSP (hình ảnh) tới MediaMTX server.
    - Thiết lập server TCP để nhận/gửi lệnh, trạng thái, dữ liệu xử lý.

2. **PC**
    - Kết nối tới RTSP server (MediaMTX), nhận stream.
    - Kết nối tới server TCP trên RPI để gửi lệnh/cài đặt, nhận trạng thái, dữ liệu xử lý.
    - Hiển thị video, biểu đồ dữ liệu, log, trạng thái.

## 3. Yêu cầu hệ thống

### a. Trên Raspberry Pi

- Cài đặt và cấu hình MediaMTX để stream RTSP.
- Sử dụng script (ví dụ `rpi.py`) để stream video qua RTSP.
- Chạy thêm một server TCP (có thể dùng Python socket) để nhận/gửi lệnh, trạng thái, dữ liệu xử lý.

### b. Trên PC

- Kết nối tới RTSP stream để nhận và hiển thị video.
- Kết nối tới server TCP để gửi lệnh/cài đặt, nhận trạng thái, dữ liệu xử lý.
- Hiển thị video, biểu đồ dữ liệu, log, trạng thái.

## 4. Định dạng dữ liệu TCP

- Mỗi gói tin truyền qua TCP gồm 4 byte:

  | Byte   | Vai trò         | Ghi chú                                                        |
  |--------|-----------------|----------------------------------------------------------------|
  | Byte 0 | type            | 0 = command, 1 = response, 2 = error                           |
  | Byte 1 | id              | Xác định lệnh/kiểu dữ liệu (VD: 0x01 = bật đếm ngón tay)        |
  | Byte 2 | value           | Dữ liệu gửi kèm (số lượng ngón tay, trạng thái, mã lỗi, ...)    |
  | Byte 3 | checksum        | Byte0 XOR Byte1 XOR Byte2 để kiểm tra tính toàn vẹn            |

- **Ví dụ:**
  - Client gửi lệnh bật đếm ngón tay: `[0, 0x01, 0x01, checksum]` (type=0, id=1, value=1)
  - Server phản hồi OK: `[1, 0x01, 0x00, checksum]` (type=1, id=1, value=0)
  - Server phản hồi lỗi: `[2, 0x01, 0xFF, checksum]` (type=2, id=1, value=255)
  - Server gửi dữ liệu detect: `[1, 0x02, 0x03, checksum]` (type=1, id=2, value=3)

- **Ý nghĩa các ID phổ biến:**

  | ID (Byte 1) | Ý nghĩa                        |
  |-------------|-------------------------------|
  | 0x01        | Bật/tắt chế độ nhận diện       |
  | 0x02        | Gửi số lượng ngón tay detect   |
  | 0x03        | Gửi trạng thái cảm biến khác   |
  | 0x04        | Gửi nhiệt độ, độ ẩm,...        |

- **Checksum:**
  - Tính bằng phép XOR: `checksum = byte0 ^ byte1 ^ byte2`
  - Giúp kiểm tra tính toàn vẹn gói tin.

- **Không cần đồng bộ thời gian tuyệt đối, chỉ cần gần đúng.**

## 5. Luồng dữ liệu TCP giữa Client và Server

- **Client gửi lệnh → Server phản hồi:**
  - Client gửi lệnh (type=0), server trả về phản hồi (type=1) hoặc lỗi (type=2).
- **Server tự động gửi dữ liệu:**
  - Khi có dữ liệu mới (ví dụ detect ngón tay), server chủ động gửi về client (type=1, id=2, value=số ngón).

---

**Sơ đồ tổng quát:**

```
[Camera] --(video)--> [RPI] --(RTSP)--> [MediaMTX] --(RTSP)--> [PC]
                           |
                           +--(TCP: lệnh, trạng thái, dữ liệu xử lý)--> [PC]
```

- Lệnh điều khiển, trạng thái, dữ liệu xử lý đều truyền qua TCP.
- Video truyền qua RTSP.

---

**Nếu cần ví dụ code TCP server/client hoặc hướng dẫn chi tiết, hãy yêu cầu cụ thể.**
