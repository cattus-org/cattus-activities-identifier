# Documentação Técnica - Sistema de Monitoramento de Gatos

## Arquitetura Detalhada

### Padrões de Design Utilizados

#### 1. Singleton Pattern (Config)
A classe `Config` centraliza todas as configurações do sistema, garantindo consistência e evitando múltiplas instâncias conflitantes.

#### 2. Observer Pattern (ActivityNotifier)
O `ActivityTracker` observa e notifica o `ActivityNotifier` sobre mudanças de estado das atividades dos gatos, mantendo o desacoplamento entre rastreamento e notificação.

#### 3. Strategy Pattern (MarkerDetector)
Permite a implementação de diferentes algoritmos de detecção de marcadores, possibilitando fácil troca ou extensão do método de detecção.

#### 4. Manager Pattern
Cada componente principal do sistema é gerenciado por uma classe própria (ex: `CameraManager`, `DisplayManager`), facilitando a manutenção e a escalabilidade.

### Componentes Principais e Fluxo de Inicialização

```python
# Sequência de inicialização do sistema
Config() → CameraManager() → MarkerDetector() → ActivityTracker() → DisplayManager() → APIClient() → ActivityNotifier()
```

- **Config**: Carrega e disponibiliza parâmetros globais.
- **CameraManager**: Estabelece conexão com câmera RTSP, captura e fornece frames para o pipeline.
- **MarkerDetector**: Detecta marcadores ArUco e estima suas poses.
- **ActivityTracker**: Atualiza o estado e histórico das atividades de cada gato.
- **DisplayManager**: Gerencia interface gráfica para exibição em tempo real.
- **APIClient**: Realiza comunicação HTTP com servidores externos.
- **ActivityNotifier**: Responsável por enviar notificações de eventos para API externa.

## Fluxo de Dados Detalhado

### Loop Principal de Processamento

```python
while True:
    frame = camera_manager.get_frame()           # Captura frame da câmera (RTSP)
    posicoes = marker_detector.detect_markers()  # Detecta marcadores presentes e estima posição 3D
    activity_tracker.update(posicoes)            # Atualiza estado e histórico de atividades dos gatos
    activity_tracker.cleanup_inactive_cats()     # Remove gatos que ficaram inativos por período configurado
    display_manager.draw_info()                  # Sobrepõe informações visuais nos frames
    display_manager.show_frame()                 # Exibe frame processado ao usuário
```

### Fluxo de Análise de Atividade

```
Posição Detectada → Cálculo de Distância → Análise Temporal (janela deslizante) → Mudança de Estado (start/stop) → Notificação API
```

## Algoritmos e Processos Técnicos

### Estimativa de Pose 3D

A estimativa de pose 3D é um componente crítico do sistema, permitindo determinar a posição espacial exata de cada marcador (gatos e pote) em relação à câmera. Este processo utiliza algoritmos de visão computacional avançados para converter coordenadas 2D da imagem em coordenadas 3D no espaço real.

#### Identificação de Marcadores ArUco

O sistema utiliza marcadores ArUco do dicionário `DICT_ARUCO_ORIGINAL` para identificação única de cada objeto. Cada marcador possui um padrão binário distinto que é robusto a variações de iluminação e pode ser detectado rapidamente mesmo em condições desafiadoras.

O processo de detecção envolve:
1. Conversão do frame para escala de cinza para melhorar o contraste
2. Aplicação de filtros para reduzir ruído
3. Detecção de contornos quadrados que correspondem aos marcadores
4. Decodificação do padrão binário para identificar o ID único

```python
def detect_markers(self, frame):
    """Detecta marcadores no frame e retorna suas posições"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = self.detector.detectMarkers(gray)
```

#### Fundamentos Matemáticos da Estimativa de Pose

A estimativa de pose 3D é baseada na solução do problema PnP (Perspective-n-Point), que determina a posição e orientação de um objeto 3D em relação à câmera com base em pontos correspondentes 2D-3D.

##### Modelo Geométrico do Marcador

Cada marcador é modelado como um quadrado plano no espaço 3D com coordenadas conhecidas:

