import cv2
import time
import numpy as np

class DisplayManager:
    """Classe responsável pela exibição e interface visual"""
    
    def __init__(self, config):
        self.config = config
    
    def setup_window(self):
        """Configura a janela de exibição"""
        cv2.namedWindow(self.config.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            self.config.WINDOW_NAME, 
            self.config.WINDOW_WIDTH, 
            self.config.WINDOW_HEIGHT
        )
    
    def draw_info(self, frame, posicoes, estado, marker_detector=None):
        """Desenha informações de distância e estado na tela"""
        # Desenha informações dos marcadores detectados
        self._draw_marker_info(frame, posicoes)

        # Desenha distâncias
        self._draw_distances(frame, posicoes, estado)

        # Desenha estado de alimentação
        self._draw_feeding_status(frame, estado)

        # Desenha informações do cache do pote se disponível
        if marker_detector is not None:
            self._draw_bowl_cache_info(frame, marker_detector)
    
    def _draw_marker_info(self, frame, posicoes):
        """Desenha informações dos marcadores detectados"""
        y_offset = 30
        for nome, dados in posicoes.items():
            # Verifica se é do cache
            from_cache = dados.get('from_cache', False)
            cache_indicator = " [CACHE]" if from_cache else ""

            text = f"{nome} (ID: {dados['id']}) - {dados['tipo'].upper()}{cache_indicator}"
            color = (0, 255, 255) if dados['tipo'] == 'pote' else (255, 0, 255)

            # Se for do cache, usa cor diferente
            if from_cache:
                color = (0, 200, 200)  # Amarelo mais escuro para cache

            cv2.putText(
                frame, text,
                (frame.shape[1] - 500, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )
            y_offset += 25
    
    def _draw_distances(self, frame, posicoes, estado):
        """Desenha as distâncias entre gatos e pote"""
        pote_nome = self.config.POTE_RACAO["nome"]
        if pote_nome not in posicoes:
            return

        # Posiciona no canto inferior direito
        frame_height, frame_width = frame.shape[:2]
        y_offset = frame_height - 30  # Começa 30 pixels acima da borda inferior

        for cat_id, potes in estado.items():
            # Verifica se o gato ainda está sendo detectado
            if cat_id not in posicoes:
                continue

            dados = potes[pote_nome]
            if len(dados["distancias"]) == 0:
                continue

            dist_media = np.mean(dados["distancias"])
            text = f"Gato ID {cat_id}: {dist_media*100:.1f} cm"

            # Calcula a largura do texto para posicioná-lo corretamente à direita
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            x_position = frame_width - text_size[0] - 10  # 10 pixels da borda direita

            cv2.putText(
                frame, text,
                (x_position, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )
            y_offset -= 40  # Move para cima para o próximo gato
    
    def _draw_feeding_status(self, frame, estado):
        """Desenha o status de alimentação"""
        pote_nome = self.config.POTE_RACAO["nome"]
        y_offset = frame.shape[0] - 60

        for cat_id, potes in estado.items():
            dados = potes[pote_nome]

            if dados["comendo"]:
                agora = time.time()
                dur = agora - dados["start_time"]
                text = f"Gato ID {cat_id} COMENDO ({dur:.1f}s)"
                color = (0, 0, 255)  # Vermelho
            else:
                text = f"Gato ID {cat_id} NAO COMENDO"
                color = (255, 255, 255)  # Branco

            cv2.putText(
                frame, text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
            )

            y_offset -= 30

    def _draw_bowl_cache_info(self, frame, marker_detector):
        """Desenha informações sobre o cache de posição do pote"""
        if not self.config.BOWL_CACHE_ENABLED:
            return

        cache_info = marker_detector.get_bowl_cache_info()

        # Posiciona no canto superior esquerdo
        y_start = 30

        # Status do cache
        if cache_info["has_position"]:
            status = "ATIVO" if cache_info["is_reliable"] else "INICIALIZANDO"
            color = (0, 255, 0) if cache_info["is_reliable"] else (0, 255, 255)
        else:
            status = "INATIVO"
            color = (0, 0, 255)

        cv2.putText(
            frame, f"Cache Pote: {status}",
            (10, y_start),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )

        # Informações detalhadas se o cache estiver ativo
        if cache_info["has_position"]:
            y_start += 25

            # Número de detecções
            cv2.putText(
                frame, f"Deteccoes: {cache_info['detection_count']}",
                (10, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )

            # Idade do cache
            if cache_info["age_seconds"] is not None:
                y_start += 20
                cv2.putText(
                    frame, f"Idade: {cache_info['age_seconds']:.1f}s",
                    (10, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )

    def show_frame(self, frame):
        """Exibe o frame e verifica se deve sair"""
        cv2.imshow(self.config.WINDOW_NAME, frame)
        return cv2.waitKey(1) & 0xFF == ord('q')

    def cleanup(self):
        """Limpa recursos da interface"""
        cv2.destroyAllWindows()