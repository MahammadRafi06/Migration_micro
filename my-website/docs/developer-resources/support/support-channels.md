---
id: support-channels
title: Support Channels
sidebar_label: Support Channels
description: Comprehensive guide to available support channels, escalation procedures, and best practices for getting help
draft: false
---

# Support Channels

Comprehensive guide to getting help with your edge platform deployment. This page outlines all available support channels, when to use each one, and how to effectively communicate your issues for faster resolution.

## Support Channel Quick Reference

| Issue Type | Urgency | Best Channel | Response Time | Availability |
|------------|---------|--------------|---------------|--------------|
| Production Down | Critical | Emergency Hotline | 15 minutes | 24/7 |
| Security Incident | Critical | Security Hotline | 30 minutes | 24/7 |
| Performance Issues | High | Enterprise Support | 2 hours | 24/7 |
| Configuration Help | Medium | Standard Support | 24 hours | Business Hours |
| General Questions | Low | Community Forum | Best effort | Community-driven |
| Feature Requests | Low | GitHub Issues | Next planning cycle | Business Hours |

## Official Support Tiers

### Enterprise Support (Premium)

**Who should use this**: Production deployments, mission-critical applications, customers with SLA requirements.

**Contact Information**:
- **Primary Email**: enterprise-support@armada-platform.com
- **Escalation Email**: enterprise-escalation@armada-platform.com
- **Phone Support**: +1-800-ARMADA-1 (1-800-276-2321)
- **Emergency Hotline**: +1-800-ARMADA-911 (24/7)

**Service Level Agreements**:
- **Critical Issues** (Production Down): 15-minute response, 4-hour resolution target
- **High Priority** (Major Functionality Impacted): 2-hour response, 8-hour resolution target
- **Medium Priority** (Minor Functionality Impacted): 8-hour response, 24-hour resolution target
- **Low Priority** (General Questions): 24-hour response, 72-hour resolution target

**What's Included**:
- Dedicated technical account manager
- Direct access to engineering team
- Architecture and deployment consultation
- Priority bug fixes and feature requests
- Pre-release access and testing
- Custom training sessions
- Health checks and optimization reviews

**Coverage**:
- 24/7 support for Critical and High priority issues
- Business hours support for Medium and Low priority issues
- Multi-timezone coverage (Americas, EMEA, APAC)

### Standard Support

**Who should use this**: Development environments, non-critical applications, small to medium deployments.

**Contact Information**:
- **Email**: support@armada-platform.com
- **Support Portal**: https://support.armada-platform.com
- **Phone**: +1-800-ARMADA-2 (Business hours only)

**Service Level Agreements**:
- **High Priority**: 8-hour response during business hours
- **Medium Priority**: 24-hour response during business hours
- **Low Priority**: 48-hour response during business hours

**What's Included**:
- Email and portal-based support
- Access to knowledge base and documentation
- Bug reports and fixes in regular release cycle
- Community forum access with expert moderation

**Coverage**:
- Business hours: Monday-Friday, 9 AM - 6 PM in your local timezone
- Supported timezones: PST, EST, GMT, CET, IST, JST

### Community Support (Free)

**Who should use this**: Developers learning the platform, open-source users, non-commercial deployments.

**What's Included**:
- Community-driven support
- Access to public documentation
- Bug reporting through GitHub
- Feature requests and discussions
- Peer-to-peer knowledge sharing

## Community Channels

### Discussion Forums

**Primary Community Forum**
- **URL**: https://community.armada-platform.com
- **Best for**: General questions, deployment advice, sharing experiences
- **Moderation**: Community-driven with expert oversight
- **Response Time**: Usually within 24-48 hours

**Stack Overflow**
- **Tag**: `armada-platform`, `edge-computing`, `kubernetes-edge`
- **Best for**: Technical questions, code examples, specific problems
- **Guidelines**: Follow Stack Overflow's question format and guidelines

**Reddit Community**
- **Subreddit**: r/ArmadaPlatform
- **Best for**: News, discussions, showcasing projects, informal Q&A
- **Moderation**: Community guidelines enforced

### Real-Time Chat

**Discord Server**
- **Invite Link**: https://discord.gg/armada-platform
- **Channels**:
  - `#general-help`: General questions and support
  - `#technical-discussion`: Deep technical conversations
  - `#deployment-showcase`: Share your implementations
  - `#announcements`: Platform updates and news
- **Best for**: Real-time help, quick questions, community interaction
- **Active Hours**: Global community with peak activity during business hours

**Slack Workspace**
- **Invite**: Request access through support portal
- **Channels**:
  - `#platform-help`: General support questions
  - `#development`: Development-related discussions
  - `#integrations`: Third-party tool integrations
  - `#feedback`: Product feedback and suggestions
- **Best for**: Professional discussions, integration support

### Video Support

**Office Hours**
- **Schedule**: Tuesdays and Thursdays, 2 PM PST / 10 PM GMT
- **Platform**: Zoom (link shared in community channels)
- **Format**: Live Q&A session with platform experts
- **Duration**: 1 hour
- **Recording**: Sessions recorded and shared

