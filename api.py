import cv2
import cv2.aruco as aruco
import numpy as np
import requests
import time
import math

# ID do pote (único fixo)
ID_POTE = 0

# Distância limite em cm
DISTANCIA_LIMITE_CM = 30

# URLs da API
API_START = "http://localhost:3000/api/activity/start"
API_END = "http://localhost:3000/api/activity/end"

# Dicionário para controlar estado de cada gato
gatos_estado = {}  # {cat_id: {'perto': bool, 'ultimo_tempo_perto': float}}
TEMPO_SAIDA = 3  # segundos sem detectar perto para considerar que saiu

# Carrega parâmetros da câmera
cap = cv2.VideoCapture(0)
# Matriz da câmera (precisa calibrar para precisão real)
camera_matrix = np.array([[800, 0, 320],
                          [0, 800, 240],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1))

# Dicionário ArUco
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

def calcular_distancia(tvec1, tvec2):
    return np.linalg.norm(tvec1 - tvec2) * 100  # metros → cm

def inicializar_gato(cat_id):
    """Inicializa o estado de um novo gato se não existir"""
    if cat_id not in gatos_estado:
        gatos_estado[cat_id] = {
            'perto': False,
            'ultimo_tempo_perto': 0
        }

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detecta marcadores
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejected = detector.detectMarkers(frame)

    tvecs_detectados = {}
    gatos_detectados = []

    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            # estimatePoseSingleMarkers is not available; use solvePnP instead
            obj_pts = np.array([
                [-0.05/2,  0.05/2, 0],
                [ 0.05/2,  0.05/2, 0],
                [ 0.05/2, -0.05/2, 0],
                [-0.05/2, -0.05/2, 0]
            ], dtype=np.float32)
            img_pts = corners[i].reshape(4, 2).astype(np.float32)
            success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, camera_matrix, dist_coeffs)
            if not success:
                continue
            tvec = tvec.reshape(1, 1, 3)
            rvec = rvec.reshape(1, 1, 3)
            aruco.drawDetectedMarkers(frame, corners)

            # Desenha o eixo no marcador
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)

            # Guarda posição
            tvecs_detectados[marker_id] = tvec[0][0]
            
            # Identifica gatos (qualquer ID diferente de 0)
            if marker_id != ID_POTE:
                gatos_detectados.append(marker_id)
                inicializar_gato(marker_id)

        # Verifica distância para cada gato detectado
        if ID_POTE in tvecs_detectados and gatos_detectados:
            for cat_id in gatos_detectados:
                distancia = calcular_distancia(tvecs_detectados[cat_id], tvecs_detectados[ID_POTE])
                
                # Mostra informações na tela
                y_offset = 30 + (list(gatos_detectados).index(cat_id) * 30)
                cv2.putText(frame, f"Gato {cat_id}: {distancia:.1f} cm", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if distancia <= DISTANCIA_LIMITE_CM:
                    gatos_estado[cat_id]['ultimo_tempo_perto'] = time.time()
                    if not gatos_estado[cat_id]['perto']:
                        gatos_estado[cat_id]['perto'] = True
                        print(f"Gato {cat_id} chegou no pote 🐱🍽️")
                        # requests.post(API_START, json={"catId": cat_id})
                else:
                    # Verifica se já ficou longe por mais de TEMPO_SAIDA
                    if (gatos_estado[cat_id]['perto'] and 
                        (time.time() - gatos_estado[cat_id]['ultimo_tempo_perto'] > TEMPO_SAIDA)):
                        gatos_estado[cat_id]['perto'] = False
                        print(f"Gato {cat_id} saiu do pote 🚶‍♂️")
                        # requests.post(API_END, json={"catId": cat_id})

        # Verifica gatos que saíram de cena (não foram detectados)
        gatos_em_cena = set(gatos_detectados)
        for cat_id in list(gatos_estado.keys()):
            if cat_id not in gatos_em_cena:
                # Gato não está mais visível
                if (gatos_estado[cat_id]['perto'] and 
                    (time.time() - gatos_estado[cat_id]['ultimo_tempo_perto'] > TEMPO_SAIDA)):
                    gatos_estado[cat_id]['perto'] = False
                    print(f"Gato {cat_id} saiu de cena 👻")
                    # requests.post(API_END, json={"catId": cat_id})

    cv2.imshow("Deteccao ArUco - Multi Gatos", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
        break

cap.release()
cv2.destroyAllWindows()