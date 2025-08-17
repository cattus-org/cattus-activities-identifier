import cv2

class CameraManager:
    """Classe responsável pelo gerenciamento da câmera"""
    
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Inicializa a conexão com a câmera"""
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    def get_frame(self):
        """Captura e retorna um frame da câmera"""
        if self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def release(self):
        """Libera os recursos da câmera"""
        if self.cap is not None:
            self.cap.release()