```python
def estimate_pose(self, corners, marker_size):
    """
    Estima a pose 3D do marcador ArUco usando solvePnP.
    """
    # Define objeto em 3D (cantos do quadrado no sistema de coordenadas do objeto)
    obj_pts = np.array([
        [-marker_size/2, marker_size/2, 0],    # Canto superior esquerdo
        [marker_size/2, marker_size/2, 0],     # Canto superior direito
        [marker_size/2, -marker_size/2, 0],    # Canto inferior direito
        [-marker_size/2, -marker_size/2, 0]    # Canto inferior esquerdo
    ], dtype=np.float32)

    # Extrai pontos 2D detectados na imagem
    img_pts = corners.reshape(4, 2).astype(np.float32)

    # Resolve o problema PnP para obter vetores de rotação e translação
    success, rvec, tvec = cv2.solvePnP(
        obj_pts,
        img_pts,
        self.config.camera_matrix,
        self.config.dist_coeffs
    )

    if success:
        return rvec, tvec
    else:
        return None, None
```

##### Parâmetros de Calibração da Câmera

Para obter resultados precisos, o sistema requer parâmetros de calibração da câmera:

**Matriz de Câmera Intrínseca:**
```python
# Matriz da câmera intrínseca (parâmetros de calibração)
camera_matrix = np.array([
    [fx,  0, cx],
    [ 0, fy, cy],
    [ 0,  0,  1]
], dtype=np.float32)
```

Onde:
- `fx`, `fy`: Fatores focais em pixels nas direções x e y (relacionados à distância focal e tamanho do pixel)
- `cx`, `cy`: Coordenadas do centro óptico (ponto principal) em pixels

**Coeficientes de Distorção:**
```python
# Coeficientes de distorção da lente
dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
```

Onde:
- `k1`, `k2`, `k3`: Coeficientes de distorção radial
- `p1`, `p2`: Coeficientes de distorção tangencial

##### Vetores de Saída e Transformações

O algoritmo `solvePnP` retorna dois vetores fundamentais:

1. **Vetor de Rotação (`rvec`)**: Representa a orientação do marcador em coordenadas de Euler (3x1)
2. **Vetor de Translação (`tvec`)**: Representa a posição 3D do marcador em relação à câmera (3x1)

Para obter a matriz de rotação completa:
```python
# Converte vetor de rotação para matriz de rotação
rotation_matrix, _ = cv2.Rodrigues(rvec)
```

A posição 3D final é obtida diretamente do vetor de translação:
```python
# Posição 3D em coordenadas da câmera (metros ou unidades do tamanho do marcador)
position_3d = tvec.flatten()  # [x, y, z]
```

#### Cálculo de Distâncias 3D

Com as posições 3D de dois marcadores, o sistema calcula a distância euclidiana entre eles:

```python
# Cálculo da distância 3D entre dois pontos
def calculate_3d_distance(pos1, pos2):
    """
    Calcula a distância euclidiana 3D entre duas posições.

    Args:
        pos1: array [x, y, z] posição do primeiro ponto
        pos2: array [x, y, z] posição do segundo ponto

    Returns:
        float: distância em unidades do tamanho do marcador (metros)
    """
    return np.linalg.norm(pos1 - pos2)
```

A distância resultante é usada para determinar a proximidade entre gato e pote, fundamental para a detecção de atividades.

#### Sistema de Cache de Posição do Pote

Para melhorar a robustez e performance, o sistema implementa um mecanismo de cache para a posição do pote:

```python
# Estrutura do cache de posição do pote
bowl_position_cache = {
    "position": None,           # Última posição 3D conhecida
    "last_detected": None,      # Timestamp da última detecção
    "last_updated": None,       # Timestamp da última atualização do cache
    "detection_count": 0,       # Contador de detecções
    "is_reliable": False        # Indicador de confiabilidade
}
```

##### Estratégia de Atualização do Cache

1. **Atualização Controlada**: O cache é atualizado em intervalos configuráveis para evitar flutuações bruscas:
   ```python
   # Verifica se deve atualizar o cache
   should_update = (
       cache["position"] is None or
       cache["last_updated"] is None or
       (current_time - cache["last_updated"]) >= UPDATE_INTERVAL
   )
   ```

