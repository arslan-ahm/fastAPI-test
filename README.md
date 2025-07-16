# Recipe API

A FastAPI-based recipe generation API using LangChain and OpenAI that creates unique recipes from ingredients.

## Features

- **Text-based Recipe Generation**: Input a list of ingredients and get a unique recipe
- **Image-based Recipe Generation**: Upload an image of ingredients and get a recipe
- **OpenAI Integration**: Uses GPT models for creative recipe generation
- **Clean Architecture**: Well-structured codebase with separation of concerns

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recipe-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key.

5. **Run the application**
   ```bash
   python main.py
   ```

## API Endpoints

### 1. Generate Recipe from Ingredients List

**POST** `/api/recipes/from-ingredients`

```json
{
  "ingredients": ["chicken breast", "tomatoes", "basil", "mozzarella"],
  "cuisine_type": "Italian",
  "dietary_restrictions": ["gluten-free"]
}
```

### 2. Generate Recipe from Image

**POST** `/api/recipes/from-image`

Upload an image file containing ingredients.

## Project Structure

```
recipe-api/
├── main.py                    # Application entry point
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── recipes.py     # Recipe endpoints
│   │   └── dependencies.py    # API dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   └── exceptions.py      # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recipe_service.py  # Recipe generation logic
│   │   └── image_service.py   # Image processing logic
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # Utility functions
├── requirements.txt
├── .env.example
├── .env
└── README.md
```

## Usage Examples

### Using curl

```bash
# Generate recipe from ingredients
curl -X POST "http://localhost:8000/api/recipes/from-ingredients" \
     -H "Content-Type: application/json" \
     -d '{
       "ingredients": ["chicken", "rice", "vegetables"],
       "cuisine_type": "Asian"
     }'

# Generate recipe from image
curl -X POST "http://localhost:8000/api/recipes/from-image" \
     -F "file=@ingredients.jpg"
```

## License

MIT License
