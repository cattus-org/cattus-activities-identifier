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

    def get_frame(self):
        with self.connection_lock:
            if not self.is_connected or self.cap is None:
                self.logger.warning("Câmera não conectada. Tentando reconectar...")
                self._initialize_camera_async()
                # Evita loop rápido que consome CPU
                time.sleep(0.5)
                return None

            ret, frame = self.cap.read()

            if not ret or not self._is_frame_valid(frame):
                self.consecutive_failures += 1
                self.logger.warning(f"Falha ao capturar frame válido. Falhas consecutivas: {self.consecutive_failures}")

                if self.consecutive_failures >= self.config.MAX_CONSECUTIVE_FAILURES:
                    self.logger.warning("Número máximo de falhas consecutivas atingido. Reiniciando conexão da câmera.")
                    self._initialize_camera_async()
                    self.consecutive_failures = 0

                # Evita loop rápido que consome CPU
                time.sleep(0.5)
                return None

            self.consecutive_failures = 0
            return frame

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
        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_connected = False

    def __del__(self):
        self.release()

