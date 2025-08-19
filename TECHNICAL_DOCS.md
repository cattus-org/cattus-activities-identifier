# Documentação Técnica - Sistema de Monitoramento de Gatos

## Arquitetura Detalhada

### Padrões de Design Utilizados

#### 1. Singleton Pattern (Config)
A classe `Config` centraliza todas as configurações do sistema, garantindo consistência.

#### 2. Observer Pattern (ActivityNotifier)
O `ActivityTracker` notifica o `ActivityNotifier` sobre mudanças de estado.

#### 3. Strategy Pattern (MarkerDetector)
Diferentes estratégias de detecção podem ser implementadas.

#### 4. Manager Pattern
Cada componente principal tem seu próprio gerenciador (Camera, Display, etc.).

## Fluxo de Dados Detalhado

### 1. Inicialização do Sistema

```python
# Sequência de inicialização
Config() → CameraManager() → MarkerDetector() → ActivityTracker() → DisplayManager() → APIClient() → ActivityNotifier()
```

### 2. Loop Principal de Processamento

```python
while True:
    frame = camera_manager.get_frame()           # Captura frame
    posicoes = marker_detector.detect_markers()  # Detecta marcadores
    activity_tracker.update(posicoes)            # Atualiza rastreamento
    activity_tracker.cleanup_inactive_cats()     # Remove gatos inativos
    display_manager.draw_info()                  # Desenha informações
    display_manager.show_frame()                 # Exibe frame
```

### 3. Fluxo de Detecção de Atividade

```
Posição Detectada → Cálculo de Distância → Análise Temporal → Mudança de Estado → Notificação API
```

## Algoritmos Implementados

### 1. Estimativa de Pose 3D

```python
def estimate_pose(self, corners, marker_size):
    # Define pontos 3D do marcador
    obj_pts = np.array([
        [-marker_size/2, marker_size/2, 0],
        [marker_size/2, marker_size/2, 0],
        [marker_size/2, -marker_size/2, 0],
        [-marker_size/2, -marker_size/2, 0]
    ])
    
    # Resolve PnP para obter pose
    success, rvec, tvec = cv2.solvePnP(
        obj_pts, corners, camera_matrix, dist_coeffs
    )
```

### 2. Análise Temporal de Atividade

```python
def _analyze_activity(self, cat_id, pote_nome, distancia):
    # Adiciona distância à janela deslizante
    self.estado[cat_id][pote_nome]["distancias"].append(distancia)
    
    # Calcula média das distâncias
    avg_distance = np.mean(list(distancias))
    
    # Determina estado baseado em thresholds
    if avg_distance < self.config.ENTER_THRESH:
        # Lógica para iniciar atividade
    elif avg_distance > self.config.EXIT_THRESH:
        # Lógica para finalizar atividade
```

### 3. Suavização de Estados

O sistema usa uma janela deslizante para evitar mudanças bruscas de estado:

- **WINDOW_SIZE**: Número de medições consideradas
- **MIN_TIME_START**: Tempo mínimo para confirmar início
- **MIN_TIME_STOP**: Tempo mínimo para confirmar fim

## Estruturas de Dados

### 1. Configuração de Marcadores

```python
# Pote de ração (fixo)
POTE_RACAO = {
    "tipo": "pote",
    "nome": "Pote Racao",
    "size": 0.02
}

# Gatos (dinâmico)
detected_cats = {
    marker_id: {
        "tipo": "gato",
        "size": 0.02
    }
}
```

### 2. Estado de Rastreamento

```python
estado = {
    cat_id: {
        pote_nome: {
            "comendo": bool,              # Estado atual
            "start_time": datetime,       # Início da atividade
            "distancias": deque,          # Janela de distâncias
            "ultimo_estado": bool,        # Estado anterior
            "tempo_estado": float         # Tempo no estado atual
        }
    }
}
```

### 3. Atividades Ativas (API)

```python
active_activities = {
    (cat_id, activity_type): activity_id
}
```

## Tratamento de Erros e Robustez

### 1. Reconexão de Câmera

```python
def _initialize_camera(self):
    for attempt in range(self.max_retries):
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            # Configurações e testes
            if self.cap.isOpened():
                return True
        except Exception as e:
            self.logger.error(f"Tentativa {attempt + 1} falhou: {e}")
            time.sleep(self.retry_delay)
```

### 2. Tratamento de Falhas na API

```python
def _make_request(self, method, endpoint, data=None):
    try:
        response = self.session.request(method, url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        self.logger.error(f"Erro na requisição: {e}")
        return None
```

### 3. Cleanup Automático

```python
def cleanup_all_activities(self):
    """Finaliza todas as atividades ativas ao sair do sistema"""
    for (cat_id, activity_type), activity_id in self.active_activities.items():
        self.notify_activity_end(cat_id, activity_type)
```

## Performance e Otimizações

### 1. Gerenciamento de Buffer

- **Buffer mínimo**: Reduz latência
- **Timeout configurável**: Evita travamentos
- **Liberação automática**: Previne vazamentos de memória

