# Harness Starter

빈 저장소에서 시작해 만든 최소 구성의 하네스 엔지니어링 스타터 프로젝트입니다.

현재 학습 목표는, 코드베이스를 유지보수 가능하고 실제 운영 구조에 가깝게 유지하는 하네스 제약을 적용하면서 캐릭터 배틀 웹사이트를 만드는 것입니다.

이 저장소는 하네스 엔지니어링 워크플로의 4가지 핵심 축을 보여줍니다.

1. `AGENTS.md`의 기계 판독 가능한 에이전트 규칙
2. `tests/`와 CI의 결정론적 검증 게이트
3. 코드 구조에 명시된 도구/데이터 경계
4. 하네스 실행 재시도 로직의 피드백 루프

## 프로젝트 구조

```text
.
├── AGENTS.md
├── README.md
├── backend/
├── frontend/
├── infra/
├── docs/
│   ├── api_contract.md
│   ├── architecture.md
│   ├── battle_rules.md
│   ├── harness_automation.md
│   ├── engineering_rules.md
│   ├── product_brief.md
│   └── site_scope.md
├── evals/
│   └── sample_eval.jsonl
├── src/
│   └── harness_starter/
│       ├── cli.py
│       ├── context_manager.py
│       ├── harness_loop.py
│       ├── models.py
│       ├── router.py
│       ├── validators.py
│       └── workers.py
└── tests/
    ├── test_context_manager.py
    ├── test_harness_loop.py
    └── test_validators.py
```

## 스타터가 하는 일

- 로컬 `docs/` 디렉터리만 컨텍스트로 읽습니다.
- 모호한 요청은 명확화 경로로 라우팅합니다.
- 제한된 `plan -> answer -> validate -> retry` 루프를 실행합니다.
- 인용이 없거나 승인된 컨텍스트 밖 텍스트를 인용한 응답은 거부합니다.
- 결정론적 CI 작업을 위해 저장소 단위의 `repair`, `hygiene`, `rule-promotion` 루프를 제공합니다.
- 중복 코드 방지, 과도한 단일 파일 구현 제한 같은 코드 품질 제약을 포함합니다.
- 익명 캐릭터 생성 및 LLM 1:1 배틀 판정이라는 구체적인 타깃 서비스를 문서화합니다.
- 구현 스택을 React + Vite, FastAPI, Redis, PostgreSQL, pgvector로 고정합니다.

## 빠른 시작

원하면 가상환경을 만듭니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

테스트 실행:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

로컬 규칙 기반 워커 실행:

```bash
PYTHONPATH=src python3 -m harness_starter.cli "Build a docs-grounded assistant"
```

저장소 repair 루프 실행:

```bash
python3 -m harness_starter.ops_cli repair --max-attempts 2
```

저장소 관리형 pre-commit 훅 설치:

```bash
python3 -m harness_starter.ops_cli install-hooks
```

pre-commit 훅은 로컬에서 repair 루프를 실행하고, 민감 토큰/개인키가 포함된 커밋을 차단하며, 결정론적 text-lint 실패는 자동 수정 후 다시 stage하고, 제한된 repair 루프로 복구할 수 없으면 커밋을 차단합니다.

야간 hygiene 스캔 실행:

```bash
python3 -m harness_starter.ops_cli hygiene --fail-on-findings
```

rule-promotion 후보 생성:

```bash
python3 -m harness_starter.ops_cli promote --threshold 2 --write-report
```

나중에 실제 OpenAI 워커를 연결하려면 optional 패키지를 설치하고 `OPENAI_API_KEY`를 설정합니다.

```bash
pip install -e ".[openai]"
PYTHONPATH=src python3 -m harness_starter.cli --worker openai "Summarize the project rules"
```

## 다음 단계 제안

1. 마이그레이션을 추가하고 로컬 스키마 부트스트랩을 마이그레이션 기반 플로우로 전환합니다.
2. React 페이지를 구현된 백엔드 API와 연결합니다.
3. VM 클러스터에서 pull 가능한 로컬 레지스트리를 구성합니다.
4. 로컬에 Python 의존성을 설치한 뒤 백엔드 통합 테스트를 추가합니다.
5. 애플리케이션 플로우가 안정화되면 기존 Jenkins `Jenkinsfile`에 이미지 빌드/푸시/배포 단계를 확장합니다.

## 현재 로컬 검증 방법

프론트엔드:

```bash
cd frontend
npm install
npm run build
```

프론트엔드 개발 서버:

```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

백엔드:

```bash
cd backend
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked
.venv/bin/pip check
uv run --locked python -m compileall app
uv run --locked python -c "from app.main import app; print(app.title)"
```

위 백엔드 명령은 머신에 `uv`가 이미 설치되어 있다는 전제입니다.

백엔드 개발 서버:

```bash
cd backend
DATABASE_URL=postgresql+psycopg://app:app@localhost:15432/character_battle \
REDIS_URL=redis://localhost:16379/0 \
OPENAI_API_KEY=your_key_here \
uv run --locked uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Compose 인프라만 실행:

```bash
docker compose -f infra/docker-compose.infra.yml up -d
```

노출 호스트 포트:

- PostgreSQL: `15432`
- Redis: `16379`

프론트 컨테이너 포함 전체 로컬 스택 실행:

```bash
OPENAI_API_KEY=your_key_here \
docker compose up --build -d
```

노출 호스트 포트:

- frontend: `13000`
- PostgreSQL: `15432`
- Redis: `16379`

백엔드는 기본적으로 프론트엔드만 외부에 노출된다는 하네스 규칙을 맞추기 위해 Compose 내부 네트워크에 유지합니다.

기본 Compose 엔트리포인트:

- [`docker-compose.yml`](/Users/hanyoonsoo/harness-engineering-playground/docker-compose.yml)
- 저장소 루트에서 실행하면 `.env`가 자동으로 로드됩니다.
# character-battle-service
