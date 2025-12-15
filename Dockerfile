FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install optional dependencies for reports (if reportlab is needed)
RUN pip install reportlab requests

# Copy the entire project
COPY . .

# Set PYTHONPATH so imports work correctly from root
ENV PYTHONPATH=/app

# Run the backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
