# Polymarket "Narrative vs. Reality" Arbitrage Agent

## Project Overview

This project implements an autonomous arbitrage detection system that identifies when breaking news should move Polymarket prices before the market actually updates. The system uses AI-powered reasoning to detect "narrative vs. reality" discrepancies and capitalize on information asymmetries.

### Core Value Proposition

**The Problem**: Polymarket prices often lag behind breaking news due to human reaction time and manual market updates. This creates arbitrage opportunities where information from news events isn't immediately reflected in market prices.

**The Solution**: An automated system that:
1. Continuously monitors breaking news via Brave Search MCP
2. Uses Sequential Thinking MCP for deep reasoning on market impact
3. Queries Polymarket Gamma API for current market prices
4. Identifies discrepancies where news should move prices but hasn't yet
5. Executes trades or alerts on profitable opportunities

**Why It Works**: The system moves faster than human traders by automating the "Search → Reason → Compare → Execute" loop in seconds rather than minutes or hours.

## Technology Stack

### Core Technologies
- **Python 3.11+**: Primary implementation language
- **LangGraph**: Workflow orchestration and agent coordination
- **Polymarket Gamma API**: Real-time market data and trading
- **Polymarket CLOB API**: Order placement and execution

### AI/ML Integration
- **Claude Code**: Development environment with multi-agent system
- **Brave Search MCP**: Real-time news retrieval and monitoring
- **Sequential Thinking MCP**: Deep reasoning on news-to-market impact

### Infrastructure
- **Docker**: Containerization for consistency
- **GitHub Actions**: CI/CD pipeline
- **Pytest**: Testing framework
- **PostgreSQL/SQLite**: Database (dev/prod support)

## Multi-Agent System Architecture

This project uses **7 specialized AI agents** implemented as Claude Code Skills. Each agent has autonomous capabilities and can generate complete artifacts independently.

### Agent Roles

#### 1. Product Manager (`/product-manager`)
- **Skill**: Define requirements, prioritize features, create PRDs
- **When to invoke**: "Define user stories", "Create PRD", "Prioritize backlog"
- **Output**: Product specifications, roadmaps, acceptance criteria

#### 2. System Designer (`/system-designer`)
- **Skill**: Design architecture, define schemas, create API specs
- **When to invoke**: "Design architecture", "Create API spec", "Define data model"
- **Output**: Architecture diagrams, OpenAPI specs, ADRs

#### 3. Developer (`/developer`)
- **Skill**: Implement features, write code, integrate APIs
- **When to invoke**: "Implement feature", "Write code", "Integrate API"
- **Output**: Python modules, LangGraph workflows, tests

#### 4. QA/Test Engineer (`/qa-test-engineer`)
- **Skill**: Design tests, ensure quality, validate functionality
- **When to invoke**: "Create test plan", "Test this feature", "Quality check"
- **Output**: Test suites, test reports, coverage metrics

#### 5. DevOps Engineer (`/devops-engineer`)
- **Skill**: Configure deployment, set up CI/CD, manage infrastructure
- **When to invoke**: "Deploy this", "Set up CI/CD", "Containerize app"
- **Output**: Docker configs, CI/CD pipelines, deployment docs

#### 6. Security Analyst (`/security-analyst`)
- **Skill**: Review security, identify vulnerabilities, audit code
- **When to invoke**: "Security review", "Check vulnerabilities", "Audit code"
- **Output**: Security reports, policies, remediation steps

#### 7. Data Analyst (`/data-analyst`)
- **Skill**: Analyze performance, track metrics, generate insights
- **When to invoke**: "Analyze performance", "Create dashboard", "Track metrics"
- **Output**: Metrics dashboards, performance reports, insights

### How Agents Collaborate

Agents work iteratively through a structured workflow:

```
Product Manager → System Designer → Developer → QA → Security → DevOps → Data Analyst → Iterate
```

**Example Workflow**:
1. User: "Create a feature to monitor election news"
2. Product Manager generates PRD and user stories
3. System Designer creates architecture and API specs
4. Developer implements the feature with tests
5. QA validates functionality
6. Security reviews for vulnerabilities
7. DevOps deploys to staging
8. Data Analyst tracks performance metrics
9. Product Manager validates against requirements
10. Iterate based on feedback

## System Architecture

### High-Level Design

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

### Component Details

#### 1. News Monitoring Agent
- **Purpose**: Continuously fetch breaking news from Brave Search
- **Input**: Search queries, topic filters
- **Output**: News articles with timestamps and relevance scores
- **MCP**: Brave Search MCP

#### 2. Reasoning Engine
- **Purpose**: Analyze news impact on specific markets
- **Input**: News articles, market descriptions
- **Output**: Impact assessment, expected price movement
- **MCP**: Sequential Thinking MCP

#### 3. Market Analysis Module
- **Purpose**: Fetch current Polymarket prices
- **Input**: Market IDs, token IDs
- **Output**: Current prices, order books, spreads
- **API**: Polymarket Gamma API

#### 4. Arbitrage Detection Engine
- **Purpose**: Compare expected vs. actual prices
- **Input**: Impact assessments, current prices
- **Output**: Arbitrage opportunities with confidence scores

#### 5. Trade Execution Module
- **Purpose**: Execute trades when opportunities identified
- **Input**: Trade signals, confidence thresholds
- **Output**: Executed trades, confirmations
- **API**: Polymarket CLOB API

#### 6. Alert Generation Module
- **Purpose**: Generate human-readable alerts
- **Input**: Opportunities, trades executed
- **Output**: Formatted alerts, notifications

## Getting Started

### Prerequisites

