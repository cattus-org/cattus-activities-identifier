# Guia de Instalação e Configuração

## Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS 10.15+, ou Linux (Ubuntu 18.04+)
- Python 3.8 ou superior

### Hardware
- Câmera IP com suporte RTSP
- Computador com pelo menos 4GB RAM
- Processador com suporte a instruções AVX (para OpenCV otimizado)

### Marcadores ArUco
- Impressora para imprimir marcadores
- Papel de boa qualidade (preferencialmente fosco)
- Marcadores do dicionário DICT_4X4_50

## Instalação Passo a Passo

### 1. Preparação do Ambiente

#### Windows
```bash
# Instalar Python 3.8+ do site oficial
# https://www.python.org/downloads/

# Verificar instalação
python --version
pip --version
```

#### macOS
```bash
# Usando Homebrew
brew install python@3.9

# Ou usando pyenv
pyenv install 3.9.0
pyenv global 3.9.0
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install libopencv-dev python3-opencv
```

### 2. Clone do Projeto

```bash
git clone <url-do-repositorio>
cd sistema-monitoramento-gatos
```

### 3. Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Instalação de Dependências

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar instalação do OpenCV
python -c "import cv2; print(cv2.__version__)"
```

### 5. Configuração do Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações
nano .env  # ou seu editor preferido
```

### 6. Configuração da Câmera

#### Teste de Conectividade
```bash
# Testar URL RTSP
ffplay rtsp://usuario:senha@ip:porta/stream

# Ou usando VLC Media Player
# Abrir VLC → Mídia → Abrir Fluxo de Rede → Inserir URL RTSP
```

#### Configurações Comuns de Câmeras

**Hikvision**
```
rtsp://admin:senha@192.168.1.100:554/Streaming/Channels/101
```

**Dahua**
```
rtsp://admin:senha@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

**Axis**
```
rtsp://admin:senha@192.168.1.100:554/axis-media/media.amp
```

**Genérica**
```
rtsp://admin:senha@192.168.1.100:554/onvif1
```

### 7. Preparação dos Marcadores ArUco

#### Geração de Marcadores

```python
# Script para gerar marcadores (opcional)
import cv2
import numpy as np

# Dicionário ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Gerar marcador ID 10 (pote)
marker_img = cv2.aruco.generateImageMarker(aruco_dict, 10, 200)
cv2.imwrite('marker_10_pote.png', marker_img)

# Gerar marcadores para gatos (IDs 1-9)
for i in range(1, 10):
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, i, 200)
    cv2.imwrite(f'marker_{i}_gato.png', marker_img)
```

#### Impressão dos Marcadores

1. **Tamanho recomendado**: 3x3 cm para gatos, 4x4 cm para pote
2. **Qualidade**: 300 DPI mínimo
3. **Papel**: Fosco ou semi-fosco (evita reflexos)
4. **Fixação**: Cole em superfície rígida (papelão, plástico)

#### Posicionamento

- **Pote**: Fixar na lateral ou base do pote
- **Gatos**: Coleira com marcador (cuidado com segurança)
- **Altura**: Marcadores devem ficar visíveis para a câmera
- **Iluminação**: Evitar sombras ou reflexos diretos

## Configuração Detalhada

### 1. Arquivo config.py

```python
# Principais configurações a ajustar:

# URL da câmera RTSP
RTSP_URL = "rtsp://admin:senha@192.168.1.100:554/onvif1"

# ID do marcador do pote (deve corresponder ao marcador impresso)
POTE_RACAO_ID = 10

# Thresholds de distância (ajustar conforme ambiente)
ENTER_THRESH = 0.10  # 10cm para iniciar atividade
EXIT_THRESH = 0.20   # 20cm para finalizar atividade

# Tempos mínimos (evita detecções falsas)
MIN_TIME_START = 2.0  # 2 segundos para confirmar início
MIN_TIME_STOP = 2.0   # 2 segundos para confirmar fim
```

### 2. Calibração da Câmera (Opcional)

Para melhor precisão, calibre a câmera:

```python
# Matriz da câmera (ajustar conforme calibração)
camera_matrix = np.array([
    [fx,  0, cx],  # fx = distância focal X, cx = centro X
    [ 0, fy, cy],  # fy = distância focal Y, cy = centro Y
    [ 0,  0,  1]
], dtype=np.float32)