**Webinar Series**
- **Frequency**: Monthly deep-dive sessions
- **Topics**: Best practices, new features, case studies
- **Registration**: https://webinars.armada-platform.com
- **Archive**: Previous sessions available on demand

## Self-Service Resources

### Documentation Hub

**Main Documentation**
- **URL**: https://docs.armada-platform.com
- **Content**: Complete platform documentation, tutorials, guides
- **Search**: Full-text search with advanced filtering
- **Updates**: Continuously updated with platform releases

**API Reference**
- **URL**: https://api.armada-platform.com
- **Content**: Complete API documentation with examples
- **Interactive**: Try API calls directly from documentation
- **SDKs**: Available for multiple programming languages

**Video Tutorials**
- **URL**: https://tutorials.armada-platform.com
- **Content**: Step-by-step video guides
- **Playlists**: Organized by skill level and use case
- **Subtitles**: Available in multiple languages

### Knowledge Base

**Troubleshooting Guides**
- **URL**: https://kb.armada-platform.com/troubleshooting
- **Content**: Common issues, error codes, diagnostic procedures
- **Search**: Symptom-based search functionality
- **Difficulty**: Categorized by complexity level

**Best Practices Library**
- **URL**: https://kb.armada-platform.com/best-practices
- **Content**: Production deployment guidelines, security recommendations
- **Case Studies**: Real-world implementation examples
- **Checklists**: Deployment and maintenance checklists

**FAQ Database**
- **URL**: https://kb.armada-platform.com/faq
- **Organization**: Categorized by topic and user type
- **Voting**: Community-voted most helpful answers
- **Updates**: Regularly updated based on support trends

## Issue Reporting and Bug Tracking

### GitHub Repository

**Main Repository**: https://github.com/armada-platform/platform

**Issue Types**:
- **Bug Reports**: Use bug report template
- **Feature Requests**: Use feature request template
- **Documentation Issues**: Use documentation template
- **Security Issues**: Use security template (private)

**Labels and Prioritization**:
- `severity/critical`: Production-breaking issues
- `severity/high`: Major functionality impact
- `severity/medium`: Minor functionality impact
- `severity/low`: Cosmetic or enhancement
- `type/bug`: Bug reports
- `type/feature`: Feature requests
- `component/api`: API-related issues
- `component/ui`: User interface issues

### Bug Report Template

When reporting bugs, please use this comprehensive template:

```markdown
## Bug Report

### Environment Information
- **Platform Version**: [e.g., v2.1.3]
- **Kubernetes Version**: [e.g., v1.28.2]
- **Node Operating System**: [e.g., Ubuntu 22.04]
- **Container Runtime**: [e.g., containerd 1.6.8]
- **Deployment Method**: [e.g., Helm, kubectl, CLI]
- **Cloud Provider**: [e.g., AWS, Azure, GCP, On-premises]

### Issue Description
**Brief Summary**: [One-line description of the issue]

**Detailed Description**: [Comprehensive description of what's happening]

### Reproduction Steps
1. [First step]
2. [Second step]
3. [Third step]
4. [Continue with specific steps]

### Expected vs Actual Behavior
**Expected**: [What should happen]
**Actual**: [What actually happens]

### Evidence
**Screenshots**: [If applicable, attach screenshots]

**Logs**: 
```bash
# Platform logs
kubectl logs -n armada-system deployment/armada-controller

# Application logs
kubectl logs <pod-name> -n <namespace>

# System events
kubectl get events --sort-by='.lastTimestamp' -A
```

**Configuration Files**: [Attach relevant YAML files, with sensitive data redacted]

### Impact Assessment
- **Severity**: [Critical/High/Medium/Low]
- **Users Affected**: [Number or percentage]
- **Workaround Available**: [Yes/No - if yes, describe]

### Additional Context
[Any other relevant information, related issues, or context]
```

### Feature Request Template

```markdown
## Feature Request

### Problem Statement
**Current Limitation**: [Describe what you cannot do today]
**Business Impact**: [Explain why this matters]

### Proposed Solution
**Feature Description**: [Detailed description of proposed feature]
**User Experience**: [How users would interact with this feature]
**Technical Approach**: [If you have ideas on implementation]

### Alternatives Considered
[Other solutions you've considered and why they don't work]

### Use Cases
1. [Primary use case]
2. [Secondary use case]
3. [Edge cases]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Priority and Timeline
**Business Priority**: [High/Medium/Low]
**Desired Timeline**: [When you need this feature]
```

## Emergency Procedures

### Critical Production Issues

**Definition**: Issues that result in complete service unavailability or data loss.

**Immediate Actions**:
1. **Call Emergency Hotline**: +1-800-ARMADA-911
2. **Send Emergency Email**: emergency@armada-platform.com
3. **Join Emergency Slack**: #platform-emergency

**Information to Provide**:
- Customer ID and contact information
- Brief description of the issue
- Business impact and affected users
- Any immediate actions taken
- Preferred callback number

**What Happens Next**:
- Incident commander assigned within 15 minutes
- War room established if needed
- Regular updates every 30 minutes
- Post-incident review scheduled

### Security Incidents

