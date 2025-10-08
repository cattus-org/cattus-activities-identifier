import cv2
import time
import logging
import threading
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import asyncio
from typing import AsyncGenerator

class StreamingManager:
    """Classe responsável por gerenciar o streaming via FastAPI"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Frame compartilhado para streaming
        self.current_frame = None
        self.frame_lock = threading.Lock()

        # Estado do servidor
        self.server_thread = None
        self.is_running = False

        # Inicializa o app FastAPI apenas se o streaming estiver habilitado
        if self.config.STREAMING_ENABLED:
            self.app = FastAPI(title="Cat Activity Monitor Streaming API")
            self._setup_api_routes()
            self._setup_cors()

    def _setup_cors(self):
        """Configura CORS para permitir acesso cross-origin"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_api_routes(self):
        """Configura as rotas da API"""
        @self.app.get("/")
        async def root():
            return {"message": "Cat Activity Monitor Streaming API"}

        @self.app.get("/stream")
        async def video_feed():
            """Endpoint que fornece o stream de vídeo"""
            return StreamingResponse(self._generate_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

        @self.app.get("/health")
        async def health_check():
            """Endpoint para verificar a saúde do serviço"""
            return {"status": "healthy", "streaming_enabled": self.config.STREAMING_ENABLED}

    async def _generate_stream(self) -> AsyncGenerator[bytes, None]:
        """Gera o stream de vídeo assíncrono"""
        while self.is_running:
            frame_data = None
            with self.frame_lock:
                if self.current_frame is not None:
                    # Converte o frame para JPEG
                    ret, buffer = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        frame_data = frame_bytes

            if frame_data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

            # Pequeno delay para controlar o FPS
            await asyncio.sleep(0.03)  # Aproximadamente 30 FPS

    def update_frame(self, frame):
        """Atualiza o frame atual para streaming"""
        if self.config.STREAMING_ENABLED and self.is_running:
            with self.frame_lock:
                self.current_frame = frame.copy()

    def start_server(self):
        """Inicia o servidor FastAPI em uma thread separada"""
        if not self.config.STREAMING_ENABLED:
            self.logger.info("Streaming está desabilitado nas configurações")
            return

        if self.is_running:
            self.logger.warning("Servidor de streaming já está em execução")
            return

        try:
            self.is_running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.logger.info(f"Servidor de streaming iniciado.")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar servidor de streaming: {e}")
            self.is_running = False

    def _run_server(self):
        """Executa o servidor FastAPI"""
        try:
            uvicorn.run(
                self.app,
                host=self.config.STREAMING_HOST,
                port=self.config.STREAMING_PORT,
                log_level="warning"
            )
        except Exception as e:
            self.logger.error(f"Erro no servidor de streaming: {e}")
        finally:
            self.is_running = False

    def stop_server(self):
        """Para o servidor de streaming"""
        if self.is_running:
            self.is_running = False
            self.logger.info("Servidor de streaming parado")
            self.logger.info("Servidor de streaming parado")