#!/usr/bin/env python3
"""
Concept2Comic API Server

A Flask API that generates educational comic strips using Google Gemini AI.
Converts any concept into a fun, engaging 4-panel comic with consistent mascot characters.

Test Mode:
Set environment variable TEST_MODE=true to use placeholder data instead of API calls.
"""

import json
import os
import base64
import time
from typing import Dict, List
import google.generativeai as genai
import io
from flask import Flask, request, jsonify, send_from_directory
from google.genai import types
from PIL import Image
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comic_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value
    else:
        logger.warning(f".env file not found at {env_file}")

# Load environment variables
load_env_file()

# Test mode configuration
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

class ComicGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the comic generator with API keys."""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key and not TEST_MODE:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        if not TEST_MODE:
            # Configure Gemini for text generation
            logger.info("Configuring Gemini API...")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini model initialized successfully")
            
            # Configure Google GenAI client for image generation
            from google import genai as google_genai
            logger.info("Initializing image generation client...")
            self.genai_client = google_genai.Client(api_key=self.api_key)
            logger.info("Image generation client initialized successfully")
        
    def create_placeholder_comic_data(self, concept: str, use_party_cat: bool = False) -> Dict:
        """Create placeholder comic data for test mode."""
        if use_party_cat:
            return {
                "title": f"Party Cat Explains: {concept}",
                "panels": [
                    {
                        "text": "Hi! I'm Party Cat, and I'm here to teach you about this concept!",
                        "image_prompt": "Party Cat (black cat with red party hat) waving hello with a big smile"
                    },
                    {
                        "text": "Let me show you how this works in a fun way!",
                        "image_prompt": "Party Cat pointing at something interesting with excitement"
                    },
                    {
                        "text": "See how it all comes together? Pretty cool, right?",
                        "image_prompt": "Party Cat doing a little dance of understanding"
                    },
                    {
                        "text": "Now you know the basics! Ready to learn more?",
                        "image_prompt": "Party Cat giving a thumbs up with a proud expression"
                    }
                ],
                "further_exploration": "Try exploring related concepts or dive deeper into advanced topics! Check out [Educational Psychology](https://en.wikipedia.org/wiki/Educational_psychology) or [Learning Theory](https://en.wikipedia.org/wiki/Learning_theory_(education)) for more insights."
            }
        else:
            return {
                "title": f"Learning About: {concept}",
                "panels": [
                    {
                        "text": "Welcome! Let's explore this concept together!",
                        "image_prompt": "A friendly mascot character waving hello"
                    },
                    {
                        "text": "Here's how it works in simple terms!",
                        "image_prompt": "The mascot demonstrating the concept visually"
                    },
                    {
                        "text": "Pretty interesting, don't you think?",
                        "image_prompt": "The mascot showing understanding and excitement"
                    },
                    {
                        "text": "Great job learning! You're doing awesome!",
                        "image_prompt": "The mascot celebrating and encouraging the learner"
                    }
                ],
                "further_exploration": "Keep exploring and learning more about related topics! Visit [Knowledge](https://en.wikipedia.org/wiki/Knowledge) or [Education](https://en.wikipedia.org/wiki/Education) on Wikipedia for deeper insights."
            }
    
    def create_placeholder_images(self) -> List[str]:
        """Create placeholder base64 images for test mode."""
        colors = ['#FFE5E5', '#E5F3FF', '#E5FFE5', '#FFF5E5']  # Light red, blue, green, orange
        base64_images = []
        
        for i, color in enumerate(colors):
            img = Image.new('RGB', (400, 400), color=color)
            base64_images.append(self._image_to_base64(img))
        
        return base64_images
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    def generate_comic_data(self, concept: str, use_party_cat: bool = False) -> Dict:
        """Generate comic strip data using Gemini."""
        if use_party_cat:
            prompt = f"""You are a world-class prompt engineer and a playful educational comics writer. Using our mascot, party cat, a black cat with a red party hat, create a 4-panel micro-comic led by party cat, that teaches a key idea about the concept below. The mascot, party cat, should embody the concept in a memorable, friendly way while keeping the same look through the panels. Keep narration concise and engaging.

CRITICAL IMAGE RULES:
- ABSOLUTELY NO TEXT IN THE IMAGES. No letters, words, captions, signage, labels, typography, or speech bubbles. All words must be outside the image in the JSON "text" fields only.
- Images must rely on visual storytelling: party cat acting, pointing, demonstrating, reacting.
- Party cat must maintain consistent appearance: black cat with red party hat in all panels.

STYLE:
- Retro 90s comic-book look with VIBRANT FULL COLOR throughout
- Bold, dynamic black ink lines; energetic poses and expressions
- Ben-Day/halftone dot shading, screentone textures; minimal gradients
- Pop CMYK colors (magenta, cyan, yellow, black); high contrast and saturation
- Use bright, vivid colors for all elements - characters, backgrounds, objects
- NEVER use black and white or grayscale - always use rich, saturated colors
- Slight off-register print feel; subtle newsprint paper grain
- Consistent party cat design across panels

