# Use the official Prefect image as the base image
FROM prefecthq/prefect:3-python3.12

# Install the required libraries
RUN apt-get update && apt-get install -y build-essential
RUN pip install polars matplotlib reportlab "prefect[sqlalchemy]" pandas psycopg2-binary geoalchemy2 pyarrow>=8.0.0 cassandra-driver

# Set the working directory (optional)
WORKDIR /root/flows

# Specify the default command (this can be overridden by Docker Compose entrypoint)
CMD ["bash"]