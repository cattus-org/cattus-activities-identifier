# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Sistema de cache para posição do pote de ração
- Detecção dinâmica de novos gatos
- Configuração de thresholds para detecção de atividade
- Sistema de logging completo
- Tratamento robusto de erros e reconexão automática
- Interface visual com informações em tempo real
- Integração com API externa para armazenamento de dados
- Suporte a câmeras RTSP
- Estimativa de pose 3D dos marcadores
- Análise temporal com janela deslizante
- Mapeamento configurável de tipos de atividade
- Cleanup automático de gatos inativos
- Streaming via FastAPI com informações sobrepostas
- Configuração flexível para exibição local e streaming
- Opções para habilitar/desabilitar interface e informações

### Melhorado
- Otimização do algoritmo de detecção de atividade
- Melhoria no gerenciamento de recursos da câmera
- Aperfeiçoamento do sistema de notificações
- Aprimoramento da detecção de marcadores ArUco
- Otimização do processo de finalização do sistema

### Corrigido
- Problemas de vazamento de memória na câmera
- Erros de reconexão com a API
- Problemas de detecção em ambientes com pouca luz
- Correções no cálculo de distâncias 3D
- Ajustes na detecção de início/fim de atividades

### Planejado
- Suporte a múltiplos potes simultaneamente
- Interface web para monitoramento remoto
- Análise de padrões comportamentais
- Notificações push (Telegram, email)
- Suporte a múltiplas câmeras
- Detecção de outros comportamentos (dormir, brincar)
- Calibração automática de câmera
- Dashboard com estatísticas
- Exportação de dados para CSV/Excel
- Integração com sistemas veterinários

## [1.0.0] - 2024-01-15

### Adicionado
- Sistema completo de monitoramento de atividades de gatos
- Detecção automática de marcadores ArUco
- Rastreamento em tempo real de posições 3D
- Análise de atividades baseada em proximidade
- Integração com API externa para armazenamento de dados
- Interface visual com informações em tempo real
- Sistema de logging completo
- Configuração flexível via arquivo de configuração
- Tratamento robusto de erros e reconexão automática
- Suporte a múltiplos gatos simultâneos
- Detecção dinâmica de novos gatos
- Cleanup automático de gatos inativos
- Notificações de início e fim de atividades
- Suporte a câmeras RTSP
- Estimativa de pose 3D dos marcadores
- Análise temporal com janela deslizante
- Mapeamento configurável de tipos de atividade

### Componentes Principais
- **main.py**: Orquestrador principal do sistema
- **config.py**: Centralizador de configurações
- **marker_detector.py**: Detector de marcadores ArUco
- **activity_tracker.py**: Rastreador de atividades
- **camera_manager.py**: Gerenciador de câmera RTSP
- **display_manager.py**: Interface visual
- **api_client.py**: Cliente para comunicação com API
- **activity_notifier.py**: Notificador de atividades

### Características Técnicas
- Suporte ao dicionário ArUco DICT_4X4_50
- Cálculo de distâncias 3D precisas
- Thresholds configuráveis para detecção de atividade
- Tempos mínimos para evitar detecções falsas
- Reconexão automática de câmera e API
- Logs estruturados com diferentes níveis
- Configuração via variáveis de ambiente
- Tratamento de múltiplos gatos independentes

### Dependências
- opencv-python==4.11.0.86
- numpy==2.1.1
- requests==2.32.4
- python-dotenv==1.0.0
- certifi==2025.8.3
- charset-normalizer==3.4.3
- idna==3.10
- urllib3==2.5.0

### Configurações Padrão
- Threshold de entrada: 10cm
- Threshold de saída: 20cm
- Tempo mínimo para iniciar: 2.0s
- Tempo mínimo para parar: 2.0s
- Janela de suavização: 5 amostras
- Timeout da API: 10s
- Resolução padrão: 1920x1080
- Buffer da câmera: 1 frame

### Documentação
- README.md: Visão geral e guia básico
- TECHNICAL_DOCS.md: Documentação técnica detalhada
- INSTALLATION.md: Guia de instalação e configuração
- EXAMPLES.md: Exemplos de uso e casos de teste
- .env.example: Arquivo de exemplo para configurações

