#### The "Narrative vs. Reality" Arbitrage Agent

**Goal:** Detect when "Breaking News" should move a market before the Polymarket price actually updates.

- **MCPs used:**  **[Brave Search](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search):** For real-time news retrieval.

    - **[Sequential Thinking](https://www.google.com/search?q=https://github.com/modelcontextprotocol/servers/tree/main/src/sequential-thinking&authuser=1):** To help the LLM perform deep reasoning on whether news _actually_ impacts specific resolution criteria.

- **Code Implementation:** Build a **LangGraph** workflow that polls a news API (or uses Brave Search). If a high-impact event is found, the agent uses a custom Python tool to fetch current Polymarket prices via their [Gamma API](https://docs.polymarket.com/) and identifies discrepancies.

- **Why it's cool:** It moves faster than a human could by automating the "Search → Reason → Compare" loop.