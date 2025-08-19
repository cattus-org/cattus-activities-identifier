# Sistema de Monitoramento de Atividades de Gatos

## Visão Geral

Este projeto é um sistema inteligente de monitoramento de atividades de gatos que utiliza visão computacional e marcadores ArUco para rastrear automaticamente quando os gatos se aproximam de potes de comida ou água. O sistema detecta, rastreia e registra atividades como comer, beber e outras interações, enviando os dados para uma API externa para análise e armazenamento.

## Características Principais

- **Detecção Automática**: Utiliza marcadores ArUco para identificar gatos e potes
- **Rastreamento em Tempo Real**: Monitora continuamente as posições e atividades
- **Integração com API**: Envia dados de atividades para sistema externo
- **Interface Visual**: Exibe informações em tempo real na tela
- **Configuração Flexível**: Sistema altamente configurável via arquivo de configuração
- **Logging Completo**: Sistema de logs detalhado para monitoramento e debug
- **Tratamento de Erros**: Robustez na conexão com câmeras e API

## Arquitetura do Sistema

### Componentes Principais

1. **main.py** - Orquestrador principal do sistema
2. **config.py** - Centralizador de configurações
3. **marker_detector.py** - Detector de marcadores ArUco
4. **activity_tracker.py** - Rastreador de atividades
5. **camera_manager.py** - Gerenciador de câmera RTSP
6. **display_manager.py** - Interface visual
7. **api_client.py** - Cliente para comunicação com API
8. **activity_notifier.py** - Notificador de atividades

### Fluxo de Funcionamento

```
Câmera RTSP → Detecção ArUco → Rastreamento → Análise de Atividade → API + Display
```

## Instalação

### Pré-requisitos

- Python 3.8+
- OpenCV com suporte a ArUco
- Câmera IP com suporte RTSP
- Marcadores ArUco impressos

### Dependências

```bash
pip install -r requirements.txt
```

### Configuração do Ambiente

1. Crie um arquivo `.env` na raiz do projeto:

```env
API_BASE_URL=http://localhost:3000
API_KEY=sua_chave_api_aqui
```

2. Configure os marcadores ArUco:
   - Imprima marcadores do dicionário DICT_4X4_50
   - ID 10: Pote de ração (configurável)
   - Outros IDs: Gatos (detecção automática)

## Configuração

### Parâmetros Principais (config.py)

#### Configurações da API
```python
API_BASE_URL = "http://localhost:3000"  # URL da API
API_KEY = "sua_chave"                   # Token de autenticação
API_TIMEOUT = 10                        # Timeout em segundos
API_ENABLED = True                      # Habilitar/desabilitar API
```

#### Configurações da Câmera
```python
RTSP_URL = "rtsp://user:pass@ip:port/stream"  # URL da câmera
CAMERA_WIDTH = 1920                           # Largura da captura
CAMERA_HEIGHT = 1080                          # Altura da captura
CAMERA_BUFFER_SIZE = 1                        # Tamanho do buffer
```

#### Configurações de Detecção
```python
POTE_RACAO_ID = 10              # ID do marcador do pote
ENTER_THRESH = 0.10             # Distância para iniciar atividade
EXIT_THRESH = 0.20              # Distância para finalizar atividade
MIN_TIME_START = 2.0            # Tempo mínimo para iniciar (segundos)
MIN_TIME_STOP = 2.0             # Tempo mínimo para parar (segundos)
```

## Uso

### Execução Básica

```bash
python main.py
```

### Controles da Interface

- **ESC**: Sair do programa
- **Janela de vídeo**: Mostra detecções em tempo real
- **Informações na tela**: Distâncias, estados e IDs dos marcadores

### Logs

O sistema gera logs em:
- **Console**: Informações em tempo real
- **Arquivo**: `cattus_activities.log`

## API Integration

### Endpoints Utilizados

