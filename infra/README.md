# Infrastructure

Local development should start supporting services before application services.

Current infrastructure plan:

- PostgreSQL with pgvector for transactional and vector data
- Redis for session and cache state

The backend should remain internal by default. Only the frontend should bind to a host port in the default local setup.

Local Kubernetes note:

- the cluster runs inside VMs, so deployable images should come from a registry reachable by cluster nodes
- do not rely on host-local Docker images as the long-term deployment path
