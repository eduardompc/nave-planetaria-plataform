# Imagem oficial do Python mais leve
FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc e bufe a saída do console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Porta padrão exposta pela maioria dos serviços de nuvem
ENV PORT=8050
ENV DEBUG=False

# Diretório de trabalho no contêiner
WORKDIR /app

# Instala as dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto para o contêiner
COPY . /app/

# Garante que a pasta database existe para o SQLite
RUN mkdir -p /app/database

# Inicializa o banco de dados antes do servidor (se necessário)
RUN python init_db.py

# Expõe a porta de rede
EXPOSE 8050

# Executa o servidor usando o Gunicorn em produção
CMD gunicorn app:server --bind 0.0.0.0:$PORT