**Definition**: Suspected security breaches, vulnerabilities, or unauthorized access.

**Immediate Actions**:
1. **Call Security Hotline**: +1-800-ARMADA-SEC
2. **Send Secure Email**: security@armada-platform.com (encrypted preferred)
3. **Do NOT post in public channels**

**Security Incident Types**:
- Suspected data breach
- Unauthorized access attempts
- Vulnerability discoveries
- Suspicious system behavior
- Compliance violations

**Response Process**:
- Security team engaged immediately
- Secure communication channel established
- Investigation initiated within 1 hour
- Regular encrypted updates provided
- Compliance notifications handled as required

## Best Practices for Effective Support

### Before Contacting Support

**1. Search Existing Resources**
- Check documentation and knowledge base
- Search community forums and GitHub issues
- Review release notes for known issues
- Try basic troubleshooting steps

**2. Gather Diagnostic Information**
```bash
# Platform information
kubectl get nodes -o wide
kubectl get pods -A
kubectl version

# Resource usage
kubectl top nodes
kubectl top pods -A

# Recent events
kubectl get events --sort-by='.lastTimestamp' -A --since=1h

# Logs
kubectl logs -n armada-system deployment/armada-controller --since=1h
```

**3. Prepare Your Environment**
- Ensure you have administrative access
- Have configuration files ready (with secrets redacted)
- Prepare to provide screen sharing access if needed
- Document any recent changes

### Writing Effective Support Requests

**Subject Line Best Practices**:
- ❌ "Help!", "Urgent!", "Not working"
- ✅ "Pod scheduling failure on edge nodes v2.1.3"
- ✅ "API authentication errors after upgrade to v2.2.0"
- ✅ "Network connectivity issues between zones"

**Message Structure**:
1. **Context**: What you're trying to achieve
2. **Problem**: What's not working
3. **Impact**: How it affects your operations
4. **Steps Taken**: What you've already tried
5. **Request**: What you need from support

**Communication Tips**:
- Be specific and factual
- Include relevant error messages and logs
- Mention your support tier and urgency
- Provide contact preferences
- Set realistic expectations for response time

### During Support Interactions

**Collaboration Best Practices**:
- Respond promptly to support requests
- Provide requested information completely
- Ask questions if instructions are unclear
- Share screen when helpful
- Document solutions for future reference

**Escalation When Needed**:
- If response time exceeds SLA
- If initial support level cannot resolve issue
- If business impact increases
- If you need architectural guidance

### After Issue Resolution

**Follow-Up Actions**:
- Verify the solution works in your environment
- Document the resolution for your team
- Consider if this should become a runbook
- Provide feedback on support experience
- Share solution with community if appropriate

## Support Tools and Integrations

### Support Portal Features

**Ticket Management**:
- Create and track support cases
- Upload files and logs securely
- Real-time status updates
- Historical case viewing

**Knowledge Integration**:
- Suggested articles based on issue description
- Related community discussions
- Similar resolved cases

**Communication Options**:
- In-portal messaging
- Email notifications
- SMS alerts for critical issues
- Calendar integration for scheduled calls

### Monitoring Integration

**Connect Your Monitoring**:
- Share Prometheus metrics with support
- Integrate alerting with support tickets
- Provide log aggregation access
- Enable remote diagnostic access

**Proactive Support**:
- Health check automation
- Performance monitoring
- Security scanning
- Capacity planning alerts

## Regional Support

### Americas
- **Primary Coverage**: PST/EST timezones
- **Languages**: English, Spanish, Portuguese
- **Local Phone**: +1-800-ARMADA-1
- **Business Hours**: 6 AM - 9 PM PST

### Europe, Middle East, Africa (EMEA)
- **Primary Coverage**: GMT/CET timezones
- **Languages**: English, German, French, Italian
- **Local Phone**: +44-800-ARMADA-EU
- **Business Hours**: 8 AM - 6 PM GMT

### Asia-Pacific (APAC)
- **Primary Coverage**: JST/IST timezones
- **Languages**: English, Japanese, Mandarin
- **Local Phone**: +81-800-ARMADA-JP
- **Business Hours**: 9 AM - 6 PM JST

## Feedback and Continuous Improvement

### Support Experience Feedback

**Post-Case Surveys**:
- Automated surveys after case closure
- Response time and quality ratings
- Suggestions for improvement
- Feature requests based on support needs

**Annual Support Review**:
- Support metrics and trends analysis
- Process improvement recommendations
- Training and resource gap identification
- Support tool enhancement planning

### Community Contribution

**Help Others**:
- Answer questions in community forums
- Share your solutions and configurations
- Contribute to documentation improvements
- Participate in beta testing programs

**Become a Community Expert**:
- Apply for community moderator roles
- Contribute to knowledge base articles
- Lead community calls and presentations
- Mentor other community members

## Next Steps

For additional support resources:

- [Community Resources](./community-resources.md) - Detailed guide to community engagement
- [Release Notes & Roadmap](./release-notes-roadmap.md) - Stay updated on platform development
- [Troubleshooting Guides](../troubleshooting/) - Self-service diagnostic resources 