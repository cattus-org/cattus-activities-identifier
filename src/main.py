import sys
import os
# Adiciona o diretório raiz do projeto ao path para permitir importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from src.core.marker_detector import MarkerDetector
from src.tracking.activity_tracker import ActivityTracker
from src.managers.camera_manager import CameraManager
from src.managers.display_manager import DisplayManager
from src.api.api_client import APIClient
from src.tracking.activity_notifier import ActivityNotifier
import logging

def setup_logging():
    """Configura o sistema de logging"""
    # Verifica se o logging já foi configurado para evitar duplicação
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cattus_activities.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Função principal do programa"""
    # Configura logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Inicializa componentes
    config = Config()
    camera_manager = CameraManager(
        rtsp_url=config.RTSP_URL,
        camera_width=config.CAMERA_WIDTH,
        camera_height=config.CAMERA_HEIGHT,
        buffer_size=config.CAMERA_BUFFER_SIZE
    )
    marker_detector = MarkerDetector(config)
    activity_tracker = ActivityTracker(config)
    display_manager = DisplayManager(config)
    
    # Inicializa cliente da API e notificador
    api_client = APIClient(config.API_BASE_URL, config.API_KEY, config.API_TIMEOUT)
    activity_notifier = ActivityNotifier(
        api_client, 
        config.ACTIVITY_TYPE_MAPPING, 
        config.API_ENABLED
    )
    
    # Conecta o notificador ao activity_tracker
    activity_tracker.set_activity_notifier(activity_notifier)
    
    # Configura a janela de exibição
    display_manager.setup_window()
    
    logger.info("Sistema iniciado com sucesso")
    
    try:
        while True:
            # Captura frame da câmera
            frame = camera_manager.get_frame()
            if frame is None:
                break
            
            # Detecta marcadores ArUco
            posicoes = marker_detector.detect_markers(frame)
            
            # Atualiza rastreamento de atividades
            activity_tracker.update(posicoes)
            
            # Remove gatos inativos do rastreamento
            active_cats = [identificador for identificador, dados in posicoes.items() if dados["tipo"] == "gato"]
            activity_tracker.cleanup_inactive_cats(active_cats)
            
            # Desenha informações na tela
            display_manager.draw_info(frame, posicoes, activity_tracker.get_estado())
            
            # Exibe frame e verifica se deve sair
            if display_manager.show_frame(frame):
                break
    
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
    finally:
        logger.info("Finalizando sistema...")
        
        # Finaliza todas as atividades ativas antes de sair
        if 'activity_notifier' in locals():
            activity_notifier.cleanup_all_activities()
        
        camera_manager.release()
        display_manager.cleanup()

if __name__ == "__main__":
    main()