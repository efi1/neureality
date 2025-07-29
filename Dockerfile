# Use an official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the app folder into the container
COPY app/ ./

# Install Python dependencies from app_requirements.txt
RUN pip install --no-cache-dir -r app_requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Expose port for FastAPI/Uvicorn
EXPOSE 8000

# Healthcheck route
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Start FastAPI app using uvicorn
CMD ["uvicorn", "clients.fastapi.tasks_base:app", "--host", "0.0.0.0", "--port", "8000"]