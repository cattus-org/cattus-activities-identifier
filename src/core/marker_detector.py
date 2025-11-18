import cv2
import numpy as np
import time
import logging

class MarkerDetector:
    """Classe responsável pela detecção de marcadores ArUco"""

    def __init__(self, config):
        self.config = config
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        self.logger = logging.getLogger(__name__)

        # Cache para armazenar gatos detectados dinamicamente
        self.detected_cats = {}
        # Registro do tempo da última detecção de cada gato
        self.cat_last_seen = {}

        # Cache de posição do pote de ração
        self.bowl_position_cache = {
            "position": None,
            "last_detected": None,
            "last_updated": None,
            "detection_count": 0,
            "is_reliable": False
        }
    
    def estimate_pose(self, corners, marker_size):
        """Estima a pose do marcador no espaço 3D"""
        # Define objeto em 3D (cantos do quadrado)
        obj_pts = np.array([
            [-marker_size/2, marker_size/2, 0],
            [marker_size/2, marker_size/2, 0],
            [marker_size/2, -marker_size/2, 0],
            [-marker_size/2, -marker_size/2, 0]
        ], dtype=np.float32)
        
        img_pts = corners.reshape(4, 2).astype(np.float32)
        success, rvec, tvec = cv2.solvePnP(
            obj_pts, img_pts, 
            self.config.camera_matrix, 
            self.config.dist_coeffs
        )
        return (rvec, tvec) if success else (None, None)
    
    def _get_marker_info(self, marker_id):
        """Retorna informações do marcador baseado no ID"""
        if marker_id == self.config.POTE_RACAO_ID:
            return self.config.POTE_RACAO
        else:
            # Todos os outros IDs são considerados gatos
            current_time = time.time()

            if marker_id not in self.detected_cats:
                self.detected_cats[marker_id] = {
                    "tipo": "gato",
                    "size": self.config.DEFAULT_MARKER_SIZE
                }
                print(f"[INFO] Novo gato detectado: ID {marker_id}")

            # Atualiza o tempo da última detecção
            self.cat_last_seen[marker_id] = current_time

            return self.detected_cats[marker_id]

    def _update_bowl_cache(self, position):
        """Atualiza o cache de posição do pote"""
        current_time = time.time()

        # Incrementa contador de detecções
        self.bowl_position_cache["detection_count"] += 1

        # Para evitar overflow e impacto no desempenho, resetamos o contador
        # quando ele atinge um valor muito alto, mas mantemos o status de confiável
        MAX_DETECTION_COUNT = 100000  # 100 mil detecções é mais do que suficiente
        if self.bowl_position_cache["detection_count"] >= MAX_DETECTION_COUNT:
            # Resetamos o contador mas mantemos o status de confiável
            self.bowl_position_cache["detection_count"] = MAX_DETECTION_COUNT // 2
            self.logger.debug(f"Contador de detecções resetado para evitar overflow: {self.bowl_position_cache['detection_count']}")

        self.bowl_position_cache["last_detected"] = current_time

        # Verifica se deve atualizar a posição em cache
        should_update = (
            self.bowl_position_cache["position"] is None or
            self.bowl_position_cache["last_updated"] is None or
            (current_time - self.bowl_position_cache["last_updated"]) >= self.config.BOWL_CACHE_UPDATE_INTERVAL
        )

        if should_update:
            self.bowl_position_cache["position"] = position.copy()
            self.bowl_position_cache["last_updated"] = current_time

            # Marca como confiável se tiver detecções suficientes
            if self.bowl_position_cache["detection_count"] >= self.config.BOWL_CACHE_CONFIDENCE_THRESHOLD:
                if not self.bowl_position_cache["is_reliable"]:
                    self.bowl_position_cache["is_reliable"] = True
                    self.logger.info(f"Cache de posição do pote agora é confiável (detecções: {self.bowl_position_cache['detection_count']})")

            self.logger.debug(f"Cache de posição do pote atualizado: {position}")

    def _get_cached_bowl_position(self):
        """Retorna a posição em cache do pote se disponível e válida"""
        if not self.config.BOWL_CACHE_ENABLED:
            return None

        cache = self.bowl_position_cache

        # Verifica se há posição em cache
        if cache["position"] is None or not cache["is_reliable"]:
            return None

        # Verifica se o cache não está muito antigo
        current_time = time.time()
        if cache["last_detected"] is None:
            return None

        age = current_time - cache["last_detected"]
        if age > self.config.BOWL_CACHE_MAX_AGE:
            self.logger.warning(f"Cache de posição do pote expirado (idade: {age:.1f}s)")
            return None

        return cache["position"]

    def get_bowl_cache_info(self):
        """Retorna informações sobre o estado do cache do pote"""
        cache = self.bowl_position_cache
        current_time = time.time()

        info = {
            "has_position": cache["position"] is not None,
            "is_reliable": cache["is_reliable"],
            "detection_count": cache["detection_count"],
            "age_seconds": current_time - cache["last_detected"] if cache["last_detected"] else None,
            "last_updated_seconds": current_time - cache["last_updated"] if cache["last_updated"] else None
        }

        return info
    
    def detect_markers(self, frame):
        """Detecta marcadores no frame e retorna suas posições"""
        # Se a flag de debug estiver ativada, desenha marcador ArUco ID 0 um pouco afastado do canto superior esquerdo
        if getattr(self.config, 'DEBUG_SHOW_TEST_MARKER', False):
            marker_id = 0
            marker_size_px = 100  # Tamanho do marcador em pixels
            offset_x, offset_y = 30, 30  # Distância do canto superior esquerdo
            marker_img = cv2.aruco.generateImageMarker(self.aruco_dict, marker_id, marker_size_px)
            marker_img_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
            # Insere o marcador com offset
            frame[offset_y:offset_y+marker_size_px, offset_x:offset_x+marker_size_px] = marker_img_bgr

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        posicoes = {}
        bowl_detected = False

        if ids is not None:
            # Desenha marcadores detectados se habilitado
            if self.config.SHOW_MARKER_VISUALIZATION:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for i, marker_id in enumerate(ids.flatten()):
                # Converte marker_id para int Python nativo para evitar problemas de serialização
                marker_id = int(marker_id)

                # Obtém informações do marcador (pote ou gato)
                info = self._get_marker_info(marker_id)
                rvec, tvec = self.estimate_pose(corners[i], info["size"])

                if tvec is None:
                    continue

                # Desenha eixos do marcador se habilitado
                if self.config.SHOW_MARKER_VISUALIZATION:
                    cv2.drawFrameAxes(
                        frame,
                        self.config.camera_matrix,
                        self.config.dist_coeffs,
                        rvec, tvec, 0.03
                    )

                    # Adiciona label com ID do marcador
                    center = np.mean(corners[i][0], axis=0).astype(int)
                    cv2.putText(
                        frame, f"ID:{marker_id}",
                        (center[0] - 20, center[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2
                    )

                # Usa o ID do marcador como chave em vez do nome
                if info["tipo"] == "gato":
                    key = marker_id  # Para gatos, usa o ID diretamente
                else:
                    key = info["nome"]  # Para o pote, mantém o nome
                    bowl_detected = True
                    # Atualiza cache de posição do pote
                    self._update_bowl_cache(tvec.flatten())

                posicoes[key] = {
                    "tipo": info["tipo"],
                    "pos": tvec.flatten(),
                    "id": marker_id
                }

        # Se o pote não foi detectado, tenta usar posição em cache
        if not bowl_detected and self.config.BOWL_CACHE_ENABLED:
            cached_position = self._get_cached_bowl_position()
            if cached_position is not None:
                bowl_name = self.config.POTE_RACAO["nome"]
                posicoes[bowl_name] = {
                    "tipo": "pote",
                    "pos": cached_position,
                    "id": self.config.POTE_RACAO_ID,
                    "from_cache": True  # Indica que veio do cache
                }

                # Desenha indicador visual de que está usando cache
                self._draw_cached_bowl_indicator(frame, cached_position)

                cache_info = self.get_bowl_cache_info()
                self.logger.debug(f"Usando posição em cache do pote (idade: {cache_info['age_seconds']:.1f}s)")

        return posicoes

    def _draw_cached_bowl_indicator(self, frame, position):
        """Desenha um indicador visual quando está usando posição em cache do pote"""
        # Projeta a posição 3D para 2D na tela
        try:
            # Usa uma posição aproximada na tela baseada na posição 3D
            # Como não temos os corners originais, fazemos uma projeção simples
            img_points, _ = cv2.projectPoints(
                np.array([[0, 0, 0]], dtype=np.float32),
                np.array([[0, 0, 0]], dtype=np.float32),  # rvec zero
                position.reshape(3, 1),  # tvec
                self.config.camera_matrix,
                self.config.dist_coeffs
            )

            center = tuple(img_points[0][0].astype(int))

            # Desenha círculo pontilhado para indicar posição em cache
            cv2.circle(frame, center, 30, (0, 255, 255), 2)  # Amarelo
            cv2.circle(frame, center, 35, (0, 255, 255), 1)  # Amarelo

            # Adiciona texto indicando cache
            cv2.putText(
                frame, "CACHE",
                (center[0] - 25, center[1] + 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2
            )

        except Exception as e:
            self.logger.debug(f"Erro ao desenhar indicador de cache: {e}")

    def get_detected_cats(self):
        """Retorna lista de gatos detectados dinamicamente"""
        return self.detected_cats.copy()

    def cleanup_inactive_cats(self):
        """Remove gatos que não são mais detectados há muito tempo"""
        if not hasattr(self.config, 'CAT_INACTIVITY_TIMEOUT'):
            # Se não houver configuração de timeout, usa um valor padrão
            CAT_INACTIVITY_TIMEOUT = 300  # 5 minutos
        else:
            CAT_INACTIVITY_TIMEOUT = self.config.CAT_INACTIVITY_TIMEOUT

        current_time = time.time()
        inactive_cats = []

        # Identifica gatos inativos
        for cat_id, last_seen_time in list(self.cat_last_seen.items()):
            if current_time - last_seen_time > CAT_INACTIVITY_TIMEOUT:
                inactive_cats.append(cat_id)

        # Remove gatos inativos
        for cat_id in inactive_cats:
            self.detected_cats.pop(cat_id, None)
            self.cat_last_seen.pop(cat_id, None)

        return len(inactive_cats)

    def reset_bowl_cache(self):
        """Reseta o cache de posição do pote"""
        self.bowl_position_cache = {
            "position": None,
            "last_detected": None,
            "last_updated": None,
            "detection_count": 0,
            "is_reliable": False
        }
        self.logger.info("Cache de posição do pote resetado")