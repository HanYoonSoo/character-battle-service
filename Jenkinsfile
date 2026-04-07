pipeline {
  agent any

  options {
    disableConcurrentBuilds()
  }

  environment {
    PYTHONPATH = 'src'
    UV_CACHE_DIR = "${WORKSPACE}/.cache/uv"

    REGISTRY = 'docker-registry.registry.svc.cluster.local:5000'
    FRONTEND_IMAGE = "${REGISTRY}/character-battle-frontend"
    BACKEND_IMAGE = "${REGISTRY}/character-battle-backend"
    IMAGE_TAG = "${BUILD_NUMBER}"
    K8S_NAMESPACE = 'character-battle'

    REPO_URL = 'https://github.com/HanYoonSoo/character-battle-service.git'
    KANIKO_IMAGE = 'gcr.io/kaniko-project/executor:v1.23.2'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Capture Commit') {
      steps {
        script {
          env.SCM_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          echo "SCM_COMMIT=${env.SCM_COMMIT}"
        }
      }
    }

    stage('Repository Harness') {
      steps {
        sh '''
          set +e
          python3 -m harness_starter.ops_cli gates
          HARNESS_RC=$?
          if [ "${HARNESS_RC}" -ne 0 ]; then
            echo "Repository harness failed. Dumping verbose unit test output for diagnostics."
            python3 -m unittest discover -s tests -p "test_*.py" -v || true
            exit "${HARNESS_RC}"
          fi
        '''
      }
    }

    stage('Frontend Verify') {
      steps {
        dir('frontend') {
          sh 'npm ci'
          sh 'npm run build'
        }
      }
    }

    stage('Backend Verify') {
      steps {
        dir('backend') {
          sh 'python3.11 -m venv .uv-bootstrap'
          sh '.uv-bootstrap/bin/pip install uv==0.11.3'
          sh '.uv-bootstrap/bin/uv lock --check'
          sh '.uv-bootstrap/bin/uv sync --locked'
          sh '.uv-bootstrap/bin/uv pip check --python .venv/bin/python'
          sh '.uv-bootstrap/bin/uv run --locked python -m compileall app'
          sh '.uv-bootstrap/bin/uv run --locked python -c "from app.main import app; print(app.title)"'
        }
      }
    }

    stage('Manifest Verify') {
      steps {
        sh 'kubectl kustomize infra/k8s/base >/tmp/character-battle-manifests.yaml'
      }
    }

    stage('Build & Push Images (Kaniko)') {
      steps {
        sh '''
          set -euo pipefail

          FRONT_JOB="kaniko-frontend-${BUILD_NUMBER}"
          BACK_JOB="kaniko-backend-${BUILD_NUMBER}"

          cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ${FRONT_JOB}
  namespace: ${K8S_NAMESPACE}
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      volumes:
        - name: ws
          emptyDir: {}
      initContainers:
        - name: fetch-source
          image: alpine/git:2.45.2
          command: ["/bin/sh", "-c"]
          args:
            - |
              set -eu
              git clone ${REPO_URL} /workspace
              cd /workspace
              git checkout ${SCM_COMMIT}
          volumeMounts:
            - name: ws
              mountPath: /workspace
      containers:
        - name: kaniko
          image: ${KANIKO_IMAGE}
          args:
            - --context=dir:///workspace/frontend
            - --dockerfile=/workspace/frontend/Dockerfile
            - --destination=${FRONTEND_IMAGE}:${IMAGE_TAG}
            - --insecure
            - --skip-tls-verify
          volumeMounts:
            - name: ws
              mountPath: /workspace
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${BACK_JOB}
  namespace: ${K8S_NAMESPACE}
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      volumes:
        - name: ws
          emptyDir: {}
      initContainers:
        - name: fetch-source
          image: alpine/git:2.45.2
          command: ["/bin/sh", "-c"]
          args:
            - |
              set -eu
              git clone ${REPO_URL} /workspace
              cd /workspace
              git checkout ${SCM_COMMIT}
          volumeMounts:
            - name: ws
              mountPath: /workspace
      containers:
        - name: kaniko
          image: ${KANIKO_IMAGE}
          args:
            - --context=dir:///workspace/backend
            - --dockerfile=/workspace/backend/Dockerfile
            - --destination=${BACKEND_IMAGE}:${IMAGE_TAG}
            - --insecure
            - --skip-tls-verify
          volumeMounts:
            - name: ws
              mountPath: /workspace
EOF

          kubectl -n ${K8S_NAMESPACE} wait --for=condition=complete job/${FRONT_JOB} --timeout=1800s || {
            kubectl -n ${K8S_NAMESPACE} logs job/${FRONT_JOB} --all-containers=true --tail=-1 || true
            exit 1
          }

          kubectl -n ${K8S_NAMESPACE} wait --for=condition=complete job/${BACK_JOB} --timeout=1800s || {
            kubectl -n ${K8S_NAMESPACE} logs job/${BACK_JOB} --all-containers=true --tail=-1 || true
            exit 1
          }

          kubectl -n ${K8S_NAMESPACE} logs job/${FRONT_JOB} --all-containers=true --tail=200 || true
          kubectl -n ${K8S_NAMESPACE} logs job/${BACK_JOB} --all-containers=true --tail=200 || true
        '''
      }
    }

    stage('Deploy') {
      steps {
        sh '''
          set -euo pipefail
          kubectl apply -k infra/k8s/base -n ${K8S_NAMESPACE}

          kubectl -n ${K8S_NAMESPACE} set image deployment/frontend \
            frontend=${FRONTEND_IMAGE}:${IMAGE_TAG}

          kubectl -n ${K8S_NAMESPACE} set image deployment/backend \
            backend=${BACKEND_IMAGE}:${IMAGE_TAG}

          kubectl -n ${K8S_NAMESPACE} rollout status deployment/frontend --timeout=180s
          kubectl -n ${K8S_NAMESPACE} rollout status deployment/backend --timeout=180s
        '''
      }
    }

    stage('Smoke Check') {
      steps {
        sh '''
          kubectl -n ${K8S_NAMESPACE} get deploy
          kubectl -n ${K8S_NAMESPACE} get pods
          kubectl -n ${K8S_NAMESPACE} get svc
        '''
      }
    }
  }

  post {
    always {
      sh '''
        kubectl -n ${K8S_NAMESPACE} delete job kaniko-frontend-${BUILD_NUMBER} --ignore-not-found=true || true
        kubectl -n ${K8S_NAMESPACE} delete job kaniko-backend-${BUILD_NUMBER} --ignore-not-found=true || true
      '''
      archiveArtifacts artifacts: '.harness/**/*', allowEmptyArchive: true
    }
  }
}
