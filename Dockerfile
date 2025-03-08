FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a volume mount point for the database
VOLUME ["/data"]

# Set environment variables
ENV FRIENDSHIP_DB_PATH=/data/friendships.db
ENV FRIENDSHIP_API_PORT=5000
ENV FRIENDSHIP_API_HOST=0.0.0.0

# Expose the API port
EXPOSE 5000

# Run the API server
CMD ["python", "main.py", "--api"]
