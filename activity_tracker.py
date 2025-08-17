import time
import numpy as np
from collections import deque

class ActivityTracker:
    """Classe responsável pelo rastreamento de atividades dos gatos"""
    
    def __init__(self, config):
        self.config = config
        self.estado = {}
        self.pote_nome = config.POTE_RACAO["nome"]
    
    def _ensure_cat_tracking(self, gato_nome):
        """Garante que o gato está sendo rastreado"""
        if gato_nome not in self.estado:
            self.estado[gato_nome] = {
                self.pote_nome: {
                    "comendo": False,
                    "start_time": None,
                    "distancias": deque(maxlen=self.config.WINDOW_SIZE),
                    "ultimo_estado": False,
                    "tempo_estado": 0
                }
            }
            print(f"[INFO] Iniciando rastreamento para {gato_nome}")
    
    def update(self, posicoes):
        """Atualiza o estado de atividade baseado nas posições detectadas"""
        # Verifica se o pote está presente
        if self.pote_nome not in posicoes:
            return
        
        # Atualiza rastreamento para cada gato detectado
        for nome, dados in posicoes.items():
            if dados["tipo"] == "gato":
                self._ensure_cat_tracking(nome)
                
                # Calcula distância entre gato e pote
                dist = np.linalg.norm(
                    dados["pos"] - posicoes[self.pote_nome]["pos"]
                )
                
                cat_data = self.estado[nome][self.pote_nome]
                cat_data["distancias"].append(dist)
                dist_media = np.mean(cat_data["distancias"])
                
                # Atualiza estado de alimentação
                self._update_feeding_state(nome, cat_data, dist_media)
    
    def _update_feeding_state(self, gato_nome, dados, dist_media):
        """Atualiza o estado de alimentação baseado na distância média"""
        agora = time.time()
        
        if not dados["comendo"]:
            # Verifica se deve começar a comer
            if dist_media < self.config.ENTER_THRESH:
                if not dados["ultimo_estado"]:
                    dados["ultimo_estado"] = True
                    dados["tempo_estado"] = agora
                elif agora - dados["tempo_estado"] >= self.config.MIN_TIME_START:
                    dados["comendo"] = True
                    dados["start_time"] = agora
                    print(f"[EVENTO] {gato_nome} começou a comer!")
            else:
                dados["ultimo_estado"] = False
        else:
            # Verifica se deve parar de comer
            if dist_media > self.config.EXIT_THRESH:
                if dados["ultimo_estado"]:
                    dados["ultimo_estado"] = False
                    dados["tempo_estado"] = agora
                elif agora - dados["tempo_estado"] >= self.config.MIN_TIME_STOP:
                    dur = agora - dados["start_time"]
                    print(f"[EVENTO] {gato_nome} parou de comer após {dur:.1f}s")
                    dados["comendo"] = False
                    dados["start_time"] = None
            else:
                dados["ultimo_estado"] = True
    
    def get_estado(self):
        """Retorna o estado atual de rastreamento"""
        return self.estado
    
    def cleanup_inactive_cats(self, active_cats):
        """Remove gatos que não estão mais sendo detectados"""
        inactive_cats = [cat for cat in self.estado.keys() if cat not in active_cats]
        for cat in inactive_cats:
            print(f"[INFO] Removendo rastreamento de {cat} (não detectado)")
            del self.estado[cat]