Return only valid JSON using exactly this schema:

{{
  "title": "string - short, catchy, party cat-forward title",
  "panels": [
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; party cat action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; party cat action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; party cat action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; party cat action; NO TEXT IN IMAGE" }}
  ],
  "further_exploration": "string - one or two suggestions for what to learn next with relevant Wikipedia hotlinks (format: [Topic Name](https://en.wikipedia.org/wiki/Article_Name))"
}}

Concept: {concept}"""
        else:
            prompt = f"""You are a world-class prompt engineer and a playful educational comics writer.

Create a fun, mascot-led 4-panel micro-comic that teaches a key idea about the concept below. The mascot should embody the concept in a memorable, friendly way (e.g., for gravity: a cute planet mascot). Keep narration concise and engaging.

CRITICAL IMAGE RULES:
- ABSOLUTELY NO TEXT IN THE IMAGES. No letters, words, captions, signage, labels, typography, or speech bubbles. All words must be outside the image in the JSON "text" fields only.
- Images must rely on visual storytelling: the mascot acting, pointing, demonstrating, reacting.

STYLE:
- Retro 90s comic-book look with VIBRANT FULL COLOR throughout
- Bold, dynamic black ink lines; energetic poses and expressions
- Ben-Day/halftone dot shading, screentone textures; minimal gradients
- Pop CMYK colors (magenta, cyan, yellow, black); high contrast and saturation
- Use bright, vivid colors for all elements - characters, backgrounds, objects
- NEVER use black and white or grayscale - always use rich, saturated colors
- Slight off-register print feel; subtle newsprint paper grain
- Consistent mascot design across panels

Return only valid JSON using exactly this schema:

{{
  "title": "string - short, catchy, mascot-forward title",
  "panels": [
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; mascot action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; mascot action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; mascot action; NO TEXT IN IMAGE" }},
    {{ "text": "string - 1–2 sentences of dialogue/narration (outside image)", "image_prompt": "string - vivid scene; mascot action; NO TEXT IN IMAGE" }}
  ],
  "further_exploration": "string - one or two suggestions for what to learn next with relevant Wikipedia hotlinks (format: [Topic Name](https://en.wikipedia.org/wiki/Article_Name))"
}}

