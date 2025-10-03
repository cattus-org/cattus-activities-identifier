FROM python:3.13-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretório para o .env
RUN mkdir -p /app/config

# Expôr porta para streaming
EXPOSE 8000

# Comando padrão para executar a aplicação
CMD ["python", "-m src.main"]