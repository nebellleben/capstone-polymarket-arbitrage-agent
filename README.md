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

## Quick Start

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

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Polymarket API Credentials
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_SECRET_KEY=your_secret_key_here
POLYMARKET_CLOB_HOST=api.polymarket.com
POLYMARKET_GAMMA_HOST=gamma-api.polymarket.com

# MCP Server Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
CONFIDENCE_THRESHOLD=0.7
MIN_PROFIT_MARGIN=0.05
MAX_POSITION_SIZE=1000
```

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

**Last Updated**: 2025-01-12
**Repository**: https://github.com/nebellleben/capstone-polymarket-arbitrage-agent
