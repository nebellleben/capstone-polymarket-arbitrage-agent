# Project Requirements - Cantonese Word Game

This document outlines the requirements for the Cantonese Word Game project to maximize scoring across all evaluation criteria.

## 1. Problem Description (README) - Target: 2 points

### Requirements:
- **Clear problem statement**: Describe the educational problem being solved
- **System functionality**: Detailed explanation of what the system does
- **Expected behavior**: Clear description of user interactions and outcomes
- **README structure**: Must include:
  - Project overview
  - Problem statement
  - Features and functionality
  - User stories/use cases
  - Screenshots or diagrams (if applicable)

## 2. AI System Development (Tools, Workflow, MCP) - Target: 2 points

### Requirements:
- **AI tools documentation**: Document all AI tools used (e.g., coding assistants, prompts, workflows)
- **Development workflow**: Describe the AI-assisted development process
- **MCP integration**: **MUST** include MCP (Model Context Protocol) usage:
  - MCP server implementation OR
  - MCP tools integration OR
  - MCP workflow documentation
- **AGENTS.md or similar**: Create documentation file describing:
  - AI tools and prompts used
  - Development workflow
  - MCP server/tools/workflow details
  - How AI was leveraged throughout the project

## 3. Technologies and System Architecture - Target: 2 points

### Requirements:
- **Technology stack documentation**: Clearly list and explain:
  - Frontend framework (e.g., React, Vue, Angular)
  - Backend framework (e.g., FastAPI, Flask, Express)
  - Database technology (e.g., PostgreSQL, SQLite)
  - Containerization (Docker)
  - CI/CD tools (e.g., GitHub Actions, GitLab CI)
- **Architecture explanation**: Document how technologies fit together:
  - System architecture diagram or description
  - Component interactions
  - Data flow
  - API communication patterns

## 4. Front-end Implementation - Target: 3 points

### Requirements:
- **Functional frontend**: Fully working user interface
- **Well-structured code**: 
  - Clear component organization
  - Separation of concerns
  - Reusable components
- **Centralized backend communication**:
  - API client/service layer
  - Single point for all backend calls
  - Error handling for API calls
- **Frontend tests**:
  - Unit tests for components
  - Integration tests for user flows
  - Test coverage for core logic
  - Clear instructions on how to run tests
  - Test documentation

## 5. API Contract (OpenAPI Specifications) - Target: 2 points

### Requirements:
- **Complete OpenAPI specification**:
  - All endpoints documented
  - Request/response schemas
  - Error responses
  - Authentication (if applicable)
- **Frontend alignment**: 
  - OpenAPI spec must fully reflect frontend requirements
  - All frontend API calls must be documented
- **Contract-driven development**:
  - OpenAPI spec used as contract for backend development
  - Backend must implement all specified endpoints
  - Version control for API spec

## 6. Back-end Implementation - Target: 3 points

### Requirements:
- **Well-structured backend**:
  - Clear project structure
  - Separation of concerns (routes, services, models)
  - Code organization best practices
- **OpenAPI compliance**:
  - All endpoints match OpenAPI specification
  - Request/response validation
  - Error handling per spec
- **Backend tests**:
  - Unit tests for core functionality
  - API endpoint tests
  - Service layer tests
  - Clear test documentation
  - Instructions on how to run tests

## 7. Database Integration - Target: 2 points

### Requirements:
- **Database layer**:
  - Proper ORM or database abstraction
  - Migration system
  - Schema definition
- **Multi-environment support**:
  - **MUST** support SQLite (development)
  - **MUST** support PostgreSQL (production)
  - Environment-based configuration
  - Clear documentation on switching between databases
- **Documentation**:
  - Database schema documentation
  - Migration instructions
  - Environment setup guide

## 8. Containerization - Target: 2 points

### Requirements:
- **Docker setup**:
  - Dockerfile for frontend
  - Dockerfile for backend
  - docker-compose.yml for full system
- **Complete system via Docker**:
  - Entire system runs via `docker-compose up`
  - No manual steps required
  - Database included in docker-compose
- **Clear instructions**:
  - How to build images
  - How to run with docker-compose
  - Environment variable configuration

## 9. Integration Testing - Target: 2 points

### Requirements:
- **Separated integration tests**:
  - Clear separation from unit tests
  - Dedicated test directory/structure
- **Coverage**:
  - Key user workflows tested
  - Database interactions tested
  - API integration tests
  - End-to-end critical paths
- **Documentation**:
  - How to run integration tests
  - What workflows are covered
  - Test data setup instructions

## 10. Deployment - Target: 2 points

### Requirements:
- **Cloud deployment**:
  - Application deployed to cloud platform (e.g., AWS, GCP, Azure, Railway, Render, Fly.io)
  - Working URL provided
  - Application accessible and functional
- **Deployment proof**:
  - Screenshot or link to deployed application
  - Documentation of deployment process
  - Environment configuration

## 11. CI/CD Pipeline - Target: 2 points

### Requirements:
- **CI pipeline**:
  - Automated test execution on push/PR
  - Tests must run in CI environment
- **CD pipeline**:
  - Automatic deployment when tests pass
  - Deployment triggered by CI success
  - Clear pipeline configuration
- **Pipeline documentation**:
  - CI/CD workflow explanation
  - Configuration files (e.g., .github/workflows)
  - Pipeline status badges (optional but recommended)

## 12. Reproducibility - Target: 2 points

### Requirements:
- **Complete instructions**:
  - Setup instructions (dependencies, environment)
  - How to run locally
  - How to run tests (unit, integration)
  - How to deploy
  - End-to-end workflow documentation
- **Clear documentation**:
  - Step-by-step guides
  - Prerequisites listed
  - Troubleshooting section (if needed)
  - Environment variable documentation

## Summary Checklist

To maximize points (25 total), ensure:

- [ ] README with clear problem description and functionality (2 pts)
- [ ] AGENTS.md or similar documenting AI tools, workflow, and **MCP usage** (2 pts)
- [ ] Architecture documentation explaining all technologies (2 pts)
- [ ] Functional frontend with centralized API calls and **tests** (3 pts)
- [ ] Complete OpenAPI specification aligned with frontend (2 pts)
- [ ] Well-structured backend following OpenAPI with **tests** (3 pts)
- [ ] Database supporting **both SQLite and PostgreSQL** (2 pts)
- [ ] Full system runs via **docker-compose** (2 pts)
- [ ] Integration tests clearly separated and documented (2 pts)
- [ ] Application **deployed to cloud** with working URL (2 pts)
- [ ] CI/CD pipeline that **runs tests and deploys** (2 pts)
- [ ] Complete setup/run/test/deploy instructions (2 pts)

## Notes

- **MCP is critical**: Must document MCP usage to get full points for criterion #2
- **Tests are critical**: Frontend and backend tests needed for full points on criteria #4 and #6
- **Dual database support**: Must support both SQLite and PostgreSQL for criterion #7
- **Deployment is required**: Must have working cloud deployment for criterion #10
- **CI/CD must deploy**: Pipeline must both test AND deploy for criterion #11

