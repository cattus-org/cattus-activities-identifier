import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Classe para centralizar todas as configurações do sistema"""

    def __init__(self):
        # Configurações da API
        self.API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")  # Ajuste para sua URL
        self.API_KEY = os.getenv("API_KEY")  # Token de autenticação (fallback para valor padrão)
        self.API_TIMEOUT = 10  # Timeout em segundos
        self.API_ENABLED = True  # Flag para habilitar/desabilitar envio para API

        # Mapeamento de tipos de atividade (opcional)
        self.ACTIVITY_TYPE_MAPPING = {
            "eating": "eat",
            "drinking": "drink",
            "sleeping": "sleep",
            "playing": "play",
            # Adicione mais mapeamentos conforme necessário
        }
        
        # Configurações da janela de visualização
        self.WINDOW_WIDTH = 960
        self.WINDOW_HEIGHT = 540
        self.WINDOW_NAME = "Deteccao Gato/Pote"
        
        # URL da câmera RTSP
        self.RTSP_URL = "rtsp://admin:cattuscamera2025@192.168.1.72:554/onvif1"
        
        # Configurações da câmera
        self.CAMERA_WIDTH = 1920
        self.CAMERA_HEIGHT = 1080
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