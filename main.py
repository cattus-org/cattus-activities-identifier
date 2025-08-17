from config import Config
from marker_detector import MarkerDetector
from activity_tracker import ActivityTracker
from camera_manager import CameraManager
from display_manager import DisplayManager

def main():
    """Função principal do programa"""
    # Inicializa componentes
    config = Config()
    camera_manager = CameraManager(config.RTSP_URL)
    marker_detector = MarkerDetector(config)
    activity_tracker = ActivityTracker(config)
    display_manager = DisplayManager(config)
    
    # Configura a janela de exibição
    display_manager.setup_window()
    
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
            active_cats = [nome for nome, dados in posicoes.items() if dados["tipo"] == "gato"]
            activity_tracker.cleanup_inactive_cats(active_cats)
            
            # Desenha informações na tela
            display_manager.draw_info(frame, posicoes, activity_tracker.get_estado())
            
            # Exibe frame e verifica se deve sair
            if display_manager.show_frame(frame):
                break
                
    finally:
        camera_manager.release()
        display_manager.cleanup()

if __name__ == "__main__":
    main()