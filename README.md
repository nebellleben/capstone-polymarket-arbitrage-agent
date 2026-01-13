# Polymarket "Narrative vs. Reality" Arbitrage Agent

An autonomous arbitrage detection system that identifies when breaking news should move Polymarket prices before the market actually updates.

## Overview

This project uses AI-powered reasoning to detect "narrative vs. reality" discrepancies and capitalize on information asymmetries in Polymarket prediction markets.

### The Problem

Polymarket prices often lag behind breaking news due to human reaction time and manual market updates. This creates arbitrage opportunities where information from news events isn't immediately reflected in market prices.

### The Solution

An automated system that:
1. Continuously monitors breaking news via Brave Search MCP
2. Uses Sequential Thinking MCP for deep reasoning on market impact
3. Queries Polymarket Gamma API for current market prices
4. Identifies discrepancies where news should move prices but hasn't yet
5. Executes trades or alerts on profitable opportunities

### Key Features

- **Real-time News Monitoring**: Continuous monitoring via Brave Search MCP
- **AI-Powered Reasoning**: Sequential thinking to assess market impact
- **Arbitrage Detection**: Compare expected vs. actual market prices
- **Web Dashboard**: Monitor system status and view alerts in real-time
- **Telegram Notifications**: Instant alerts when opportunities are detected
- **Automated Trading**: Execute trades on profitable opportunities
- **Multi-Agent Development**: 7 specialized AI agents for autonomous development

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Arbitrage Detection System              │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   News      │     │  Reasoning  │     │   Market    │
│  Monitoring │────▶│   Engine    │────▶│  Analysis   │
│ (Brave MCP) │     │ (Seq. Think)│     │ (Gamma API) │
└─────────────┘     └─────────────┘     └─────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                   ┌─────────────┐
                   │ Arbitrage   │
                   │ Detection   │
                   │   Engine    │
                   └─────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
         ┌─────────────┐         ┌─────────────┐
         │   Trade     │         │    Alert    │
         │ Execution   │         │ Generation  │
         └─────────────┘         └─────────────┘
```

## 🚀 Try It Now - Live Production System

The system is **currently deployed and running** on Railway, monitoring markets 24/7.

**Production URL**: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/

### 📊 Test the Web Dashboard

Visit the live web interface to see the system in action:

**1. Main Dashboard**
```
https://capstone-polymarket-arbitrage-agent-production.up.railway.app/
```
Shows API information and system status.

**2. Check System Health**
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/health
```
Expected response:
```json
{"status":"healthy","timestamp":"2026-01-13T..."}
```

**3. View System Status**
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/status
```
Shows worker status, database connection, and uptime.

**4. See Recent Alerts**
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/alerts/recent
```
Returns the most recent arbitrage opportunities detected.

**5. Get Alert Statistics**
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/alerts/stats
```
Shows total alerts, breakdown by severity, and more.

**6. Interactive API Documentation (Swagger UI)**
```
https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/docs
```
Browse and test all available API endpoints interactively!

### 📱 Test Telegram Notifications

Want to receive alerts on your phone? Here's how to test the Telegram integration:

**Quick Test (2 minutes)**:

1. **Get Your Telegram Chat ID**:
   ```bash
   # Open Telegram and search for @userinfobot
   # Send /start to get your numeric Chat ID
   ```

2. **Send a Test Alert**:
   Use the API to trigger a test notification (this feature will be added soon!)

**Or receive alerts when opportunities are detected**:

The system monitors markets continuously and will send Telegram alerts when it detects arbitrage opportunities. Alerts include:
- Market question and current/expected prices
- News headline and link
- AI reasoning explanation
- Recommended action
- Confidence score

**Alert Severity Levels**:
- 🔴 **CRITICAL** - High confidence, high profit opportunities
- ⚠️ **WARNING** - Medium confidence/profit (default)
- ℹ️ **INFO** - Low confidence/profit (optional)

### What's Running Now

The deployed system is continuously:
1. ✅ Monitoring breaking news every 60 seconds
2. ✅ Fetching Polymarket market data every 5 minutes
3. ✅ Analyzing news impact using AI reasoning
4. ✅ Detecting arbitrage opportunities
5. ✅ Generating alerts and sending Telegram notifications
6. ✅ Serving the monitoring dashboard 24/7

## 👨‍💻 For Developers: Run Locally

Want to run the system yourself or contribute? Here's how to set it up locally.

### Prerequisites

- Python 3.11+
- Polymarket account with API credentials
- Brave Search MCP configured
- Sequential Thinking MCP configured

### Installation

```bash
# Clone the repository
git clone https://github.com/nebellleben/capstone-polymarket-arbitrage-agent.git
cd capstone-polymarket-arbitrage-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the system
python -m src.workflows.arbitrage_detection_graph
```

### Local Environment Configuration

For local development, create a `.env` file based on `.env.example`:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API credentials
# Required: BRAVE_API_KEY, ANTHROPIC_API_KEY
# Optional: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (for local testing)
```