### Testes
- Teste de conectividade de câmera
- Teste de comunicação com API
- Teste de detecção de marcadores ArUco
- Teste de cálculo de distâncias
- Teste de rastreamento de atividades
- Teste de múltiplos gatos
- Teste de reconexão automática
- Teste de performance (FPS)

### Logs e Monitoramento
- Logs em arquivo: cattus_activities.log
- Logs no console em tempo real
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Rotação automática de logs
- Informações de performance e debug

### API Integration
- Autenticação via API key
- Endpoints para criar e finalizar atividades
- Teste de conectividade (health check)
- Timeout configurável
- Retry automático para falhas temporárias
- Mapeamento de tipos de atividade

### Interface Visual
- Janela redimensionável
- Exibição de marcadores detectados
- Informações de distância em tempo real
- Status de atividades
- IDs dos marcadores
- Eixos 3D dos marcadores
- Cores diferenciadas para gatos e potes

### Tratamento de Erros
- Reconexão automática de câmera
- Fallback para falhas de API
- Cleanup automático ao sair
- Logs detalhados de erros
- Timeouts configuráveis
- Validação de dados de entrada

---

## Versionamento

Este projeto segue o [Semantic Versioning](https://semver.org/):

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades adicionadas de forma compatível
- **PATCH**: Correções de bugs compatíveis

### Convenções de Commit

Este projeto usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Mudanças de formatação
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Mudanças em ferramentas e configurações

### Exemplos de Commits

```
feat(detector): adicionar suporte a múltiplos dicionários ArUco
fix(camera): corrigir reconexão automática após timeout
docs(readme): atualizar guia de instalação
refactor(tracker): melhorar algoritmo de detecção de atividade
test(api): adicionar testes de integração
chore(deps): atualizar dependências do OpenCV
```

### Branches

- `main`: Branch principal com código estável
- `develop`: Branch de desenvolvimento
- `feature/*`: Branches para novas funcionalidades
- `fix/*`: Branches para correções
- `release/*`: Branches para preparação de releases

### Tags

As tags seguem o formato `v{MAJOR}.{MINOR}.{PATCH}`:

- `v1.0.0`: Primeira versão estável
- `v1.1.0`: Nova funcionalidade menor
- `v1.0.1`: Correção de bug

### Roadmap

#### v1.1.0 - Melhorias de Usabilidade
- [ ] Interface web básica
- [ ] Configuração via interface
- [ ] Exportação de dados
- [ ] Notificações por email

#### v1.2.0 - Múltiplos Potes
- [ ] Suporte a vários potes simultaneamente
- [ ] Diferentes tipos de atividade por pote
- [ ] Configuração dinâmica de potes
- [ ] Estatísticas por pote

#### v2.0.0 - Arquitetura Distribuída
- [ ] Suporte a múltiplas câmeras
- [ ] Processamento distribuído
- [ ] API REST completa
- [ ] Dashboard web avançado
- [ ] Análise de padrões comportamentais

#### v2.1.0 - Inteligência Artificial
- [ ] Detecção sem marcadores (IA)
- [ ] Reconhecimento facial de gatos
- [ ] Análise comportamental avançada
- [ ] Predição de problemas de saúde

### Compatibilidade

#### Versões Suportadas do Python
- Python 3.8+
- Python 3.9 (recomendado)
- Python 3.10
- Python 3.11

#### Sistemas Operacionais
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+
- Debian 10+
- CentOS 8+

#### Dependências Críticas
- OpenCV 4.5+
- NumPy 1.20+
- Requests 2.25+

### Migração entre Versões

#### De v0.x para v1.0.0
- Atualizar arquivo de configuração
- Verificar compatibilidade da API
- Atualizar marcadores ArUco se necessário

#### Futuras Migrações
- Guias de migração serão fornecidos para mudanças breaking
- Scripts de migração automática quando possível
- Período de suporte para versões anteriores

### Suporte

#### Versões com Suporte Ativo
- v1.0.x: Suporte completo (bugs e segurança)

#### Versões com Suporte de Segurança
- Nenhuma ainda (primeira versão)

#### Versões Descontinuadas
- Nenhuma ainda (primeira versão)

### Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adicionar nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Nota**: Este changelog será atualizado a cada nova versão. Para ver todas as mudanças, consulte o histórico de commits no repositório.