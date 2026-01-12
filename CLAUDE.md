# Polymarket Arbitrage Agent - Development Constitution

## Project Identity

This is an **autonomous arbitrage detection system** for Polymarket prediction markets. The project uses AI to identify "narrative vs. reality" discrepancies - where breaking news should move market prices but hasn't yet.

### Core Philosophy

**Speed and Automation**: The system must execute the "Search → Reason → Compare → Execute" loop in seconds, not minutes. Every component should be optimized for minimal latency.

**Multi-Agent First**: All development happens through the 7-agent system. No code should be written without the appropriate agent's involvement.

**Testing as Documentation**: Tests are the primary source of truth for system behavior. When implementing features, write tests first that describe expected behavior.

### Project Goals

1. **Detect arbitrage opportunities faster than human traders**
2. **Use AI reasoning to assess market impact of breaking news**
3. **Execute trades automatically when confidence thresholds are met**
4. **Provide transparency through detailed logging and metrics**

### Non-Goals

- Building a general trading bot (focus only on news-driven arbitrage)
- Predicting market movements (only detect mispricings)
- UI/frontend development (this is a backend system)

## Technology Stack & Rationale

### Core Technologies

- **Python 3.11+**: Chosen for async/await support, strong typing, and extensive ML/AI ecosystem
- **LangGraph**: Workflow orchestration - enables stateful, multi-step AI reasoning
- **Polymarket Gamma API**: Real-time market data - fastest source of price information
- **Polymarket CLOB API**: Order execution - direct market access

### AI/ML Integration

- **Claude Code**: Development environment with multi-agent skills
- **Brave Search MCP**: Real-time news retrieval - fastest breaking news source
- **Sequential Thinking MCP**: Deep reasoning on news-to-market impact

### Architecture Decisions

**Why LangGraph over custom workflow engine?**
- Built-in state management
- Visual debugging capabilities
- Native integration with LangChain ecosystem
- Easier to iterate on prompt chains

**Why async/await throughout?**
- I/O-bound operations (API calls, database queries)
- Need to monitor multiple news sources concurrently
- Performance critical for arbitrage opportunities

**Why separate Gamma and CLOB clients?**
- Gamma: Read-only market data (no auth required for public endpoints)
- CLOB: Write operations (requires signing, more complex auth)
- Separation of concerns enables better error handling

## Multi-Agent System

### Agent Responsibilities

This project uses **7 specialized AI agents**. Each has autonomous decision-making authority within their domain.

#### 1. Product Manager (`/product-manager`)
**Authority**: Feature requirements and priorities
**Responsibilities**:
- Create PRDs for new features
- Define acceptance criteria
- Prioritize backlog items
- Validate implementations against requirements

**When to invoke**: "Define requirements", "Create PRD", "Prioritize features"

**Outputs**: Product specs, user stories, roadmaps

#### 2. System Designer (`/system-designer`)
**Authority**: Architecture and data models
**Responsibilities**:
- Design system architecture
- Define API contracts (OpenAPI specs)
- Create data models and schemas
- Document architectural decisions (ADRs)

**When to invoke**: "Design architecture", "Create API spec", "Define data model"

**Outputs**: Architecture diagrams, OpenAPI specs, ADRs

#### 3. Developer (`/developer`)
**Authority**: Implementation and code quality
**Responsibilities**:
- Implement features according to specs
- Write clean, tested code
- Follow project coding standards
- Integrate APIs and MCP servers

**When to invoke**: "Implement feature", "Write code", "Integrate API"

**Outputs**: Python modules, LangGraph workflows, tests

#### 4. QA/Test Engineer (`/qa-test-engineer`)
**Authority**: Quality assurance and testing strategy
**Responsibilities**:
- Design test plans and test cases
- Ensure >80% code coverage
- Validate functionality against requirements
- Create and maintain test fixtures

**When to invoke**: "Create test plan", "Test this feature", "Quality check"

**Outputs**: Test suites, test reports, coverage metrics

