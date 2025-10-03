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
        self.API_ENABLED = False  # Flag para habilitar/desabilitar envio para API

        # Configurações do Streaming via FastAPI
        self.STREAMING_ENABLED = True
        self.STREAMING_PORT = 8000
        self.STREAMING_HOST = "0.0.0.0"

        # Mapeamento de tipos de atividade (opcional)
        self.DISPLAY_INFO_ENABLED = True
        self.ACTIVITY_TYPE_MAPPING = {
            "eating": "eat",
            "drinking": "drink",
            "sleeping": "sleep",
            "playing": "play",
            # Adicione mais mapeamentos conforme necessário
        }

        # Configurações da janela de visualização
        self.DISPLAY_ENABLED = False
        self.WINDOW_WIDTH = 960
        self.WINDOW_HEIGHT = 540
        self.WINDOW_NAME = "Deteccao Gato/Pote"

        # URL da câmera RTSP
        self.RTSP_URL = os.getenv("CAMERA_URL")
        
        # Configurações da câmera
        self.CAMERA_WIDTH = 1920
        self.CAMERA_HEIGHT = 1080
        self.CAMERA_BUFFER_SIZE = 1
        self.CAMERA_MAX_DISCARD_FRAMES = 3  # Maximum number of frames to discard in capture loop

        # Quantidade de frames capturados para resetar a conexão da câmera
        self.CAMERA_RESET_FRAME_COUNT = 300

        # Flag para habilitar/desabilitar o reset da conexão da câmera após certo número de frames
        self.ENABLE_CAMERA_RESET = False

        # ID do pote de ração (será excluído da detecção automática)
        self.POTE_RACAO_ID = 0

        # Configuração do pote de ração
        self.POTE_RACAO = {
            "tipo": "pote",
            "nome": "Pote Racao",
            "size": 0.02
        }

        # Tamanho padrão para marcadores de gatos detectados automaticamente
        self.DEFAULT_MARKER_SIZE = 0.02

        # Configurações do cache de posição do pote
        self.BOWL_CACHE_ENABLED = True  # Habilita o cache de posição do pote
        self.BOWL_CACHE_UPDATE_INTERVAL = 10.0  # Intervalo em segundos para atualizar a posição em cache
        self.BOWL_CACHE_MAX_AGE = 300.0  # Tempo máximo em segundos para usar posição em cache
        self.BOWL_CACHE_CONFIDENCE_THRESHOLD = 5  # Número mínimo de detecções para considerar posição confiável

        # Thresholds para detecção de atividade
        self.ENTER_THRESH = 0.45
        self.EXIT_THRESH = 0.50
        self.MIN_TIME_START = 4.0
        self.MIN_TIME_STOP = 3.0
        self.WINDOW_SIZE = 8

        # Tempo em segundos para manter memória de gato inativo
        self.CAT_INACTIVITY_TIMEOUT = 5
        self.MIN_ACTIVITY_DURATION_TO_REGISTER = 5  # Duração mínima da atividade para registrar no banco

        self.FRAME_VARIANCE_THRESHOLD = 5
        self.MAX_CONSECUTIVE_FAILURES = 3

        # Matriz da câmera e coeficientes de distorção
        self.camera_matrix = np.array([
            [1000, 0, 640],
            [0, 1000, 360],
            [0, 0, 1]
        ], dtype=np.float32)

        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)