### 2. Processamento de Imagem

- **Conversão para escala de cinza**: Apenas para detecção
- **Reutilização de objetos**: Evita alocações desnecessárias
- **Cache de gatos detectados**: Evita recriação de objetos

### 3. Comunicação com API

- **Session reutilizável**: Mantém conexões HTTP
- **Timeout configurável**: Evita bloqueios
- **Retry automático**: Para falhas temporárias

## Configurações Avançadas

### 1. Calibração de Câmera

```python
# Matriz intrínseca da câmera
camera_matrix = np.array([
    [fx,  0, cx],
    [ 0, fy, cy],
    [ 0,  0,  1]
])

# Coeficientes de distorção
dist_coeffs = np.array([k1, k2, p1, p2, k3])
```

### 2. Thresholds de Atividade

```python
ENTER_THRESH = 0.10    # Distância para iniciar (metros)
EXIT_THRESH = 0.20     # Distância para finalizar (metros)
MIN_TIME_START = 2.0   # Tempo mínimo para confirmar início
MIN_TIME_STOP = 2.0    # Tempo mínimo para confirmar fim
WINDOW_SIZE = 5        # Tamanho da janela deslizante
```

### 3. Configurações de Rede

```python
API_TIMEOUT = 10           # Timeout para requisições HTTP
CAMERA_TIMEOUT = 10        # Timeout para conexão da câmera
MAX_RETRIES = 3           # Máximo de tentativas de reconexão
RETRY_DELAY = 2           # Delay entre tentativas
```

## Logs e Monitoramento

### 1. Níveis de Log

- **INFO**: Eventos importantes do sistema
- **DEBUG**: Informações detalhadas para desenvolvimento
- **WARNING**: Situações que merecem atenção
- **ERROR**: Erros que não impedem o funcionamento
- **CRITICAL**: Erros que podem parar o sistema

### 2. Formato de Log

```
2024-01-01 12:00:00,000 - module_name - LEVEL - message
```

### 3. Arquivos de Log

- **cattus_activities.log**: Log principal do sistema
- **Console**: Output em tempo real

## Extensões Possíveis

### 1. Múltiplos Potes

```python
# Configuração para múltiplos potes
POTES = {
    10: {"nome": "Pote Racao", "tipo": "comida"},
    11: {"nome": "Pote Agua", "tipo": "agua"},
    12: {"nome": "Pote Snacks", "tipo": "petisco"}
}
```

### 2. Análise de Comportamento

```python
# Detecção de padrões comportamentais
def analyze_behavior_patterns(self, cat_id):
    # Análise de frequência de alimentação
    # Detecção de mudanças de comportamento
    # Alertas de saúde baseados em atividade
```

### 3. Interface Web

```python
# API REST para interface web
@app.route('/api/cats/<int:cat_id>/activities')
def get_cat_activities(cat_id):
    # Retorna atividades do gato
```

### 4. Notificações Push

```python
# Integração com serviços de notificação
def send_push_notification(self, message):
    # Firebase, Telegram, Email, etc.
```

## Testes e Validação

### 1. Testes Unitários

```python
def test_distance_calculation():
    # Testa cálculo de distância 3D
    
def test_activity_detection():
    # Testa detecção de início/fim de atividade
    
def test_api_communication():
    # Testa comunicação com API
```

### 2. Testes de Integração

```python
def test_full_pipeline():
    # Testa fluxo completo do sistema
    
def test_error_recovery():
    # Testa recuperação de erros
```

### 3. Validação de Performance

- **FPS**: Frames por segundo processados
- **Latência**: Tempo entre detecção e notificação
- **Uso de memória**: Monitoramento de vazamentos
- **Uso de CPU**: Otimização de processamento

## Segurança

### 1. Autenticação API

- **API Key**: Token de autenticação
- **HTTPS**: Comunicação criptografada
- **Timeout**: Prevenção de ataques DoS

### 2. Validação de Dados

```python
def validate_cat_id(self, cat_id):
    if not isinstance(cat_id, int) or cat_id < 0:
        raise ValueError("ID do gato inválido")
```

### 3. Sanitização de Logs

```python
def sanitize_log_data(self, data):
    # Remove informações sensíveis dos logs
    return {k: v for k, v in data.items() if k not in SENSITIVE_FIELDS}
```

## Deployment

### 1. Containerização

```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 2. Configuração de Produção

```python
# Configurações específicas para produção
PRODUCTION_CONFIG = {
    "LOG_LEVEL": "INFO",
    "API_TIMEOUT": 30,
    "MAX_RETRIES": 5,
    "BUFFER_SIZE": 1
}
```

### 3. Monitoramento

- **Health checks**: Verificação de saúde do sistema
- **Métricas**: Coleta de dados de performance
- **Alertas**: Notificações de problemas

---

Esta documentação técnica fornece uma visão aprofundada da implementação e pode ser usada como referência para desenvolvimento, manutenção e extensão do sistema.