# Unhinged: Product Manager Perspective (2025)

**Author:** VP Product  
**Date:** November 16, 2025  
**Audience:** Product Team, Design, Engineering Leadership

## Product Vision

Unhinged is a native graphics platform that makes system administration intuitive through natural language interfaces. Users describe what they want to accomplish, and the system orchestrates the necessary kernel commands.

## Core User Personas

### 1. DevOps Engineer (35-45 years old)
- Manages 100+ servers
- Needs rapid troubleshooting
- Values automation and repeatability
- Pain: SSH fatigue, manual command lookup

### 2. Junior Developer (22-28 years old)
- Learning system administration
- Needs guidance and explanation
- Values learning opportunities
- Pain: Command syntax complexity, fear of breaking things

### 3. System Administrator (40-55 years old)
- Responsible for infrastructure stability
- Needs safety guarantees and audit trails
- Values predictability
- Pain: Legacy tools, security concerns

### 4. Power User (28-40 years old)
- Wants full system control
- Values transparency and customization
- Needs performance
- Pain: GUI limitations, hidden complexity

## Product Pillars

### 1. Intent Recognition
Users express intent in natural language. System translates to commands.
- "My headphone volume is too low" → pactl set-sink-volume
- "Show me disk usage" → df -h | sort -k5 -rn
- "Find large files" → find / -size +1G

### 2. Safety First
- Dangerous commands require confirmation
- Audit trail of all executed commands
- Rollback capabilities for system changes
- Dry-run mode for preview

### 3. Learning & Transparency
- Show the commands being executed
- Explain why each command is needed
- Provide man page context
- Build user expertise over time

### 4. Extensibility
- Custom command templates
- Plugin architecture for domain-specific tools
- Integration with existing workflows
- API for third-party tools

## Feature Roadmap

**MVP (Q4 2025):**
- Natural language → command orchestration
- 100+ common system administration tasks
- Safety checks and confirmation flow
- Basic audit logging

**Phase 2 (Q1-Q2 2026):**
- Weaviate semantic indexing
- Advanced DAG execution with data flow
- Multi-user session management
- Custom template creation

**Phase 3 (Q3-Q4 2026):**
- LLM-based reasoning enhancement
- Predictive command suggestions
- Integration with monitoring systems
- Mobile companion app

## Success Criteria

- 80% of common admin tasks discoverable via natural language
- <2 second response time for command discovery
- 99% accuracy in command selection
- Zero unintended destructive commands executed

## Competitive Advantage

1. **Natural Language First** - Not a GUI wrapper, true intent recognition
2. **Kernel-Native** - Direct system access, no abstraction layers
3. **Open Source** - Community-driven, transparent development
4. **Learning Platform** - Users become better system administrators

## Go-to-Market Strategy

1. **Developer Community** - GitHub, HackerNews, Reddit
2. **Enterprise Pilots** - DevOps teams at scale
3. **Educational Institutions** - Teaching system administration
4. **Open Source Ecosystem** - Integration with popular tools