#### 5. Security Analyst (`/security-analyst`)
**Authority**: Security and vulnerability management
**Responsibilities**:
- Review code for security vulnerabilities
- Ensure API key safety
- Validate input handling
- Conduct regular security audits

**When to invoke**: "Security review", "Check vulnerabilities", "Audit code"

**Outputs**: Security reports, policies, remediation steps

#### 6. DevOps Engineer (`/devops-engineer`)
**Authority**: Deployment and infrastructure
**Responsibilities**:
- Configure deployment pipelines
- Set up CI/CD
- Manage infrastructure (Docker, cloud)
- Ensure system scalability

**When to invoke**: "Deploy this", "Set up CI/CD", "Containerize app"

**Outputs**: Docker configs, CI/CD pipelines, deployment docs

#### 7. Data Analyst (`/data-analyst`)
**Authority**: Performance tracking and insights
**Responsibilities**:
- Track system performance metrics
- Monitor arbitrage detection accuracy
- Generate performance dashboards
- Analyze trading results

**When to invoke**: "Analyze performance", "Create dashboard", "Track metrics"

**Outputs**: Metrics dashboards, performance reports, insights

### Agent Collaboration Flow

Standard feature development follows this pipeline:

```
Product Manager → System Designer → Developer → QA → Security → DevOps → Data Analyst → (back to Product Manager for validation)
```

**Critical Rules**:
1. Never skip agents in the pipeline
2. Each agent must approve before passing to next
3. Security analyst must review all code before deployment
4. QA must validate against Product Manager's requirements
5. Data Analyst tracks metrics to validate Product Manager's assumptions

## Code Standards

### Python Conventions

```python
# Always use type hints
def fetch_market_data(market_id: str) -> MarketData | None:
    """Fetch market data from Gamma API.

    Args:
        market_id: The market identifier

    Returns:
        MarketData object or None if not found
    """
    pass

# Use async/await for I/O operations
async def get_price(token_id: str) -> PriceData:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/price/{token_id}")
        return PriceData(**response.json())

# Use pydantic for data validation
from pydantic import BaseModel, Field

class MarketImpact(BaseModel):
    expected_price_change: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
```

### File Organization

```
src/
├── agents/          # LangGraph agent implementations
│   └── <agent_name>.py
├── tools/           # API clients, utilities
│   ├── polymarket_client.py
│   └── brave_search.py
├── workflows/       # LangGraph workflow orchestration
│   └── arbitrage_detection_graph.py
└── utils/           # Shared utilities
    ├── logging.py
    └── config.py
```

**Rules**:
- Keep modules under 300 lines
- One class per file unless closely related
- Use `__init__.py` to expose public API
- Name files after their primary class/function

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Error Handling

```python
# Define custom exceptions
class PolymarketClientError(Exception):
    """Base exception for Polymarket client errors."""
    pass

class MarketNotFoundError(PolymarketClientError):
    """Raised when market is not found."""
    pass

# Use specific exception handling
try:
    market = await client.get_market(market_id)
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error fetching market: {e}")
    raise MarketNotFoundError(f"Market {market_id} not found")
except httpx.NetworkError as e:
    logger.error(f"Network error: {e}")
    raise PolymarketClientError("Network connection failed")
```

### Logging

```python
import structlog

logger = structlog.get_logger()

# Always include context
logger.info("fetching_market_data", market_id=market_id)

# Use appropriate log levels
logger.debug("detailed_debugging_info")
logger.info("normal_operation", detail="value")
logger.warning("something_unexpected", error=error)
logger.error("error_occurred", exception=str(e))
```

## Testing Standards

### Test Organization

```
tests/
├── unit/           # Test individual functions/classes
├── integration/    # Test component interactions
└── e2e/           # Test full workflows
```

### Testing Guidelines

1. **Test-First Development**: Write tests before implementation
2. **Mock External APIs**: Never call real APIs in tests
3. **Use Fixtures**: Share test setup via `conftest.py`
4. **Test Edge Cases**: Not just happy path
5. **Maintain >80% Coverage**: Enforced via CI/CD

### Test Examples

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.tools.polymarket_client import PolymarketClient

