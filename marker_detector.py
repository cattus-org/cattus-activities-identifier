import cv2
import numpy as np

class MarkerDetector:
    """Classe responsável pela detecção de marcadores ArUco"""
    
    def __init__(self, config):
        self.config = config
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # Cache para armazenar gatos detectados dinamicamente
        self.detected_cats = {}
    
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
            if marker_id not in self.detected_cats:
                self.detected_cats[marker_id] = {
                    "tipo": "gato",
                    "nome": f"Gato_{marker_id}",
                    "size": self.config.DEFAULT_MARKER_SIZE
                }
                print(f"[INFO] Novo gato detectado: Gato_{marker_id} (ID: {marker_id})")
            
            return self.detected_cats[marker_id]
    
    def detect_markers(self, frame):
        """Detecta marcadores no frame e retorna suas posições"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        posicoes = {}
        
        if ids is not None:
            # Desenha marcadores detectados
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            for i, marker_id in enumerate(ids.flatten()):
                # Obtém informações do marcador (pote ou gato)
                info = self._get_marker_info(marker_id)
                rvec, tvec = self.estimate_pose(corners[i], info["size"])
                
                if tvec is None:
                    continue
                
                # Desenha eixos do marcador
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
                
                posicoes[info["nome"]] = {
                    "tipo": info["tipo"], 
                    "pos": tvec.flatten(),
                    "id": marker_id
                }
        
        return posicoes
    
    def get_detected_cats(self):
        """Retorna lista de gatos detectados dinamicamente"""
        return self.detected_cats.copy()