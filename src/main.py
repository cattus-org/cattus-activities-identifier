import logging
import time
from .managers.camera_manager import CameraManager
from .core.marker_detector import MarkerDetector
from .tracking.activity_tracker import ActivityTracker
from .managers.display_manager import DisplayManager
from .api.api_client import APIClient
from .tracking.activity_notifier import ActivityNotifier


# Configuração básica do logging para garantir que os logs apareçam
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    try:
        from config.config import Config
        config = Config()
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return

    camera_manager = None
    marker_detector = None
    activity_tracker = None
    display_manager = None
    api_client = None
    activity_notifier = None

    try:
        camera_manager = CameraManager(config)
        marker_detector = MarkerDetector(config)
        activity_tracker = ActivityTracker(config)
        display_manager = DisplayManager(config)
        api_client = APIClient(config.API_BASE_URL, config.API_KEY, config.API_TIMEOUT)
        activity_notifier = ActivityNotifier(api_client, config.ACTIVITY_TYPE_MAPPING, config.API_ENABLED)

        activity_tracker.set_activity_notifier(activity_notifier)

        logger.info("Sistema iniciado com sucesso")
        display_manager.setup_window()

        while True:
            frame = camera_manager.get_frame()

            if frame is None:
                # Frame inválido ou câmera desconectada, aguarda um pouco antes de tentar novamente
                time.sleep(0.1)
                continue

            markers = marker_detector.detect_markers(frame)
            activity_tracker.update(markers)
            activity_tracker.cleanup_inactive_cats(list(markers.keys()))

            # Limpa gatos inativos do detector também
            cleaned_count = marker_detector.cleanup_inactive_cats()
            if cleaned_count > 0:
                logger.debug(f"Limpados {cleaned_count} gatos inativos do detector")

            display_manager.draw_info(frame, markers, activity_tracker.estado, marker_detector)

            if display_manager.show_frame(frame):
                break

    except KeyboardInterrupt:
        logger.info("Interrupção pelo usuário. Finalizando sistema...")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    finally:
        logger.info("Iniciando processo de finalização do sistema...")

        # Finaliza todas as atividades ativas
        if activity_notifier:
            try:
                activity_notifier.cleanup_all_activities()
                logger.info("Atividades ativas finalizadas com sucesso")
            except Exception as e:
                logger.error(f"Erro ao finalizar atividades ativas: {e}")

        # Libera recursos da câmera
        if camera_manager:
            try:
                camera_manager.release()
                logger.info("Recursos da câmera liberados com sucesso")
            except Exception as e:
                logger.error(f"Erro ao liberar recursos da câmera: {e}")

        # Limpa interface
        if display_manager:
            try:
                display_manager.cleanup()
                logger.info("Interface limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar interface: {e}")

        logger.info("Sistema finalizado")


if __name__ == "__main__":
    main()