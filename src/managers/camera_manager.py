import cv2
import time
import logging
from threading import Lock

from config.config import Config

class CameraManager:
    def __init__(self, config: Config):
        self.config = config
        self.rtsp_url = config.RTSP_URL
        self.camera_width = config.CAMERA_WIDTH
        self.camera_height = config.CAMERA_HEIGHT
        self.buffer_size = config.CAMERA_BUFFER_SIZE
        self.connection_timeout = 10
        self.max_retries = 3
        self.retry_delay = 5
        self.cap = None
        self.is_connected = False
        self.connection_lock = Lock()
        self.logger = logging.getLogger(__name__)
        self.last_error = None
        self._frame_count = 0
        self._consecutive_failures = 0

        # Tentar inicializar a câmera
        self._initialize_camera()

    def _initialize_camera(self):
        with self.connection_lock:
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Tentativa {attempt + 1}/{self.max_retries} de conexão com a câmera: {self.rtsp_url}")

                    if self.cap is not None:
                        self.cap.release()

                    self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

                    self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.connection_timeout * 1000)
                    self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)

                    ret, test_frame = self.cap.read()
                    if not ret or test_frame is None:
                        raise ConnectionError("Falha ao capturar frame de teste")

                    self.is_connected = True
                    self.last_error = None
                    self.logger.info("Conexão com a câmera estabelecida com sucesso")
                    return True
                except Exception as e:
                    self.last_error = str(e)
                    self.is_connected = False
                    self.logger.error(f"Erro na tentativa {attempt + 1}: {e}")

                    if self.cap is not None:
                        self.cap.release()
                        self.cap = None

                    if attempt < self.max_retries - 1:
                        self.logger.info(f"Aguardando {self.retry_delay} segundos antes da próxima tentativa...")
                        time.sleep(self.retry_delay)

            self.logger.error(f"Falha ao conectar com a câmera após {self.max_retries} tentativas")
            return False

    def get_frame(self):
        if not self.is_connected or self.cap is None:
            self.logger.warning("Câmera não conectada. Tentando reconectar...")
            if not self._initialize_camera():
                return None

        max_consecutive_failures = 5

        self._frame_count += 1
        if self.config.ENABLE_CAMERA_RESET and self._frame_count >= self.config.CAMERA_RESET_FRAME_COUNT:
            self.logger.info("Reinicializando conexão da câmera para limpar buffer interno")
            self._initialize_camera()
            self._frame_count = 0

        try:
            ret, frame = self.cap.read()

            if not ret or frame is None or frame.size == 0:
                self.logger.warning("Falha ao capturar frame válido. Verificando conexão...")
                self.is_connected = False
                self._consecutive_failures += 1

                if self._consecutive_failures >= max_consecutive_failures:
                    self.logger.info("Muitas falhas consecutivas. Tentando reconectar a câmera...")
                    if not self._initialize_camera():
                        return None
                    self._consecutive_failures = 0
                else:
                    if self._initialize_camera():
                        ret, frame = self.cap.read()
                        if ret and frame is not None and frame.size > 0:
                            self._consecutive_failures = 0
                            return frame
                        else:
                            return None
                    else:
                        return None

            self._consecutive_failures = 0
            return frame

        except Exception as e:
            self.logger.error(f"Erro ao capturar frame: {e}")
            self.is_connected = False
            self.last_error = str(e)
            return None

    def is_camera_connected(self):
        return self.is_connected and self.cap is not None and self.cap.isOpened()

    def get_connection_status(self):
        return {
            'connected': self.is_connected,
            'camera_opened': self.cap is not None and self.cap.isOpened() if self.cap else False,
            'last_error': self.last_error,
            'rtsp_url': self.rtsp_url
        }

    def reconnect(self):
        self.logger.info("Forçando reconexão com a câmera...")
        self.is_connected = False
        return self._initialize_camera()

    def release(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                self.logger.error(f"Erro ao liberar câmera: {e}")
            finally:
                self.cap = None
        self.is_connected = False

    def __del__(self):
        try:
            if hasattr(self, 'connection_lock') and self.connection_lock:
                with self.connection_lock:
                    self.release()
            else:
                self.release()
        except Exception:
            pass