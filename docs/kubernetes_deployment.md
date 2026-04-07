# Kubernetes Deployment

## Exposure Rule

- Frontend: `NodePort`
- Backend: `ClusterIP`
- PostgreSQL: `ClusterIP`
- Redis: `ClusterIP`

This matches the requirement that only the frontend should be reachable from outside the cluster.

## Frontend Exposure

The frontend service should be the only public entrypoint.

Recommended local pattern:

- frontend container serves static assets with Nginx
- Nginx proxies `/api` to the internal backend service
- NodePort is assigned on the frontend service only

## Suggested NodePort

- `30080`

This fits the default Kubernetes NodePort range.

## Images

Recommended image names:

- `character-battle-frontend:latest`
- `character-battle-backend:latest`

## Local VM Cluster Image Strategy

This project targets a local Kubernetes cluster that runs inside virtual machines.

Implication:

- images built on the host are not guaranteed to be directly visible to cluster nodes

Recommended rule:

- Jenkins or local build flows should publish images to a registry reachable from the VM cluster
- deployments should reference registry-backed image tags
- do not treat host-local Docker cache as the deployment source of truth

## Deployment Command

Preferred deployment style:

```bash
kubectl apply -k infra/k8s/base -n character-battle
```

This repository owns the application manifests only.

- the target namespace should already exist before deployment
- PostgreSQL and Redis manifests may live in a separate platform repository
- the backend still expects reachable PostgreSQL and Redis endpoints inside the target namespace or through routable service names

## Secrets

Kubernetes secrets should hold:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- optional application secret material

## CI/CD Note

When Jenkins is introduced:

- keep Jenkins in a separate namespace such as `jenkins`
- keep application workloads in `character-battle`
- allow platform-owned PostgreSQL and Redis manifests to be applied separately from this repository
- expose only the application frontend by `NodePort` inside the application namespace
- if local operator access is needed, Jenkins may use a separate narrowly scoped `NodePort` in the `jenkins` namespace
- do not expose the backend for CI convenience
- prefer GitHub SCM polling over public webhook exposure in the local VM-cluster setup
