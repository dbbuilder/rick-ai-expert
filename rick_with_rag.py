"""
Rick AI Expert with Full RAG Integration
Enhanced with scraped Anterix knowledge using Simple RAG system
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from loguru import logger
from dotenv import load_dotenv

from simple_rag import SimpleAnterixRAG

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Rick - Anterix AI Expert with RAG",
    description="AI-powered assistant with Anterix knowledge base",
    version="2.0.0"
)

# Global components
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
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

class RickWithRAG:
    """Rick AI with integrated RAG system"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.has_openai = bool(self.api_key)

        # Initialize RAG system - handle both local and production paths
        if os.getenv("PRODUCTION"):
            spider_db_path = "/app/data/anterix_full_site.db"
            logger.info(f"🚀 Production mode: Using database at {spider_db_path}")
        else:
            # Local development paths
            local_paths = [
                "/mnt/d/dev2/clients/anterix/scraper/anterix_full_site.db",
                "./data/anterix_full_site.db",
                "../scraper/anterix_full_site.db"
            ]
            spider_db_path = None
            for path in local_paths:
                if os.path.exists(path):
                    spider_db_path = path
                    logger.info(f"💻 Development mode: Using database at {spider_db_path}")
                    break

            if not spider_db_path:
                logger.warning("No database found - will use demo knowledge")
                spider_db_path = None
        logger.info("Initializing RAG system...")
        self.rag = SimpleAnterixRAG(spider_db_path)
        rag_stats = self.rag.get_stats()

        # OpenAI client will be initialized per request with proper v1.x style

        logger.info(f"🤖 Rick initialized:")
        logger.info(f"   OpenAI: {'✅ Available' if self.has_openai else '❌ Missing'}")
        logger.info(f"   RAG: ✅ {rag_stats['total_chunks']} knowledge chunks loaded")
        logger.info(f"   Database: {'✅ Connected' if rag_stats['has_database'] else '❌ Missing'}")

    async def chat(self, user_message: str) -> dict:
        """Process user message with RAG-enhanced responses"""

        # Get relevant knowledge from RAG
        relevant_context = self.rag.get_context_for_query(user_message, max_tokens=1500)
        knowledge_sources = self.rag.search(user_message, top_k=3)

        if self.has_openai:
            try:
                return await self._openai_response_with_rag(user_message, relevant_context, knowledge_sources)
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                return self._demo_response_with_rag(user_message, knowledge_sources)
        else:
            return self._demo_response_with_rag(user_message, knowledge_sources)

    async def _openai_response_with_rag(self, message: str, context: str, sources: List) -> dict:
        """Generate response using OpenAI API enhanced with RAG context"""

        system_prompt = f"""You are Rick, an expert on Anterix technology and solutions. You help utilities and critical infrastructure organizations understand Private LTE solutions, 900 MHz spectrum, and grid modernization.

IMPORTANT: Use the provided Anterix information below to give accurate, specific answers. When the provided information directly answers the user's question, prioritize it over general knowledge.

{context}

Be helpful, knowledgeable, and enthusiastic about Anterix solutions. Provide specific, actionable information while maintaining a professional but friendly tone. When referencing specific information from the sources above, you can mention it's from Anterix's latest materials."""

        try:
            client = openai.OpenAI(api_key=self.api_key)

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=700,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            content = response.choices[0].message.content

            return {
                "response": content,
                "speaker": "Rick",
                "timestamp": datetime.now().isoformat(),
                "mode": "openai_rag",
                "knowledge_sources": [{"title": s.title, "url": s.url, "relevance": f"{s.relevance_score:.3f}"} for s in sources[:2]],
                "suggested_actions": self._extract_actions(content),
                "context_used": len(context) > 100
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _demo_response_with_rag(self, message: str, sources: List) -> dict:
        """Generate demo response enhanced with RAG knowledge"""

        # Use the most relevant source if available
        if sources and sources[0].relevance_score > 0.1:
            best_source = sources[0]
            response = f"""Based on Anterix's latest information:

**{best_source.title}**

{best_source.content[:400]}...

This information comes directly from Anterix's materials. Would you like me to provide more specific details about any aspect of Private LTE or grid modernization?

**I can help you with:**
• Private LTE technology and 900 MHz spectrum
• Grid modernization solutions for utilities
• Business value and ROI analysis
• Implementation planning and next steps

What specific questions do you have about Anterix solutions?"""

            mode = "demo_rag"
        else:
            # Fallback to standard demo response
            response = self._get_standard_demo_response(message)
            mode = "demo"

        return {
            "response": response,
            "speaker": "Rick",
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "knowledge_sources": [{"title": s.title, "url": s.url, "relevance": f"{s.relevance_score:.3f}"} for s in sources[:2]],
            "suggested_actions": ["Learn more about Private LTE", "Contact Anterix", "Request demo"]
        }

    def _get_standard_demo_response(self, message: str) -> str:
        """Standard demo response fallback"""
        return f"""Hello! I'm Rick, your Anterix AI expert assistant.

I have access to comprehensive information about Anterix solutions and can help you understand:

• **Private LTE Networks**: Using licensed 900 MHz spectrum for critical infrastructure
• **Grid Modernization**: Smart grid applications and utility communications
• **Business Value**: ROI analysis and cost-benefit calculations
• **Implementation**: Planning, deployment, and integration support

What would you like to know about Anterix solutions? I can provide specific, detailed information based on the latest Anterix materials and case studies.

**Try asking:** "What are the benefits of Private LTE for utilities?" or "How does 900 MHz spectrum work?"
"""

    def _extract_actions(self, content: str) -> List[str]:
        """Extract suggested actions from response"""
        actions = []
        content_lower = content.lower()

        if any(word in content_lower for word in ["contact", "reach out", "speak with"]):
            actions.append("Contact Anterix")
        if any(word in content_lower for word in ["demo", "demonstration", "pilot"]):
            actions.append("Request demo")
        if any(word in content_lower for word in ["whitepaper", "document", "resource"]):
            actions.append("Download resources")
        if any(word in content_lower for word in ["calculate", "roi", "business case"]):
            actions.append("Calculate ROI")

        return actions

    def get_stats(self) -> dict:
        """Get Rick system statistics"""
        rag_stats = self.rag.get_stats()
        return {
            "openai_available": self.has_openai,
            "rag_enabled": True,
            "knowledge_chunks": rag_stats["total_chunks"],
            "has_database": rag_stats["has_database"],
            "categories": rag_stats["categories"],
            "vocabulary_size": rag_stats["vocabulary_size"]
        }

# Initialize Rick with RAG
rick = None

@app.on_event("startup")
async def startup_event():
    global rick
    logger.info("🚀 Starting Rick AI Expert with RAG integration...")
    rick = RickWithRAG()
    logger.info("✅ Rick AI Expert with RAG ready!")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Enhanced HTML interface showing RAG capabilities"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Rick - Anterix AI Expert (with RAG)</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .rag-badge { background: #10b981; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-left: 10px; }
        .chat-container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .messages { height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background: #fafafa; }
        .message { margin-bottom: 15px; padding: 12px; border-radius: 8px; }
        .user { background: #3b82f6; color: white; margin-left: 20%; }
        .rick { background: #e5e7eb; color: #374151; margin-right: 20%; position: relative; }
        .sources { background: #f0f9ff; border-left: 3px solid #3b82f6; padding: 8px; margin-top: 8px; font-size: 11px; }
        .input-area { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 12px 24px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2563eb; }
        .status { text-align: center; margin-bottom: 15px; padding: 12px; background: #f0f9ff; border-radius: 5px; display: flex; justify-content: center; gap: 20px; }
        .status-item { display: flex; align-items: center; gap: 5px; }
        .features { background: #ecfdf5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .features h3 { margin: 0 0 10px 0; color: #065f46; }
        .features ul { margin: 0; padding-left: 20px; }
        .features li { color: #059669; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Rick - Anterix AI Expert <span class="rag-badge">RAG ENABLED</span></h1>
        <p>Enhanced with 96+ knowledge chunks from Anterix website</p>
    </div>

    <div class="features">
        <h3>🧠 Enhanced Capabilities</h3>
        <ul>
            <li><strong>Real Anterix Knowledge:</strong> 96 knowledge chunks from latest website content</li>
            <li><strong>Smart Search:</strong> Finds relevant information using semantic matching</li>
            <li><strong>Source Citations:</strong> Shows which Anterix pages inform each response</li>
            <li><strong>GPT-4o Mini:</strong> Latest OpenAI model for optimal cost and performance</li>
        </ul>
    </div>

    <div class="chat-container">
        <div class="status" id="status">
            <div class="status-item">
                <span id="connection-status">🔴 Connecting...</span>
            </div>
            <div class="status-item">
                <span id="ai-status">🤖 Loading...</span>
            </div>
            <div class="status-item">
                <span id="rag-status">🧠 RAG Loading...</span>
            </div>
        </div>

        <div class="messages" id="messages">
            <div class="message rick">
                👋 Hi! I'm Rick, your enhanced Anterix AI expert.<br><br>
                🧠 <strong>NEW:</strong> I now have access to 96+ knowledge chunks from the Anterix website!<br><br>
                I can provide specific, accurate information about:<br>
                • Private LTE networks and 900 MHz spectrum<br>
                • Grid modernization solutions and case studies<br>
                • Business value, ROI analysis, and implementation planning<br>
                • Latest Anterix products, services, and partnerships<br><br>
                <strong>Try asking:</strong> "What are the latest benefits of Private LTE?" or "Tell me about Anterix's grid modernization solutions"
            </div>
        </div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask Rick about Anterix solutions with enhanced knowledge..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let ws = null;
        const clientId = 'client_' + Math.random().toString(36).substr(2, 9);

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws/${clientId}`);

            ws.onopen = function() {
                document.getElementById('connection-status').textContent = '🟢 Connected';
                checkSystemStatus();
            };

            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                if (message.type === 'message') {
                    addMessage(message, 'rick');
                }
            };

            ws.onclose = function() {
                document.getElementById('connection-status').textContent = '🔴 Disconnected';
                setTimeout(connect, 3000);
            };
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (message && ws.readyState === WebSocket.OPEN) {
                addMessage({response: message}, 'user');
                ws.send(JSON.stringify({type: 'chat', message: message}));
                input.value = '';
            }
        }

        function addMessage(message, sender) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${sender}`;

            let content = sender === 'user' ? message.response : message.response || message.content;
            content = content.replace(/\\n/g, '<br>');

            let sourcesHtml = '';
            if (message.knowledge_sources && message.knowledge_sources.length > 0) {
                const sources = message.knowledge_sources.map(s =>
                    `📄 <a href="${s.url}" target="_blank">${s.title}</a> (relevance: ${s.relevance})`
                ).join('<br>');
                sourcesHtml = `<div class="sources"><strong>Sources:</strong><br>${sources}</div>`;
            }

            div.innerHTML = content + sourcesHtml;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function checkSystemStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();

                document.getElementById('ai-status').textContent =
                    data.rick_stats?.openai_available ? '🤖 GPT-4o Mini Active' : '🤖 Demo Mode';

                document.getElementById('rag-status').textContent =
                    `🧠 RAG: ${data.rick_stats?.knowledge_chunks || 0} chunks`;

            } catch (error) {
                console.error('Status check failed:', error);
            }
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        connect();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Enhanced health check with RAG statistics"""
    rick_stats = rick.get_stats() if rick else {}

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
        "rick_stats": rick_stats
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for RAG-enhanced chat"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "").strip()

                if user_message:
                    # Process with RAG-enhanced Rick
                    response = await rick.chat(user_message)

                    # Send enhanced response
                    await manager.send_personal_message({
                        "type": "message",
                        "response": response["response"],
                        "speaker": response["speaker"],
                        "timestamp": response["timestamp"],
                        "mode": response["mode"],
                        "knowledge_sources": response.get("knowledge_sources", []),
                        "suggested_actions": response.get("suggested_actions", []),
                        "context_used": response.get("context_used", False)
                    }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for production (DigitalOcean, Heroku, etc.)
    port = int(os.getenv("PORT", 8081))
    logger.info(f"🚀 Starting Rick AI Expert on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")