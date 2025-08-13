import cv2
import cv2.aruco as aruco
import numpy as np
import requests
import time
import math

# IDs dos marcadores
ID_GATO = 1
ID_POTE = 1000

# Distância limite em cm
DISTANCIA_LIMITE_CM = 30

# URLs da API
API_START = "http://localhost:3000/api/activity/start"
API_END = "http://localhost:3000/api/activity/end"

# Flags de estado
gato_perto = False
ultimo_tempo_perto = 0
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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detecta marcadores
    corners, ids, rejected = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

    tvecs_detectados = {}

    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], 0.05, camera_matrix, dist_coeffs)
            aruco.drawDetectedMarkers(frame, corners)

            # Desenha o eixo no marcador
            aruco.drawAxis(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)

            # Guarda posição
            tvecs_detectados[marker_id] = tvec[0][0]

        # Verifica se ambos estão visíveis
        if ID_GATO in tvecs_detectados and ID_POTE in tvecs_detectados:
            distancia = calcular_distancia(tvecs_detectados[ID_GATO], tvecs_detectados[ID_POTE])
            cv2.putText(frame, f"Distancia: {distancia:.1f} cm", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if distancia <= DISTANCIA_LIMITE_CM:
                ultimo_tempo_perto = time.time()
                if not gato_perto:
                    gato_perto = True
                    print("Gato chegou no pote 🐱🍽️")
                    requests.post(API_START, json={"catId": ID_GATO})
            else:
                # Verifica se já ficou longe por mais de TEMPO_SAIDA
                if gato_perto and (time.time() - ultimo_tempo_perto > TEMPO_SAIDA):
                    gato_perto = False
                    print("Gato saiu do pote 🚶‍♂️")
                    requests.post(API_END, json={"catId": ID_GATO})

    cv2.imshow("Deteccao ArUco", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
        break

cap.release()
cv2.destroyAllWindows()
