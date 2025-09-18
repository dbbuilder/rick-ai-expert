"""
Rick - Anterix AI Expert
Main application entry point
"""

import os
import sys
import asyncio
import uvicorn
from loguru import logger

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for Rick application"""
    logger.info("Starting Rick - Anterix AI Expert")

    # Configuration from environment variables
    host = os.getenv("RICK_HOST", "0.0.0.0")
    port = int(os.getenv("RICK_PORT", "8080"))
    debug = os.getenv("RICK_DEBUG", "false").lower() == "true"
    workers = int(os.getenv("RICK_WORKERS", "1"))

    # Log configuration
    logger.info(f"Configuration:")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug: {debug}")
    logger.info(f"  Workers: {workers}")

    # Check for OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        logger.info("✅ OpenAI API key found - AI features enabled")
    else:
        logger.warning("⚠️ No OpenAI API key - using demo mode")

    # Run the application
    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level="info" if not debug else "debug",
        access_log=True
    )

if __name__ == "__main__":
    main()