2. **Confiabilidade Baseada em Detecções**: A posição só é considerada confiável após um número mínimo de detecções:
   ```python
   # Marca como confiável após threshold de detecções
   if cache["detection_count"] >= CONFIDENCE_THRESHOLD:
       cache["is_reliable"] = True
   ```

3. **Expiração do Cache**: Posições muito antigas são descartadas:
   ```python
   # Verifica se o cache está expirado
   if age > MAX_AGE:
       return None  # Cache expirado
   ```

##### Benefícios do Sistema de Cache

1. **Tolerância a Falhas**: O sistema continua funcionando mesmo quando o marcador do pote não é detectado temporariamente
2. **Redução de Processamento**: Evita recálculos repetidos da mesma posição
3. **Suavização de Dados**: Fornece uma posição estável para cálculos contínuos
4. **Indicadores Visuais**: O sistema mostra visualmente quando está usando dados em cache

#### Visualização de Pose e Eixos

Para auxiliar na verificação visual do funcionamento do sistema, os eixos de coordenadas de cada marcador são desenhados na imagem:

```python
# Desenha eixos do sistema de coordenadas do marcador
cv2.drawFrameAxes(
    frame,
    self.config.camera_matrix,
    self.config.dist_coeffs,
    rvec, tvec, 0.03  # Comprimento dos eixos: 3cm
)
```

Cada eixo representa:
- **Eixo X (vermelho)**: Direção horizontal
- **Eixo Y (verde)**: Direção vertical
- **Eixo Z (azul)**: Direção de profundidade (apontando para fora do marcador)

#### Considerações sobre Precisão

A precisão da estimativa de pose 3D depende de vários fatores:

1. **Qualidade da Calibração da Câmera**: Parâmetros de calibração precisos são essenciais
2. **Tamanho do Marcador**: Marcadores maiores geralmente proporcionam melhor precisão
3. **Distância da Câmera**: A precisão tende a diminuir com distâncias muito grandes
4. **Iluminação**: Condições de iluminação adequadas melhoram a detecção
5. **Distorção da Lente**: Correção adequada dos coeficientes de distorção é crucial

O sistema foi projetado para manter uma precisão adequada para a detecção de atividades de gatos, com tolerâncias que consideram o tamanho típico de um gato e as distâncias envolvidas no cenário de monitoramento.

### Análise Temporal com Janela Deslizante

- Utiliza uma janela deslizante (deque) para armazenar as últimas N distâncias.
- Calcula a média móvel para evitar flutuações bruscas.
- Configurações importantes:
  - `WINDOW_SIZE`: tamanho da janela (ex: 8)
  - `MIN_TIME_START` e `MIN_TIME_STOP`: tempos mínimos para confirmar mudança de estado.

Exemplo:

```python
self.estado[cat_id][pote_nome]["distancias"].append(distancia)
avg_distance = np.mean(self.estado[cat_id][pote_nome]["distancias"])

if avg_distance < self.config.ENTER_THRESH:
    # Possível início de atividade
    # Confirmar se tempo mínimo de start foi ultrapassado antes de mudar estado para ativo

elif avg_distance > self.config.EXIT_THRESH:
    # Possível fim de atividade
    # Confirmar tempo mínimo antes de considerar inativo
```

### Lógica de Mudança de Estado

- Evita falsos positivos / negativos por meio da confirmação temporal.
- Altera estado `comendo` após confirmação com base em thresholds e duração.
- Mantém timestamps para controle de duração no estado atual.

## Estruturas de Dados Chave

### Configuração de Marcadores

```python
# Exemplo de pote de ração fixo
POTE_RACAO = {
    "tipo": "pote",
    "nome": "Pote Racao",
    "size": 0.02  # tamanho físico do marcador em metros
}

# Dicionário dinâmico para gatos detectados
detected_cats = {
    marker_id: {
        "tipo": "gato",
        "size": 0.02
    }
}
```

### Estado de Rastreamento por Gato e Pote

```python
estado = {
    cat_id: {
        pote_nome: {
            "comendo": bool,              # Indica se gato está alimentando
            "start_time": datetime,       # Inicio do evento
            "distancias": deque,          # Janela deslizante de distâncias medidas
            "ultimo_estado": bool,        # Último estado confirmado
            "tempo_estado": float         # Timestamp da última mudança de estado
        }
    }
}
```

