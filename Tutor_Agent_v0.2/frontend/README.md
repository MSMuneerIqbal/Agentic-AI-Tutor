# Tutor GPT Frontend

Next.js frontend for the Tutor GPT agentic tutoring system.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Structure

- `app/` - Next.js App Router pages
- `components/` - React components (ChatClient, TavilyCard, QuizQuestion, etc.)
- `lib/` - Utilities and helpers
- `tests/` - Frontend tests

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