Concept: {concept}"""

        try:
            logger.info("Generating comic strip data...")
            response = self.model.generate_content(prompt)
            logger.info("Received response from Gemini API")
            
            response_text = response.text.strip()
            
            # Clean up the response text
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Additional JSON cleaning
            response_text = response_text.strip()
            
            # Try to fix common JSON issues
            try:
                comic_data = json.loads(response_text)
                logger.info("Successfully parsed JSON response")
                return comic_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.error(f"Problematic JSON: {response_text}")
                
                # Try to extract JSON from the response if it's embedded in text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        cleaned_json = json_match.group(0)
                        comic_data = json.loads(cleaned_json)
                        logger.info("Successfully parsed cleaned JSON response")
                        return comic_data
                    except json.JSONDecodeError as e2:
                        logger.error(f"Cleaned JSON also failed: {e2}")
                        logger.error(f"Cleaned JSON: {cleaned_json}")
                
                # If all else fails, create a fallback response
                logger.warning("Using fallback comic data due to JSON parsing failure")
                return self.create_placeholder_comic_data(concept, use_party_cat)
            
        except Exception as e:
            logger.error(f"Error generating comic data: {e}")
            logger.warning("Using fallback comic data due to unexpected error")
            return self.create_placeholder_comic_data(concept, use_party_cat)

    def generate_grid_image(self, comic_data: Dict, use_party_cat: bool) -> Image.Image:
        """Generate a single 2×2 grid image covering all four panels to ensure consistency."""
        logger.info("Starting grid image generation.")
        panels = comic_data.get('panels', [])
        if len(panels) != 4:
            logger.error("Grid mode requires exactly 4 panels.")
            raise ValueError("Grid mode requires exactly 4 panels in comic_data")

        style_prefix = (
            "Retro 90s comic-book aesthetic with VIBRANT FULL COLOR throughout, bold dynamic black ink lines, energetic poses, expressive faces. "
            "Ben-Day/halftone dot shading and screentone textures; minimal gradients. "
            "Pop CMYK colors (magenta, cyan, yellow, black) with high contrast and saturation; slight off-register print feel. "
            "Use bright, vivid colors for all elements - characters, backgrounds, objects. "
            "NEVER use black and white or grayscale - always use rich, saturated colors. "
            "Subtle newsprint paper grain; hand-inked look, clean but organic line work. "
            "Dynamic composition reminiscent of 90s comics. "
            "NO TEXT, no letters, no words, no captions, no signage, no labels, no typography, "
            "no speech bubbles. Visual storytelling only. "
        )

        mascot_clause = (
            "The mascot is Party Cat: a black cat with a red party hat. Keep appearance identical across quadrants. "
            if use_party_cat
            else "Maintain one consistent mascot character design across all quadrants. "
        )

        quadrant_instructions = (
            "Create one single square image arranged as a 2×2 grid with four equal quadrants: "
            "top-left, top-right, bottom-left, bottom-right. Do not draw numbers, letters, labels, "
            "captions, or speech bubbles. Do not draw panel borders or grid lines; just compose the scenes so "
            "each occupies its quadrant naturally. Keep consistent lighting, proportions, colors, and character details across quadrants. "
        )

        scenes = (
            f"Top-left: {panels[0]['image_prompt']}\n"
            f"Top-right: {panels[1]['image_prompt']}\n"
            f"Bottom-left: {panels[2]['image_prompt']}\n"
            f"Bottom-right: {panels[3]['image_prompt']}"
        )

        full_prompt = f"{style_prefix}{mascot_clause}{quadrant_instructions}Render the following four scenes, one per quadrant:\n{scenes}"

        try:
            logger.info("Generating single 2×2 grid image for all panels...")
            
            response = self.genai_client.models.generate_image(
                model='imagen-4.0-generate-001',
                prompt=full_prompt
            )

            logger.info("Successfully received response from Imagen API.")
            
            generated_image = response.generated_images[0]
            image_bytes = generated_image.image.image_bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            logger.info("Successfully created PIL image from response.")
            return pil_image
        except Exception as e:
            logger.error(f"An unexpected error occurred during grid image generation: {e}")
            logger.info("Using a placeholder grid image.")
            return Image.new('RGB', (800, 800), color='lightblue')

    def slice_grid_to_base64(self, grid_image: Image.Image) -> List[str]:
        """Slice a 2×2 grid image into four equal panels and return them as base64 strings."""
        width, height = grid_image.size
        mid_x = width // 2
        mid_y = height // 2

        boxes = [
            (0, 0, mid_x, mid_y),                # top-left -> panel 1
            (mid_x, 0, width, mid_y),           # top-right -> panel 2
            (0, mid_y, mid_x, height),          # bottom-left -> panel 3
            (mid_x, mid_y, width, height),      # bottom-right -> panel 4
        ]

        base64_images = []
        for box in boxes:
            crop = grid_image.crop(box)
            buffered = io.BytesIO()
            crop.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_images.append(img_str)
        return base64_images

# Initialize Flask app
app = Flask(__name__)

# Simple CORS support
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

# Initialize comic generator
try:
    generator = ComicGenerator()
    logger.info(f"Comic generator initialized. Test mode: {TEST_MODE}")
except ValueError as e:
    if not TEST_MODE:
        logger.error(f"Failed to initialize comic generator: {e}")
        generator = None
    else:
        generator = ComicGenerator()
        logger.info("Comic generator initialized in test mode")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "test_mode": TEST_MODE,
        "generator_initialized": generator is not None
    })

@app.route('/generate_comic', methods=['POST', 'OPTIONS'])
def generate_comic_endpoint():
    """API endpoint to generate a comic strip."""
    logger.info("Received request for /generate_comic")
    
    # Handle preflight CORS requests
    if request.method == 'OPTIONS':
        return ('', 204)
    
    if not generator:
        logger.error("Comic generator not initialized")
        return jsonify({"error": "Service unavailable"}), 503
    
    data = request.json
    concept = data.get('concept')
    use_party_cat = data.get('use_party_cat', False)
    logger.info(f"Concept: {concept}, Party Cat: {use_party_cat}, Test Mode: {TEST_MODE}")

    if not concept:
        logger.error("Concept is required but was not provided.")
        return jsonify({"error": "Concept is required"}), 400

    try:
        if TEST_MODE:
            logger.info("*** RUNNING IN TEST MODE *** - using placeholder data")
            time.sleep(2)  # Simulate API delay
            
            comic_data = generator.create_placeholder_comic_data(concept, use_party_cat)
            panel_images_base64 = generator.create_placeholder_images()
            logger.info("*** TEST MODE: Using placeholder data instead of real API calls ***")
        else:
            logger.info("Generating comic data (text)...")
            comic_data = generator.generate_comic_data(concept, use_party_cat)
            logger.info("Generating comic image grid...")
            grid_image = generator.generate_grid_image(comic_data, use_party_cat)
            
            logger.info("Slicing grid image into panels...")
            panel_images_base64 = generator.slice_grid_to_base64(grid_image)
            logger.info("Finished slicing grid image.")

        response_panels = []
        if 'panels' in comic_data and len(comic_data['panels']) == len(panel_images_base64):
            for i, panel_data in enumerate(comic_data['panels']):
                response_panels.append({
                    'text': panel_data.get('text', ''),
                    'image': panel_images_base64[i]
                })

        logger.info("Successfully assembled response. Sending back to client.")
        return jsonify({
            'title': comic_data.get('title', 'Comic Title'),
            'further_exploration': comic_data.get('further_exploration', ''),
            'panels': response_panels,
            'test_mode': TEST_MODE
        })

    except Exception as e:
        logger.error(f"Error in /generate_comic endpoint: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == "__main__":
    port = int(os.getenv('BACKEND_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Concept2Comic API on port {port}")
    logger.info(f"Test mode: {TEST_MODE}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
