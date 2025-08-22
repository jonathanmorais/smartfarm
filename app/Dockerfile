FROM python:3.9-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY app.py .

# Cria diretório de logs
RUN mkdir -p logs

EXPOSE 5000

CMD ["python", "app.py"]
