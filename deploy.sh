#!/bin/bash

set -e

echo "🚀 Deploying Nano Ugin on port 4545..."

cd "$(dirname "$0")"

# Простая проверка - просто пытаемся выполнить команду
echo "🐳 Checking Docker..."
docker --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

echo "🐳 Checking Docker Compose..."
docker-compose --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

echo "✅ Docker is available: $(docker --version)"
echo "✅ Docker Compose is available: $(docker-compose --version)"

# Останавливаем старые контейнеры
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Проверяем существование docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Creating basic one..."
    
    # Создаем базовый docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=nano_ugin
      - POSTGRES_USER=nano_user
      - POSTGRES_PASSWORD=nano_password


  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    working_dir: /app/nano_ugin
    ports:
      - "4545:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://nano_user:nano_password@db:5432/nano_ugin
      - DEBUG=True

volumes:
  postgres_data:
EOF
    echo "✅ Created docker-compose.yml"
fi

# Проверяем Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found. Creating one..."
    
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF
    echo "✅ Created Dockerfile"
fi

# Обновляем порт в docker-compose.yml если нужно
if grep -q "8000:8000" docker-compose.yml; then
    echo "🔧 Updating port to 4545..."
    sed -i 's/8000:8000/4545:8000/g' docker-compose.yml
    echo "✅ Port updated to 4545"
fi

# Собираем и запускаем
echo "📦 Building containers..."
docker-compose build --no-cache

echo "🐳 Starting services..."
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
# Ждем пока база данных будет готова
for i in {1..30}; do
    if docker-compose exec db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    else
        if [ $i -eq 30 ]; then
            echo "❌ Database failed to start within 30 seconds"
            echo "📋 Showing database logs:"
            docker-compose logs db
            exit 1
        fi
        echo "⏳ Waiting for database... ($i/30)"
        sleep 1
    fi
done

# Даем дополнительное время
sleep 3

echo "📋 Applying database migrations..."
docker-compose exec web python manage.py migrate --noinput

echo "🔧 Creating superuser..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin');
    print('✅ Superuser created: admin/admin');
else:
    print('⚠️ Superuser already exists');
"

echo "📊 Setting up system data..."
docker-compose exec web python setup_system.py

echo "📦 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo "🔍 Checking services status..."
docker-compose ps

# Даем время приложению запуститься
sleep 5

# Проверяем работу приложения
echo "🔧 Testing application..."
if curl -f http://localhost:4545/ > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
else
    echo "⚠️ Application might be starting up, showing logs..."
    docker-compose logs web --tail=20
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "🌐 Access your application at: http://localhost:4545"
echo "🔑 Admin panel: http://localhost:4545/admin"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Check status: docker-compose ps"
echo "   Run management commands: docker-compose exec web python manage.py <command>"
