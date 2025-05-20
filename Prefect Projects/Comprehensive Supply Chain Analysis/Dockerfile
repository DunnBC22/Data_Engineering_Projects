# Use the official Prefect image as the base image
FROM prefecthq/prefect:3.0.10-python3.11

# Install the required libraries
RUN apt-get update && apt-get install -y build-essential
RUN pip install pymysql
RUN pip install elasticsearch
RUN pip install polars matplotlib reportlab prefect pandas "prefect[sqlalchemy]" pyarrow>=8.0.0

# Set the working directory (optional)
WORKDIR /root/flows

# Specify the default command (this can be overridden by Docker Compose entrypoint)
CMD ["bash"]