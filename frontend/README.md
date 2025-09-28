# Concept2Comic - Next.js Frontend

A Next.js application that converts the original HTML/CSS/JS frontend into a modern React-based application.

## Features

- **React Components**: Converted from vanilla HTML/CSS/JS to React components with hooks
- **Modern Styling**: CSS modules and global styles using Next.js conventions
- **Client-Side Rendering**: Uses `'use client'` directive for interactive components
- **Dynamic Imports**: html2canvas is dynamically imported to avoid SSR issues
- **State Management**: Uses React hooks for managing application state
- **Responsive Design**: Maintains the original responsive design

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── globals.css      # Global styles
│   ├── layout.js        # Root layout component
│   └── page.js          # Main page component
├── components/          # Reusable components (if needed)
├── package.json         # Dependencies and scripts
├── next.config.js       # Next.js configuration
└── README.md           # This file
```

## Key Changes from Original

1. **HTML → React Components**: The single HTML file is now split into React components
2. **Vanilla JS → React Hooks**: Event handlers and state management use React hooks
3. **CSS → Next.js Styling**: CSS is organized using Next.js conventions
4. **Dynamic Imports**: html2canvas is imported dynamically to prevent SSR issues
5. **Modern React Patterns**: Uses functional components, hooks, and modern React patterns

## API Integration

The application connects to the same backend API as the original:
- API endpoint: `http://localhost:5001/generate_comic`
- Handles the same request/response format
- Maintains all original functionality

## Build and Deploy

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Dependencies

- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **html2canvas**: For downloading comics as images
- **ESLint**: Code linting
