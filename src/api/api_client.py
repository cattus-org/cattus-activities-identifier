import requests
from datetime import datetime
from typing import Dict, Any, Optional
import logging

class APIClient:
    """Cliente para comunicação com a API de atividades dos gatos"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        """
        Inicializa o cliente da API
        
        Args:
            base_url: URL base da API
            api_key: Token de autenticação da API
            timeout: Timeout para requisições em segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configura headers padrão incluindo o token de autenticação
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': api_key
        })
        
        # Configura logging
        self.logger = logging.getLogger(__name__)
    
    def create_activity(self, cat_id: int, activity_title: str, timestamp: datetime = None) -> Optional[int]:
        """
        Cria uma nova atividade na API

        Args:
            cat_id: ID do gato
            activity_title: Título da atividade (eat, drink, etc.)
            timestamp: Timestamp do início da atividade (padrão: agora)

        Returns:
            int: ID da atividade criada ou None se falhou
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Garante que o timestamp tenha o formato correto com 'Z'
        started_at = timestamp.isoformat()
        if not started_at.endswith('Z'):
            started_at += 'Z'

        # Converte cat_id para int Python nativo para evitar problemas de serialização JSON
        # com tipos numpy (como numpy.intc)
        cat_id = int(cat_id)

        payload = {
            'catId': cat_id,
            'title': activity_title,
            'startedAt': started_at,
            'endedAt': started_at  # Inicialmente igual ao startedAt
        }

        return self._create_activity_request(payload)
    
    def finish_activity(self, activity_id: int, end_time: datetime = None) -> bool:
        """
        Finaliza uma atividade existente

        Args:
            activity_id: ID da atividade a ser finalizada
            end_time: Timestamp do fim da atividade (padrão: agora)

        Returns:
            bool: True se a requisição foi bem-sucedida
        """
        if end_time is None:
            end_time = datetime.now()

        # Garante que o timestamp tenha o formato correto com 'Z'
        ended_at = end_time.isoformat()
        if not ended_at.endswith('Z'):
            ended_at += 'Z'

        # Converte activity_id para int Python nativo para evitar problemas de serialização JSON
        activity_id = int(activity_id)

        payload = {
            'endedAt': ended_at
        }

        return self._make_request('PATCH', f'/activities/{activity_id}', payload)
    
    def _create_activity_request(self, data: Dict[Any, Any]) -> Optional[int]:
        """
        Faz uma requisição POST para criar atividade e retorna o ID
        
        Args:
            data: Dados para enviar na requisição
            
        Returns:
            int: ID da atividade criada ou None se falhou
        """
        url = f"{self.base_url}/activities/"
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            # Extrai o ID da resposta
            response_data = response.json()
            activity_id = response_data.get('data').get('id')
            
            if activity_id:
                self.logger.info(f"Atividade criada com sucesso - ID: {activity_id}")
                return int(activity_id)
            else:
                self.logger.error("Resposta da API não contém ID da atividade")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout na criação de atividade: {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão na criação de atividade: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP na criação de atividade: {url} - Status: {e.response.status_code}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Resposta do erro: {e.response.text}")
            return None
        except ValueError as e:
            self.logger.error(f"Erro ao decodificar JSON da resposta: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Erro inesperado na criação de atividade: {url} - {str(e)}")
            return None
    
    def _make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None) -> bool:
        """
        Faz uma requisição HTTP para a API
        
        Args:
            method: Método HTTP (GET, POST, PATCH, etc.)
            endpoint: Endpoint da API
            data: Dados para enviar na requisição
            
        Returns:
            bool: True se a requisição foi bem-sucedida
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'POST' and data:
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == 'PATCH' and data:
                response = self.session.patch(url, json=data, timeout=self.timeout)
            elif method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            else:
                self.logger.error(f"Método HTTP não suportado: {method}")
                return False
            
            # Verifica se a requisição foi bem-sucedida
            response.raise_for_status()
            
            self.logger.info(f"Requisição bem-sucedida: {method} {url} - Status: {response.status_code}")
            
            # Log da resposta para debug (opcional)
            if response.content:
                self.logger.debug(f"Resposta da API: {response.text}")
            
            return True
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout na requisição: {method} {url}")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão: {method} {url}")
            return False
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP: {method} {url} - Status: {e.response.status_code}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Resposta do erro: {e.response.text}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado na requisição: {method} {url} - {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API

        Returns:
            bool: True se a conexão está funcionando
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code in [200, 404, 401]  # 404 também indica que a API está respondendo
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout ao testar conexão com API: {self.base_url}")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão ao testar API: {self.base_url}")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao testar conexão com API: {e}")
            return False