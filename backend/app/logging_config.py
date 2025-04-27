import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from app.config import settings

class SecurityJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with security-related fields"""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add ISO timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add environment info
        log_record['environment'] = settings.ENVIRONMENT
        log_record['app_version'] = settings.VERSION
        
        # Add process and thread info for debugging
        if settings.DEBUG:
            log_record['process'] = record.process
            log_record['thread'] = record.thread
            log_record['threadName'] = record.threadName
        
        # Mask sensitive data in production
        if settings.is_production() and 'password' in str(message_dict):
            log_record['message'] = self.mask_sensitive_data(log_record['message'])
    
    @staticmethod
    def mask_sensitive_data(message: str) -> str:
        """Mask sensitive data in log messages"""
        sensitive_fields = ['password', 'token', 'secret', 'key', 'auth']
        masked_message = message
        
        for field in sensitive_fields:
            # Match field followed by any non-whitespace characters
            import re
            pattern = fr'{field}[=:]\s*\S+'
            masked_message = re.sub(
                pattern,
                f'{field}=*****',
                masked_message,
                flags=re.IGNORECASE
            )
        
        return masked_message

def setup_logging():
    """Configure secure logging with both file and console output"""
    # Set base log level
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatters
    json_formatter = SecurityJsonFormatter(
        fmt="%(timestamp)s %(levelname)s %(name)s %(funcName)s %(filename)s %(lineno)d %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    if settings.is_production():
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Secure log file permissions
        if os.name != 'nt':  # Not Windows
            os.chmod(log_dir, 0o750)
        
        # Application log
        app_log_file = log_dir / "app.log"
        file_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
        
        # Secure log file permissions
        if os.name != 'nt':  # Not Windows
            os.chmod(app_log_file, 0o640)
        
        # Security audit log
        audit_logger = logging.getLogger('security_audit')
        audit_log_file = log_dir / "security_audit.log"
        audit_handler = RotatingFileHandler(
            audit_log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        audit_handler.setFormatter(json_formatter)
        audit_logger.addHandler(audit_handler)
        
        # Secure audit log file permissions
        if os.name != 'nt':  # Not Windows
            os.chmod(audit_log_file, 0o640)

    # Configure uvicorn loggers
    for logger_name in ["uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = logger.handlers
        uvicorn_logger.propagate = False

    logging.info(f"Logging configured with level: {logging.getLevelName(log_level)}")
    if settings.is_production():
        logging.info("File logging enabled in production mode") 