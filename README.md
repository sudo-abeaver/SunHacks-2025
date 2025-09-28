# Concept2Comic

Transform any concept into engaging educational comic strips using AI! This application uses Google Gemini AI to generate fun, 4-panel comics with consistent mascot characters that make learning enjoyable.

## Features

- 🎨 AI-powered comic generation using Google Gemini
- 📚 Educational focus with mascot characters
- 🖼️ 4-panel comic format
- 🎭 Consistent character design across panels
- 🌐 Modern web interface built with Next.js
- 🔧 Test mode for development without API calls

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Google Gemini API key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd concept2comic-production
```

### 2. Environment Configuration

Copy the example environment file and configure your API key:

```bash
cp env.example .env
```

Edit `.env` and add your Google Gemini API key:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

To get a Google Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 3. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Start the backend server:

```bash
python app.py
```

The backend will run on `http://localhost:5000`

### 4. Frontend Setup

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Enter any concept you want to turn into a comic
3. Click "Generate Comic" and wait for the AI to create your educational comic strip
4. Download or share your generated comic!

## Development

### Test Mode

For development without using API credits, you can enable test mode by setting `TEST_MODE=true` in your `.env` file. This will return placeholder comic data instead of making actual API calls.

### Project Structure

```
concept2comic-production/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.js         # Main application page
│   │   ├── layout.js       # App layout
│   │   └── globals.css     # Global styles
│   ├── components/
│   │   └── HalftoneParticles.js  # Visual effects
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── .env                    # Environment variables (create from env.example)
├── env.example             # Environment template
└── README.md              # This file
```

### API Endpoints

- `POST /generate-comic` - Generate a comic from a concept
- `GET /health` - Health check endpoint

## Troubleshooting

### Common Issues

**Backend won't start:**
- Make sure you have Python 3.8+ installed
- Check that all requirements are installed: `pip install -r backend/requirements.txt`
- Verify your `.env` file has the correct API key

**Frontend won't start:**
- Ensure Node.js 16+ is installed
- Delete `node_modules` and run `npm install` again
- Check for port conflicts (default is 3000)

**API errors:**
- Verify your Google Gemini API key is valid
- Check your internet connection
- Enable test mode for development: `TEST_MODE=true`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini AI for comic generation
- Next.js for the frontend framework
- Flask for the backend API
- All contributors and testers
