import time
import numpy as np
from collections import deque
from datetime import datetime
import logging

class ActivityTracker:
    """Classe responsável pelo rastreamento de atividades dos gatos"""

    def __init__(self, config):
        self.config = config
        self.estado = {}
        self.pote_nome = config.POTE_RACAO["nome"]
        self.last_seen = {}  # Dicionário para armazenar o último timestamp de detecção do gato
        self.logger = logging.getLogger(__name__)

        # Validação do timeout para evitar valores inválidos
        if not hasattr(self.config, "CAT_INACTIVITY_TIMEOUT") or self.config.CAT_INACTIVITY_TIMEOUT <= 0:
            self.logger.warning("CAT_INACTIVITY_TIMEOUT inválido ou não definido. Usando valor padrão 3 segundos.")
            self.config.CAT_INACTIVITY_TIMEOUT = 3

    def _ensure_cat_tracking(self, cat_id: int):
        """Garante que o gato está sendo rastreado"""
        if cat_id not in self.estado:
            self.estado[cat_id] = {
                self.pote_nome: {
                    "comendo": False,
                    "start_time": None,
                    "distancias": deque(maxlen=self.config.WINDOW_SIZE),
                    "ultimo_estado": False,
                    "tempo_estado": 0
                }
            }
            self.logger.info(f"Iniciando rastreamento para gato ID {cat_id}")

    def update(self, posicoes):
        """Atualiza o estado de atividade baseado nas posições detectadas"""
        # Verifica se o pote está presente
        if self.pote_nome not in posicoes:
            return

        agora = time.time()

        # Atualiza rastreamento para cada gato detectado
        for identificador, dados in posicoes.items():
            if dados["tipo"] == "gato":
                # Converte identificador para int Python nativo
                try:
                    if isinstance(identificador, str):
                        cat_id = int(identificador)
                    else:
                        cat_id = int(identificador)
                except (ValueError, TypeError):
                    cat_id = abs(hash(str(identificador))) % 1000

                self._ensure_cat_tracking(cat_id)

                # Atualiza o timestamp da última detecção
                self.last_seen[cat_id] = agora

                # Calcula distância entre gato e pote
                dist = np.linalg.norm(
                    dados["pos"] - posicoes[self.pote_nome]["pos"]
                )

                cat_data = self.estado[cat_id][self.pote_nome]
                cat_data["distancias"].append(dist)
                dist_media = np.mean(cat_data["distancias"])

                # Atualiza estado de alimentação
                self._update_feeding_state(cat_id, cat_data, dist_media)

    def _update_feeding_state(self, cat_id: int, dados, dist_media):
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
                    self.logger.info(f"Gato ID {cat_id} começou a comer!")
                    # Notifica início da atividade
                    self._on_activity_start(cat_id, "eating")
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
                    self.logger.info(f"Gato ID {cat_id} parou de comer após {dur:.1f}s")
                    # Notifica fim da atividade (converte timestamp para datetime)
                    start_datetime = datetime.fromtimestamp(dados["start_time"])
                    self._on_activity_end(cat_id, "eating", start_datetime)
                    dados["comendo"] = False
                    dados["start_time"] = None
            else:
                dados["ultimo_estado"] = True

    def get_estado(self):
        """Retorna o estado atual de rastreamento"""
        return self.estado

    def cleanup_inactive_cats(self, active_cats):
        """Remove gatos que não estão mais sendo detectados após um tempo de tolerância"""
        agora = time.time()

        # Converte active_cats para IDs se necessário
        active_cat_ids = []
        for cat in active_cats:
            try:
                cat_id = int(cat) if isinstance(cat, str) else cat
            except (ValueError, TypeError):
                cat_id = abs(hash(str(cat))) % 1000
            active_cat_ids.append(cat_id)

        # Lista gatos para remoção considerando o tempo de inatividade
        inactive_cats = []
        for cat_id in list(self.estado.keys()):
            if cat_id not in active_cat_ids:
                last_seen_time = self.last_seen.get(cat_id, 0)
                if agora - last_seen_time > self.config.CAT_INACTIVITY_TIMEOUT:
                    # Antes de remover, verifica se o gato estava em atividade
                    cat_data = self.estado.get(cat_id, {}).get(self.pote_nome, None)
                    if cat_data and cat_data.get("comendo", False):
                        duracao_atividade = agora - cat_data.get("start_time", agora)
                        if duracao_atividade >= self.config.MIN_ACTIVITY_DURATION_TO_REGISTER:
                            # Finaliza e registra a atividade
                            start_datetime = datetime.fromtimestamp(cat_data["start_time"])
                            if hasattr(self, 'activity_notifier'):
                                self.activity_notifier.notify_activity_end(cat_id, "eating", start_datetime)
                        else:
                            # Atividade muito curta, descarta sem registrar
                            self.logger.info(f"Atividade de gato ID {cat_id} descartada por ser menor que {self.config.MIN_ACTIVITY_DURATION_TO_REGISTER} segundos")
                    inactive_cats.append(cat_id)

        for cat_id in inactive_cats:
            self.logger.info(f"Removendo rastreamento de gato ID {cat_id} (não detectado por mais de {self.config.CAT_INACTIVITY_TIMEOUT} segundos)")
            del self.estado[cat_id]
            if cat_id in self.last_seen:
                del self.last_seen[cat_id]

    def set_activity_notifier(self, notifier):
        """Define o notificador de atividades"""
        self.activity_notifier = notifier

    def _on_activity_start(self, cat_id: int, activity_type: str):
        """Chamado quando uma atividade inicia"""
        if hasattr(self, 'activity_notifier'):
            self.activity_notifier.notify_activity_start(cat_id, activity_type)

    def _on_activity_end(self, cat_id: int, activity_type: str, start_time):
        """Chamado quando uma atividade termina"""
        if hasattr(self, 'activity_notifier'):
            self.activity_notifier.notify_activity_end(cat_id, activity_type, start_time)

    def remove_cat(self, cat_id: int):
        """Remove explicitamente um gato do rastreamento e do last_seen"""
        if cat_id in self.estado:
            del self.estado[cat_id]
        if cat_id in self.last_seen:
            del self.last_seen[cat_id]
        self.logger.info(f"Removido explicitamente rastreamento de gato ID {cat_id}")