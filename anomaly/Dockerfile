FROM python:3

# Create app directory
WORKDIR /app

# Copy required files
COPY app.py ./
COPY anomaly.yaml ./
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Expose the port used by your service
EXPOSE 8120

# Run the service
CMD ["python", "app.py"]



