# Kubernetes Notes

Local Kubernetes direction for this project:

- expose the frontend with a `NodePort` service only
- keep the backend behind a `ClusterIP` service
- treat PostgreSQL and Redis as platform-managed dependencies outside this repository
- manage backend connection secrets and OpenAI credentials with Kubernetes secrets

Apply the application manifests to an existing namespace with:

```bash
kubectl apply -k infra/k8s/base -n character-battle
```

The target namespace and the PostgreSQL/Redis manifests are expected to come from a separate platform repository.

Do not make the backend a public service unless there is a specific reason and an additional security review.
