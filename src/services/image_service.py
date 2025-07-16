"""Image processing service for extracting ingredients from images."""

import base64
from typing import List
from PIL import Image
import io
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from ..core.config import settings
from ..core.exceptions import ImageProcessingError, OpenAIKeyMissingError


class ImageService:
    """Service for processing images and extracting ingredient information."""
    
    def __init__(self):
        """Initialize the image service."""
        if not settings.openai_api_key:
            raise OpenAIKeyMissingError()
            
        # Use GPT-4 Vision for image analysis
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",  # Updated to use GPT-4o which supports vision
            api_key=settings.openai_api_key,
            max_tokens=1000
        )
    
    async def extract_ingredients_from_image(self, image_data: bytes) -> List[str]:
        """
        Extract ingredients from an uploaded image.
        
        Args:
            image_data: Raw image data bytes
            
        Returns:
            List of identified ingredients
        """
        try:
            # Validate and process the image
            processed_image = self._process_image(image_data)
            
            # Convert image to base64 for API
            base64_image = self._image_to_base64(processed_image)
            
            # Create the prompt for ingredient extraction
            prompt = """
            Please analyze this image and identify all the ingredients you can see. 
            Focus on foods, vegetables, fruits, meats, and other cooking ingredients.
            
            Return your response as a simple list of ingredients, one per line, like this:
            - tomatoes
            - onions
            - garlic
            - chicken breast
            - olive oil
            
            Only include actual ingredients that you can clearly identify in the image.
            Do not include cooking utensils, plates, or non-food items.
            Be specific about the type of ingredient when possible (e.g., "red bell pepper" instead of just "pepper").
            """
            
            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            )
            
            # Get response from vision model
            response = await self.vision_llm.ainvoke([message])
            
            # Parse ingredients from response
            ingredients = self._parse_ingredients_response(response.content)
            
            if not ingredients:
                raise ImageProcessingError("No ingredients could be identified in the image")
            
            return ingredients
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image: {str(e)}")
    
    def _process_image(self, image_data: bytes) -> Image.Image:
        """
        Process and validate the uploaded image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processed PIL Image
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if it's too large (max 1024x1024 for API efficiency)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            raise ImageProcessingError(f"Invalid image format: {str(e)}")
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            return base64.b64encode(image_bytes).decode('utf-8')
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to encode image: {str(e)}")
    
    def _parse_ingredients_response(self, response_content: str) -> List[str]:
        """
        Parse the ingredients from the LLM response.
        
        Args:
            response_content: Raw response from the vision model
            
        Returns:
            List of cleaned ingredient names
        """
        try:
            ingredients = []
            lines = response_content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Remove bullet points and numbering
                if line.startswith('- '):
                    line = line[2:].strip()
                elif line.startswith('• '):
                    line = line[2:].strip()
                elif line and line[0].isdigit() and '. ' in line:
                    line = line.split('. ', 1)[1].strip()
                
                # Skip empty lines and non-ingredient text
                if line and not line.lower().startswith(('here', 'i can see', 'the image', 'ingredients:')):
                    # Clean up the ingredient name
                    ingredient = line.lower().strip()
                    if ingredient and len(ingredient) > 1:
                        ingredients.append(ingredient)
            
            # Remove duplicates while preserving order
            unique_ingredients = []
            seen = set()
            for ingredient in ingredients:
                if ingredient not in seen:
                    unique_ingredients.append(ingredient)
                    seen.add(ingredient)
            
            return unique_ingredients[:15]  # Limit to 15 ingredients for practical use
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to parse ingredients response: {str(e)}")
