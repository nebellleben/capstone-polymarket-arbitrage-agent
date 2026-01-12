# Agent Collaboration Patterns

This document describes how the 7 AI agents work together to build and maintain the Polymarket arbitrage system.

## Overview

The agents follow an **iterative, collaborative workflow** where each agent contributes their expertise to the project. Agents hand off work through shared artifacts and communicate through well-defined interfaces.

## Agent Roles at a Glance

| Agent | Expertise | Key Outputs |
|-------|-----------|-------------|
| Product Manager | Requirements, prioritization | PRDs, user stories, roadmap |
| System Designer | Architecture, data models | Architecture diagrams, API specs, ADRs |
| Developer | Implementation, testing | Code, unit tests, integrations |
| QA/Test Engineer | Quality assurance | Test plans, test suites, quality reports |
| DevOps Engineer | Infrastructure, deployment | Docker configs, CI/CD pipelines |
| Security Analyst | Security, compliance | Security reviews, policies |
| Data Analyst | Performance, metrics | Dashboards, insights, reports |

## Collaboration Workflow

### Feature Development Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Feature Request                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              2. Product Manager                              │
│  • Create PRD                                                │
│  • Define user stories                                       │
│  • Set acceptance criteria                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              3. System Designer                               │
│  • Design architecture                                       │
│  • Create data models                                        │
│  • Write API specs                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              4. Developer                                    │
│  • Implement feature                                         │
│  • Write unit tests                                          │
│  • Integrate APIs                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              5. QA/Test Engineer                             │
│  • Create test plan                                          │
│  • Run tests                                                 │
│  • Validate acceptance criteria                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              6. Security Analyst                             │
│  • Review code for vulnerabilities                            │
│  • Validate security requirements                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              7. DevOps Engineer                              │
│  • Deploy to staging                                         │
│  • Configure monitoring                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              8. Data Analyst                                 │
│  • Track performance metrics                                 │
│  • Validate success criteria                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   ITERATE    │
                    │  Based on   │
                    │  Feedback   │
                    └──────────────┘
