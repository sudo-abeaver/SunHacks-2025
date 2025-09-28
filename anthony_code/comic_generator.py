#!/usr/bin/env python3
"""
Comic Strip Generator using Google Gemini API
Generates educational comic strips with text and images based on user concepts.
"""

import json
import os
import base64
from typing import Dict, List
import google.generativeai as genai

# Load environment variables
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass
from google import genai as google_genai
from google.genai import types
from PIL import Image
from PIL import ImageDraw, ImageFont
import textwrap
import io
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

class ComicGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the comic generator with API keys."""
        # Gemini API Key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Please provide GEMINI_API_KEY environment variable or pass it as parameter")

        # Configure Gemini for text generation
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Configure Google GenAI client for image generation
        self.genai_client = google_genai.Client(api_key=self.api_key)
        
        self.console = Console()
        
    def get_user_concept(self) -> tuple[str, bool, bool]:
        """Get the concept, mascot choice, and image mode from user input."""
        self.console.print("\n[bold blue]🎨 Comic Strip Generator[/bold blue]")
        self.console.print("Enter a concept you'd like to learn about through a comic strip!")
        concept = input("\n📚 Concept: ").strip()
        
        self.console.print("\n[bold yellow]Choose your mascot:[/bold yellow]")
        self.console.print("1. Generic mascot (AI creates a custom character for your concept)")
        self.console.print("2. Party Cat (our signature black cat with a red party hat)")
        
        use_party_cat = False
        while True:
            choice = input("\n🎭 Mascot choice (1 or 2): ").strip()
            if choice == "1":
                use_party_cat = False
                break
            elif choice == "2":
                use_party_cat = True
                break
            else:
                self.console.print("[red]Please enter 1 or 2[/red]")

        self.console.print("\n[bold yellow]Choose image generation mode:[/bold yellow]")
        self.console.print("1. Generate 4 separate images (default)")
        self.console.print("2. Generate a single 2×2 grid image for all panels (best consistency), then auto-slice")

        use_grid = False
        while True:
            mode = input("\n🖼️ Image mode (1 or 2): ").strip()
            if mode == "1":
                use_grid = False
                break
            elif mode == "2":
                use_grid = True
                break
            else:
                self.console.print("[red]Please enter 1 or 2[/red]")

        return concept, use_party_cat, use_grid
    
    def generate_comic_data(self, concept: str, use_party_cat: bool = False) -> Dict:
        """Generate comic strip data using Gemini."""
        if use_party_cat:
            prompt = f"""You are a world-class prompt engineer and a playful educational comics writer. Using our mascot, party cat, a black cat with a red party hat, create a 4-panel micro-comic led by party cat, that teaches a key idea about the concept below. The mascot, party cat, should embody the concept in a memorable, friendly way while keeping the same look through the panels. Keep narration concise and engaging.

CRITICAL IMAGE RULES:
- ABSOLUTELY NO TEXT IN THE IMAGES. No letters, words, captions, signage, labels, typography, or speech bubbles. All words must be outside the image in the JSON "text" fields only.
- Images must rely on visual storytelling: party cat acting, pointing, demonstrating, reacting.
- Party cat must maintain consistent appearance: black cat with red party hat in all panels.

STYLE:
- Colorful, cartoony, high-contrast visuals
- Clear composition, readable character silhouettes, simple backgrounds
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
  "further_exploration": "string - one or two suggestions for what to learn next"
}}

Concept: {concept}"""
        else:
            prompt = f"""You are a world-class prompt engineer and a playful educational comics writer.

Create a fun, mascot-led 4-panel micro-comic that teaches a key idea about the concept below. The mascot should embody the concept in a memorable, friendly way (e.g., for gravity: a cute planet mascot). Keep narration concise and engaging.

CRITICAL IMAGE RULES:
- ABSOLUTELY NO TEXT IN THE IMAGES. No letters, words, captions, signage, labels, typography, or speech bubbles. All words must be outside the image in the JSON "text" fields only.
- Images must rely on visual storytelling: the mascot acting, pointing, demonstrating, reacting.

STYLE:
- Colorful, cartoony, high-contrast visuals
- Clear composition, readable character silhouettes, simple backgrounds
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
  "further_exploration": "string - one or two suggestions for what to learn next"
}}

