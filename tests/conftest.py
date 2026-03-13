import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "heuristic"
os.environ["API_SERVICE_API_KEY"] = "external-dev-key"
os.environ["INTERNAL_SERVICE_API_KEY"] = "internal-dev-key"
os.environ["INGESTION_SERVICE_URL"] = "http://127.0.0.1:9"
os.environ["AGENT_CORE_SERVICE_URL"] = "http://127.0.0.1:9"
os.environ["ARCHIVE_SERVICE_URL"] = "http://127.0.0.1:9"
os.environ["EVALUATION_SERVICE_URL"] = "http://127.0.0.1:9"
os.environ["INTERNAL_REQUEST_TIMEOUT_SECONDS"] = "0.1"
