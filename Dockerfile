# Usamos una versión ligera y moderna de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el script del entorno al contenedor
COPY app.py .

# Comando por defecto para ejecutar el entrenamiento e integración general
CMD ["python", "app.py"]
