# Rick AI Expert - Deployment Guide

## Overview

Rick is designed to be deployed in multiple ways to suit different needs and environments. Here are the recommended deployment options:

## 🚀 Deployment Options

### 1. **DigitalOcean App Platform** (Recommended for Production)

**Best for**: Production deployment with auto-scaling and minimal DevOps overhead

```bash
# Deploy to DigitalOcean App Platform
doctl apps create --spec deployment/digitalocean-app.yaml

# Or use the web interface
# Upload the entire rick-ai-expert folder as a GitHub repo
# DigitalOcean will auto-detect the Dockerfile and deploy
```

**Pros:**
- Auto-scaling based on traffic
- Built-in load balancing
- SSL/TLS termination
- Automatic deployments from GitHub
- Cost-effective (~$12-25/month)

**Setup Steps:**
1. Push code to GitHub repository
2. Connect DigitalOcean to GitHub
3. Set environment variables (OPENAI_API_KEY)
4. Deploy with automatic CI/CD

### 2. **AWS ECS Fargate** (Enterprise Grade)

**Best for**: Enterprise deployments with advanced networking and compliance needs

```bash
# Build and push to ECR
aws ecr create-repository --repository-name rick-ai-expert
docker build -t rick-ai-expert .
docker tag rick-ai-expert:latest YOUR_ECR_URI/rick-ai-expert:latest
docker push YOUR_ECR_URI/rick-ai-expert:latest

# Deploy with ECS
aws ecs create-service --service-name rick-ai --task-definition rick-ai-task
```

**Pros:**
- Enterprise-grade security and compliance
- VPC integration
- Advanced monitoring with CloudWatch
- Integration with AWS ecosystem

### 3. **Azure Container Instances** (Quick & Simple)

**Best for**: Rapid prototyping and demonstrations

```bash
# Deploy to Azure
az container create \
  --resource-group anterix-rg \
  --name rick-ai-expert \
  --image YOUR_ACR/rick-ai-expert:latest \
  --ports 8080 \
  --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY
```

### 4. **Kubernetes** (High Availability)

**Best for**: High-traffic production environments requiring maximum control

```bash
# Deploy to Kubernetes
kubectl apply -f deployment/k8s/
kubectl expose deployment rick-ai-expert --type=LoadBalancer --port=80 --target-port=8080
```

### 5. **Self-Hosted with Docker Compose** (Development/Internal)

**Best for**: Development, testing, or internal corporate deployments

```bash
# Clone and deploy locally
git clone [repository]
cd rick-ai-expert

# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Deploy with Docker Compose
docker-compose up -d

# Access at http://localhost:8080
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Essential
OPENAI_API_KEY=sk-your-openai-api-key-here
RICK_HOST=0.0.0.0
RICK_PORT=8080

# Optional
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4 for better responses
RICK_DEBUG=false
RICK_WORKERS=2
```

### OpenAI API Configuration

**Recommendation: Yes, use OpenAI API** for the following reasons:

#### ✅ **Why OpenAI API?**

1. **Quality**: GPT-3.5/GPT-4 provides superior conversational quality
2. **Context Understanding**: Better at understanding technical Anterix concepts
3. **Cost-Effective**: ~$0.002 per 1K tokens (very affordable for business use)
4. **Reliability**: 99.9% uptime SLA
5. **Scalability**: Handles unlimited concurrent users

#### 💡 **Cost Analysis**
- Average conversation: 2,000 tokens
- Cost per conversation: ~$0.004 (less than half a penny)
- 1,000 conversations/month: ~$4
- Very cost-effective for business value provided

#### 🔄 **Fallback Strategy**
Rick includes intelligent fallbacks:

1. **Primary**: OpenAI GPT-3.5-turbo/GPT-4
2. **Fallback**: Built-in knowledge-based responses
3. **Emergency**: Static FAQ responses

```python
# Automatic fallback handling
if openai_available:
    response = await openai_chat(message)
else:
    response = knowledge_base_search(message)
```

## 🌐 Domain and SSL Setup

### Custom Domain Configuration

```bash
# For production deployment
# 1. Point DNS to your deployment:
rick.anterix.com -> deployment-ip-address

# 2. Configure SSL (automatic with most cloud providers)
# 3. Update CORS settings if embedding in anterix.com
```

### Embedding in Anterix Website

```html
<!-- Add to any Anterix page -->
<div id="rick-chat-widget"></div>
<script>
  // Load Rick as iframe widget
  const widget = document.createElement('iframe');
  widget.src = 'https://rick.anterix.com/embed';
  widget.style.width = '400px';
  widget.style.height = '500px';
  widget.style.border = 'none';
  widget.style.borderRadius = '8px';
  document.getElementById('rick-chat-widget').appendChild(widget);
</script>
```

## 📊 Monitoring and Analytics

### Health Monitoring

```bash
# Health check endpoint
curl https://rick.anterix.com/health

# Returns:
{
  "status": "healthy",
  "knowledge_base": {"total_items": 150},
  "ai_engine": {"has_api_key": true},
  "active_connections": 5
}
```

### Analytics Integration

```javascript
// Add to Rick's frontend
// Track usage patterns
analytics.track('rick_conversation_started');
analytics.track('rick_question_asked', {
  category: 'technology',
  topic: 'private_lte'
});
```

## 🔐 Security Configuration

### API Security
- Rate limiting: 100 requests/minute per IP
- CORS configured for anterix.com domains
- Input validation and sanitization
- No sensitive data logging

### OpenAI Security
- API keys stored as environment variables
- No conversation data stored on OpenAI servers
- Request timeout limits
- Error handling prevents key exposure

## 📈 Scaling Recommendations

### Traffic Levels

| Users/Day | Deployment | Cost/Month |
|-----------|------------|------------|
| < 100 | Single container | $12-25 |
| 100-1,000 | Auto-scaling (2-4 instances) | $25-75 |
| 1,000-10,000 | Load balanced (4-10 instances) | $75-200 |
| 10,000+ | Kubernetes cluster | $200+ |

### Performance Optimization

1. **Caching**: Implement Redis for frequently asked questions
2. **CDN**: Use CloudFlare for static assets
3. **Database**: Migrate to PostgreSQL for production knowledge base
4. **Monitoring**: Implement comprehensive logging and metrics

## 🚀 Quick Start Commands

### For DigitalOcean (Recommended)

```bash
# 1. Push to GitHub
git push origin main

# 2. Create DigitalOcean app
doctl apps create --spec deployment/digitalocean-app.yaml

# 3. Set environment variables in DO dashboard
# OPENAI_API_KEY = your-key

# 4. Deploy automatically from GitHub
```

### For Local Development

```bash
# 1. Setup
cd rick-ai-expert
pip install -r requirements.txt

# 2. Build knowledge base
python scripts/build_knowledge_base.py

# 3. Run locally
export OPENAI_API_KEY="your-key"
python rick.py

# 4. Access at http://localhost:8080
```

## 💡 Integration with Anterix Website

### Embedding Options

1. **Chat Widget**: Bottom-right corner of every page
2. **Dedicated Page**: /support/ai-assistant
3. **Solution Pages**: Contextual help on specific solution pages
4. **Contact Form**: Pre-qualification before human handoff

### Analytics Tracking

Track Rick's impact:
- Questions asked by category
- User satisfaction ratings
- Conversion to contact forms
- Most requested information

This deployment strategy ensures Rick can scale with Anterix's needs while providing excellent user experience and maintaining cost efficiency.