# Recipe API - Vercel Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- [Vercel CLI](https://vercel.com/cli) installed: `npm i -g vercel`
- LLM7 Token from [https://token.llm7.io/](https://token.llm7.io/)
- Vercel account

### 2. Environment Setup
1. Copy `.env.example` to `.env`
2. Add your LLM7_TOKEN:
```env
LLM7_TOKEN=your_actual_token_here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### 3. Deploy
```bash
# Option 1: Using deployment script
chmod +x deploy.sh
./deploy.sh

# Option 2: Manual deployment
vercel --prod
```

### 4. Configure Environment Variables
In Vercel Dashboard → Project → Settings → Environment Variables:
- `LLM7_TOKEN`: Your token from llm7.io
- `API_HOST`: `0.0.0.0`
- `API_PORT`: `8000`
- `DEBUG`: `False`

### 5. Test Your Deployment
- Health check: `https://your-domain.vercel.app/health`
- API docs: `https://your-domain.vercel.app/docs`
- Recipe from ingredients: `POST https://your-domain.vercel.app/api/recipes/from-ingredients`
- Recipe from image: `POST https://your-domain.vercel.app/api/recipes/from-image`

## 📋 API Endpoints

### Pakistani Cuisine Focus
The API defaults to Pakistani cuisine but supports 15+ international cuisines:
- Pakistani (default)
- Indian, Bangladeshi, Turkish, Arabic, Persian, Afghan
- Chinese, Thai, Japanese, Italian, Mexican, French, American, Mediterranean

### Example Usage

#### Text-based Recipe Generation
```bash
curl -X POST "https://your-domain.vercel.app/api/recipes/from-ingredients" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "onions", "tomatoes", "ginger-garlic paste"],
    "style": "Pakistani",
    "people": 4
  }'
```

#### Image-based Recipe Generation
```bash
curl -X POST "https://your-domain.vercel.app/api/recipes/from-image" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/your/image.jpg" \
  -F "style=Pakistani" \
  -F "people=4"
```

## 🔧 Technical Details

### Architecture
- **Framework**: FastAPI with Pydantic validation
- **AI Service**: LLM7 (OpenAI-compatible API)
- **Models**: 
  - `open-mixtral-8x22b` for text-based recipes
  - `gpt-4o-mini-2024-07-18` for image processing
- **Deployment**: Vercel with Python runtime

### Project Structure
```
recipe-api/
├── api/index.py          # Vercel entry point
├── src/
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic (LLM7, Recipe services)
│   ├── models/           # Pydantic schemas
│   ├── core/             # Configuration
│   └── utils/            # Helper functions
├── main.py               # FastAPI application
├── vercel.json           # Vercel configuration
└── requirements.txt      # Dependencies
```

### Features
- 🇵🇰 **Pakistani cuisine expertise** with authentic recipes
- 🌍 **Multi-cuisine support** (15+ international cuisines)
- 🖼️ **Image processing** for ingredient recognition
- 📝 **Text input** for ingredient lists
- 🏥 **Diet preferences** (vegetarian, vegan, gluten-free, etc.)
- ⚡ **Fast API responses** with comprehensive recipe details
- 📚 **Auto-generated documentation** at `/docs`

## 🐛 Troubleshooting

### Common Issues
1. **"Module not found" errors**: Check PYTHONPATH in vercel.json
2. **Timeout errors**: Increase maxDuration in vercel.json (currently 60s)
3. **Image upload fails**: Check file size limits (50MB max)
4. **API key errors**: Verify LLM7_TOKEN in environment variables

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## 📞 Support
- API Documentation: `/docs` endpoint
- Health Check: `/health` endpoint
- LLM7 Token: [https://token.llm7.io/](https://token.llm7.io/)
