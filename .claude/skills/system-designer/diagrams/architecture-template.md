# System Architecture Diagrams

This document contains templates for various architecture diagrams using Mermaid syntax.

## High-Level System Architecture

```mermaid
graph TB
    subgraph "External Systems"
        News[Brave Search API]
        Polymarket[Polymarket Gamma API]
        CLOB[Polymarket CLOB API]
    end

    subgraph "Arbitrage Detection System"
        Monitor[News Monitoring Service]
        Reason[Reasoning Engine]
        Market[Market Data Service]
        Detect[Arbitrage Detection Engine]
        Execute[Trade Execution Service]
        Alert[Alert Generation Service]
    end

    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Cache)]
        Queue[(Message Queue)]
    end

    Monitor --> News
    Reason --> Monitor
    Market --> Polymarket
    Detect --> Reason
    Detect --> Market
    Execute --> CLOB
    Alert --> Detect
    Execute --> Detect

    Monitor --> DB
    Reason --> DB
    Market --> Cache
    Detect --> Cache
    Execute --> DB
    Alert --> Queue

    News -.->|API Calls| Monitor
    Polymarket -.->|Market Data| Market
    CLOB -.->|Trade Execution| Execute
```

## Component Diagram

```mermaid
graph LR
    subgraph "Component 1: [Component Name]"
        C1A[Sub-component A]
        C1B[Sub-component B]
    end

    subgraph "Component 2: [Component Name]"
        C2A[Sub-component A]
        C2B[Sub-component B]
    end

    C1A -->|Interface 1| C2A
    C1B -->|Interface 2| C2B
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Service
    participant Database
    participant External

    User->>API: Request
    API->>Service: Process
    Service->>Database: Query
    Database-->>Service: Data
    Service->>External: External API Call
    External-->>Service: Response
    Service-->>API: Result
    API-->>User: Response
```

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Monitoring: Start
    Monitoring --> Analyzing: News Detected
    Analyzing --> Detecting: Analysis Complete
    Detecting --> Alerting: Opportunity Found
    Detecting --> Monitoring: No Opportunity
    Alerting --> Executing: High Confidence
    Alerting --> Monitoring: Low Confidence
    Executing --> Monitoring: Trade Complete
    Monitoring --> Idle: Stop
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    ENTITY1 ||--o{ ENTITY2 : "relationship name"
    ENTITY1 {
        id PK
        field1 type
        field2 type
        created_at timestamp
    }
    ENTITY2 {
        id PK
        entity1_id FK
        field1 type
        field2 type
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Load Balancer]
    end

    subgraph "Application Servers"
        APP1[App Server 1]
        APP2[App Server 2]
        APP3[App Server 3]
    end

    subgraph "Database Layer"
        DB Primary[(Primary DB)]
        DB Replica1[(Replica 1)]
        DB Replica2[(Replica 2)]
    end

    subgraph "Cache Layer"
        Cache1[(Cache 1)]
        Cache2[(Cache 2)]
    end

    LB --> APP1
    LB --> APP2
    LB --> APP3

    APP1 --> Cache1
    APP2 --> Cache2
    APP3 --> Cache1

    APP1 --> DB Primary
    APP2 --> DB Primary
    APP3 --> DB Primary

    DB Primary --> DB Replica1
    DB Primary --> DB Replica2
```

## Sequence Diagram for Error Handling

```mermaid
sequenceDiagram
    participant Client
    participant Service
    participant Database
    participant Logger

    Client->>Service: Request
    Service->>Database: Query
    Database-->>Service: Error

    alt Retryable Error
        Service->>Service: Log Error
        Service->>Database: Retry (exponential backoff)
        Database-->>Service: Success
        Service-->>Client: Response
    else Non-Retryable Error
        Service->>Logger: Log Critical Error
        Service-->>Client: Error Response
    end
```

## Usage Instructions

1. Copy the appropriate template
2. Replace placeholder text with actual component names
3. Adjust relationships and data flow
4. Add or remove components as needed
5. Include diagram in architecture documentation

## Best Practices

- Keep diagrams simple and focused
- Use consistent naming conventions
- Label all relationships and data flows
- Include error handling paths where relevant
- Use appropriate diagram type for your purpose
- Update diagrams when architecture changes
