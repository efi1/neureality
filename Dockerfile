# Use an official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the app folder into the container
COPY app/ ./

# Install Python dependencies from app_requirements.txt
RUN pip install --no-cache-dir -r app_requirements.txt

# Start FastAPI app using uvicorn
CMD ["uvicorn", "clients.fastapi.tasks_base:app", "--host", "0.0.0.0", "--port", "8000"]