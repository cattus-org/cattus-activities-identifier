# Sistema de Monitoramento de Atividades de Gatos

## Visão Geral

Este projeto é um sistema inteligente de monitoramento de atividades de gatos que utiliza visão computacional e marcadores ArUco para rastrear automaticamente quando os gatos se aproximam de potes de comida ou água. O sistema detecta, rastreia e registra atividades como comer, beber e outras interações, enviando os dados para uma API externa para análise e armazenamento.

## Estrutura do Projeto

```
cattus-activities-identifier/
├── src/                          # Código fonte principal
│   ├── main.py                   # Arquivo principal de execução
│   ├── core/                     # Funcionalidades centrais
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
└── tests/                        # Testes unitários e de integração
```

## Características Principais

- **Detecção Automática**: Utiliza marcadores ArUco para identificar gatos e potes
- **Rastreamento em Tempo Real**: Monitora continuamente as posições e atividades
- **Integração com API**: Envia dados de atividades para sistema externo
- **Interface Visual**: Exibe informações em tempo real na tela
- **Configuração Flexível**: Sistema altamente configurável via arquivo de configuração
- **Logging Completo**: Sistema de logs detalhado para monitoramento e debug
- **Tratamento de Erros**: Robustez na conexão com câmeras e APIs

## Como Executar

```bash
# Navegar para o diretório do projeto
cd cattus-activities-identifier

# Executar o sistema
python src/main.py
```

## Configuração

As configurações do sistema estão localizadas em `config/config.py`. Consulte a documentação técnica em `docs/TECHNICAL_DOCS.md` para detalhes sobre as opções disponíveis.

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

## Estado Atual do Projeto

O sistema está funcional com as seguintes características e melhorias recentes:

- Captura de vídeo via RTSP usando OpenCV com backend FFMPEG.
- Tratamento robusto de conexão com a câmera, incluindo tentativas automáticas de reconexão.
- Melhorias no método de captura de frames para lidar com falhas consecutivas e forçar reconexão, reduzindo artefatos e perda de conexão.
- Detecção e rastreamento de atividades de gatos utilizando marcadores ArUco.
- Envio de dados de atividades para API externa para análise e armazenamento.
- Sistema de logging detalhado para monitoramento e diagnóstico.

Essas melhorias aumentam a estabilidade do sistema e a qualidade do monitoramento em tempo real.

Continuamos trabalhando para aprimorar a detecção, a interface visual e a integração com APIs externas.
