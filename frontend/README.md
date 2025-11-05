# CFG SQL Query Tool - Frontend

A Next.js frontend for querying fitness data using natural language, powered by GPT-5's Context-Free Grammar feature.

## Features

- Password-protected access
- Natural language query input
- Example queries for reference
- Raw JSON results display
- Clean, responsive UI built with shadcn/ui

## Setup

### Prerequisites

- Node.js 18+ installed
- Backend API running on port 8000 (or configured API URL)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

Copy `.env.example` to `.env.local` and update the values:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
# Set your access password
NEXT_PUBLIC_PASSWORD=your-secure-password

# Backend API URL (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Usage

1. Enter the password you configured in `.env.local`
2. Type a natural language query about your fitness data
3. Click "Submit Query" to see results
4. Results are displayed as raw JSON

### Example Queries

- "Calculate the average daily distance for the last 30 days"
- "Sum the total calories burned in the last 7 days"
- "Count the days in the last 30 days where I burned more than 500 calories"
- "Show me all days where I ran more than 5 kilometers and burned over 400 calories"
- "List all days in the last week where I had zero active time"
- "Find the maximum distance in a single day over the last 6 months"

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with shadcn CSS variables
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main page (password gate + query interface)
├── components/
│   ├── example-queries.tsx   # Example queries display
│   ├── password-gate.tsx     # Password protection component
│   ├── query-interface.tsx   # Main query UI
│   └── ui/                   # shadcn UI components
│       ├── alert.tsx
│       ├── button.tsx
│       ├── card.tsx
│       └── input.tsx
├── lib/
│   ├── api.ts                # Backend API client
│   └── utils.ts              # Utility functions
└── .env.local                # Environment variables
```

## Technologies

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Radix UI primitives

## Security Note

The password protection is implemented client-side for simplicity. For production use, implement proper server-side authentication to protect your API keys.