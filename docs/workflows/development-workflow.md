# Development Workflow

This document describes the standard development workflow for the Polymarket arbitrage agent project using the multi-agent system.

## Overview

The development workflow follows an iterative, agent-driven process where each AI agent contributes their expertise to build high-quality software.

## Prerequisites

Before starting development, ensure:
- Claude Code is installed and configured
- All agent skills are loaded in `.claude/skills/`
- Development environment is set up (Python, Docker, etc.)
- Git repository is initialized

## Workflow Stages

### Stage 1: Requirements Definition

**Agent**: Product Manager (`/product-manager`)

**Trigger**: New feature request or user story

**Activities**:
1. Gather and clarify requirements
2. Create Product Requirements Document (PRD)
3. Define user stories with acceptance criteria
4. Identify success metrics
5. Prioritize features

**Outputs**:
- `/docs/prd/{feature-name}.md`
- `/docs/user-stories/{feature-name}.md`

**Definition of Done**:
- [ ] Requirements are clear and specific
- [ ] Success criteria are measurable
- [ ] User stories follow standard format
- [ ] Dependencies identified
- [ ] Stakeholders reviewed

### Stage 2: System Design

**Agent**: System Designer (`/system-designer`)

**Input**: PRD from Product Manager

**Activities**:
1. Review PRD and requirements
2. Design system architecture
3. Create data models
4. Define API specifications
5. Document design decisions (ADRs)

**Outputs**:
- `/docs/architecture/system-architecture.md`
- `/docs/architecture/data-model.md`
- `/docs/architecture/api-spec.yaml`
- `/docs/adr/{decision-number}-{title}.md`

**Definition of Done**:
- [ ] Architecture diagram created
- [ ] Data model defined
- [ ] API specified
- [ ] Design decisions documented
- [ ] Developer can implement from specs

### Stage 3: Implementation

**Agent**: Developer (`/developer`)

**Input**: Architecture and specs from System Designer

**Activities**:
1. Review design specifications
2. Implement feature following architecture
3. Write unit tests
4. Add error handling
5. Document code

**Outputs**:
- `/src/{module}/` - Implementation
- `/tests/unit/test_{module}.py` - Unit tests

**Definition of Done**:
- [ ] Code follows PEP 8
- [ ] Type hints included
- [ ] Docstrings written
- [ ] Unit tests pass
- [ ] Coverage >80%
- [ ] Code documented

### Stage 4: Quality Assurance

**Agent**: QA/Test Engineer (`/qa-test-engineer`)

**Input**: Implementation from Developer

**Activities**:
1. Review acceptance criteria
2. Create test plan
3. Write integration tests
4. Execute all tests
5. Report bugs and issues

**Outputs**:
- `/tests/integration/` - Integration tests
- `/docs/test-plan/{feature-name}.md`
- Test reports

**Definition of Done**:
- [ ] Test plan created
- [ ] Integration tests written
- [ ] All acceptance criteria tested
- [ ] Test coverage >80%
- [ ] No critical bugs

### Stage 5: Security Review

**Agent**: Security Analyst (`/security-analyst`)

**Input**: Code and tests from Developer and QA

**Activities**:
1. Review code for security issues
2. Check for vulnerabilities
3. Validate API key management
4. Verify input validation
5. Document security assessment

**Outputs**:
- `/docs/security/review-{feature-name}.md`
- Security issue reports (if any)

**Definition of Done**:
- [ ] Security review completed
- [ ] No critical vulnerabilities
- [ ] API keys properly managed
- [ ] Input validation verified
- [ ] Security document created

### Stage 6: Deployment

**Agent**: DevOps Engineer (`/devops-engineer`)

**Input**: Approved code from all previous stages

**Activities**:
1. Create/update Docker configurations
2. Update CI/CD pipeline
3. Deploy to staging
4. Configure monitoring
5. Verify deployment

