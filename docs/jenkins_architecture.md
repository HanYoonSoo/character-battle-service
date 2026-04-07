# Jenkins Architecture

## Recommended Shape

- Jenkins controller: `StatefulSet`
- Jenkins build executors: ephemeral agent Pods
- Jenkins namespace: `jenkins`

Why this fits:

- the controller keeps state and benefits from persistent storage
- agents should remain disposable and isolated
- CI infrastructure stays separate from application workloads

## Harness Alignment

Jenkins should run the harness gates, not bypass them.

Required guardrails:

- pipelines stored as code with `Jenkinsfile`
- builds run on agent Pods, not on the controller
- registry publish happens before Kubernetes deployment
- if agent Pods run inside the cluster, prefer ServiceAccount-backed `kubectl` over shipping a separate kubeconfig file

## Webhook And Local VM Cluster Caveat

Because the Kubernetes cluster runs in local VMs, inbound webhooks may be awkward unless Jenkins is reachable from the source control system.

Acceptable options:

- expose Jenkins intentionally and narrowly for webhook delivery
- use a tunnel
- use SCM polling when webhook delivery is not practical

Current chosen option:

- GitHub SCM polling

What to avoid:

- assuming a local private Jenkins URL is reachable from the internet

## Minimal Jenkins Components

- controller with persistent volume
- Kubernetes plugin for agent Pods
- Git plugin
- Pipeline plugin

## Deployment Mode

- publish images to a local registry reachable from the VM nodes
- deploy application manifests with `kubectl apply -k`

## Namespace Split

- `jenkins`: CI controller and agent Pods
- `character-battle`: frontend, backend, and any colocated runtime dependencies

This separation keeps CI concerns away from the runtime application namespace.

## Repository Boundary

This repository assumes a Jenkins controller already exists.

What this repository owns:

- the root `Jenkinsfile`
- repository-level harness commands such as `repair`, `hygiene`, and `promote`
- application Kubernetes manifests for `frontend` and `backend`

Recommended split:

- the root `Jenkinsfile` should be the main `main`-branch CI/CD pipeline
- `repair`, `hygiene`, and `promote` should run as separate Jenkins jobs instead of parameter branches inside the deploy pipeline

## Kubernetes Access For Deploys

- prefer running the main pipeline on Jenkins agent Pods inside the cluster
- let those agent Pods use their mounted ServiceAccount token for `kubectl`
- bind the Jenkins ServiceAccount to a deploy Role in `character-battle`
- avoid managing a separate kubeconfig credential when in-cluster ServiceAccount access is available

What this repository does not own:

- Jenkins controller Kubernetes manifests
- Jenkins controller bootstrap secrets
- Jenkins controller plugin installation manifests
- namespace bootstrap manifests for `character-battle`
- PostgreSQL and Redis Kubernetes manifests when those are managed by a separate platform repository
