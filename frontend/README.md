# LLMPlayBench Frontend

React-based frontend for LLMPlayBench, providing a playground UI for testing LLMs and a dashboard for monitoring performance metrics.

## Structure

```shell
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── Layout.jsx        # Main layout with header and footer
│   │   ├── MetricsChart.jsx  # Performance charts visualization
│   │   ├── ModelSelector.jsx # Model selection dropdown
│   │   └── RequestList.jsx   # Recent requests table
│   ├── lib/           # Utility functions and API client
│   │   └── api.js           # API client for backend communication
│   ├── pages/         # Main page components
│   │   ├── Dashboard.jsx    # Metrics dashboard page
│   │   └── Playground.jsx   # LLM playground page
│   ├── styles/        # CSS styles
│   │   └── index.css        # Main stylesheet with Tailwind imports
│   ├── App.jsx        # Main application component
│   └── main.jsx       # Application entry point
├── public/            # Public assets
├── index.html         # HTML entry point
├── tailwind.config.js # Tailwind CSS configuration
├── package.json       # Dependencies and scripts
└── README.md          # This file
```

## Features

- **Playground UI:**
  - Interactive prompt input and response display
  - Model selection with quantization options
  - Configurable parameters (max tokens, temperature)
  - Response metrics (generation time)

- **Dashboard:**
  - Performance metrics visualization (latency, tokens, tokens/sec)
  - Model filtering and benchmarking
  - Recent requests log
  - Summary statistics

- **Components:**
  - Responsive layout with navigation
  - Interactive charts using Recharts
  - Dynamic data loading from backend API
  - Authentication integration with API keys

## API Integration

The frontend communicates with the backend through a dedicated API client (`src/lib/api.js`) that handles:

- Model listing
- Text generation
- Metrics retrieval
- Model benchmarking

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run serve
```

## Environment Variables

Create a `.env` file in the frontend directory with:

```shell
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=read-dev-key
```

## Author

Adnan Sattar

- Email: <adnansattar09@gmail.com>
- GitHub: <https://github.com/AdnanSattar>
- LinkedIn: <https://www.linkedin.com/in/adnansattar09/>
