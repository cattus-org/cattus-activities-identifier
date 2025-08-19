import cv2
import time
import logging
from threading import Lock

class CameraManager:
    """Classe responsável pelo gerenciamento da câmera com tratativa de erros"""
    
    def __init__(self, rtsp_url, camera_width=1280, camera_height=720, buffer_size=1, max_retries=3, retry_delay=2, connection_timeout=10):
        self.rtsp_url = rtsp_url
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.buffer_size = buffer_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        self.cap = None
        self.is_connected = False
        self.last_error = None
        self.connection_lock = Lock()

        # Configurar logging - apenas obter o logger, sem adicionar handlers
        self.logger = logging.getLogger(__name__)

        # Tentar inicializar a câmera
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Inicializa a conexão com a câmera com tratativa de erros"""
        with self.connection_lock:
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Tentativa {attempt + 1}/{self.max_retries} de conexão com a câmera: {self.rtsp_url}")
                    
                    # Liberar conexão anterior se existir
                    if self.cap is not None:
                        self.cap.release()
                    
                    # Criar nova conexão
                    self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                    
                    # Configurar timeout
                    self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.connection_timeout * 1000)
                    self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)  # 5 segundos para leitura
                    
                    # Verificar se a conexão foi estabelecida
                    if not self.cap.isOpened():
                        raise ConnectionError("Falha ao abrir a conexão com a câmera")
                    
                    # Configurar propriedades da câmera
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
                    
                    # Testar captura de um frame para verificar se a conexão está funcionando
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
        """Captura e retorna um frame da câmera com tratativa de erros"""
        if not self.is_connected or self.cap is None:
            self.logger.warning("Câmera não conectada. Tentando reconectar...")
            if not self._initialize_camera():
                return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                self.logger.warning("Falha ao capturar frame. Verificando conexão...")
                self.is_connected = False
                
                # Tentar reconectar
                if self._initialize_camera():
                    ret, frame = self.cap.read()
                    return frame if ret else None
                else:
                    return None
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Erro ao capturar frame: {e}")
            self.is_connected = False
            self.last_error = str(e)
            return None
    
    def is_camera_connected(self):
        """Verifica se a câmera está conectada"""
        return self.is_connected and self.cap is not None and self.cap.isOpened()
    
    def get_connection_status(self):
        """Retorna informações sobre o status da conexão"""
        return {
            'connected': self.is_connected,
            'camera_opened': self.cap is not None and self.cap.isOpened() if self.cap else False,
            'last_error': self.last_error,
            'rtsp_url': self.rtsp_url
        }
    
    def reconnect(self):
        """Força uma tentativa de reconexão"""
        self.logger.info("Forçando reconexão com a câmera...")
        self.is_connected = False
        return self._initialize_camera()
    
    def release(self):
        """Libera os recursos da câmera"""
        with self.connection_lock:
            self.logger.info("Liberando recursos da câmera...")
            self.is_connected = False
            
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception as e:
                    self.logger.error(f"Erro ao liberar câmera: {e}")
                finally:
                    self.cap = None
    
    def __del__(self):
        """Destrutor para garantir que os recursos sejam liberados"""
        self.release()