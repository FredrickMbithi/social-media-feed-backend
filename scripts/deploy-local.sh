#!/bin/bash

echo "================================"
echo " Local Docker Deployment"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Create superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

# Seed data (optional)
echo "🌱 Seed test data? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec -T web python manage.py seed_data
fi

# Health check
echo "🩺 Checking health..."
sleep 5
curl -f http://localhost:8000/health/ || echo "⚠️  Health check failed"

echo "================================"
echo " ✅ Deployment complete!"
echo "================================"
echo "GraphQL Playground: http://localhost:8000/graphql/"
echo "Admin Panel: http://localhost:8000/admin/"
echo "Nginx (if enabled): http://localhost/"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"
echo "================================"
