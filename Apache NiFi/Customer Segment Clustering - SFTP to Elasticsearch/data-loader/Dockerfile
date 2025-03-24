FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy our Python scripts into the container
COPY create_index.py /app/create_index.py

# Default command is set via docker-compose command override.
CMD ["sh", "-c", "python /app/create_index.py"]