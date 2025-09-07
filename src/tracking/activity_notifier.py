import logging
import threading
from typing import Dict
from datetime import datetime
from ..api.api_client import APIClient

class ActivityNotifier:
    """Gerencia notificações de atividades para a API"""
    
    def __init__(self, api_client: APIClient, activity_mapping: Dict[str, str] = None, enabled: bool = True):
        """
        Inicializa o notificador de atividades
        
        Args:
            api_client: Cliente da API
            activity_mapping: Mapeamento de tipos de atividade (opcional)
            enabled: Se as notificações estão habilitadas
        """
        self.api_client = api_client
        self.activity_mapping = activity_mapping or {}
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
        
        # Dicionário para armazenar IDs das atividades ativas
        # Formato: {(cat_id, activity_type): activity_id}
        self.active_activities: Dict[tuple, int] = {}
        
        # Lock para sincronização de acesso ao dicionário de atividades
        self._lock = threading.Lock()
        
        # Testa conexão com a API se habilitada
        if self.enabled:
            if self.api_client.test_connection():
                self.logger.info("Conexão com API estabelecida com sucesso")
            else:
                self.logger.warning("Não foi possível conectar com a API")
    
    def notify_activity_start(self, cat_id: int, activity_type: str, timestamp: datetime = None) -> bool:
        """
        Notifica o início de uma atividade
        
        Args:
            cat_id: ID do gato
            activity_type: Tipo de atividade
            timestamp: Timestamp do início (padrão: agora)
            
        Returns:
            bool: True se a notificação foi enviada com sucesso
        """
        if not self.enabled:
            self.logger.debug(f"Notificações desabilitadas - ignorando início de atividade: {cat_id} - {activity_type}")
            return True
        
        # Converte tipo de atividade se houver mapeamento
        activity_title = self.activity_mapping.get(activity_type, activity_type)
        
        # Verifica se já existe uma atividade ativa para este gato e tipo
        activity_key = (cat_id, activity_type)
        
        # Usa lock para sincronização de acesso ao dicionário
        with self._lock:
            if activity_key in self.active_activities:
                self.logger.warning(f"Atividade já ativa para Cat ID {cat_id} - {activity_title}")
                return True
        
        self.logger.info(f"Criando nova atividade: Cat ID {cat_id} - {activity_title}")
        
        # Cria a atividade na API
        activity_id = self.api_client.create_activity(cat_id, activity_title, timestamp)
        
        if activity_id:
            # Armazena o ID da atividade com lock
            with self._lock:
                self.active_activities[activity_key] = activity_id
            self.logger.info(f"Atividade criada com sucesso: Cat ID {cat_id} - {activity_title} (Activity ID: {activity_id})")
            return True
        else:
            self.logger.error(f"Falha ao criar atividade: Cat ID {cat_id} - {activity_title}")
            return False
    
    def notify_activity_end(self, cat_id: int, activity_type: str, 
                           start_time: datetime, end_time: datetime = None) -> bool:
        """
        Notifica o fim de uma atividade
        
        Args:
            cat_id: ID do gato
            activity_type: Tipo de atividade
            start_time: Timestamp do início da atividade (não usado, mantido para compatibilidade)
            end_time: Timestamp do fim (padrão: agora)
            
        Returns:
            bool: True se a notificação foi enviada com sucesso
        """
        if not self.enabled:
            self.logger.debug(f"Notificações desabilitadas - ignorando fim de atividade: {cat_id} - {activity_type}")
            return True
        
        # Converte tipo de atividade se houver mapeamento
        activity_title = self.activity_mapping.get(activity_type, activity_type)
        
        # Busca a atividade ativa com lock
        activity_key = (cat_id, activity_type)
        activity_id = None
        
        with self._lock:
            activity_id = self.active_activities.get(activity_key)
        
        if not activity_id:
            self.logger.warning(f"Nenhuma atividade ativa encontrada para finalizar: Cat ID {cat_id} - {activity_title}")
            return False
        
        if end_time is None:
            end_time = datetime.now()
        
        self.logger.info(f"Finalizando atividade: Cat ID {cat_id} - {activity_title} (Activity ID: {activity_id})")
        
        # Finaliza a atividade na API
        success = self.api_client.finish_activity(activity_id, end_time)
        
        if success:
            # Remove a atividade da lista de ativas com lock
            with self._lock:
                if activity_key in self.active_activities:
                    del self.active_activities[activity_key]
            self.logger.info(f"Atividade finalizada com sucesso: Cat ID {cat_id} - {activity_title}")
            return True
        else:
            self.logger.error(f"Falha ao finalizar atividade: Cat ID {cat_id} - {activity_title}")
            return False
    
    def get_active_activities(self) -> Dict[tuple, int]:
        """
        Retorna as atividades ativas
        
        Returns:
            Dict: Dicionário com as atividades ativas
        """
        with self._lock:
            return self.active_activities.copy()
    
    def force_end_activity(self, cat_id: int, activity_type: str, end_time: datetime = None) -> bool:
        """
        Força o fim de uma atividade específica
        
        Args:
            cat_id: ID do gato
            activity_type: Tipo de atividade
            end_time: Timestamp do fim (padrão: agora)
            
        Returns:
            bool: True se a atividade foi finalizada
        """
        activity_key = (cat_id, activity_type)
        activity_id = None
        
        with self._lock:
            activity_id = self.active_activities.get(activity_key)
        
        if not activity_id:
            return False
        
        if end_time is None:
            end_time = datetime.now()
        
        success = self.api_client.finish_activity(activity_id, end_time)
        
        if success:
            with self._lock:
                if activity_key in self.active_activities:
                    del self.active_activities[activity_key]
            self.logger.info(f"Atividade forçadamente finalizada: Cat ID {cat_id} - {activity_type}")
        
        return success
    
    def cleanup_all_activities(self, end_time: datetime = None) -> int:
        """
        Finaliza todas as atividades ativas (útil para limpeza no shutdown)
        
        Args:
            end_time: Timestamp do fim (padrão: agora)
            
        Returns:
            int: Número de atividades finalizadas
        """
        with self._lock:
            if not self.active_activities:
                return 0
        
        if end_time is None:
            end_time = datetime.now()
        
        finalized_count = 0
        activities_to_remove = []
        
        # Copia as atividades ativas para evitar manter o lock durante as requisições
        with self._lock:
            active_activities_copy = self.active_activities.copy()
        
        for activity_key, activity_id in active_activities_copy.items():
            cat_id, activity_type = activity_key
            
            if self.api_client.finish_activity(activity_id, end_time):
                activities_to_remove.append(activity_key)
                finalized_count += 1
                self.logger.info(f"Atividade finalizada na limpeza: Cat ID {cat_id} - {activity_type}")
        
        # Remove as atividades finalizadas
        with self._lock:
            for activity_key in activities_to_remove:
                if activity_key in self.active_activities:
                    del self.active_activities[activity_key]
        
        self.logger.info(f"Limpeza concluída: {finalized_count} atividades finalizadas")
        return finalized_count
    
    def enable_notifications(self):
        """Habilita as notificações"""
        self.enabled = True
        self.logger.info("Notificações habilitadas")
    
    def disable_notifications(self):
        """Desabilita as notificações"""
        self.enabled = False
        self.logger.info("Notificações desabilitadas")