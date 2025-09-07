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
    logger.info("Iniciando sistema...")

    config = None
    try:
        from config.config import Config
        config = Config()
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return

    camera_manager = CameraManager(config)
    marker_detector = MarkerDetector(config)
    activity_tracker = ActivityTracker(config)
    display_manager = DisplayManager(config)
    api_client = APIClient(config.API_BASE_URL, config.API_KEY, config.API_TIMEOUT)
    activity_notifier = ActivityNotifier(api_client, config)

    activity_tracker.set_activity_notifier(activity_notifier)

    try:
        logger.info("Sistema iniciado com sucesso")

        while True:
            frame = camera_manager.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            markers = marker_detector.detect_markers(frame)
            activity_tracker.update(markers)
            activity_tracker.cleanup_inactive_cats(list(markers.keys()))

            display_manager.draw_info(frame, markers, activity_tracker.estado, marker_detector)
            display_manager.setup_window()

            if display_manager.show_frame(frame):
                break

            time.sleep(0.01)

    except KeyboardInterrupt:
        logger.info("Interrupção pelo usuário. Finalizando sistema...")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    finally:
        camera_manager.release()
        display_manager.cleanup()
        activity_notifier.cleanup_all_activities()
        logger.info("Sistema finalizado")


if __name__ == "__main__":
    main()