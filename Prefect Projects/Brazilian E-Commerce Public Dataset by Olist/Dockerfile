# Use the official Prefect image as the base image
FROM prefecthq/prefect:3-python3.12

RUN pip install --no-cache-dir pymysql polars matplotlib reportlab prefect psycopg2-binary pandas "prefect[sqlalchemy]" "pyarrow>=8.0.0" geoalchemy2

# Set the working directory (optional)
WORKDIR /root/flows

# Specify the default command (this can be overridden by Docker Compose entrypoint)
CMD ["bash"]