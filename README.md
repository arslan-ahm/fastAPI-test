# Recipe API

A sophisticated recipe API powered by LLM7 with Pakistani cuisine focus.

## Features

- **LLM7 Integration**: Uses advanced language models for recipe generation
- **Pakistani Cuisine Focus**: Specialized in authentic Pakistani recipes
- **Image-based Recipes**: Generate recipes from ingredient images
- **Multiple Cuisines**: Supports 16 international cuisines
- **Dietary Preferences**: Accommodates 5 dietary restrictions

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/recipes/styles` - Available cuisine styles
- `GET /api/recipes/diets` - Available dietary types
- `GET /api/recipes/health` - Recipe service health
- `POST /api/recipes/from-ingredients` - Generate recipe from ingredients
- `POST /api/recipes/from-image` - Generate recipe from image

## Environment Variables

```bash
LLM7_TOKEN=your_llm7_token_here
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py

# Run tests
python test_api.py
```

## Deployment

This API is configured for Vercel deployment:

1. Set the `LLM7_TOKEN` environment variable in Vercel
2. Deploy using `vercel --prod`

The API will be available at your Vercel domain.

## Fixed Issues

- ✅ Removed problematic dependencies (mangum, google-generativeai)
- ✅ Simplified handler for Vercel compatibility
- ✅ Fixed router prefix conflicts
- ✅ Added proper Python path configuration
- ✅ Optimized for serverless deployment

## Tech Stack

- FastAPI
- LLM7 (OpenAI-compatible API)
- Pydantic
- Python 3.12+

## Sample Usage

### Generate Recipe from Ingredients

```bash
curl -X POST "https://your-vercel-domain.vercel.app/api/recipes/from-ingredients" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "basmati rice", "yogurt", "garam masala"],
    "style": "Pakistani",
    "diet": "Non-Vegetarian"
  }'
```

### Get Available Styles

```bash
curl "https://your-vercel-domain.vercel.app/api/recipes/styles"
```

The API returns authentic Pakistani recipes with detailed instructions and cultural context.
