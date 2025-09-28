# Comic Strip Generator

A Python application that generates educational comic strips using Google's Gemini API and Imagen 4.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp ../.env.example ../.env
   ```

2. Edit the `.env` file and add your API key:
   ```
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

### 4. Run the Application

```bash
python comic_generator.py
```

## Features

- Generate educational comic strips from any concept
- Choose between generic mascots or Party Cat
- Two image generation modes:
  - Individual panel generation
  - Single 2×2 grid with automatic slicing
- Rich console output with tables and formatting
- Automatic final comic assembly

## Output Files

The application generates several files in the `anthony_code` directory:
- `panel_1.png` through `panel_4.png` - Individual comic panels
- `final_comic.png` - Assembled comic with text
- `comic_data.json` - Comic data in JSON format
- `final_grid.png` - Grid image (if using grid mode)

All files are saved in the same directory where you run the script from.

## Security Note

Never commit your `.env` file to version control. The `.env` file is already added to `.gitignore` to prevent accidental commits.