### Atividades Ativas para Controle na API

```python
active_activities = {
    (cat_id, activity_type): activity_id  # Atividades ainda abertas/ativas para evitar duplicatas na API
}
```

## Tratamento de Erros e Robustez

### Reconexão Automática da Câmera

```python
def _initialize_camera(self):
    for attempt in range(self.max_retries):
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if self.cap.isOpened():
                return True
        except Exception as e:
            self.logger.error(f"Tentativa {attempt + 1} falhou: {e}")
            time.sleep(self.retry_delay)  # Delay configurável entre tentativas
    return False
```

- Evita travamentos por falha temporária na conexão.
- Loga erros para análise posterior.

### Tratamento de Falhas na API

```python
def _make_request(self, method, endpoint, data=None):
    try:
        url = self.base_url + endpoint
        response = self.session.request(method, url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        self.logger.error(f"Erro na requisição: {e}")
        return None
```

- Usa sessão HTTP reutilizável para eficiência.
- Timeout configurável para evitar bloqueio.
- Loga erros detalhados para manutenção.

### Cleanup Automático Durante Finalização

```python
def cleanup_all_activities(self):
    """Finaliza todas as atividades ativas corretamente na saída do sistema"""
    for (cat_id, activity_type), activity_id in self.active_activities.items():
        self.notify_activity_end(cat_id, activity_type)
    self.active_activities.clear()
```

- Garante fechamento correto das atividades na API evitando estados inconsistentes.

## Performance e Otimizações

### Gerenciamento de Buffer e Latência

- Uso de buffer mínimo em captura de frame para reduzir atraso.
- Timeout para evitar travamentos em conexões lentas.
- Liberação automática e periódica de recursos para evitar leaks.

### Processamento de Imagem

- Conversão para escala de cinza só quando necessário para detectar marcadores, reduzindo custo computacional.
- Reutilização de objetos como `deque` e estruturas para evitar alocações frequentes.
- Cache de informações do pote para evitar recalcular posição fixa em cada frame.

### Comunicação com API

- Sessão HTTP persistente para reduzir overhead.
- Retry automático para requisições temporariamente falhas.
- Timeout configurável para evitar bloqueios.

## Configurações Avançadas de Sistema

### Calibração da Câmera

```python
camera_matrix = np.array([
    [fx,  0, cx],
    [ 0, fy, cy],
    [ 0,  0,  1]
], dtype=np.float32)

dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
```

- Parâmetros obtidos via calibração para correção e estimativa acurada do pose 3D.

### Thresholds para Detecção de Atividade

```python
ENTER_THRESH = 0.15    # Distância (em metros) para reconhecer início de alimentação
EXIT_THRESH = 0.25     # Distância para reconhecer fim da alimentação
MIN_TIME_START = 3.0   # Tempo em segundos para confirmar início
MIN_TIME_STOP = 2.0    # Tempo para confirmar fim
WINDOW_SIZE = 8        # Número de amostras na janela deslizante
```

### Configurações de Rede e Tempo

```python
API_TIMEOUT = 10          # Timeout para requisições à API (segundos)
CAMERA_TIMEOUT = 10       # Timeout para conexão da câmera
MAX_RETRIES = 3           # Número máximo de tentativas (API e câmera)
RETRY_DELAY = 2           # Delay entre tentativas (segundos)
```

### Configurações de Interface e Streaming

```python
DISPLAY_ENABLED = True        # Habilita/desabilita a janela de exibição local
DISPLAY_INFO_ENABLED = True  # Habilita/desabilita informações sobrepostas na interface
STREAMING_ENABLED = True     # Habilita/desabilita o servidor de streaming via FastAPI
STREAMING_PORT = 8000        # Porta para o servidor de streaming
STREAMING_HOST = "0.0.0.0"   # Endereço IP para o servidor de streaming
```

#### Opções de Visualização

- **DISPLAY_ENABLED**: Controla se a janela de interface gráfica será exibida localmente. Útil para ambientes headless ou quando apenas o streaming é necessário.
- **DISPLAY_INFO_ENABLED**: Controla se informações sobrepostas (distâncias, identificadores, estados) serão desenhadas na interface e no streaming.
- **STREAMING_ENABLED**: Ativa o servidor FastAPI para fornecer streaming via HTTP. Permite acesso remoto ao feed de vídeo.

