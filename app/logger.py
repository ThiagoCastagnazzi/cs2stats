import logging
import sys
from datetime import datetime
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_filename = log_dir / f"scraper_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),  # Mostra no terminal também
    ],
)

logger = logging.getLogger("cs2_scraper")
