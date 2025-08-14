import cv2
import numpy as np
import time
from collections import deque

# --- CONFIGURAÇÕES ---
MARKERS = {
    1: {"tipo": "gato", "nome": "Gato Preto", "size": 0.05},
    2: {"tipo": "pote", "nome": "Pote Racao", "size": 0.08},
    3: {"tipo": "pote", "nome": "Pote Agua", "size": 0.08}
}

ENTER_THRESH = 0.20
EXIT_THRESH = 0.25
MIN_TIME_START = 2.0
MIN_TIME_STOP = 2.0
WINDOW_SIZE = 5

camera_matrix = np.array([[1000, 0, 640],
                          [0, 1000, 360],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1), dtype=np.float32)

estado = {}
for mid, info in MARKERS.items():
    if info["tipo"] == "gato":
        estado[info["nome"]] = {}
        for pid, pinfo in MARKERS.items():
            if pinfo["tipo"] == "pote":
                estado[info["nome"]][pinfo["nome"]] = {
                    "comendo": False,
                    "start_time": None,
                    "distancias": deque(maxlen=WINDOW_SIZE),
                    "ultimo_estado": False,
                    "tempo_estado": 0
                }

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

def estimate_pose(corners, marker_size):
    # corners: Nx1x4x2 array (we pass a single marker)
    # Define objeto em 3D (cantos do quadrado)
    obj_pts = np.array([
        [-marker_size/2, marker_size/2, 0],
        [marker_size/2, marker_size/2, 0],
        [marker_size/2, -marker_size/2, 0],
        [-marker_size/2, -marker_size/2, 0]
    ], dtype=np.float32)
    img_pts = corners.reshape(4, 2).astype(np.float32)
    success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, camera_matrix, dist_coeffs)
    return (rvec, tvec) if success else (None, None)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    posicoes = {}

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            if marker_id not in MARKERS:
                continue

            info = MARKERS[marker_id]
            rvec, tvec = estimate_pose(corners[i], info["size"])
            if tvec is None:
                continue

            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)
            posicoes[info["nome"]] = {"tipo": info["tipo"], "pos": tvec.flatten()}

    for gato_nome, potes in estado.items():
        if gato_nome not in posicoes:
            continue
        for pote_nome, dados in potes.items():
            if pote_nome not in posicoes:
                continue

            dist = np.linalg.norm(posicoes[gato_nome]["pos"] - posicoes[pote_nome]["pos"])
            dados["distancias"].append(dist)
            dist_media = np.mean(dados["distancias"])
            cv2.putText(frame, f"{gato_nome}->{pote_nome}: {dist_media*100:.1f} cm",
                        (10, 30 + list(estado.keys()).index(gato_nome)*40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            agora = time.time()
            if not dados["comendo"]:
                if dist_media < ENTER_THRESH:
                    if not dados["ultimo_estado"]:
                        dados["ultimo_estado"] = True
                        dados["tempo_estado"] = agora
                    elif agora - dados["tempo_estado"] >= MIN_TIME_START:
                        dados["comendo"] = True
                        dados["start_time"] = agora
                else:
                    dados["ultimo_estado"] = False
            else:
                if dist_media > EXIT_THRESH:
                    if dados["ultimo_estado"]:
                        dados["ultimo_estado"] = False
                        dados["tempo_estado"] = agora
                    elif agora - dados["tempo_estado"] >= MIN_TIME_STOP:
                        dur = agora - dados["start_time"]
                        print(f"[EVENTO] {gato_nome} parou de comer {pote_nome} após {dur:.1f}s")
                        dados["comendo"] = False
                        dados["start_time"] = None
                else:
                    dados["ultimo_estado"] = True

            # Mostrar estado
            if dados["comendo"]:
                dur = agora - dados["start_time"]
                cv2.putText(frame, f"{gato_nome} COMENDO ({dur:.1f}s)", (10, frame.shape[0]-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"{gato_nome} NAO COMENDO", (10, frame.shape[0]-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Deteccao Gato/Pote", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
