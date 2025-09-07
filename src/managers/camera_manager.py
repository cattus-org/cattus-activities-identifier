import cv2
import time
import logging
import threading
import numpy as np

class CameraManager:
    def __init__(self, config):
        self.config = config
        self.rtsp_url = config.RTSP_URL
        self.width = config.CAMERA_WIDTH
        self.height = config.CAMERA_HEIGHT
        self.buffer_size = config.CAMERA_BUFFER_SIZE
        self.reset_frame_count = config.CAMERA_RESET_FRAME_COUNT
        self.enable_camera_reset = config.ENABLE_CAMERA_RESET

        self.cap = None
        self.is_connected = False
        self.connection_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        self.last_error = None
        self.consecutive_failures = 0

        self.reconnecting = False  # Flag para indicar se está reconectando

        # Correção: definir frame_lock e variáveis para captura contínua
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        self.running = True
        self.capture_thread = None

        self._initialize_camera_async()

    def _initialize_camera(self):
        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None

            self.logger.info(f"Tentando conectar na câmera RTSP: {self.rtsp_url}")

            max_retries = 5
            retry_delay = 5  # segundos

            for attempt in range(max_retries):
                self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

                if self.cap.isOpened():
                    self.is_connected = True
                    self.logger.info("Conexão com a câmera estabelecida com sucesso.")
                    self.reconnecting = False
                    # Iniciar thread de captura contínua
                    if self.capture_thread is None or not self.capture_thread.is_alive():
                        self.running = True
                        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
                        self.capture_thread.start()
                    return
                else:
                    self.logger.warning(f"Falha ao conectar na câmera. Tentativa {attempt + 1} de {max_retries}.")
                    time.sleep(retry_delay)

            self.is_connected = False
            self.last_error = "Falha ao conectar na câmera após várias tentativas."
            self.logger.error(self.last_error)
            self.reconnecting = False

    def _initialize_camera_async(self):
        if self.reconnecting:
            self.logger.info("Reconexão já em andamento, ignorando nova tentativa.")
            return

        self.reconnecting = True

        def target():
            self._initialize_camera()

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def _is_frame_valid(self, frame):
        if frame is None or frame.size == 0:
            return False

        if frame.shape[0] < 10 or frame.shape[1] < 10:
            return False

        # Verifica a variância do frame para detectar frames muito uniformes (possivelmente inválidos)
        variance = np.var(frame)
        if variance < self.config.FRAME_VARIANCE_THRESHOLD:
            return False

        return True

    def _capture_loop(self):
        max_discard_frames = self.config.CAMERA_MAX_DISCARD_FRAMES
        while self.running:
            with self.connection_lock:
                if not self.is_connected or self.cap is None:
                    cap = None
                else:
                    cap = self.cap

            if cap is None:
                self.logger.debug("Capture thread: camera not connected, sleeping.")
                time.sleep(0.1)
                continue

            ret, frame = cap.read()

            discard_count = 0
            while discard_count < max_discard_frames:
                ret2, frame2 = cap.read()
                if not ret2:
                    break
                frame = frame2
                discard_count += 1

            if not ret or not self._is_frame_valid(frame):
                self.consecutive_failures += 1
                self.logger.warning(f"Falha ao capturar frame válido. Falhas consecutivas: {self.consecutive_failures}")

                if self.consecutive_failures >= self.config.MAX_CONSECUTIVE_FAILURES:
                    self.logger.warning("Número máximo de falhas consecutivas atingido. Reiniciando conexão da câmera.")
                    self._initialize_camera_async()
                    self.consecutive_failures = 0
                time.sleep(0.1)
                continue

            self.consecutive_failures = 0

            with self.frame_lock:
                self.latest_frame = frame

            time.sleep(0.03)  # Ajuste do sleep para balancear uso de CPU e delay
        self.logger.info("Capture thread stopped.")
    def release(self):
        self.logger.info("Releasing camera manager resources.")
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=5)
            if self.capture_thread.is_alive():
                self.logger.warning("Capture thread did not stop after join timeout.")
        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_connected = False
    def release(self):
        self.logger.info("Releasing camera manager resources.")
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=5)
            if self.capture_thread.is_alive():
                self.logger.warning("Capture thread did not stop after join timeout.")

        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_connected = False

    def get_frame(self):
        with self.frame_lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()

    def is_camera_connected(self):
        with self.connection_lock:
            return self.is_connected

    def get_connection_status(self):
        with self.connection_lock:
            return {
                "is_connected": self.is_connected,
                "last_error": self.last_error
            }

    def reconnect(self):
        self.logger.info("Reiniciando conexão da câmera manualmente.")
        self._initialize_camera_async()

    def release(self):
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=2)

        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_connected = False

    def __del__(self):
        self.release()

