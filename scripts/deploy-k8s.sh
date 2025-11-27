#!/bin/bash

echo "================================"
echo " Kubernetes Deployment"
echo "================================"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Apply manifests
echo "📦 Creating namespace..."
kubectl apply -f k8s/01-namespace.yaml
echo "🔧 Creating Postgres and Redis..."
kubectl apply -f k8s/02-postgres.yaml
kubectl apply -f k8s/03-redis.yaml
echo "🌐 Deploying web application..."
kubectl apply -f k8s/04-web.yaml
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n socialfeed --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=web -n socialfeed --timeout=180s || true

echo "================================"
echo " ✅ Deployment complete!"
echo "================================"
echo "Check status: kubectl get pods -n socialfeed"
echo "View logs: kubectl logs -f -l app=web -n socialfeed"
echo "Port forward: kubectl port-forward -n socialfeed svc/web 8000:8000"
echo "================================"
