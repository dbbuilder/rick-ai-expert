"""
Quick test script for Rick AI Expert
Tests OpenAI integration and knowledge base functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chat.ai_engine import RickAIEngine
from knowledge.knowledge_base import AnterixKnowledgeBase

async def test_rick():
    """Test Rick's functionality"""
    print("🚀 Testing Rick - Anterix AI Expert")
    print("=" * 50)

    # Test 1: Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"✅ OpenAI API Key: {'Present' if api_key else 'Missing'}")
    if api_key:
        print(f"   Key prefix: {api_key[:20]}...")

    # Test 2: Initialize Knowledge Base
    print("\n📚 Initializing Knowledge Base...")
    try:
        kb = AnterixKnowledgeBase()

        # Load from spider data
        spider_db_path = "/mnt/d/dev2/clients/anterix/scraper/spider_anterix_full.db"
        if os.path.exists(spider_db_path):
            print(f"✅ Found spider database: {spider_db_path}")
            kb.load_from_spider_data(spider_db_path)
        else:
            print(f"⚠️  Spider database not found: {spider_db_path}")
            # Try alternative path
            alt_path = "../scraper/spider_anterix.db"
            if os.path.exists(alt_path):
                print(f"✅ Found alternative database: {alt_path}")
                kb.load_from_spider_data(alt_path)

        # Get stats
        stats = kb.get_knowledge_stats()
        print(f"✅ Knowledge Base Stats:")
        print(f"   Total items: {stats['total_items']}")
        print(f"   Categories: {list(stats['categories'].keys())}")
        print(f"   Vector collection: {stats['vector_collection_count']}")

    except Exception as e:
        print(f"❌ Knowledge Base Error: {e}")
        kb = None

    # Test 3: Initialize AI Engine
    print("\n🤖 Initializing AI Engine...")
    try:
        ai_engine = RickAIEngine(
            api_key=api_key,
            knowledge_base=kb
        )
        print("✅ AI Engine initialized successfully")
    except Exception as e:
        print(f"❌ AI Engine Error: {e}")
        return

    # Test 4: Test Knowledge Search
    if kb:
        print("\n🔍 Testing Knowledge Search...")
        test_queries = ["private lte", "900 MHz", "grid modernization"]

        for query in test_queries:
            try:
                results = kb.search(query, limit=2)
                print(f"✅ Query '{query}': {len(results)} results")
                if results:
                    for i, result in enumerate(results[:1]):
                        print(f"   {i+1}. {result['title'][:60]}... (score: {result['relevance_score']:.2f})")
            except Exception as e:
                print(f"❌ Search error for '{query}': {e}")

    # Test 5: Test AI Chat
    print("\n💬 Testing AI Chat...")
    test_messages = [
        "What is Private LTE?",
        "How can Anterix help utilities?",
        "Tell me about 900 MHz spectrum"
    ]

    for message in test_messages:
        try:
            print(f"\n🧑 User: {message}")
            response = await ai_engine.chat(message)

            if response and response.get('response'):
                rick_reply = response['response'][:200] + "..." if len(response['response']) > 200 else response['response']
                print(f"🤖 Rick: {rick_reply}")

                # Show knowledge sources if any
                if response.get('knowledge_sources'):
                    print(f"📚 Sources: {len(response['knowledge_sources'])} knowledge items used")

            else:
                print("❌ No response generated")

        except Exception as e:
            print(f"❌ Chat error: {e}")

    # Test 6: Health Check Summary
    print("\n🏥 Health Check Summary")
    print("=" * 30)
    print(f"✅ OpenAI API: {'Available' if api_key else 'Missing'}")
    print(f"✅ Knowledge Base: {stats['total_items'] if kb and stats else 0} items")
    print(f"✅ AI Engine: {'Functional' if ai_engine else 'Error'}")

    print(f"\n🎯 Rick is ready to serve as Anterix AI Expert!")
    print(f"📱 Start with: python rick.py")
    print(f"🌐 Access at: http://localhost:8080")

if __name__ == "__main__":
    asyncio.run(test_rick())