# Coeficientes de distorção
dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
```

### 3. Configuração da API

#### Arquivo .env
```env
API_BASE_URL=http://localhost:3000
API_KEY=sua_chave_api_aqui
```

#### Teste de Conectividade
```bash
# Testar conexão com a API
curl -H "x-api-key: sua_chave" http://localhost:3000/health
```

## Execução e Testes

### 1. Teste Básico

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Executar sistema
python main.py
```

### 2. Verificação de Funcionamento

#### Checklist de Teste:
- [ ] Câmera conecta e exibe imagem
- [ ] Marcadores são detectados (aparecem IDs na tela)
- [ ] Distâncias são calculadas e exibidas
- [ ] Estados de atividade mudam conforme aproximação
- [ ] Logs são gerados no console e arquivo
- [ ] API recebe notificações (se habilitada)

### 3. Solução de Problemas Comuns

#### Câmera não conecta
```bash
# Verificar conectividade
ping 192.168.1.100

# Testar URL RTSP
ffplay rtsp://admin:senha@192.168.1.100:554/onvif1

# Verificar logs
tail -f cattus_activities.log
```

#### Marcadores não detectados
- Verificar iluminação (evitar sombras/reflexos)
- Confirmar qualidade de impressão
- Ajustar posicionamento da câmera
- Verificar se marcadores estão limpos

#### API não responde
```bash
# Testar conectividade
curl -H "x-api-key: sua_chave" http://localhost:3000/health

# Verificar logs de erro
grep "ERROR" cattus_activities.log
```

## Configuração de Produção

### 1. Serviço do Sistema (Linux)

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/cattus-monitor.service
```

```ini
[Unit]
Description=Cattus Activity Monitor
After=network.target

[Service]
Type=simple
User=cattus
WorkingDirectory=/home/cattus/sistema-monitoramento-gatos
Environment=PATH=/home/cattus/sistema-monitoramento-gatos/venv/bin
ExecStart=/home/cattus/sistema-monitoramento-gatos/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar serviço
sudo systemctl enable cattus-monitor
sudo systemctl start cattus-monitor
sudo systemctl status cattus-monitor
```

### 2. Monitoramento e Logs

```bash
# Visualizar logs em tempo real
sudo journalctl -u cattus-monitor -f

# Rotação de logs
sudo nano /etc/logrotate.d/cattus-monitor
```

```
/home/cattus/sistema-monitoramento-gatos/cattus_activities.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 cattus cattus
}
```

### 3. Backup e Recuperação

```bash
# Script de backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/cattus_backup_$DATE.tar.gz \
    /home/cattus/sistema-monitoramento-gatos \
    --exclude=venv \
    --exclude=__pycache__ \
    --exclude=*.log
```

## Manutenção

### 1. Atualizações

```bash
# Atualizar dependências
pip install -r requirements.txt --upgrade

# Verificar compatibilidade
python -c "import cv2, numpy, requests; print('OK')"
```

### 2. Limpeza de Logs

```bash
# Limpar logs antigos
find . -name "*.log" -mtime +30 -delete

# Compactar logs
gzip cattus_activities.log.old
```

### 3. Monitoramento de Performance

```bash
# Verificar uso de recursos
top -p $(pgrep -f "python main.py")

# Verificar espaço em disco
df -h

# Verificar logs de erro
grep -i error cattus_activities.log | tail -20
```

## Suporte

### Logs Importantes

```bash
# Logs do sistema
tail -f cattus_activities.log

# Logs de erro específicos
grep "ERROR\|CRITICAL" cattus_activities.log

# Logs de conexão da câmera
grep "camera\|rtsp" cattus_activities.log -i

# Logs da API
grep "api\|http" cattus_activities.log -i
```

### Informações para Suporte

Ao reportar problemas, inclua:

1. **Versão do Python**: `python --version`
2. **Versão do OpenCV**: `python -c "import cv2; print(cv2.__version__)"`
3. **Sistema operacional**: `uname -a` (Linux/macOS) ou `systeminfo` (Windows)
4. **Logs relevantes**: Últimas 50 linhas do log
5. **Configuração**: Arquivo config.py (sem senhas)
6. **Modelo da câmera**: Marca e modelo da câmera IP

---

Este guia deve cobrir a maioria dos cenários de instalação e configuração. Para casos específicos, consulte a documentação técnica ou abra uma issue no repositório.