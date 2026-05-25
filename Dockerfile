# Build frontend
# Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
RUN npm run build

# Build backend
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY samples ./samples

# Copy frontend build directly
COPY --from=frontend-build /app/frontend/dist /app/backend/static

WORKDIR /app/backend
RUN python3 manage.py collectstatic --noinput
EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]