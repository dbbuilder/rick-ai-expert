# 🔐 GitHub Secrets Configuration

## Required GitHub Secrets

To deploy Rick AI Expert, you need to set up the following GitHub secrets:

### 1. Navigate to Repository Settings
- Go to your GitHub repository: `https://github.com/YOUR_USERNAME/rick-ai-expert`
- Click **Settings** tab
- Click **Secrets and variables** > **Actions**

### 2. Add Required Secrets

Click **New repository secret** and add:

#### `OPENAI_API_KEY`
- **Name**: `OPENAI_API_KEY`
- **Value**: `sk-proj-[your-actual-openai-api-key-here]`
- **Description**: OpenAI API key for GPT-4o mini integration

### 3. Verify Secrets

After adding, you should see:
- ✅ `OPENAI_API_KEY` (hidden)

### 4. Deployment Reference

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will automatically use these secrets:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  PRODUCTION: true
```

### 5. Platform-Specific Environment Variables

When deploying to different platforms, use these same values:

#### DigitalOcean App Platform
```
OPENAI_API_KEY = [Use your actual API key]
PRODUCTION = true
```

#### Railway
```
OPENAI_API_KEY=[Use your actual API key]
PRODUCTION=true
```

#### Heroku
```bash
heroku config:set OPENAI_API_KEY="[your-actual-key]"
heroku config:set PRODUCTION="true"
```

## Security Notes

- ✅ API keys are stored securely in GitHub Secrets
- ✅ Keys are not exposed in repository code
- ✅ Keys are injected at deployment time
- ✅ GitHub prevents accidental key exposure in commits

## Testing Locally

For local development, create a `.env` file (gitignored):

```bash
OPENAI_API_KEY=your-actual-key-here
PRODUCTION=false
```

**Never commit `.env` files to the repository!**