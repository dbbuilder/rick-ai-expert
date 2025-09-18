"""
Simplified Rick AI Expert for immediate testing
Includes OpenAI integration and basic chat functionality
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
from fastapi.staticfiles import StaticFiles
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Rick - Anterix AI Expert",
    description="AI-powered assistant for Anterix solutions",
    version="1.0.0"
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

class SimpleRick:
    """Simplified Rick AI with OpenAI integration"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.has_openai = bool(self.api_key)

        if self.has_openai:
            # Use the synchronous client for compatibility
            openai.api_key = self.api_key

        logger.info(f"Rick initialized - OpenAI: {'✅ Available' if self.has_openai else '❌ Missing'}")

    async def chat(self, user_message: str) -> dict:
        """Process user message and generate response"""

        if self.has_openai:
            try:
                return await self._openai_response(user_message)
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                return self._demo_response(user_message)
        else:
            return self._demo_response(user_message)

    async def _openai_response(self, message: str) -> dict:
        """Generate response using OpenAI API"""

        system_prompt = """You are Rick, an expert on Anterix technology and solutions. You help utilities and critical infrastructure organizations understand:

- Private LTE networks and 900 MHz spectrum
- Grid modernization and smart grid applications
- Critical infrastructure communications
- Business value and ROI of Private LTE
- Implementation planning and next steps

Be helpful, knowledgeable, and enthusiastic about Anterix solutions. Provide specific, actionable information while maintaining a professional but friendly tone."""

        try:
            # Use the modern OpenAI client with GPT-4o mini
            client = openai.OpenAI(api_key=self.api_key)

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o-mini",  # Latest, fastest, most cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=600,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            content = response.choices[0].message.content

            return {
                "response": content,
                "speaker": "Rick",
                "timestamp": datetime.now().isoformat(),
                "mode": "openai",
                "suggested_actions": self._extract_actions(content)
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _demo_response(self, message: str) -> dict:
        """Generate demo response when OpenAI is not available"""

        message_lower = message.lower()

        if any(term in message_lower for term in ['private lte', 'plte']):
            response = """Hi! I'm Rick, your Anterix technology expert.

Private LTE is Anterix's flagship solution that provides utilities with their own dedicated broadband wireless network using licensed 900 MHz spectrum. Key benefits include:

• **Secure Communications**: Licensed spectrum ensures interference-free, cyber-secure operations
• **Wide Coverage**: 900 MHz provides superior propagation for vast utility service territories
• **Grid Modernization**: Enables smart grid applications like advanced metering, distribution automation, and real-time monitoring
• **Cost Efficiency**: Reduces long-term operational expenses vs. leased circuits

Would you like to know more about implementation or specific use cases?"""

        elif any(term in message_lower for term in ['900 mhz', 'spectrum']):
            response = """Great question about 900 MHz spectrum!

The 900 MHz band (896-901 MHz and 935-940 MHz) is specifically allocated by the FCC for critical infrastructure communications. Here's why it's perfect for utilities:

• **Licensed Spectrum**: Anterix holds the largest portion, ensuring interference-free operation
• **Superior Propagation**: Lower frequency travels farther and penetrates buildings better
• **Wide Area Coverage**: Fewer cell sites needed compared to higher frequency bands
• **Regulatory Support**: FCC specifically designated this for critical infrastructure

This spectrum enables utilities to deploy their own Private LTE networks for grid modernization applications."""

        elif any(term in message_lower for term in ['cost', 'roi', 'business case']):
            response = """The business case for Anterix Private LTE is compelling for utilities:

**Cost Benefits:**
• Reduced operational expenses vs. multiple leased circuits
• Lower total cost of ownership over 10+ years
• Avoided costs from communication failures and outages

**Revenue Opportunities:**
• Enable new grid services and customer applications
• Support rural broadband initiatives and partnerships
• Improved operational efficiency and productivity

**Risk Mitigation:**
• Enhanced cybersecurity for critical operations
• Improved grid reliability and resilience
• Regulatory compliance for critical infrastructure protection

Typical ROI timeframe: 3-5 years. Would you like to discuss specific calculations for your utility?"""

        elif any(term in message_lower for term in ['help', 'utility', 'solution']):
            response = """Anterix helps utilities modernize their communications infrastructure and enable the smart grid of the future.

**Our Solutions:**
• Private LTE networks using 900 MHz licensed spectrum
• Grid modernization applications and use cases
• Cybersecurity and network resilience solutions
• Business case development and implementation planning

**Key Applications:**
• Advanced Metering Infrastructure (AMI)
• Distribution Automation (DA)
• Outage Management and Restoration
• Field Workforce Communications
• Video Surveillance and Security

**Getting Started:**
• Spectrum analysis and network planning
• Pilot deployments and proof of concepts
• Business case development
• Full network deployment and integration

What specific challenges is your utility facing that we can help address?"""

        else:
            response = f"""Hello! I'm Rick, your Anterix AI expert assistant.

I can help you understand:
• Private LTE technology and 900 MHz spectrum
• Grid modernization solutions for utilities
• Business value and ROI analysis
• Implementation planning and next steps
• Cybersecurity for critical infrastructure

What would you like to know about Anterix solutions?

**Popular Questions:**
• "What is Private LTE?"
• "How does 900 MHz spectrum work?"
• "What's the business case for utilities?"
• "How can Anterix help with grid modernization?"

Feel free to ask me anything about Anterix technology!"""

        return {
            "response": response,
            "speaker": "Rick",
            "timestamp": datetime.now().isoformat(),
            "mode": "demo",
            "suggested_actions": ["Learn about Private LTE", "Explore 900 MHz benefits", "Calculate ROI"]
        }

    def _extract_actions(self, content: str) -> List[str]:
        """Extract suggested actions from response"""
        actions = []
        if "contact" in content.lower():
            actions.append("Contact Anterix")
        if "demo" in content.lower():
            actions.append("Request demo")
        if "whitepaper" in content.lower():
            actions.append("Download resources")
        return actions

# Initialize Rick
rick = SimpleRick()

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Rick - Anterix AI Expert is starting up!")
    logger.info(f"✅ OpenAI: {'Available' if rick.has_openai else 'Demo Mode'}")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple HTML interface for testing"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Rick - Anterix AI Expert</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .chat-container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .messages { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background: #fafafa; }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 8px; }
        .user { background: #3b82f6; color: white; margin-left: 20%; }
        .rick { background: #e5e7eb; color: #374151; margin-right: 20%; }
        .input-area { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2563eb; }
        .status { text-align: center; margin-bottom: 15px; padding: 10px; background: #f0f9ff; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Rick - Anterix AI Expert</h1>
        <p>Your intelligent assistant for Private LTE and grid modernization</p>
    </div>

    <div class="chat-container">
        <div class="status" id="status">
            <span id="connection-status">Connecting...</span> |
            <span id="ai-status">Loading...</span>
        </div>

        <div class="messages" id="messages">
            <div class="message rick">
                👋 Hi! I'm Rick, your Anterix technology expert.<br><br>
                I can help you understand:<br>
                • Private LTE networks and 900 MHz spectrum<br>
                • Grid modernization solutions<br>
                • Business value and ROI analysis<br>
                • Implementation planning<br><br>
                What would you like to know about Anterix solutions?
            </div>
        </div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask Rick about Private LTE, 900 MHz, grid modernization..." />
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
                document.getElementById('ai-status').textContent = '🤖 Rick Ready';
            };

            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                if (message.type === 'message') {
                    addMessage(message.response, 'rick');
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
                addMessage(message, 'user');
                ws.send(JSON.stringify({type: 'chat', message: message}));
                input.value = '';
            }
        }

        function addMessage(content, sender) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.innerHTML = content.replace(/\\n/g, '<br>');
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openai_available": rick.has_openai,
        "active_connections": len(manager.active_connections)
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "").strip()

                if user_message:
                    # Process with Rick
                    response = await rick.chat(user_message)

                    # Send response
                    await manager.send_personal_message({
                        "type": "message",
                        "response": response["response"],
                        "speaker": response["speaker"],
                        "timestamp": response["timestamp"],
                        "mode": response["mode"]
                    }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")