Concept: {concept}"""

        try:
            self.console.print("🤖 Generating comic strip data...")
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            comic_data = json.loads(response_text)
            return comic_data
            
        except json.JSONDecodeError as e:
            self.console.print(f"[red]Error parsing JSON response: {e}[/red]")
            self.console.print(f"[yellow]Raw response: {response_text}[/yellow]")
            raise
        except Exception as e:
            self.console.print(f"[red]Error generating comic data: {e}[/red]")
            raise

    def generate_image(self, prompt: str) -> Image.Image:
        """Generate an image using Imagen 4 Fast."""
        self.console.print(f"🎨 Generating image with Imagen 4 Fast: {prompt[:50]}...")
        
        # Add a style prefix to the user's prompt
        style_prefix = (
            "Playful cartoon character with simple geometric shapes, bold uneven black outlines, "
            "flat vivid colors, slight hand-drawn wobble, imperfect edges, clean crayon/marker style, "
            "minimal shading, white background, vector-like but organic. "
            "Slightly shaky line art, organic imperfect strokes, childlike but polished. "
            "Soft crayon texture, subtle paper grain. "
            "Clean edges but not mathematically perfect, vector illustration with natural hand-drawn vibe. "
            "NO TEXT, no letters, no words, no captions, no signage, no labels, no typography, "
            "no speech bubbles. Visual storytelling only. "
        )
        full_prompt = f"{style_prefix}{prompt}"
        
        try:
            response = self.genai_client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=full_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )
            
            # Get the first (and only) generated image
            generated_image = response.generated_images[0]
            
            # Convert the Google GenAI Image to PIL Image
            image_bytes = generated_image.image.image_bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            return pil_image
            
        except Exception as e:
            self.console.print(f"[red]An unexpected error occurred during image generation: {e}[/red]")
            # If anything fails, return a placeholder
            self.console.print("[bold yellow]Using a placeholder image.[/bold yellow]")
            return Image.new('RGB', (400, 300), color='lightblue')

    def generate_grid_image(self, comic_data: Dict, use_party_cat: bool) -> Image.Image:
        """Generate a single 2×2 grid image covering all four panels to ensure consistency."""
        panels = comic_data.get('panels', [])
        if len(panels) != 4:
            raise ValueError("Grid mode requires exactly 4 panels in comic_data")

        style_prefix = (
            "Playful cartoon character with simple geometric shapes, bold uneven black outlines, "
            "flat vivid colors, slight hand-drawn wobble, imperfect edges, clean crayon/marker style, "
            "minimal shading, white background, vector-like but organic. "
            "Slightly shaky line art, organic imperfect strokes, childlike but polished. "
            "Soft crayon texture, subtle paper grain. "
            "Clean edges but not mathematically perfect, vector illustration with natural hand-drawn vibe. "
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
            self.console.print("🧩 Generating single 2×2 grid image for all panels...")
            response = self.genai_client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=full_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )

            generated_image = response.generated_images[0]
            image_bytes = generated_image.image.image_bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            return pil_image
        except Exception as e:
            self.console.print(f"[red]An unexpected error occurred during grid image generation: {e}[/red]")
            self.console.print("[bold yellow]Using a placeholder grid image.[/bold yellow]")
            return Image.new('RGB', (800, 800), color='lightblue')

    def slice_grid_and_save(self, grid_image: Image.Image) -> List[str]:
        """Slice a 2×2 grid image into four equal panels and save them as panel_1..4.png."""
        width, height = grid_image.size
        mid_x = width // 2
        mid_y = height // 2

        boxes = [
            (0, 0, mid_x, mid_y),                # top-left -> panel 1
            (mid_x, 0, width, mid_y),           # top-right -> panel 2
            (0, mid_y, mid_x, height),          # bottom-left -> panel 3
            (mid_x, mid_y, width, height),      # bottom-right -> panel 4
        ]

        saved_paths = []
        for i, box in enumerate(boxes, start=1):
            crop = grid_image.crop(box)
            path = f"panel_{i}.png"
            crop.save(path)
            saved_paths.append(path)
        return saved_paths
    
    def display_comic(self, comic_data: Dict, use_party_cat: bool, use_grid: bool):
        """Display the comic strip in a nice table format and handle image generation mode."""
        self.console.print(f"\n[bold green]📖 {comic_data['title']}[/bold green]")
        
        # Create table for comic panels
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Panel", style="dim", width=6)
        table.add_column("Image", width=20)
        table.add_column("Story Text", width=60)
        
        if use_grid:
            grid_image = self.generate_grid_image(comic_data, use_party_cat)
            grid_path = "final_grid.png"
            try:
                grid_image.save(grid_path)
            except Exception:
                pass
            self.slice_grid_and_save(grid_image)

            for i, panel in enumerate(comic_data['panels'], 1):
                image_path = f"panel_{i}.png"
                table.add_row(
                    f"Panel {i}",
                    f"📷 [link={image_path}]View Image[/link]",
                    panel['text']
                )
        else:
            for i, panel in enumerate(comic_data['panels'], 1):
                image = self.generate_image(panel['image_prompt'])
                image_path = f"panel_{i}.png"
                image.save(image_path)
                table.add_row(
                    f"Panel {i}",
                    f"📷 [link={image_path}]View Image[/link]",
                    panel['text']
                )
        
        self.console.print(table)
        
        # Display further exploration
        self.console.print(f"\n[bold cyan]🔍 Further Exploration:[/bold cyan]")
        self.console.print(Panel(comic_data['further_exploration'], title="Next Steps"))
        
        # Show saved images info
        self.console.print(f"\n[bold yellow]💾 Images saved as: panel_1.png, panel_2.png, panel_3.png, panel_4.png[/bold yellow]")

        # Save comic data to a JSON file for the assembler script
        with open('comic_data.json', 'w') as f:
            json.dump(comic_data, f, indent=2)
        self.console.print(f"[bold green]📝 Comic data saved to comic_data.json[/bold green]")

        # Assemble final comic image
        self.assemble_final_comic(json_path='comic_data.json', output_path='final_comic.png')
        self.console.print(f"[bold green]🖼️ Final comic assembled and saved to final_comic.png[/bold green]")

    def run(self):
        """Main execution function."""
        try:
            # Get user input
            concept, use_party_cat, use_grid = self.get_user_concept()
            
            # Generate comic data
            comic_data = self.generate_comic_data(concept, use_party_cat)
            
            # Display the comic
            self.display_comic(comic_data, use_party_cat, use_grid)
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 Goodbye![/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ An error occurred: {e}[/red]")

    def assemble_final_comic(self, json_path='comic_data.json', output_path='final_comic.png'):
        """Assemble the final comic strip image combining images and text, saved to output_path."""
        # Layout constants
        PANEL_WIDTH = 512
        PANEL_HEIGHT = 512
        TEXT_WIDTH = 400
        PADDING = 20
        ROW_HEIGHT = PANEL_HEIGHT + PADDING
        TITLE_SPACE = 80

        # Load comic data
        try:
            with open(json_path, 'r') as f:
                comic_data = json.load(f)
        except FileNotFoundError:
            self.console.print(f"[red]Error: {json_path} not found. Generate images first.[/red]")
            return

        num_panels = len(comic_data.get('panels', []))
        total_width = PANEL_WIDTH + TEXT_WIDTH + (3 * PADDING)
        total_height = (num_panels * ROW_HEIGHT) - PADDING + TITLE_SPACE

        final_image = Image.new('RGB', (total_width, total_height), color='white')
        draw = ImageDraw.Draw(final_image)

        # Fonts
        try:
            title_font = ImageFont.truetype("Helvetica.ttc", 36)
            text_font = ImageFont.truetype("Helvetica.ttc", 20)
        except IOError:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Title
        comic_title = comic_data.get('title', 'My Comic')
        title_bbox = draw.textbbox((0, 0), comic_title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (total_width - title_width) / 2
        draw.text((title_x, PADDING), comic_title, font=title_font, fill='black')

        # Panels
        for i, panel in enumerate(comic_data.get('panels', [])):
            image_path = f"panel_{i+1}.png"
            try:
                panel_image = Image.open(image_path)
                panel_image = panel_image.resize((PANEL_WIDTH, PANEL_HEIGHT))
            except FileNotFoundError:
                panel_image = Image.new('RGB', (PANEL_WIDTH, PANEL_HEIGHT), color='lightgray')
                placeholder = ImageDraw.Draw(panel_image)
                placeholder.text((50, PANEL_HEIGHT / 2), "Image not found", fill='black')

            y_offset = (i * ROW_HEIGHT) + TITLE_SPACE
            final_image.paste(panel_image, (PADDING, y_offset))

            text_x = PANEL_WIDTH + (2 * PADDING)
            wrapped_text = textwrap.fill(panel.get('text', ''), width=35)
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=text_font, spacing=4)
            text_height = text_bbox[3] - text_bbox[1]
            centered_text_y = y_offset + (PANEL_HEIGHT - text_height) / 2
            draw.text((text_x, centered_text_y), wrapped_text, font=text_font, fill='black', spacing=4)

        final_image.save(output_path)

def main():
    """Main function to run the comic generator."""
    try:
        generator = ComicGenerator()
        generator.run()
    except ValueError as e:
        print(f"Error: {e}")
        print("The API key is already set in the script.")

if __name__ == "__main__":
    main()
