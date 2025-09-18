"""
FastAPI Web Application for Rick AI Expert
Real-time chat interface with WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
import asyncio
import uuid
from typing import Dict, List
from datetime import datetime
import os
from loguru import logger

from ..chat.ai_engine import RickAIEngine
from ..knowledge.knowledge_base import AnterixKnowledgeBase

# Initialize FastAPI app
app = FastAPI(
    title="Rick - Anterix AI Expert",
    description="AI-powered assistant for Anterix solutions and technology",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global components
knowledge_base = None
ai_engine = None
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize application components"""
    global knowledge_base, ai_engine

    logger.info("Starting Rick AI Expert application...")

    # Initialize knowledge base
    knowledge_base = AnterixKnowledgeBase()

    # Load knowledge from spider data if available
    spider_db_path = "/mnt/d/dev2/clients/anterix/scraper/spider_anterix.db"
    if os.path.exists(spider_db_path):
        logger.info("Loading knowledge from spider database...")
        knowledge_base.load_from_spider_data(spider_db_path)
    else:
        logger.warning("Spider database not found, using empty knowledge base")

    # Initialize AI engine
    ai_engine = RickAIEngine(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        knowledge_base=knowledge_base
    )

    logger.info("Rick AI Expert ready!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "title": "Rick - Anterix AI Expert"}
    )

@app.get("/embed", response_class=HTMLResponse)
async def embed_widget(request: Request):
    """Embeddable chat widget for Anterix website"""
    return templates.TemplateResponse(
        "embed.html",
        {"request": request, "title": "Anterix Assistant"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = knowledge_base.get_knowledge_stats() if knowledge_base else {}
    ai_summary = ai_engine.get_conversation_summary() if ai_engine else {}

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "knowledge_base": stats,
        "ai_engine": ai_summary,
        "active_connections": len(manager.active_connections)
    }

@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not available")

    return knowledge_base.get_knowledge_stats()

@app.get("/api/knowledge/categories")
async def get_categories():
    """Get available knowledge categories"""
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not available")

    return knowledge_base.get_categories()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, client_id)

    # Send welcome message
    welcome_message = {
        "type": "message",
        "speaker": "Rick",
        "content": """👋 Hi! I'm Rick, your Anterix technology expert.

I can help you understand:
• Private LTE networks and 900 MHz spectrum
• Critical infrastructure communications
• Grid modernization solutions
• Business value and ROI analysis
• Implementation planning and next steps

What would you like to know about Anterix solutions?""",
        "timestamp": datetime.now().isoformat(),
        "suggestions": [
            "Tell me about Private LTE",
            "How does 900 MHz spectrum work?",
            "What's the ROI for utilities?",
            "Show me grid modernization solutions"
        ]
    }

    await manager.send_personal_message(welcome_message, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "").strip()

                if user_message:
                    # Show typing indicator
                    typing_message = {
                        "type": "typing",
                        "speaker": "Rick",
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.send_personal_message(typing_message, client_id)

                    # Process with AI engine
                    try:
                        response = await ai_engine.chat(user_message, {"client_id": client_id})

                        # Send response
                        chat_response = {
                            "type": "message",
                            "speaker": response["speaker"],
                            "content": response["response"],
                            "timestamp": response["timestamp"],
                            "suggested_actions": response.get("suggested_actions", []),
                            "knowledge_sources": response.get("knowledge_sources", [])
                        }

                        await manager.send_personal_message(chat_response, client_id)

                    except Exception as e:
                        logger.error(f"Error processing chat: {e}")
                        error_response = {
                            "type": "message",
                            "speaker": "Rick",
                            "content": "I apologize, but I'm experiencing a technical issue. Please try again or contact Anterix directly for assistance.",
                            "timestamp": datetime.now().isoformat(),
                            "error": True
                        }
                        await manager.send_personal_message(error_response, client_id)

            elif message_data.get("type") == "feedback":
                # Handle user feedback
                feedback = message_data.get("feedback")
                logger.info(f"Received feedback from {client_id}: {feedback}")

                # Acknowledge feedback
                ack_message = {
                    "type": "feedback_ack",
                    "content": "Thank you for your feedback! It helps us improve Rick's assistance.",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(ack_message, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

@app.post("/api/chat")
async def chat_api(request: Request):
    """REST API endpoint for chat (alternative to WebSocket)"""
    data = await request.json()
    user_message = data.get("message", "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    if not ai_engine:
        raise HTTPException(status_code=503, detail="AI engine not available")

    try:
        response = await ai_engine.chat(user_message, {"source": "api"})
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"API chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/suggestions")
async def get_suggestions():
    """Get conversation starters and suggestions"""
    return {
        "suggestions": [
            {
                "text": "What is Private LTE?",
                "category": "Technology"
            },
            {
                "text": "How can Anterix help with grid modernization?",
                "category": "Solutions"
            },
            {
                "text": "What's the business case for Private LTE?",
                "category": "Business"
            },
            {
                "text": "Tell me about 900 MHz spectrum",
                "category": "Technology"
            },
            {
                "text": "How does Anterix ensure network security?",
                "category": "Security"
            },
            {
                "text": "What utilities are using Anterix solutions?",
                "category": "Case Studies"
            }
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Page not found", "status": 404}
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Internal server error", "status": 500}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )