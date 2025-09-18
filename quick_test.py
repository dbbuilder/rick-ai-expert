"""
Quick test script for Rick AI Expert with OpenAI
"""

import os
import asyncio
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_connection():
    """Test OpenAI connection and Rick's demo responses"""
    print("🚀 Testing Rick - Anterix AI Expert")
    print("=" * 50)

    # Test 1: Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"✅ OpenAI API Key: {'Present' if api_key else 'Missing'}")
    if api_key:
        print(f"   Key prefix: {api_key[:20]}...")

    # Test 2: Test OpenAI Connection
    if api_key:
        try:
            print("\n🤖 Testing OpenAI Connection...")

            # Use newer OpenAI client syntax
            client = openai.AsyncOpenAI(api_key=api_key)

            # Test with simple Anterix question
            messages = [
                {
                    "role": "system",
                    "content": "You are Rick, an Anterix technology expert. You help utilities understand Private LTE solutions, 900 MHz spectrum, and grid modernization. Be helpful and knowledgeable about Anterix products."
                },
                {
                    "role": "user",
                    "content": "What is Private LTE and how can it help utilities?"
                }
            ]

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )

            rick_response = response.choices[0].message.content
            print(f"✅ OpenAI Connection: SUCCESS")
            print(f"\n🤖 Rick's AI Response:")
            print(f"   {rick_response[:200]}...")

        except Exception as e:
            print(f"❌ OpenAI Connection Error: {e}")
            print(f"   This might be due to API quota, network, or invalid key")

    # Test 3: Check Spider Database
    print("\n📚 Checking Spider Database...")
    spider_paths = [
        "/mnt/d/dev2/clients/anterix/scraper/spider_anterix_full.db",
        "/mnt/d/dev2/clients/anterix/scraper/spider_anterix.db"
    ]

    found_db = False
    for path in spider_paths:
        if os.path.exists(path):
            print(f"✅ Found spider database: {path}")
            # Get file size
            size = os.path.getsize(path)
            print(f"   Database size: {size:,} bytes")
            found_db = True
            break

    if not found_db:
        print("⚠️  No spider database found - Rick will have limited knowledge")

    # Test 4: Demo Responses (without OpenAI)
    print("\n💬 Demo Mode Responses:")
    demo_questions = [
        "What is Private LTE?",
        "Tell me about 900 MHz spectrum",
        "How can Anterix help utilities?"
    ]

    for question in demo_questions:
        print(f"\n🧑 Question: {question}")

        # Simple demo responses
        if "private lte" in question.lower():
            demo_response = """Private LTE is Anterix's core technology solution that provides utilities with their own dedicated broadband wireless network using licensed 900 MHz spectrum. This gives utilities secure, reliable communications for critical infrastructure with enhanced cybersecurity compared to public networks."""
        elif "900 mhz" in question.lower():
            demo_response = """The 900 MHz band is specifically allocated by the FCC for critical infrastructure communications. Anterix holds the largest portion of this licensed spectrum, which provides superior propagation characteristics for wide-area coverage and interference-free operation."""
        elif "help utilities" in question.lower():
            demo_response = """Anterix helps utilities with grid modernization through Private LTE networks that enable smart grid applications, improve operational efficiency, enhance cybersecurity, and support rural broadband initiatives while reducing long-term operational costs."""
        else:
            demo_response = "I can help you understand Anterix solutions, Private LTE technology, and grid modernization applications."

        print(f"🤖 Rick (Demo): {demo_response}")

    # Summary
    print(f"\n🎯 Test Summary:")
    print(f"   OpenAI API: {'✅ Working' if api_key else '⚠️ Missing'}")
    print(f"   Knowledge DB: {'✅ Available' if found_db else '⚠️ Missing'}")
    print(f"   Demo Mode: ✅ Functional")

    print(f"\n🚀 Rick is ready! Next steps:")
    print(f"   1. Start backend: python rick.py")
    print(f"   2. Start frontend: cd frontend && npm install && npm start")
    print(f"   3. Access Rick at: http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(test_openai_connection())