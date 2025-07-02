FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos curl y build-essential para compilar paquetes nativos
RUN apt-get update && apt-get install -y curl build-essential

# Instalamos uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copiamos sólo pyproject.toml y uv.lock para cachear
COPY pyproject.toml uv.lock ./

# Instalamos las dependencias del proyecto actual con dev dependencies
RUN uv pip install --system --no-compile --editable .[dev]

# Copiamos el código
COPY . .

# Instalar wait-for-it script para esperar la base de datos
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /wait-for-it.sh

# Comando que espera la DB y luego ejecuta migraciones y servidor
CMD ["/wait-for-it.sh", "db:5432", "--timeout=60", "--", "sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
