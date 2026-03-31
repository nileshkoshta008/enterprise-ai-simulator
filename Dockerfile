# Stage 1: Build the React frontend
FROM node:18 AS build-stage
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with FastAPI Python environment
FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY *.py ./
COPY *.yaml ./
COPY *.jsonl ./
COPY *.json ./

# Copy compiled frontend
COPY --from=build-stage /app/frontend/dist /app/frontend/dist

# Expose hugging face spaces default port
EXPOSE 7860

# Run uvicorn server directly
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
