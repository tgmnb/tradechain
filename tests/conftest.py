import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("LLM_PROVIDER", "heuristic")
os.environ.setdefault("API_SERVICE_API_KEY", "external-dev-key")
os.environ.setdefault("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
os.environ.setdefault("INGESTION_SERVICE_URL", "http://test-ingestion")
os.environ.setdefault("AGENT_CORE_SERVICE_URL", "http://test-agent-core")
os.environ.setdefault("ARCHIVE_SERVICE_URL", "http://test-archive")
os.environ.setdefault("EVALUATION_SERVICE_URL", "http://test-evaluation")
