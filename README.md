# Sistema de Monitoramento de Atividades de Gatos

## Visão Geral

Este projeto é um sistema inteligente de monitoramento de atividades de gatos que utiliza visão computacional e marcadores ArUco para rastrear automaticamente quando os gatos se aproximam de potes de comida ou água. O sistema detecta, rastreia e registra atividades como comer, beber e outras interações, enviando os dados para uma API externa para análise e armazenamento.

## Estrutura do Projeto

```
cattus-activities-identifier/
├── src/                          # Código fonte principal
│   ├── main.py                   # Arquivo principal de execução
│   ├── core/                     # Funcionalidades centrais
│   │   └── marker_detector.py    # Detecção de marcadores ArUco
│   ├── managers/                 # Gerenciadores do sistema
│   │   ├── camera_manager.py     # Gerenciamento de câmera
│   │   └── display_manager.py    # Gerenciamento de display
│   ├── tracking/                 # Sistema de rastreamento
│   │   ├── activity_tracker.py   # Rastreamento de atividades
│   │   └── activity_notifier.py  # Notificação de atividades
│   └── api/                      # Integração com APIs
│       └── api_client.py         # Cliente para APIs externas
├── config/                       # Arquivos de configuração
│   └── config.py                 # Configurações do sistema
├── docs/                         # Documentação
│   ├── TECHNICAL_DOCS.md         # Documentação técnica detalhada
│   ├── INSTALLATION.md           # Guia de instalação
│   ├── EXAMPLES.md               # Exemplos de uso
│   └── CHANGELOG.md              # Histórico de mudanças
├── tests/                        # Testes unitários e de integração
│   └── test_system.py            # Testes do sistema
├── requirements.txt              # Dependências do projeto
├── .env.example                  # Exemplo de arquivo de configuração
├── README.md                     # Este arquivo
└── cattus_activities.log         # Arquivo de log do sistema
```

## Características Principais

- **Detecção Automática**: Utiliza marcadores ArUco para identificar gatos e potes
- **Rastreamento em Tempo Real**: Monitora continuamente as posições e atividades
- **Integração com API**: Envia dados de atividades para sistema externo
- **Interface Visual**: Exibe informações em tempo real na tela
- **Configuração Flexível**: Sistema altamente configurável via arquivo de configuração
- **Logging Completo**: Sistema de logs detalhado para monitoramento e debug
- **Tratamento de Erros**: Robustez na conexão com câmeras e APIs
- **Gerenciamento de Câmera**: Reconexão automática e tratamento de falhas

## Como Executar

```bash
# Navegar para o diretório do projeto
cd cattus-activities-identifier

# (Opcional) Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (criar arquivo .env)
cp .env.example .env
# Editar .env com suas configurações

# Executar o sistema
python -m src.main
```

## Testes

O projeto inclui uma estrutura básica de testes em `tests/test_system.py`. Para executar os testes:

```bash
# Executar todos os testes
python -m unittest tests/test_system.py

# Ou executar com mais detalhes
python -m unittest tests/test_system.py -v
```

*Nota: Atualmente os testes são placeholders e precisam ser implementados para cada módulo do sistema.*

## Configuração

As configurações do sistema estão localizadas em `config/config.py`. As principais configurações incluem:

- **Configurações da API**: URL base, chave de API, timeout
- **Configurações de Câmera**: URL RTSP, resolução, parâmetros de reconexão
- **Configurações de Detecção**: Thresholds de proximidade, tamanho dos marcadores
- **Configurações de Interface**: Dimensões da janela de visualização

Consulte a documentação técnica em `docs/TECHNICAL_DOCS.md` para detalhes sobre as opções disponíveis.

## Documentação

- **Instalação**: `docs/INSTALLATION.md`
- **Documentação Técnica**: `docs/TECHNICAL_DOCS.md`
- **Exemplos**: `docs/EXAMPLES.md`
- **Changelog**: `docs/CHANGELOG.md`

## Arquitetura

O sistema utiliza uma arquitetura modular com os seguintes componentes principais:

- **Managers**: Gerenciam recursos como câmera e display
- **Tracking**: Responsável pelo rastreamento e notificação de atividades
- **API**: Integração com sistemas externos
- **Core**: Funcionalidades centrais e utilitários
- **Config**: Centralização das principais configurações do projeto

### Componentes Principais

1. **CameraManager**: Gerencia a conexão com câmeras RTSP, incluindo reconexão automática
2. **MarkerDetector**: Detecta marcadores ArUco nos frames de vídeo
3. **ActivityTracker**: Rastreia as atividades dos gatos com base na proximidade com os potes
4. **ActivityNotifier**: Notifica a API sobre mudanças de estado nas atividades
5. **DisplayManager**: Exibe informações em tempo real na interface visual
6. **APIClient**: Cliente para comunicação com APIs externas

## Estado Atual do Projeto

O sistema está funcional com as seguintes características e melhorias recentes:

- Captura de vídeo via RTSP usando OpenCV com backend FFMPEG.
- Tratamento robusto de conexão com a câmera, incluindo tentativas automáticas de reconexão.
- Melhorias no método de captura de frames para lidar com falhas consecutivas e forçar reconexão, reduzindo artefatos e perda de conexão.
- Detecção e rastreamento de atividades de gatos utilizando marcadores ArUco.
- Envio de dados de atividades para API externa para análise e armazenamento.
- Sistema de logging detalhado para monitoramento e diagnóstico.
- Gerenciamento de gatos inativos com timeout configurável.

Essas melhorias aumentam a estabilidade do sistema e a qualidade do monitoramento em tempo real.

Continuamos trabalhando para aprimorar a detecção, a interface visual e a integração com APIs externas.

## Funcionalidades Planejadas

Consulte `docs/CHANGELOG.md` para ver as funcionalidades planejadas para versões futuras, incluindo:
- Suporte a múltiplos potes simultaneamente
- Interface web para monitoramento remoto
- Análise de padrões comportamentais
- Notificações push (Telegram, email)
- Suporte a múltiplas câmeras
- Detecção de outros comportamentos (dormir, brincar)