@pytest.mark.asyncio
async def test_get_market_success():
    """Test successful market fetch."""
    client = PolymarketClient()

    # Mock the HTTP client
    with patch.object(client.http_client, 'get') as mock_get:
        mock_get.return_value.json.return_value = {
            "data": {
                "market_id": "test-123",
                "question": "Test question",
                "description": "Test description",
                "end_date": "2025-12-31",
                "active": True
            }
        }

        market = await client.get_market("test-123")

        assert market.market_id == "test-123"
        assert market.active is True
```

## Architecture Patterns

### LangGraph Workflow Structure

All workflows follow this pattern:

```python
class WorkflowState(TypedDict):
    """State for the workflow."""
    messages: Annotated[list, operator.add]
    # Add workflow-specific fields

class WorkflowGraph:
    """Workflow orchestration."""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("node_name", self.node_method)

        # Define edges
        workflow.add_edge("node1", "node2")
        workflow.add_conditional_edges(
            "node",
            self.condition_method,
            {"option1": "next_node", "option2": END}
        )

        return workflow.compile()

    def node_method(self, state: WorkflowState) -> WorkflowState:
        """Node implementation."""
        # Process state
        return state

    def condition_method(self, state: WorkflowState) -> str:
        """Routing logic."""
        return "option1"
```

### MCP Integration Pattern

```python
class MCPIntegration:
    """Base class for MCP integrations."""

    def __init__(self, mcp_client):
        self.mcp = mcp_client

    async def call_mcp(self, method: str, **kwargs):
        """Call MCP method with error handling."""
        try:
            return await self.mcp.call(method, kwargs)
        except MCPError as e:
            logger.error("mcp_error", method=method, error=str(e))
            raise
```

## Development Workflow

### Feature Development Process

1. **Product Manager**: Creates PRD with acceptance criteria
2. **System Designer**: Designs architecture and API contracts
3. **Developer**: Implements feature with tests (TDD)
4. **QA**: Validates against Product Manager's requirements
5. **Security**: Reviews for vulnerabilities
6. **DevOps**: Sets up deployment/infrastructure
7. **Data Analyst**: Tracks metrics to validate success

### Commit Convention

All commits must follow conventional commits:

```
feat: add news monitoring agent
fix: resolve race condition in price fetching
docs: update API documentation
test: add integration tests for CLOB client
refactor: simplify state management
security: add input validation to API endpoints
```

### Code Review Checklist

Before merging, ensure:
- [ ] All tests pass
- [ ] Coverage maintained >80%
- [ ] Security review completed
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Type hints present
- [ ] Logging added
- [ ] Error handling comprehensive

## Project Context for AI

### Current Implementation Status

**Completed**:
- Project structure and setup
- Basic LangGraph workflow skeleton
- Polymarket client stub (async implementation)
- Initial test structure

**In Progress**:
- Brave Search MCP integration
- Sequential Thinking MCP integration
- Arbitrage detection algorithm
- Trade execution logic

**Not Started**:
- CI/CD pipeline
- Docker containerization
- Performance monitoring
- Database for tracking trades

### Key Integration Points

1. **Brave Search MCP**: `src/tools/brave_search.py` (needs implementation)
2. **Sequential Thinking MCP**: `src/agents/reasoning.py` (needs implementation)
3. **Polymarket Gamma API**: `src/tools/polymarket_client.py` (partial)
4. **Polymarket CLOB API**: `src/tools/clob_client.py` (needs implementation)

### Environment Variables Required

```bash
# Polymarket
POLYMARKET_API_KEY=
POLYMARKET_SECRET_KEY=

# MCP
BRAVE_API_KEY=

# Application
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.7
MIN_PROFIT_MARGIN=0.05
```

## Common Patterns

### Retry Logic with Tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_with_retry(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    secret_key: str
    log_level: str = "INFO"
    confidence_threshold: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings()
```

---

**Last Updated**: 2025-01-12
**Purpose**: This document serves as the "persistent memory" for Claude Code and AI agents working on this project.
