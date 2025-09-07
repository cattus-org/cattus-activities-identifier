import cv2
import time
import logging
import threading
import numpy as np

class CameraManager:
    def __init__(self, config):
        self.config = config
        self.rtsp_url = config.RTSP_URL
        self.camera_width = config.CAMERA_WIDTH
        self.camera_height = config.CAMERA_HEIGHT
        self.buffer_size = config.CAMERA_BUFFER_SIZE

        self.cap = None
        self.is_connected = False
        self.connection_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.last_error = None

        self._frame_count = 0
        self._consecutive_failures = 0
        self._reconnecting = False
        self._last_reconnect_log_time = 0
        self._reconnect_log_interval = 10  # segundos

        self._initialize_camera_async()

    def _initialize_camera(self):
        self.logger.info("Iniciando conexão com a câmera...")
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                self.logger.info(f"Tentativa {attempts + 1} de {max_attempts} para abrir a câmera.")

                # Libera a câmera anterior se existir
                with self.connection_lock:
                    if self.cap is not None:
                        self.logger.info("Liberando conexão anterior da câmera...")
                        self.cap.release()
                        self.cap = None

                cap = cv2.VideoCapture(self.rtsp_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)

                # Aguarda um pouco para a câmera estabilizar
                time.sleep(2)

                if cap.isOpened():
                    self.logger.info("Conexão com a câmera estabelecida com sucesso.")
                    with self.connection_lock:
                        self.cap = cap
                        self.is_connected = True
                    return
                else:
                    self.logger.warning(f"Falha ao abrir a câmera. Tentativa {attempts + 1} de {max_attempts}.")
                    cap.release()
            except Exception as e:
                self.logger.error(f"Erro ao conectar com a câmera: {e}")

            attempts += 1
            time.sleep(3)

        self.logger.error("Não foi possível conectar à câmera após várias tentativas.")
        with self.connection_lock:
            self.is_connected = False

    def _initialize_camera_async(self):
        def target():
            self._reconnecting = True
            try:
                self._initialize_camera()
            finally:
                self._reconnecting = False

        if not self._reconnecting:
            threading.Thread(target=target, daemon=True).start()
        else:
            now = time.time()
            if now - self._last_reconnect_log_time > self._reconnect_log_interval:
                self.logger.info("Reconexão já em andamento, ignorando nova solicitação.")
                self._last_reconnect_log_time = now

    def _is_frame_valid(self, frame):
        if frame is None:
            self.logger.debug("Frame é None.")
            return False

        if frame.shape[0] != self.camera_height or frame.shape[1] != self.camera_width:
            self.logger.debug(f"Tamanho do frame diferente do esperado. Esperado ({self.camera_height}, {self.camera_width}), obtido {frame.shape[:2]}")
            return False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        if variance < self.config.FRAME_VARIANCE_THRESHOLD:
            self.logger.debug(f"Variância do frame muito baixa: {variance}")
            return False

        return True

    def get_frame(self):
        with self.connection_lock:
            if not self.is_connected or self.cap is None:
                now = time.time()
                if now - self._last_reconnect_log_time > self._reconnect_log_interval:
                    self.logger.warning("Câmera não conectada. Tentando reconectar...")
                    self._last_reconnect_log_time = now
                self._initialize_camera_async()
                return None

            ret, frame = self.cap.read()

            if not ret or frame is None or not self._is_frame_valid(frame):
                self._consecutive_failures += 1
                self.logger.warning(f"Falha ao capturar frame válido. Falhas consecutivas: {self._consecutive_failures}")
                if self._consecutive_failures >= 5:
                    self.logger.warning("Muitas falhas consecutivas na captura de frames. Reconectando a câmera...")
                    self._consecutive_failures = 0
                    self._initialize_camera_async()
                return None

            self._consecutive_failures = 0

            self._frame_count += 1
            if self.config.ENABLE_CAMERA_RESET and self._frame_count >= self.config.CAMERA_RESET_FRAME_COUNT:
                self.logger.info("Reiniciando conexão da câmera após atingir limite de frames.")
                self._frame_count = 0
                self.logger.info("Forçando reconexão com a câmera...")
                self._initialize_camera_async()

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
        self.logger.info("Forçando reconexão com a câmera...")
        self._initialize_camera_async()

    def release(self):
        with self.connection_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_connected = False

    def __del__(self):
        self.release()