- Python 3.11+
- Claude Code CLI installed
- Polymarket account with API credentials
- Brave Search MCP configured
- Sequential Thinking MCP configured

### Setup

1. **Clone the repository**
   ```bash
   cd /Users/kelvinchan/dev/capstone-polymarket-arbitrage-agent
   ```

2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Set up Claude Code skills**
   ```bash
   # Skills are in .claude/skills/
   # Restart Claude Code to load them
   ```

5. **Run initial setup**
   ```bash
   make setup  # Or ./scripts/setup.sh
   ```

### Using the Multi-Agent System

The agents are designed to work autonomously. Here's how to use them:

#### Start a New Feature

```
You: "I want to add a feature to monitor crypto-related markets"

Claude will:
1. Automatically invoke /product-manager
2. Generate PRD and user stories
3. Invoke /system-designer for architecture
4. Invoke /developer to implement
5. Continue through the agent pipeline
```

#### Debug an Issue

```
You: "The news monitoring isn't working properly"

Claude will:
1. Invoke /developer to diagnose
2. Invoke /qa-test-engineer to create tests
3. Invoke /data-analyst to review logs
4. Propose and implement fixes
```

#### Deploy to Production

```
You: "Deploy the latest changes to production"

Claude will:
1. Invoke /qa-test-engineer to verify
2. Invoke /security-analyst to review
3. Invoke /devops-engineer to deploy
4. Invoke /data-analyst to monitor
```

## Development Workflow

### 1. Feature Development

```bash
# Start with Product Manager
"I want to add [feature description]"

# Agents will automatically:
# 1. Product Manager creates PRD
# 2. System Designer designs architecture
# 3. Developer implements feature
# 4. QA Engineer creates and runs tests
# 5. Security Analyst reviews code
# 6. DevOps Engineer handles deployment
# 7. Data Analyst tracks metrics
```

### 2. Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Generate coverage report
pytest --cov=src --cov-report=html
```

### 3. Local Development

```bash
# Start all services locally
docker-compose up

# Run the arbitrage detection system
python -m src.workflows.arbitrage_detection_graph

# Monitor logs
tail -f logs/arbitrage_agent.log
```

### 4. Deployment

```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Rollback deployment
./scripts/rollback.sh production
```

## MCP Integration

### Brave Search MCP

**Purpose**: Real-time news retrieval and monitoring

**Configuration**:
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

**Usage**:
- Monitor breaking news on specific topics
- Search for market-relevant events
- Filter news by recency and relevance
- Track news sources and credibility

### Sequential Thinking MCP

**Purpose**: Deep reasoning on news-to-market impact

**Configuration**:
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

**Usage**:
- Analyze whether news actually impacts resolution criteria
- Evaluate confidence in impact assessment
- Chain reasoning steps for complex situations
- Identify edge cases and uncertainties

## Polymarket API Integration

### Gamma API

**Purpose**: Market data and price information

**Key Endpoints**:
- `GET /markets`: List all markets
- `GET /markets/{id}`: Get market details
- `GET /price`: Get current price for token
- `GET /book`: Get order book

**Authentication**:
- Public endpoints: No auth required
- Private endpoints: API key + signature

**Usage Examples**:
```python
from src.tools.polymarket_client import PolymarketClient

client = PolymarketClient()

# Get market data
markets = client.get_markets(active=True)

# Get current price
price = client.get_price(token_id="YES_TOKEN_ID", side="buy")

# Get order book
book = client.get_order_book(token_id="TOKEN_ID")
```

### CLOB API

**Purpose**: Order placement and execution

**Key Operations**:
- Create and sign orders
- Post orders (GTC, GTD, FOK)
- Cancel orders
- Get order status
- Fetch trade history

**Usage Examples**:
```python
from py_clob_client.client import ClobClient

client = ClobClient(host="...", key="...", chain_id=137)

# Create order
order_args = OrderArgs(
    price=0.50,
    size=100.0,
    side=BUY,
    token_id="TOKEN_ID"
)
signed_order = client.create_order(order_args)

# Post order
resp = client.post_order(signed_order, OrderType.GTC)
```

## Project Structure

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
├── CLAUDE.md               # This file
├── README.md               # Project overview
└── .env.example            # Environment template
```

## Best Practices

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write descriptive docstrings
- Keep modules under 300 lines
- Use meaningful variable names

### Testing
- Maintain >80% test coverage
- Write tests before implementation (TDD)
- Mock external API calls
- Test edge cases and error conditions
- Use pytest fixtures for common setup

### Security
- Never commit API keys
- Use environment variables for secrets
- Validate all external inputs
- Implement rate limiting
- Log security-relevant events
- Regular security audits

### Documentation
- Keep CLAUDE.md updated
- Document all public APIs
- Maintain architecture diagrams
- Track design decisions (ADRs)
- Update README with changes

## Troubleshooting

### Common Issues

**Issue**: Agents not triggering
- **Solution**: Restart Claude Code to reload skills

**Issue**: API authentication failures
- **Solution**: Verify API keys in .env file

**Issue**: MCP servers not responding
- **Solution**: Check MCP server configuration and network

**Issue**: Tests failing locally
- **Solution**: Ensure all dependencies installed via `pip install -r requirements.txt`

## Contributing

When contributing to this project:

1. Use the multi-agent system for development
2. Ensure all agents approve changes (QA, Security, Data Analyst)
3. Update documentation as needed
4. Add tests for new features
5. Follow commit message conventions

## License

[Specify your license here]

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Last Updated**: 2025-01-12
**Maintained By**: Multi-Agent System (Product Manager, Developer, DevOps Engineer)
