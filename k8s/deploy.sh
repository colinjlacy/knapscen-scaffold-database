#!/bin/bash
# Quick deployment script for Kubernetes

set -e

echo "🚀 Deploying Database Scaffolding Job to Kubernetes"
echo "=================================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot access Kubernetes cluster. Please check your kubectl configuration."
    exit 1
fi

echo "✅ Kubernetes cluster accessible"

# Deploy the resources
echo "📦 Deploying Kubernetes resources..."

if command -v kustomize &> /dev/null; then
    echo "🎛️  Using Kustomize for deployment..."
    kubectl apply -k k8s/
else
    echo "📄 Using kubectl for deployment..."
    kubectl apply -f k8s/
fi

echo "✅ Resources deployed successfully!"

# Wait for the job to start
echo "⏳ Waiting for job to start..."
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/component=job -n database-scaffolding --timeout=60s || true

# Show the job status
echo ""
echo "📊 Job Status:"
kubectl get jobs -n database-scaffolding

echo ""
echo "📋 Pods:"
kubectl get pods -n database-scaffolding

echo ""
echo "🔍 To follow the logs, run:"
echo "kubectl logs -f job/database-scaffold -n database-scaffolding"

echo ""
echo "🧹 To cleanup when done, run:"
echo "kubectl delete namespace database-scaffolding"
