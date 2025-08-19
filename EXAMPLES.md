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
```

**Resultado Esperado**:
- Gato se aproxima → Sistema detecta → Inicia atividade "eating"
- Gato se afasta → Sistema detecta → Finaliza atividade
- API recebe notificações de início e fim

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
- Adicionar iluminação IR se necessário

**Configuração**:
```python
# Marcadores maiores
DEFAULT_MARKER_SIZE = 0.05  # 5cm

# Parâmetros mais tolerantes
ENTER_THRESH = 0.20
EXIT_THRESH = 0.30
WINDOW_SIZE = 7  # Mais amostras para suavizar
```

## Casos de Teste

### Teste 1: Detecção de Marcadores

**Objetivo**: Verificar se o sistema detecta corretamente os marcadores ArUco.

**Procedimento**:
1. Executar o sistema
2. Posicionar marcador ID 10 (pote) na frente da câmera
3. Posicionar marcador ID 1 (gato) na frente da câmera
4. Verificar se ambos aparecem na tela com IDs corretos

**Resultado Esperado**:
```
[INFO] Novo gato detectado: ID 1
Tela mostra: "1 (ID: 1) - GATO" e "Pote Racao (ID: 10) - POTE"
```

**Critérios de Sucesso**:
- [ ] Marcadores são detectados consistentemente
- [ ] IDs são exibidos corretamente
- [ ] Eixos 3D são desenhados nos marcadores

### Teste 2: Cálculo de Distância

**Objetivo**: Verificar se as distâncias são calculadas corretamente.

**Procedimento**:
1. Posicionar pote a uma distância conhecida (ex: 30cm)
2. Posicionar gato a distâncias variadas
3. Verificar se as distâncias exibidas correspondem às reais

**Resultado Esperado**:
```
Distância real: 30cm → Sistema mostra: ~0.30m
Distância real: 10cm → Sistema mostra: ~0.10m
```

**Critérios de Sucesso**:
- [ ] Erro máximo de ±5cm para distâncias até 50cm
- [ ] Distâncias são atualizadas em tempo real
- [ ] Valores são consistentes entre frames

### Teste 3: Detecção de Atividade

**Objetivo**: Verificar se o sistema detecta corretamente início e fim de atividades.

**Procedimento**:
1. Posicionar gato longe do pote (>30cm)
2. Aproximar gradualmente até <10cm
3. Manter próximo por 5 segundos
4. Afastar gradualmente até >25cm
5. Verificar logs e notificações

**Resultado Esperado**:
```
[INFO] Gato 1 iniciou atividade: eating
[INFO] Atividade criada na API: ID 123
[INFO] Gato 1 finalizou atividade: eating
[INFO] Atividade finalizada na API: ID 123
```

**Critérios de Sucesso**:
- [ ] Atividade inicia apenas após tempo mínimo
- [ ] Atividade finaliza apenas após tempo mínimo
- [ ] API recebe notificações corretas
- [ ] Estados são exibidos corretamente na tela

### Teste 4: Múltiplos Gatos Simultâneos

**Objetivo**: Verificar rastreamento independente de múltiplos gatos.

**Procedimento**:
1. Posicionar 2 gatos (IDs 1 e 2) longe do pote
2. Aproximar gato 1 primeiro
3. Aproximar gato 2 enquanto gato 1 ainda está próximo
4. Afastar gato 1 primeiro
5. Afastar gato 2 depois

**Resultado Esperado**:
```
10:00 - Gato 1 inicia eating
10:02 - Gato 2 inicia eating (independente)
10:05 - Gato 1 finaliza eating
10:07 - Gato 2 finaliza eating
```

**Critérios de Sucesso**:
- [ ] Cada gato é rastreado independentemente
- [ ] Atividades não interferem entre si
- [ ] API recebe notificações separadas
- [ ] Estados são exibidos corretamente para ambos

### Teste 5: Reconexão de Câmera

**Objetivo**: Verificar recuperação automática de falhas de conexão.

**Procedimento**:
1. Iniciar sistema normalmente
2. Desconectar cabo de rede da câmera
3. Aguardar tentativas de reconexão
4. Reconectar cabo de rede
5. Verificar se sistema retoma funcionamento

**Resultado Esperado**:
```
[ERROR] Erro ao capturar frame da câmera
[INFO] Tentativa 1/3 de reconexão com a câmera
[INFO] Tentativa 2/3 de reconexão com a câmera
[INFO] Câmera reconectada com sucesso
```

**Critérios de Sucesso**:
- [ ] Sistema detecta falha de conexão
- [ ] Tentativas de reconexão são realizadas
- [ ] Sistema retoma funcionamento após reconexão
- [ ] Não há travamento ou crash

### Teste 6: Falha de API

**Objetivo**: Verificar comportamento quando API está indisponível.

**Procedimento**:
1. Configurar URL de API inválida
2. Iniciar sistema
3. Simular atividade de gato
4. Verificar logs e comportamento

**Resultado Esperado**:
```
[WARNING] Não foi possível conectar com a API
[ERROR] Erro ao criar atividade na API: Connection refused
[INFO] Sistema continua funcionando localmente
```

**Critérios de Sucesso**:
- [ ] Sistema detecta falha da API
- [ ] Funcionamento local continua normal
- [ ] Logs registram tentativas e falhas
- [ ] Interface visual continua funcionando

### Teste 7: Limpeza de Gatos Inativos

**Objetivo**: Verificar remoção de gatos que saíram do campo de visão.

**Procedimento**:
1. Detectar gato próximo ao pote
2. Remover gato do campo de visão da câmera
3. Aguardar processo de limpeza
4. Verificar se gato foi removido do rastreamento

**Resultado Esperado**:
```
[INFO] Gato 1 não detectado há 30 segundos
[INFO] Removendo gato 1 do rastreamento
[INFO] Finalizando atividade ativa do gato 1
```

**Critérios de Sucesso**:
- [ ] Gatos inativos são identificados
- [ ] Atividades ativas são finalizadas
- [ ] Memória é liberada corretamente
- [ ] API é notificada sobre finalizações

## Scripts de Teste Automatizado

### Teste de Conectividade

```python
#!/usr/bin/env python3
"""
Script para testar conectividade básica do sistema
"""

