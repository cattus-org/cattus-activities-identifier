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
- Marcadores do dicionário DICT_ARUCO_ORIGINAL

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
cd cattus-activities-identifier
```

### 3. Criação do Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 5. Configuração do Arquivo .env
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
API_BASE_URL=http://localhost:3000
API_KEY=sua_chave_de_api_aqui
```

### 6. Configuração do Sistema
Edite o arquivo `config/config.py` para ajustar as configurações conforme sua necessidade:

```python
# Configurações da câmera RTSP
RTSP_URL = "rtsp://usuario:senha@ip_da_camera:porta/caminho"

# Configurações do pote
POTE_RACAO_ID = 10  # ID do marcador do pote

# Thresholds para detecção de atividade
ENTER_THRESH = 0.15  # Distância para iniciar atividade (metros)
EXIT_THRESH = 0.25   # Distância para finalizar atividade (metros)
MIN_TIME_START = 3.0 # Tempo mínimo para confirmar início (segundos)
MIN_TIME_STOP = 2.0  # Tempo mínimo para confirmar fim (segundos)
```

## Configuração da Câmera

### Câmeras Compatíveis
- Câmeras IP com suporte a RTSP
- Câmeras ONVIF compatíveis
- Câmeras USB (com adaptação)

### Configuração RTSP
Exemplo de URL RTSP:
```
rtsp://admin:minhasenha@192.168.1.100:554/onvif1
```

## Impressão dos Marcadores

### Marcadores para Gatos
- Utilize marcadores do dicionário DICT_ARUCO_ORIGINAL
- Tamanho recomendado: 3x3 cm para ambientes bem iluminados
- Tamanho recomendado: 5x5 cm para ambientes com pouca luz

### Marcador do Pote
- Utilize um ID específico configurado em `POTE_RACAO_ID`
- Posicione o marcador na base do pote de ração

## Teste da Instalação

### 1. Teste de Detecção de Câmera
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('Câmera conectada com sucesso' if cap.isOpened() else 'Falha na conexão da câmera')"
```

### 2. Teste de Detecção de Marcadores
Execute o script de teste de detecção:
```bash
python src/core/marker_detector.py
```

### 3. Teste de Conexão com API
Verifique se a API está acessível:
```bash
curl -H "x-api-key: sua_chave_de_api_aqui" http://localhost:3000/health
```

## Solução de Problemas

### Problemas Comuns

#### Câmera Não Conecta
- Verifique a URL RTSP
- Confirme as credenciais de acesso
- Teste a conexão com um software de visualização RTSP

#### Marcadores Não São Detectados
- Verifique o tamanho e qualidade dos marcadores impressos
- Ajuste a iluminação do ambiente
- Verifique a distância entre a câmera e os marcadores

#### Erros de Conexão com API
- Verifique se a API está em execução
- Confirme a chave de API no arquivo `.env`
- Verifique as configurações de rede

### Logs de Depuração
Os logs do sistema são salvos em `cattus_activities.log` e podem ser consultados para diagnóstico de problemas.

## Atualização do Sistema

### Atualização de Dependências
```bash
pip install -r requirements.txt --upgrade
```

### Atualização do Código
```bash
git pull origin main
```

Após atualizar, verifique se há mudanças nas configurações e ajuste conforme necessário.