#### Criar Atividade
```http
POST /activities
Content-Type: application/json
x-api-key: {API_KEY}

{
  "cat_id": 1,
  "activity_title": "eat",
  "started_at": "2024-01-01T12:00:00Z"
}
```

#### Finalizar Atividade
```http
PUT /activities/{activity_id}/finish
Content-Type: application/json
x-api-key: {API_KEY}

{
  "finished_at": "2024-01-01T12:05:00Z"
}
```

#### Teste de Conexão
```http
GET /health
x-api-key: {API_KEY}
```

### Mapeamento de Atividades

```python
ACTIVITY_TYPE_MAPPING = {
    "eating": "eat",
    "drinking": "drink",
    "sleeping": "sleep",
    "playing": "play"
}
```

## Detalhes Técnicos

### Detecção de Marcadores

- **Dicionário**: DICT_4X4_50 (OpenCV ArUco)
- **Estimativa de Pose**: Cálculo 3D da posição dos marcadores
- **Detecção Automática**: Gatos são detectados dinamicamente
- **Calibração**: Matriz de câmera configurável

### Algoritmo de Rastreamento

1. **Detecção**: Identifica marcadores no frame
2. **Cálculo de Distância**: Mede distância 3D entre gato e pote
3. **Análise Temporal**: Usa janela deslizante para suavizar detecções
4. **Estados**: Determina início/fim de atividades baseado em thresholds
5. **Notificação**: Envia eventos para API quando estados mudam

### Tratamento de Erros

- **Reconexão Automática**: Câmera e API
- **Timeouts Configuráveis**: Evita travamentos
- **Logs Detalhados**: Para diagnóstico
- **Cleanup Automático**: Finaliza atividades ao sair

## Estrutura de Dados

### Posições Detectadas
```python
posicoes = {
    1: {  # ID do gato
        "tipo": "gato",
        "pos": [x, y, z],  # Posição 3D
        "id": 1
    },
    "Pote Racao": {
        "tipo": "pote",
        "pos": [x, y, z],
        "id": 10
    }
}
```

### Estado de Rastreamento
```python
estado = {
    1: {  # ID do gato
        "Pote Racao": {
            "comendo": True,
            "start_time": datetime,
            "distancias": deque([...]),
            "ultimo_estado": False,
            "tempo_estado": 2.5
        }
    }
}
```

## Troubleshooting

### Problemas Comuns

#### Câmera não conecta
- Verifique URL RTSP
- Teste credenciais
- Confirme conectividade de rede
- Ajuste timeouts

#### Marcadores não detectados
- Verifique iluminação
- Confirme qualidade de impressão
- Ajuste posicionamento
- Verifique calibração da câmera

#### API não responde
- Confirme URL e chave da API
- Teste conectividade
- Verifique logs de erro
- Considere desabilitar temporariamente

### Logs de Debug

Para mais detalhes, altere o nível de log:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Desenvolvimento

### Estrutura do Código

```
├── main.py                 # Ponto de entrada
├── config.py              # Configurações
├── marker_detector.py     # Detecção ArUco
├── activity_tracker.py    # Lógica de rastreamento
├── camera_manager.py      # Gerenciamento de câmera
├── display_manager.py     # Interface visual
├── api_client.py          # Cliente HTTP
├── activity_notifier.py   # Notificações
└── requirements.txt       # Dependências
```

### Extensibilidade

O sistema foi projetado para ser facilmente extensível:

- **Novos tipos de atividade**: Adicione ao mapeamento
- **Diferentes câmeras**: Modifique CameraManager
- **Outras APIs**: Adapte APIClient
- **Novos algoritmos**: Implemente em ActivityTracker

## Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Suporte

Para suporte e dúvidas:
- Abra uma issue no repositório
- Consulte os logs do sistema
- Verifique a documentação da API

---

**Nota**: Este sistema foi desenvolvido especificamente para monitoramento de gatos domésticos e requer marcadores ArUco para funcionamento adequado.