**Required Environment Variables**:
- `BRAVE_API_KEY` - Brave Search API key (get from [Brave Search API](https://brave.com/search/api/))
- `ANTHROPIC_API_KEY` - Anthropic API key for AI reasoning

**Optional for Telegram Testing**:
- `TELEGRAM_BOT_TOKEN` - Your bot token (see [Telegram Setup Guide](docs/notifications/telegram-setup-guide.md))
- `TELEGRAM_CHAT_ID` - Your numeric Telegram Chat ID

### MCP Configuration

Configure your MCP servers in the Claude Code settings:

**Brave Search MCP**:
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Sequential Thinking MCP**:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

## Usage

### Running the Arbitrage Detection System

```bash
# Run with default search query
python -m src.workflows.arbitrage_detection_graph

# The system will:
# 1. Search for breaking news
# 2. Analyze market impact using AI reasoning
# 3. Fetch current market prices
# 4. Detect arbitrage opportunities
# 5. Execute trades if profitable
```

### Using the Polymarket Client

```python
import asyncio
from src.tools.polymarket_client import PolymarketClient

async def main():
    async with PolymarketClient() as client:
        # Get active markets
        markets = await client.get_markets(active=True)
        print(f"Found {len(markets)} active markets")

        # Get current price for a token
        price = await client.get_price(token_id="YES_TOKEN_ID", side="buy")
        print(f"Current price: {price.price}")

        # Get order book
        book = await client.get_order_book(token_id="TOKEN_ID")
        print(f"Bids: {len(book.bids)}, Asks: {len(book.asks)}")

asyncio.run(main())
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v
```

## 📚 Documentation

- **[Telegram Setup Guide](docs/notifications/telegram-setup-guide.md)** - Configure Telegram notifications
- **[Railway Deployment Guide](docs/deployment/railway-deployment.md)** - Deploy your own instance
- **[Deployment Success Story](docs/deployment/DEPLOYMENT-SUCCESS.md)** - How we deployed to production
- **[System Architecture](docs/architecture/system-architecture.md)** - Technical architecture details

## 🚢 Deploy Your Own Instance

Want to deploy your own instance? Here's how:

### Quick Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize and deploy
railway init
railway up
```

**Required Railway Variables**:
- `BRAVE_API_KEY` - Brave Search API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (optional)
- `TELEGRAM_CHAT_ID` - Telegram chat ID (optional)

For detailed deployment instructions, see [Railway Deployment Guide](docs/deployment/railway-deployment.md).

### Docker Deployment

```bash
# Build Docker image
docker build -t polymarket-arbitrage .

# Run container
docker run -p 8080:8080 \
  -e BRAVE_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  polymarket-arbitrage
```

## Development

### Project Structure

```
capstone-polymarket-arbitrage-agent/
├── .claude/
│   └── skills/              # Claude Code Skills (agents)
├── docs/                    # Documentation
│   ├── agents/             # Agent role descriptions
│   ├── architecture/       # System architecture docs
│   └── workflows/          # Workflow documentation
├── src/
│   ├── agents/             # LangGraph agent implementations
│   ├── tools/              # API integrations
│   ├── workflows/          # LangGraph workflows
│   └── utils/              # Utilities
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── CLAUDE.md               # Development documentation
├── README.md               # This file
└── .env.example            # Environment template
```

### Makefile Commands

```bash
make setup              # Set up development environment
make test               # Run all tests
make lint               # Run linters
make format             # Format code
make clean              # Clean up build artifacts
make run                # Run the arbitrage detection system
make docker-build       # Build Docker image
make docker-run         # Run with Docker Compose
```

## Multi-Agent System

This project uses 7 specialized AI agents for autonomous development:

1. **Product Manager** - Requirements and PRDs
2. **System Designer** - Architecture and API specs
3. **Developer** - Implementation and code
4. **QA Engineer** - Testing and quality assurance
5. **DevOps Engineer** - Deployment and infrastructure
6. **Security Analyst** - Security reviews and audits
7. **Data Analyst** - Performance metrics and insights

See [CLAUDE.md](CLAUDE.md) for detailed documentation on the multi-agent system.

## API Documentation

### Polymarket Gamma API

**Purpose**: Market data and price information

**Key Endpoints**:
- `GET /markets` - List all markets
- `GET /markets/{id}` - Get market details
- `GET /price` - Get current price for token
- `GET /book` - Get order book

### Polymarket CLOB API

**Purpose**: Order placement and execution

**Key Operations**:
- Create and sign orders
- Post orders (GTC, GTD, FOK)
- Cancel orders
- Get order status
- Fetch trade history

## Troubleshooting

### Common Issues

**Issue**: Agents not triggering
- **Solution**: Restart Claude Code to reload skills

**Issue**: API authentication failures
- **Solution**: Verify API keys in `.env` file

**Issue**: MCP servers not responding
- **Solution**: Check MCP server configuration and network connection

**Issue**: Tests failing locally
- **Solution**: Ensure all dependencies installed via `pip install -r requirements.txt`

## Contributing

We welcome contributions! Please follow these guidelines:

1. Use the multi-agent system for development
2. Ensure all agents approve changes (QA, Security, Data Analyst)
3. Update documentation as needed
4. Add tests for new features
5. Follow commit message conventions (see CLAUDE.md)

## License

MIT License - see LICENSE file for details

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Last Updated**: 2026-01-13
**Status**: ✅ Production Live on Railway
**Repository**: https://github.com/nebellleben/capstone-polymarket-arbitrage-agent
