pipeline {
  agent any

  options {
    disableConcurrentBuilds()
    timestamps()
  }

  environment {
    PYTHONPATH = 'src'
    UV_CACHE_DIR = "${WORKSPACE}/.cache/uv"
    REGISTRY = 'docker-registry.registry.svc.cluster.local:5000'
    FRONTEND_IMAGE = "${REGISTRY}/character-battle-frontend"
    BACKEND_IMAGE = "${REGISTRY}/character-battle-backend"
    IMAGE_TAG = "${BUILD_NUMBER}"
    K8S_NAMESPACE = 'character-battle'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Repository Harness') {
      steps {
        sh 'python3 -m harness_starter.ops_cli gates'
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
          sh '.venv/bin/pip check'
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

    stage('Build Images') {
      steps {
        sh 'docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} frontend'
        sh 'docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} backend'
      }
    }

    stage('Push Images') {
      steps {
        sh 'docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}'
        sh 'docker push ${BACKEND_IMAGE}:${IMAGE_TAG}'
      }
    }

    stage('Deploy') {
      steps {
        sh '''
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
      archiveArtifacts artifacts: '.harness/**/*', allowEmptyArchive: true
    }
  }
}