**Outputs**:
- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/` - CI/CD configs
- Deployment reports

**Definition of Done**:
- [ ] Docker image built
- [ ] Deployment to staging successful
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Rollback procedure tested

### Stage 7: Monitoring and Validation

**Agent**: Data Analyst (`/data-analyst`)

**Input**: Deployed system and metrics

**Activities**:
1. Validate success criteria
2. Track performance metrics
3. Analyze system behavior
4. Create dashboards
5. Generate insights

**Outputs**:
- `/docs/metrics/{feature-name}-report.md`
- Metrics dashboards
- Recommendations

**Definition of Done**:
- [ ] Success criteria validated
- [ ] Metrics tracked
- [ ] Performance analyzed
- [ ] Insights documented
- [ ] Recommendations provided

### Stage 8: Closure

**Agent**: Product Manager (`/product-manager`)

**Input**: Validation from Data Analyst

**Activities**:
1. Review all artifacts
2. Validate against original requirements
3. Approve feature or request changes
4. Update roadmap
5. Archive artifacts

**Outputs**:
- Feature completion report
- Updated roadmap
- Archive of all artifacts

**Definition of Done**:
- [ ] All requirements met
- [ ] Success criteria achieved
- [ ] Stakeholders notified
- [ ] Documentation updated
- [ ] Feature marked complete

## Quick Reference: Agent Invocation

```bash
# Start a new feature
"I want to add [feature description]"

# The system will automatically invoke agents in order:
# 1. Product Manager - Create PRD
# 2. System Designer - Design architecture
# 3. Developer - Implement feature
# 4. QA Engineer - Test feature
# 5. Security Analyst - Review security
# 6. DevOps Engineer - Deploy feature
# 7. Data Analyst - Validate metrics
# 8. Product Manager - Close feature
```

## Iteration Loops

### Feedback Loop

If any agent identifies issues:
1. Agent documents the issue
2. Work goes back to the appropriate agent
3. Fix is implemented
4. Process continues from that point

**Example**: QA Engineer finds a bug
→ Back to Developer to fix
→ Forward to QA Engineer to verify
→ Continue to Security Review

### Continuous Improvement

After each feature:
1. Data Analyst provides performance insights
2. Product Manager identifies improvements
3. System Designer suggests architectural refinements
4. Process improves for next iteration

## Branch Strategy

```
main (production)
  ↑
  └── staging (pre-production)
        ↑
        └── feature/{feature-name} (development)
```

### Workflow

1. Create feature branch from `staging`
2. Develop feature on feature branch
3. All agents work on feature branch
4. Create PR to `staging` when ready
5. Deploy to staging for validation
6. Merge to `main` after approval

## Code Review Process

Even with AI agents, human code review is valuable:

1. **Developer** submits implementation
2. **QA Engineer** validates tests pass
3. **Security Analyst** approves security
4. **Human reviewer** provides final approval
5. **Product Manager** closes feature

## Emergency Fixes

For critical bugs or security issues:

**Fast-Track Workflow**:
1. **Security Analyst** or **QA Engineer** identifies issue
2. **Developer** implements immediate fix
3. **QA Engineer** validates fix
4. **DevOps Engineer** deploys hotfix
5. **Data Analyst** monitors for regressions
6. **Product Manager** documents incident

Skip non-essential stages for speed, but:
- Always run tests
- Always review security
- Always monitor after deployment

## Troubleshooting

### Agent Stuck?

1. Check if inputs are clear
2. Review previous agent's output
3. Provide additional context
4. Ask specific questions

### Quality Issues?

1. Review Definition of Done for each stage
2. Ensure all checklists completed
3. Run all tests
4. Check code coverage

### Collaboration Problems?

1. Review handoff criteria
2. Check artifact completeness
3. Verify templates followed
4. Communicate clearly

## Best Practices

### For Users
- Be specific in requirements
- Provide context and constraints
- Review agent outputs
- Give feedback for improvements

### For Development
- Follow the workflow stages
- Don't skip agents (except emergencies)
- Document everything
- Test thoroughly

### For Quality
- Maintain high standards
- Don't rush through stages
- Fix issues as they're found
- Learn from each iteration

## Templates and Checklists

Each agent has templates in their `.claude/skills/{agent}/templates/` directory. Use these for consistency.

---

**Last Updated**: 2025-01-12
**Maintained By**: Product Manager Agent