import cv2
import requests
from config import Config

def test_camera_connection():
    """Testa conexão com a câmera"""
    config = Config()
    cap = cv2.VideoCapture(config.RTSP_URL)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Câmera conectada e funcionando")
            return True
        else:
            print("✗ Câmera conectada mas não retorna frames")
    else:
        print("✗ Falha ao conectar com a câmera")
    
    cap.release()
    return False

def test_api_connection():
    """Testa conexão com a API"""
    config = Config()
    
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/health",
            headers={"x-api-key": config.API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ API conectada e respondendo")
            return True
        else:
            print(f"✗ API retornou status {response.status_code}")
    except Exception as e:
        print(f"✗ Erro ao conectar com API: {e}")
    
    return False

def test_aruco_detection():
    """Testa detecção de marcadores ArUco"""
    # Criar marcador de teste
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, 1, 200)
    
    # Detectar marcador
    detector = cv2.aruco.ArucoDetector(aruco_dict)
    corners, ids, _ = detector.detectMarkers(marker_img)
    
    if ids is not None and len(ids) > 0:
        print("✓ Detecção ArUco funcionando")
        return True
    else:
        print("✗ Falha na detecção ArUco")
        return False

if __name__ == "__main__":
    print("=== Teste de Conectividade ===")
    
    tests = [
        ("Câmera", test_camera_connection),
        ("API", test_api_connection),
        ("ArUco", test_aruco_detection)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTestando {name}...")
        results.append(test_func())
    
    print(f"\n=== Resultado ===")
    print(f"Testes passaram: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ Sistema pronto para uso!")
    else:
        print("✗ Alguns componentes precisam de atenção")
```

### Teste de Performance

```python
#!/usr/bin/env python3
"""
Script para testar performance do sistema
"""

import time
import cv2
import numpy as np
from config import Config
from marker_detector import MarkerDetector

def test_fps():
    """Testa FPS de processamento"""
    config = Config()
    detector = MarkerDetector(config)
    cap = cv2.VideoCapture(config.RTSP_URL)
    
    if not cap.isOpened():
        print("✗ Não foi possível conectar com a câmera")
        return
    
    frame_count = 0
    start_time = time.time()
    test_duration = 10  # segundos
    
    print(f"Testando FPS por {test_duration} segundos...")
    
    while time.time() - start_time < test_duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Processar frame
        posicoes = detector.detect_markers(frame)
        frame_count += 1
    
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time
    
    print(f"FPS médio: {fps:.2f}")
    print(f"Frames processados: {frame_count}")
    
    cap.release()
    
    # Avaliar performance
    if fps >= 15:
        print("✓ Performance excelente")
    elif fps >= 10:
        print("⚠ Performance adequada")
    else:
        print("✗ Performance baixa - considere otimizações")

if __name__ == "__main__":
    test_fps()
```

## Cenários de Produção

### Configuração para Casa com 3 Gatos

```python
# config.py para ambiente doméstico
class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        
        # Configurações otimizadas para casa
        self.ENTER_THRESH = 0.12      # 12cm - mais sensível
        self.EXIT_THRESH = 0.18       # 18cm - evita oscilações
        self.MIN_TIME_START = 1.5     # 1.5s - mais responsivo
        self.MIN_TIME_STOP = 3.0      # 3s - evita finalizações prematuras
        self.WINDOW_SIZE = 7          # Mais suavização
        
        # Múltiplos potes
        self.POTES = {
            10: {"nome": "Pote Racao", "tipo": "comida"},
            11: {"nome": "Pote Agua", "tipo": "agua"}
        }
        
        # Gatos conhecidos
        self.GATOS_CONHECIDOS = {
            1: {"nome": "Mimi", "cor": (255, 0, 0)},
            2: {"nome": "Fifi", "cor": (0, 255, 0)},
            3: {"nome": "Lulu", "cor": (0, 0, 255)}
        }
```

### Configuração para Clínica Veterinária

```python
# config.py para ambiente clínico
class ClinicConfig(Config):
    def __init__(self):
        super().__init__()
        
        # Configurações para ambiente controlado
        self.ENTER_THRESH = 0.08      # 8cm - muito preciso
        self.EXIT_THRESH = 0.15       # 15cm - rápida detecção
        self.MIN_TIME_START = 0.5     # 0.5s - muito responsivo
        self.MIN_TIME_STOP = 1.0      # 1s - rápida finalização
        
        # Logging detalhado
        self.LOG_LEVEL = "DEBUG"
        
        # API sempre habilitada
        self.API_ENABLED = True
        self.API_TIMEOUT = 5
        
        # Múltiplas câmeras (futuro)
        self.CAMERAS = {
            "sala1": "rtsp://admin:pass@192.168.1.100:554/onvif1",
            "sala2": "rtsp://admin:pass@192.168.1.101:554/onvif1"
        }
```

## Troubleshooting por Cenário

### Problema: Detecções Intermitentes

**Sintomas**:
- Marcadores aparecem e desaparecem
- Atividades iniciam e param rapidamente
- Distâncias oscilam muito

**Soluções**:
```python
# Aumentar janela de suavização
WINDOW_SIZE = 10

# Aumentar tempos mínimos
MIN_TIME_START = 3.0
MIN_TIME_STOP = 3.0

# Ajustar thresholds
ENTER_THRESH = 0.08
EXIT_THRESH = 0.25  # Maior diferença entre entrada e saída
```

### Problema: Gatos Não Detectados

**Sintomas**:
- Marcadores não aparecem na tela
- Nenhuma atividade é registrada
- Logs mostram "Nenhum marcador detectado"

**Soluções**:
1. **Verificar iluminação**:
   - Evitar sombras nos marcadores
   - Adicionar luz difusa se necessário

2. **Verificar marcadores**:
   - Limpar marcadores (sem reflexos)
   - Verificar se não estão danificados
   - Confirmar tamanho adequado

3. **Ajustar câmera**:
   - Verificar foco
   - Ajustar ângulo
   - Confirmar resolução

### Problema: API Não Recebe Dados

**Sintomas**:
- Sistema funciona localmente
- Logs mostram erros de API
- Dados não aparecem no sistema externo

**Soluções**:
```python
# Verificar configurações
API_ENABLED = True
API_BASE_URL = "http://correct-url:3000"
API_KEY = "correct-api-key"

# Testar conectividade
curl -H "x-api-key: key" http://url:3000/health

# Verificar logs específicos
grep "api\|http" cattus_activities.log -i
```

---

Esta documentação de exemplos e testes deve ajudar na validação e uso correto do sistema em diferentes cenários.