```

## Handoff Patterns

### Product Manager → System Designer
**Artifact**: PRD (Product Requirements Document)

**Contains**:
- Feature requirements
- User stories
- Acceptance criteria
- Success metrics

**Handoff Criteria**:
- Requirements are clear and specific
- Success criteria are measurable
- Stakeholders have reviewed

### System Designer → Developer
**Artifacts**:
- Architecture diagrams
- Data model schemas
- API specifications

**Contains**:
- Component structure
- Interface definitions
- Integration patterns

**Handoff Criteria**:
- Architecture is documented
- APIs are specified
- Data models are defined

### Developer → QA Engineer
**Artifacts**:
- Source code
- Unit tests
- Implementation notes

**Contains**:
- Feature implementation
- Test coverage
- Known limitations

**Handoff Criteria**:
- Code compiles and runs
- Unit tests pass
- Code is documented

### QA Engineer → Security Analyst
**Artifacts**:
- Test results
- Bug reports
- Quality assessment

**Contains**:
- Test coverage report
- Passed/failed tests
- Issues found

**Handoff Criteria**:
- All tests executed
- Results documented
- Critical bugs identified

### Security Analyst → DevOps Engineer
**Artifacts**:
- Security review report
- Security policies
- Remediation steps

**Contains**:
- Vulnerability assessment
- Security requirements
- Compliance checks

**Handoff Criteria**:
- Security review completed
- Critical issues addressed
- Policies defined

### DevOps Engineer → Data Analyst
**Artifacts**:
- Deployed system
- Monitoring setup
- Access to metrics

**Contains**:
- Running system
- Performance data
- Health status

**Handoff Criteria**:
- System deployed successfully
- Monitoring is active
- Metrics are being collected

### Data Analyst → Product Manager
**Artifacts**:
- Performance analysis
- Success criteria validation
- Insights and recommendations

**Contains**:
- Metrics dashboard
- Performance report
- Recommendations

**Handoff Criteria**:
- Success criteria evaluated
- Insights documented
- Recommendations provided

## Collaboration Scenarios

### Scenario 1: New Feature Development

**Trigger**: User requests a new feature

**Workflow**:
1. **Product Manager**: Creates PRD and user stories
2. **System Designer**: Designs architecture and APIs
3. **Developer**: Implements feature with tests
4. **QA Engineer**: Validates functionality
5. **Security Analyst**: Reviews security
6. **DevOps Engineer**: Deploys to staging
7. **Data Analyst**: Validates success criteria
8. **Product Manager**: Approves feature

**Outcome**: Feature is complete and deployed

### Scenario 2: Bug Fix

**Trigger**: Bug reported by QA or user

**Workflow**:
1. **QA Engineer**: Documents bug with reproduction steps
2. **Developer**: Diagnoses and fixes bug
3. **Developer**: Writes regression test
4. **QA Engineer**: Verifies fix
5. **Security Analyst**: Reviews if security-related
6. **DevOps Engineer**: Deploys fix
7. **Data Analyst**: Monitors for regressions

**Outcome**: Bug is fixed and regression prevented

### Scenario 3: Performance Optimization

**Trigger**: Data Analyst identifies performance issue

**Workflow**:
1. **Data Analyst**: Provides performance metrics
2. **Developer**: Profiles and optimizes code
3. **System Designer**: Reviews architecture changes
4. **QA Engineer**: Tests optimizations
5. **DevOps Engineer**: Deploys improvements
6. **Data Analyst**: Validates improvements

**Outcome**: Performance is improved

### Scenario 4: Security Incident

**Trigger**: Security Analyst discovers vulnerability

**Workflow**:
1. **Security Analyst**: Documents vulnerability
2. **Developer**: Implements fix
3. **Security Analyst**: Validates fix
4. **QA Engineer**: Tests fix
5. **DevOps Engineer**: Deploys emergency patch
6. **Data Analyst**: Monitors for related issues

**Outcome**: Vulnerability is remediated

## Communication Channels

### Shared Artifacts

Agents communicate through shared artifacts in the repository:

- **`/docs/prd/`**: Product requirements
- **`/docs/architecture/`**: Design documents
- **`/src/`**: Source code
- **`/tests/`**: Test suites
- **`/docs/security/`**: Security policies
- **`/docs/metrics/`**: Performance data

### Direct Collaboration

For complex decisions, agents may collaborate directly:
- **Joint reviews**: System Designer + Developer
- **Security reviews**: Security Analyst + Developer
- **Performance reviews**: Data Analyst + Developer
- **Planning**: Product Manager + System Designer

## Best Practices

### For Handoffs
1. **Document everything**: Never rely on verbal communication alone
2. **Be specific**: Include all necessary context
3. **Use templates**: Follow standard formats
4. **Validate**: Confirm the receiving agent understands
5. **Track**: Use issue tracking for handoffs

### For Collaboration
1. **Start early**: Involve relevant agents from the beginning
2. **Communicate proactively**: Don't wait for problems
3. **Be respectful**: Value each agent's expertise
4. **Iterate**: Expect and welcome feedback
5. **Learn**: Share lessons learned

### For Quality
1. **Define DoD**: Clear Definition of Done for each artifact
2. **Review regularly**: periodic cross-agent reviews
3. **Automate**: Use automated checks where possible
4. **Monitor**: Track collaboration effectiveness
5. **Improve**: Continuously refine the workflow

## Troubleshooting Collaboration Issues

### Issue: Unclear Requirements
**Solution**:
- Product Manager clarifies with user
- System Designer asks feasibility questions
- Create prototype to validate understanding

### Issue: Architectural Mismatch
**Solution**:
- System Designer reviews Developer's implementation
- Create ADR to document decision
- Involve multiple agents in decision

### Issue: Quality Concerns
**Solution**:
- QA Engineer provides specific feedback
- Developer addresses issues systematically
- Product Manager validates against requirements

### Issue: Security Blocker
**Solution**:
- Security Analyst explains risk clearly
- Developer proposes remediation
- System Designer evaluates architectural impact

### Issue: Performance Problem
**Solution**:
- Data Analyst provides metrics
- Developer profiles code
- System Designer reviews architecture
- DevOps Engineer checks infrastructure

## Metrics for Collaboration Success

Track these metrics to ensure effective collaboration:

- **Cycle time**: Time from request to deployment
- **Rework rate**: Percentage of work that needs revision
- **Handoff success rate**: Percentage of smooth handoffs
- **Agent satisfaction**: Feedback from each agent
- **Quality metrics**: Bugs, coverage, performance

---

**Last Updated**: 2025-01-12
**Maintained By**: Product Manager Agent
