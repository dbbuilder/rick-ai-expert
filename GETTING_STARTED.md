# Getting Started with Rick - Anterix AI Expert

## 🚀 Quick Answers to Your Questions

### **Do we use OpenAI?**
**YES** - Rick is designed to use OpenAI API for optimal performance, but includes intelligent fallbacks:

1. **Primary Mode**: OpenAI GPT-3.5-turbo/GPT-4 for dynamic conversations
2. **Demo Mode**: Pre-programmed responses when OpenAI API key is not available
3. **Fallback Mode**: Knowledge base search + static responses

### **Cost Analysis**
- **OpenAI Cost**: ~$0.004 per conversation (less than half a penny)
- **Monthly estimate**: 1,000 conversations = ~$4
- **Very cost-effective** for the business value provided

### **React Frontend**
✅ **Complete React UI built** with modern features:
- Real-time WebSocket chat interface
- Beautiful Tailwind CSS styling
- Framer Motion animations
- Mobile-responsive design
- Demo mode indicators
- Knowledge base statistics

## 🛠️ Setup Instructions

### **Method 1: Full Setup with OpenAI (Recommended)**

```bash
# 1. Backend Setup
cd /mnt/d/dev2/clients/anterix/rick-ai-expert

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (fix sqlite3 issue)
pip install openai fastapi uvicorn websockets jinja2 sqlalchemy pandas beautifulsoup4 lxml loguru python-dotenv pydantic

# Skip problematic packages
pip install langchain sentence-transformers chromadb --no-deps || true

# Set OpenAI API key
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Build knowledge base from scraped data
python scripts/build_knowledge_base.py

# Start backend
python rick.py
```

```bash
# 2. Frontend Setup (in new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

**Access**:
- Backend API: http://localhost:8080
- React Frontend: http://localhost:3000

### **Method 2: Demo Mode (No OpenAI API Key)**

```bash
# 1. Backend Setup
cd /mnt/d/dev2/clients/anterix/rick-ai-expert
python3 -m venv venv
source venv/bin/activate

# Install minimal dependencies
pip install fastapi uvicorn websockets jinja2 sqlalchemy pandas beautifulsoup4 lxml loguru python-dotenv pydantic

# Start in demo mode (no OPENAI_API_KEY set)
python rick.py
```

```bash
# 2. Frontend Setup
cd frontend
npm install
npm start
```

**Demo Features**:
- ✅ Pre-programmed Anterix responses
- ✅ Knowledge base search
- ✅ Full UI functionality
- ❌ Dynamic AI conversations

### **Method 3: Docker Setup (Production-Ready)**

```bash
# Build and run with Docker Compose
cd /mnt/d/dev2/clients/anterix/rick-ai-expert

# Set environment variables
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start everything
docker-compose up -d

# Access at http://localhost:8080
```

## 🎯 Testing Rick

### **Demo Questions to Try**

1. **Technology Questions**:
   - "What is Private LTE?"
   - "How does 900 MHz spectrum work?"
   - "Tell me about grid modernization"

2. **Business Questions**:
   - "What's the ROI for utilities?"
   - "How can Anterix help my utility?"
   - "What's the business case for Private LTE?"

3. **Industry Questions**:
   - "Which utilities use Anterix?"
   - "How does Private LTE improve grid security?"
   - "What are the implementation steps?"

### **Expected Behavior**

**With OpenAI API Key**:
- Dynamic, contextual responses
- Follows conversation flow
- Personalized recommendations
- Technical depth based on user questions

**Demo Mode**:
- Pre-programmed responses to common questions
- Knowledge base search results
- Professional Anterix information
- Limited conversation flow

## 🔧 API Key Setup

### **Get OpenAI API Key**

1. Go to: https://platform.openai.com/api-keys
2. Create account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### **Set API Key**

**Linux/Mac**:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Windows**:
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Docker**:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

## 🌐 UI Features

### **Modern React Interface**

✅ **Components Built**:
- `ChatInterface`: Real-time chat with WebSocket
- `Header`: Connection status and branding
- `DemoControls`: API key setup instructions
- `KnowledgeBaseStats`: Database statistics
- `useWebSocket`: Custom hook for WebSocket management

✅ **Features**:
- Responsive design (mobile-friendly)
- Real-time typing indicators
- Message history
- Knowledge source citations
- Suggested actions
- Connection status monitoring
- Demo mode indicators

### **Visual Design**

- **Colors**: Anterix blue gradient theme
- **Typography**: Inter font for readability
- **Animations**: Framer Motion for smooth interactions
- **Icons**: Lucide React for consistency
- **Layout**: Grid-based responsive design

## 🚀 Deployment Options

### **Recommended: DigitalOcean App Platform**

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial Rick AI Expert"
git push origin main

# 2. Connect to DigitalOcean
# - Create new app from GitHub repo
# - Set OPENAI_API_KEY environment variable
# - Auto-deploy with Docker

# Cost: ~$12-25/month
# Features: Auto-scaling, SSL, CI/CD
```

### **Alternative: Traditional VPS**

```bash
# Any Linux VPS with Docker
docker-compose up -d

# Configure reverse proxy (nginx)
# Set up SSL certificate
# Configure domain DNS
```

## 🔍 Troubleshooting

### **Common Issues**

1. **"Module not found" errors**:
   ```bash
   pip install --no-deps package_name
   ```

2. **WebSocket connection fails**:
   - Check firewall settings
   - Verify port 8080 is open
   - Check CORS configuration

3. **OpenAI API errors**:
   - Verify API key is correct
   - Check API quota/billing
   - Test with simple request

4. **Knowledge base empty**:
   ```bash
   # Verify spider database exists
   ls -la /mnt/d/dev2/clients/anterix/scraper/*.db

   # Rebuild knowledge base
   python scripts/build_knowledge_base.py
   ```

## 📊 Monitoring

### **Health Check**
```bash
curl http://localhost:8080/health
```

### **Knowledge Base Stats**
```bash
curl http://localhost:8080/api/knowledge/stats
```

### **Test Chat API**
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Private LTE?"}'
```

## 🎯 Next Steps

1. **Test with OpenAI API key** for full functionality
2. **Deploy to production** using DigitalOcean or similar
3. **Integrate into Anterix website** as chat widget
4. **Monitor usage** and optimize responses
5. **Collect user feedback** for improvements

Rick is now ready to serve as Anterix's AI expert! 🤖