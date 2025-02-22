FROM python:3.9-slim

WORKDIR /app

# Install required packages
COPY docker/postgres/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your initialization script and related files
COPY db_init/pg_db_init.py .
COPY models/models.py ./models/
COPY core/config.py ./core/
COPY core/database.py ./core/

# Create __init__.py files to make directories proper packages
RUN touch /app/models/__init__.py
RUN touch /app/core/__init__.py

CMD ["python", "pg_db_init.py"]