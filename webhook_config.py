"""Webhook mode support for production deployment."""
import os
from telegram.ext import Application


def setup_webhook(application: Application, webhook_url: str, port: int = 8443):
    """
    Set up webhook mode for production.
    
    Args:
        application: Telegram application instance
        webhook_url: Public webhook URL (e.g., https://yourdomain.com/webhook)
        port: Port to listen on (default 8443)
    """
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook",
        allowed_updates=["message", "callback_query"]
    )


def should_use_webhook() -> bool:
    """
    Determine if webhook mode should be used based on environment.
    
    Returns:
        True if WEBHOOK_URL environment variable is set
    """
    return bool(os.getenv("WEBHOOK_URL"))


def get_webhook_config():
    """
    Get webhook configuration from environment variables.
    
    Environment variables:
        WEBHOOK_URL: Public URL for webhook (required for webhook mode)
        WEBHOOK_PORT: Port to listen on (default 8443)
    
    Returns:
        Dict with webhook_url and port, or None if webhook mode disabled
    """
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        return None
    
    port = int(os.getenv("WEBHOOK_PORT", "8443"))
    
    return {
        "webhook_url": webhook_url,
        "port": port
    }
