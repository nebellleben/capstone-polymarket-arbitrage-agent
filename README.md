# Polymarket "Narrative vs. Reality" Arbitrage Agent

An autonomous arbitrage detection system that identifies when breaking news should move Polymarket prices before the market actually updates.

## Overview

This project uses AI-powered reasoning to detect "narrative vs. reality" discrepancies and capitalize on information asymmetries in Polymarket prediction markets.

### Key Features

- **Real-time News Monitoring**: Continuous monitoring via Brave Search MCP
- **AI-Powered Reasoning**: Sequential thinking to assess market impact
- **Arbitrage Detection**: Compare expected vs. actual market prices
- **Automated Trading**: Execute trades on profitable opportunities
- **Multi-Agent System**: 7 specialized AI agents for autonomous development

## Quick Start

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

## Architecture

```
News Monitoring (Brave MCP)
    ↓
Reasoning Engine (Sequential Thinking)
    ↓
Market Analysis (Gamma API)
    ↓
Arbitrage Detection
    ↓
Trade Execution / Alerts
```

## Multi-Agent System

This project uses 7 specialized AI agents:

1. **Product Manager** - Requirements and PRDs
2. **System Designer** - Architecture and API specs
3. **Developer** - Implementation and code
4. **QA Engineer** - Testing and quality assurance
5. **DevOps Engineer** - Deployment and infrastructure
6. **Security Analyst** - Security reviews and audits
7. **Data Analyst** - Performance metrics and insights

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed project documentation and agent workflows.

## Requirements

- Python 3.11+
- Polymarket account with API credentials
- Brave Search MCP configured
- Sequential Thinking MCP configured

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read our contributing guidelines.

---

**Last Updated**: 2025-01-12
