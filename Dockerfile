# Use official Python base image with a slim version
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    METRICS_PORT=8000

# Create non-root user for running the application
RUN useradd -ms /bin/bash appuser

# Set working directory
WORKDIR $APP_HOME

# Copy only necessary files to reduce image size
COPY ./requirements.txt ./

# Install necessary packages and clean up afterwards
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Change ownership of the application directory
RUN chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose metrics port
EXPOSE $METRICS_PORT

# Run the application using uvicorn
CMD ["uvicorn", "disk_metrics_exporter:app", "--host", "0.0.0.0", "--port", "8000"]
