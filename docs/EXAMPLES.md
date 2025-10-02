# Exemplos de Uso e Casos de Teste

## Cenários de Uso

### 1. Monitoramento Básico de Alimentação

**Objetivo**: Detectar quando um gato se aproxima do pote de ração.

**Configuração**:
```python
# config.py
POTE_RACAO_ID = 10
ENTER_THRESH = 0.15  # 15cm para iniciar
EXIT_THRESH = 0.25   # 25cm para finalizar
MIN_TIME_START = 3.0 # 3 segundos para confirmar
MIN_TIME_STOP = 2.0  # 2 segundos para finalizar
WINDOW_SIZE = 8      # Janela deslizante para suavização
```

**Resultado Esperado**:
- Gato se aproxima → Sistema detecta → Inicia atividade "eating"
- Gato se afasta → Sistema detecta → Finaliza atividade
- API recebe notificações de início e fim
- Logs registrados com informações detalhadas

### 2. Múltiplos Gatos

**Objetivo**: Monitorar vários gatos simultaneamente.

**Setup**:
- Marcador ID 1: Gato "Mimi"
- Marcador ID 2: Gato "Fifi"
- Marcador ID 3: Gato "Lulu"
- Marcador ID 10: Pote de ração

**Comportamento**:
```
Tempo 10:00 - Gato 1 se aproxima do pote
Tempo 10:01 - Sistema inicia atividade para Gato 1
Tempo 10:03 - Gato 2 também se aproxima
Tempo 10:04 - Sistema inicia atividade para Gato 2
Tempo 10:05 - Gato 1 se afasta
Tempo 10:06 - Sistema finaliza atividade do Gato 1
Tempo 10:08 - Gato 2 se afasta
Tempo 10:09 - Sistema finaliza atividade do Gato 2
```

### 3. Ambiente com Pouca Luz

**Desafio**: Detecção em condições de iluminação reduzida.

**Soluções**:
- Usar marcadores maiores (5x5 cm)
- Ajustar parâmetros de detecção
- Configurar thresholds mais sensíveis

```python
# config.py
DEFAULT_MARKER_SIZE = 0.05  # 5cm para melhor detecção em pouca luz
```

### 4. Uso do Cache de Posição do Pote

**Objetivo**: Otimizar a detecção mantendo a posição do pote em cache.

**Configuração**:
```python
# config.py
BOWL_CACHE_ENABLED = True
BOWL_CACHE_UPDATE_INTERVAL = 10.0  # Atualiza a cada 10 segundos
BOWL_CACHE_MAX_AGE = 300.0         # Usa cache por até 5 minutos
BOWL_CACHE_CONFIDENCE_THRESHOLD = 5 # Precisa de 5 detecções para ser confiável
```

### 5. Configuração de Mapeamento de Atividades

**Objetivo**: Personalizar os tipos de atividades enviados para a API.

**Configuração**:
```python
# config.py
ACTIVITY_TYPE_MAPPING = {
    "eating": "eat",
    "drinking": "drink",
    "sleeping": "sleep",
    "playing": "play"
}
```

## Testes de Integração

### Teste de Conectividade com API

**Verificação**:
- Conexão com a API estabelecida
- Autenticação bem-sucedida
- Envio de dados de atividade

### Teste de Detecção de Falhas

**Cenário**: Câmera desconectada temporariamente

**Comportamento Esperado**:
- Sistema tenta reconectar automaticamente
- Logs registrados sobre falhas
- Continuidade no monitoramento após reconexão

### Teste de Limpeza de Gatos Inativos

**Cenário**: Gato não detectado por período prolongado

**Configuração**:
```python
# config.py
CAT_INACTIVITY_TIMEOUT = 5  # Remove gato após 5 segundos sem detecção
```

**Comportamento Esperado**:
- Gato removido do rastreamento após timeout
- Recursos liberados adequadamente
- Logs registrados sobre a limpeza

### 5. Modo Headless com Streaming

**Objetivo**: Executar o sistema sem interface gráfica local, mas com streaming via rede.

**Configuração**:
```env
# .env
STREAMING_ENABLED=true
STREAMING_PORT=8080
STREAMING_HOST=0.0.0.0
DISPLAY_ENABLED=false
DISPLAY_INFO_ENABLED=true
```

**Resultado Esperado**:
- Nenhuma janela é aberta localmente
- Streaming disponível em http://[IP]:8080/stream
- Todas as informações sobrepostas visíveis no streaming
- Menor uso de recursos do sistema

### 6. Streaming Sem Informações

**Objetivo**: Fornecer streaming de vídeo limpo sem sobreposições.

**Configuração**:
```env
# .env
STREAMING_ENABLED=true
STREAMING_PORT=8000
STREAMING_HOST=0.0.0.0
DISPLAY_ENABLED=false
DISPLAY_INFO_ENABLED=false
```

**Resultado Esperado**:
- Streaming disponível com vídeo limpo
- Nenhuma informação sobreposta
- Útil para gravação ou análise posterior

## Configurações Avançadas

### Otimização de Desempenho

```python
# config.py
CAMERA_BUFFER_SIZE = 1
CAMERA_MAX_DISCARD_FRAMES = 3
CAMERA_RESET_FRAME_COUNT = 300
ENABLE_CAMERA_RESET = False
```

### Ajustes de Detecção

```python
# config.py
FRAME_VARIANCE_THRESHOLD = 5
MAX_CONSECUTIVE_FAILURES = 3
MIN_ACTIVITY_DURATION_TO_REGISTER = 5  # Apenas registra atividades com mais de 5 segundos
```