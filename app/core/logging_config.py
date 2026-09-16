import logging
import sys
from app.config import settings

def setup_logging():
    """
    Sets up a structured log format. Ensures the level is loaded from settings.
    Avoids printing sensitive candidate data in logs by encouraging logger usage 
    that only outputs processing metadata.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Force reconfig of existing loggers
    )
    
    # Mute third party verbose logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully.")
