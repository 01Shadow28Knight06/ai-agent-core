# Usamos una imagen oficial ligera de Python
FROM python:3.13-slim

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de dependencias para aprovechar el caché de Docker
COPY requirements.txt .

# Instalamos las dependencias sin almacenar caché innecesaria
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código fuente del proyecto al contenedor
COPY . .

# Exponemos el puerto 8000 donde corre FastAPI
EXPOSE 8000

# Comando por defecto para encender el servidor abierto a cualquier IP (0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]