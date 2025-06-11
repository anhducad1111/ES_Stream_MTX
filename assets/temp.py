import ffmpeg
import numpy as np
import cv2

process = (
    ffmpeg
    .input("rtsp://192.168.137.112:8554/ES_MTX", rtsp_transport='udp', flags='low_delay', fflags='nobuffer', probesize='32', analyzeduration='0', r='24')
    .output('pipe:', format='rawvideo', pix_fmt='bgr24')
    .run_async(pipe_stdout=True)
)

width, height = 640, 480

while True:
    in_bytes = process.stdout.read(width * height * 3)
    if not in_bytes:
        break
    frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
    cv2.imshow("RTSP Stream", frame)
    if cv2.waitKey(1) == ord('q'):
        break

process.stdout.close()