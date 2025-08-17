import numpy as np

class Config:
    """Classe para centralizar todas as configurações do sistema"""
    
    def __init__(self):
        # Configurações da janela de visualização
        self.WINDOW_WIDTH = 960
        self.WINDOW_HEIGHT = 540
        self.WINDOW_NAME = "Deteccao Gato/Pote"
        
        # URL da câmera RTSP
        self.RTSP_URL = "rtsp://admin:cattuscamera2025@192.168.1.72:554/onvif1"
        
        # Configurações da câmera
        self.CAMERA_WIDTH = 1280
        self.CAMERA_HEIGHT = 720
        self.CAMERA_BUFFER_SIZE = 1
        
        # ID do pote de ração (será excluído da detecção automática)
        self.POTE_RACAO_ID = 10
        
        # Configuração do pote de ração
        self.POTE_RACAO = {
            "tipo": "pote", 
            "nome": "Pote Racao", 
            "size": 0.02
        }
        
        # Tamanho padrão para marcadores de gatos detectados automaticamente
        self.DEFAULT_MARKER_SIZE = 0.02
        
        # Thresholds para detecção de atividade
        self.ENTER_THRESH = 0.10
        self.EXIT_THRESH = 0.20
        self.MIN_TIME_START = 2.0
        self.MIN_TIME_STOP = 2.0
        self.WINDOW_SIZE = 5
        
        # Matriz da câmera e coeficientes de distorção
        self.camera_matrix = np.array([
            [1000, 0, 640],
            [0, 1000, 360],
            [0, 0, 1]
        ], dtype=np.float32)
        
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)