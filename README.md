# MySQL Database Schema Scaffolding

A Python script that scaffolds a MySQL database schema with tables for corporate customers, users, user roles, and customer relationship touchpoints.

## Features

- **Corporate Customers**: Track company information and subscription tiers (basic, groovy, far-out)
- **User Management**: Link users to corporate customers with role-based access
- **Customer Touchpoints**: Track CRM activities like welcome outreach, onboarding, and follow-ups
- **UUID Primary Keys**: Uses UUID identifiers for all tables
- **Sample Data**: Includes realistic sample data for testing
- **Foreign Key Relationships**: Proper database relationships with referential integrity

## Database Schema

### Tables Created

1. **corporate_customers**
   - Company name and subscription tier
   - Audit fields (created_at, updated_at)

2. **user_roles**
   - Role definitions: customer_account_owner, admin_user, generic_user

3. **users**
   - User information linked to corporate customers and roles
   - Unique email constraint across all users

4. **touchpoints**
   - Customer relationship touchpoint tracking
   - Fields: welcome_outreach, technical_onboarding, follow_up_call, feedback_session

## Setup

### Prerequisites

- Python 3.7+
- MySQL server
- Access to create databases and tables

### Installation

1. Clone this repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure database connection:

   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

### Configuration

Create a `.env` file with your MySQL database credentials:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## Usage

Run the scaffolding script:

```bash
python scaffold_database.py
```

The script will:

1. Connect to your MySQL database
2. Create all required tables with proper schema
3. Insert sample data for testing
4. Display a summary of created records

## Sample Data

The script includes sample data for:

- 5 corporate customers with different subscription tiers
- 3 user roles (customer_account_owner, admin_user, generic_user)
- 9 sample users across different companies
- Customer touchpoint records with realistic dates

## Schema Details

### Subscription Tiers

- `basic`: Entry-level subscription
- `groovy`: Mid-tier subscription  
- `far-out`: Premium subscription

### User Roles

- `customer_account_owner`: Primary account holder
- `admin_user`: Administrative privileges within the account
- `generic_user`: Standard user access

### Touchpoint Types

- `welcome_outreach`: Initial customer contact
- `technical_onboarding`: Technical setup assistance
- `follow_up_call`: Regular check-in calls
- `feedback_session`: Customer feedback collection

## Database Relationships

- Users belong to corporate customers (many-to-one)
- Users have roles (many-to-one)
- Touchpoints belong to corporate customers (one-to-one)
- Foreign key constraints ensure data integrity

## Docker Usage

### Building the Docker Image

```bash
# Build for local architecture
docker build -t knapscen-scaffold-database .

# Build for multiple architectures (requires buildx)
docker buildx build --platform linux/amd64,linux/arm64 -t knapscen-scaffold-database .
```

### Running with Docker

```bash
# Run the container with environment variables
docker run --rm \
  -e DB_HOST=your-mysql-host \
  -e DB_PORT=3306 \
  -e DB_NAME=your_database \
  -e DB_USER=your_username \
  -e DB_PASSWORD=your_password \
  knapscen-scaffold-database
```

### Docker Compose (Recommended for Testing)

The repository includes a `docker-compose.yml` file for easy testing:

```bash
# Start MySQL and run the scaffolding script
docker-compose up --build

# Clean up when done
docker-compose down -v
```

This will:
1. Start a MySQL 8.0 container with a test database
2. Build and run the scaffolding script
3. Create all tables and insert sample data
4. Exit after completion

## Kubernetes Deployment

The repository includes Kubernetes manifests to deploy the scaffolding script as a Job in your cluster.

### Kubernetes Resources

The `k8s/` directory contains:
- `namespace.yaml` - Dedicated namespace for the application
- `configmap.yaml` - Non-sensitive configuration (DB host, port, database name)
- `secret.yaml` - Sensitive database credentials
- `job.yaml` - Job that runs the scaffolding script
- `kustomization.yaml` - Kustomize configuration for easy deployment

### Prerequisites

- Access to a Kubernetes cluster
- kubectl configured to access your cluster
- MySQL database accessible from the cluster
- Docker image pushed to a registry accessible by your cluster

### Quick Deployment

1. **Update configuration:**

   Edit `k8s/configmap.yaml` with your database details:
   ```yaml
   data:
     DB_HOST: "your-mysql-host"  # MySQL service name or external host
     DB_PORT: "3306"
     DB_NAME: "your_database"
   ```

2. **Create database credentials:**

   Use the helper script to encode your credentials:
   ```bash
   ./k8s/create-secret.sh
   ```

   Or create the secret directly:
   ```bash
   kubectl create secret generic scaffold-credentials \
     --from-literal=DB_USER="your_username" \
     --from-literal=DB_PASSWORD="your_password" \
     --namespace=database-scaffolding
   ```

3. **Update the Docker image:**

   Edit `k8s/job.yaml` to point to your Docker image:
   ```yaml
   image: docker.io/yourusername/knapscen-scaffold-database:latest
   ```

4. **Deploy using kubectl:**
   ```bash
   kubectl apply -f k8s/
   ```

   Or using Kustomize:
   ```bash
   kubectl apply -k k8s/
   ```

### Alternative: Using Kustomize

For more advanced deployments, you can customize the resources:

1. **Create an overlay directory:**
   ```bash
   mkdir -p k8s/overlays/production
   ```

2. **Create a custom kustomization.yaml:**
   ```yaml
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization

   resources:
   - ../../base

   images:
   - name: knapscen-scaffold-database
     newName: your-registry.com/knapscen-scaffold-database
     newTag: v1.0.0

   patchesStrategicMerge:
   - job-patch.yaml
   ```

3. **Deploy the overlay:**
   ```bash
   kubectl apply -k k8s/overlays/production/
   ```

### Monitoring the Job

Check the job status:
```bash
kubectl get jobs -n database-scaffolding
kubectl describe job database-scaffold -n database-scaffolding
```

View the logs:
```bash
kubectl logs job/database-scaffold -n database-scaffolding
```

### Cleanup

Remove all resources:
```bash
kubectl delete -f k8s/
# or
kubectl delete namespace database-scaffolding
```

### Job Configuration

The Kubernetes Job includes:
- **Resource limits**: Memory and CPU constraints
- **Security context**: Runs as non-root user
- **Health checks**: Liveness probe to verify script functionality
- **Auto-cleanup**: Removes completed jobs after 24 hours
- **Retry logic**: Up to 3 retry attempts on failure

## CI/CD

The repository includes a GitHub Actions workflow that:

- Builds multi-architecture Docker images (AMD64 and ARM64)
- Runs security scans with Trivy
- Pushes images to Docker Hub on main branch
- Tests image functionality

### Required GitHub Secrets

To use the GitHub Actions workflow, set these repository secrets:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

## Error Handling

The script includes comprehensive error handling:

- Environment variable validation
- Database connection error handling
- Transaction rollback on errors
- Detailed logging throughout the process
