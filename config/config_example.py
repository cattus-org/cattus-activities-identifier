# Arquivo de exemplo de configuração
# Copie este arquivo para config.py e ajuste as configurações conforme necessário

# Configurações da câmera
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# Configurações dos marcadores ArUco
MARKER_SIZE = 0.05  # Tamanho do marcador em metros
ARUCO_DICT = "DICT_6X6_250"

# Configurações de rastreamento
DISTANCE_THRESHOLD = 0.3  # Distância em metros para considerar proximidade
TIME_THRESHOLD = 3.0      # Tempo em segundos para confirmar atividade
CLEANUP_INTERVAL = 30.0   # Intervalo para limpeza de gatos inativos

# Configurações da API
API_BASE_URL = "https://api.exemplo.com"
API_TIMEOUT = 10
API_RETRY_ATTEMPTS = 3

# Configurações de display
SHOW_DEBUG_INFO = True
WINDOW_NAME = "Cat Activity Monitor"

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FILE = "cat_monitor.log"