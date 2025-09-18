"""
AI Engine for Rick - Handles AI model interactions and response generation
"""

import openai
from typing import List, Dict, Optional
import json
import os
from loguru import logger
from dataclasses import dataclass

from ..core.rick_personality import RickCore
from ..knowledge.knowledge_base import AnterixKnowledgeBase

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = ""
    metadata: Dict = None

class RickAIEngine:
    """AI Engine powering Rick's conversations"""

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "gpt-3.5-turbo",
                 knowledge_base: Optional[AnterixKnowledgeBase] = None):

        # Initialize OpenAI (with fallback for demo mode)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("No OpenAI API key provided - using demo mode")

        self.model = model
        self.rick_core = RickCore()
        self.knowledge_base = knowledge_base
        self.conversation_history: List[ChatMessage] = []

    async def chat(self, user_message: str, context: Dict = None) -> Dict[str, any]:
        """Process user message and generate Rick's response"""
        logger.info(f"Processing user message: {user_message[:100]}...")

        try:
            # Search knowledge base for relevant information
            relevant_knowledge = await self._search_knowledge(user_message)

            # Build context for AI model
            system_prompt = self._build_system_prompt(relevant_knowledge)

            # Prepare messages for AI model
            messages = self._prepare_messages(system_prompt, user_message)

            # Generate response
            if self.api_key:
                response_content = await self._generate_ai_response(messages)
            else:
                response_content = self._generate_demo_response(user_message, relevant_knowledge)

            # Format response
            response = self.rick_core.format_response(response_content, context)

            # Update conversation history
            self._update_conversation_history(user_message, response_content)

            # Add knowledge sources to response
            response["knowledge_sources"] = relevant_knowledge

            return response

        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return self._handle_error_response(str(e))

    async def _search_knowledge(self, query: str, limit: int = 3) -> List[Dict]:
        """Search knowledge base for relevant information"""
        if not self.knowledge_base:
            return []

        try:
            results = self.knowledge_base.search(query, limit=limit)
            logger.info(f"Found {len(results)} relevant knowledge items")
            return results
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return []

    def _build_system_prompt(self, knowledge_items: List[Dict]) -> str:
        """Build system prompt with relevant knowledge"""
        base_prompt = self.rick_core.get_system_prompt()

        if not knowledge_items:
            return base_prompt

        # Add relevant knowledge to prompt
        knowledge_section = "\n\nRELEVANT ANTERIX INFORMATION:\n"
        for i, item in enumerate(knowledge_items, 1):
            knowledge_section += f"\n{i}. {item['title']}\n"
            knowledge_section += f"Category: {item['category']}\n"
            knowledge_section += f"Content: {item['content'][:500]}...\n"
            if item['url']:
                knowledge_section += f"Reference: {item['url']}\n"

        knowledge_section += "\nUse this information to provide accurate, specific answers about Anterix solutions."

        return base_prompt + knowledge_section

    def _prepare_messages(self, system_prompt: str, user_message: str) -> List[Dict]:
        """Prepare message format for AI model"""
        messages = [{"role": "system", "content": system_prompt}]

        # Add recent conversation history
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    async def _generate_ai_response(self, messages: List[Dict]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _generate_demo_response(self, user_message: str, knowledge_items: List[Dict]) -> str:
        """Generate demo response when API is not available"""
        message_lower = user_message.lower()

        # Simple keyword-based responses for demo
        if any(term in message_lower for term in ['private lte', 'plte', 'lte']):
            response = """Hello! I'm Rick, your Anterix technology expert.

Private LTE is Anterix's core technology solution that provides utilities with their own dedicated broadband wireless network using licensed 900 MHz spectrum. This gives utilities:

• Secure, reliable communications for critical infrastructure
• Coverage across vast service territories
• Support for grid modernization applications
• Enhanced cybersecurity compared to public networks

"""
            if knowledge_items:
                response += f"\nBased on our latest information from {len(knowledge_items)} relevant resources, "
                response += "Anterix Private LTE networks are being deployed by leading utilities across North America."

        elif any(term in message_lower for term in ['900 mhz', 'spectrum', '900']):
            response = """Great question about 900 MHz spectrum!

The 900 MHz band is specifically allocated by the FCC for critical infrastructure communications. Anterix holds the largest portion of this licensed spectrum, which provides:

• Superior propagation characteristics for wide-area coverage
• Licensed spectrum ensures interference-free operation
• Ideal for utility service territories and rural areas
• Supports high-bandwidth applications for grid modernization

This spectrum is perfect for utilities because it can cover large geographical areas with fewer cell sites."""

        elif any(term in message_lower for term in ['cost', 'roi', 'business case']):
            response = """The business case for Private LTE is compelling for utilities:

**Cost Benefits:**
• Reduced operational expenses vs. leased circuits
• Lower long-term total cost of ownership
• Avoided costs from communication failures

**Revenue Opportunities:**
• Enable new grid services and applications
• Support rural broadband initiatives
• Improved customer service capabilities

**Risk Mitigation:**
• Enhanced cybersecurity for critical operations
• Improved grid reliability and resilience
• Regulatory compliance for critical infrastructure

I'd be happy to discuss specific ROI calculations for your utility's situation."""

        else:
            response = f"""Hi there! I'm Rick, your Anterix expert assistant.

I help utilities and critical infrastructure organizations understand how Anterix's Private LTE solutions can address their communication challenges.

I can help you with:
• Private LTE technology and 900 MHz spectrum
• Grid modernization and smart grid applications
• Business case development and ROI analysis
• Regulatory and compliance questions
• Implementation planning and next steps

What specific aspect of Anterix solutions would you like to learn about?"""

        return response

    def _update_conversation_history(self, user_message: str, assistant_response: str):
        """Update conversation history"""
        from datetime import datetime
        timestamp = datetime.now().isoformat()

        self.conversation_history.extend([
            ChatMessage(role="user", content=user_message, timestamp=timestamp),
            ChatMessage(role="assistant", content=assistant_response, timestamp=timestamp)
        ])

        # Keep last 20 messages
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _handle_error_response(self, error_msg: str) -> Dict[str, any]:
        """Handle errors gracefully"""
        response_content = """I apologize, but I'm experiencing a technical issue right now.

However, I'm still here to help! For immediate assistance with Anterix solutions, please:

• Visit anterix.com for comprehensive information
• Contact our sales team directly for personalized support
• Download our solution overviews and technical resources

Is there a specific Anterix topic I can try to help with using my basic knowledge?"""

        return self.rick_core.format_response(response_content, {"error": error_msg})

    def get_conversation_summary(self) -> Dict[str, any]:
        """Get summary of current conversation"""
        return {
            "message_count": len(self.conversation_history),
            "has_api_key": bool(self.api_key),
            "model": self.model,
            "has_knowledge_base": bool(self.knowledge_base),
            "last_updated": self.conversation_history[-1].timestamp if self.conversation_history else None
        }