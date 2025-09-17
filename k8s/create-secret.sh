#!/bin/bash
# Script to help create base64-encoded credentials for Kubernetes Secret

echo "Database Credential Encoder"
echo "=========================="
echo ""

read -p "Enter database username: " username
read -s -p "Enter database password: " password
echo ""
echo ""

# Encode credentials to base64
username_encoded=$(echo -n "$username" | base64)
password_encoded=$(echo -n "$password" | base64)

echo "Encoded credentials:"
echo "==================="
echo "DB_USER: $username_encoded"
echo "DB_PASSWORD: $password_encoded"
echo ""
echo "Update k8s/secret.yaml with these values."
echo ""
echo "Alternatively, create the secret directly:"
echo "kubectl create secret generic scaffold-credentials \\"
echo "  --from-literal=DB_USER=\"$username\" \\"
echo "  --from-literal=DB_PASSWORD=\"$password\" \\"
echo "  --namespace=database-scaffolding"