#### Combinações de Configuração

| DISPLAY_ENABLED | DISPLAY_INFO_ENABLED | STREAMING_ENABLED | Resultado |
|----------------|---------------------|-------------------|-----------|
| True | True | True | Janela local + streaming com informações |
| True | False | True | Janela local + streaming sem informações |
| False | True | True | Apenas streaming com informações |
| False | False | True | Apenas streaming sem informações |
| True | True | False | Apenas janela local com informações |
| False | True | False | Nenhuma interface visual |

## Logs e Monitoramento do Sistema

### Níveis e Categorias de Logs

- **INFO**: Informações úteis para operação normal.
- **DEBUG**: Detalhes para depuração e desenvolvimento.
- **WARNING**: Avisos que podem precisar de atenção.
- **ERROR**: Erros que não bloqueiam mas merecem investigação.
- **CRITICAL**: Erros graves que podem parar o sistema.

### Formato de Logs

```
2024-01-01 12:00:00,000 - module_name - LEVEL - message
```

### Arquivos e Saídas

- Log principal: `cattus_activities.log`
- Logs simultâneos no console para monitoramento em tempo real.

## Possíveis Extensões e Novas Funcionalidades

### Suporte a Múltiplos Potes

```python
POTES = {
    10: {"nome": "Pote Racao", "tipo": "comida"},
    11: {"nome": "Pote Agua", "tipo": "agua"},
    12: {"nome": "Pote Snacks", "tipo": "petisco"}
}
```

- Permite monitoramento simultâneo de diferentes tipos de comida/água/petiscos.

### Análise Avançada de Comportamento

```python
def analyze_behavior_patterns(self, cat_id):
    """
    Detecta padrões na frequência e duração da alimentação,
    identifica possíveis alterações de saúde ou comportamento.
    """
```

### Interface Web via API REST

```python
@app.route('/api/cats/<int:cat_id>/activities')
def get_cat_activities(cat_id):
    """
    Retorna JSON com atividades registradas de determinado gato,
    permitindo integração com dashboards e sistemas externos.
    """
```

### Integração com Serviços de Notificação

```python
def send_push_notification(self, message):
    """
    Envia notificações via Firebase, Telegram, Email, etc.
    """
```

- Para alertas em tempo real ao usuário ou equipe.

## Testes e Validação

### Unitários

- Testes de cálculo de distância e pose 3D.
- Testes de detecção de início/fim de atividade.
- Testes para comunicação robusta com API.

### Integração

- Testes do fluxo completo, desde aquisição até notificação.
- Testes de recuperação de falhas e reconexão.

### Performance

- Monitoramento de FPS, latência, uso de memória e CPU.

## Segurança

### Autenticação API

- Uso de tokens/API Keys via cabeçalhos HTTP.
- Comunicação através de HTTPS para confidencialidade.
- Timeout para mitigar ataques de negação de serviço (DoS).

### Validação e Sanitização

```python
def validate_cat_id(self, cat_id):
    if not isinstance(cat_id, int) or cat_id < 0:
        raise ValueError("ID do gato inválido")
```

```python
def sanitize_log_data(self, data):
    """
    Remove dados sensíveis antes de armazenar ou exibir logs.
    """
    return {k: v for k, v in data.items() if k not in SENSITIVE_FIELDS}
```

## Deployment

### Containerização

```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

- Facilita deploy consistente em diferentes ambientes.

### Configuração de Produção

```python
PRODUCTION_CONFIG = {
    "LOG_LEVEL": "INFO",
    "API_TIMEOUT": 30,
    "MAX_RETRIES": 5,
    "BUFFER_SIZE": 1
}
```

- Otimizado para produção com logs reduzidos e timeouts maiores.

### Monitoramento Contínuo

- Health checks periódicos.
- Métricas de uso e desempenho.
- Alertas configuráveis para falhas.

---

Esta documentação técnica fornece uma visão aprofundada da implementação do sistema de monitoramento de gatos, servindo como referência para desenvolvimento, manutenção e futuras extensões.