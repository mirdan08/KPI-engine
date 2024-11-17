# Use the official FastAPI/Uvicorn image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /kpi-engine

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY /app .


# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
