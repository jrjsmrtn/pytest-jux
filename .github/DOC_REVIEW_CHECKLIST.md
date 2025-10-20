# Documentation Review Checklist

Use this checklist when reviewing documentation changes (pull requests, updates, new content).

## Overview

**Document being reviewed**: _____________________
**Reviewer**: _____________________
**Date**: _____________________
**PR/Issue**: _____________________

---

## 1. Content Quality

### Writing Quality
- [ ] **Spelling and grammar are correct**
  - No typos or spelling errors
  - Grammar follows standard English conventions
  - Consistent terminology throughout
- [ ] **Writing is clear and concise**
  - Sentences are easy to understand
  - Technical jargon is explained when first used
  - No unnecessary verbosity
- [ ] **Tone is appropriate**
  - Professional and helpful
  - Not condescending or overly casual
  - Consistent with existing documentation tone

### Accuracy
- [ ] **Technical accuracy verified**
  - All technical details are correct
  - API signatures match actual code
  - Command-line examples are accurate
  - Configuration options are current
- [ ] **Version-specific information is correct**
  - References correct version numbers
  - Deprecated features are marked as such
  - New features are labeled appropriately
- [ ] **Cross-references are accurate**
  - Links to other docs point to correct locations
  - "See also" sections reference relevant content
  - Related documentation is mentioned where appropriate

---

## 2. Code Examples

### Example Quality
- [ ] **All code examples are tested and working**
  - Examples execute without errors
  - Output matches what's shown in documentation
  - Examples use realistic scenarios
- [ ] **Examples follow best practices**
  - Code style matches project conventions
  - Security best practices are followed
  - No hardcoded credentials or sensitive data
- [ ] **Examples are complete**
  - All necessary imports are included
  - Setup steps are documented
  - Expected output is shown

### Example Coverage
- [ ] **Basic usage examples provided**
  - Simple, minimal examples for beginners
  - Common use cases are covered
- [ ] **Advanced examples provided (if applicable)**
  - Complex scenarios are demonstrated
  - Edge cases are shown
  - Integration examples are included

---

## 3. Links and References

### Internal Links
- [ ] **All internal links are valid**
  - Links to other documentation pages work
  - Anchors/fragments point to existing sections
  - No broken relative links
- [ ] **Link text is descriptive**
  - Avoid "click here" or generic text
  - Link text indicates what the link points to

### External Links
- [ ] **External links are valid and stable**
  - URLs are accessible
  - Links point to stable documentation (not blog posts)
  - Version-specific links use appropriate versions
- [ ] **External references are authoritative**
  - Links to official documentation
  - Reputable sources for technical information

### API/Code References
- [ ] **Function/class references are correct**
  - Function names match actual code
  - Module paths are accurate
  - Parameters and return types are correct

---

## 4. Diátaxis Framework Compliance

### Document Type Identification
- [ ] **Document type is clearly identified**
  - Tutorial, How-To, Reference, or Explanation
  - Document follows conventions for its type
  - Placed in correct directory

### Tutorials
If this is a tutorial:
- [ ] **Learning-oriented approach**
  - Step-by-step instructions
  - Safe to follow without prior knowledge
  - Builds confidence through doing
- [ ] **Complete and self-contained**
  - All setup steps are included
  - Learner can complete from start to finish
  - Expected outcomes are clear
- [ ] **Progressive learning path**
  - Starts with basics
  - Gradually increases complexity
  - Links to next steps

### How-To Guides
If this is a how-to guide:
- [ ] **Problem-oriented approach**
  - Addresses a specific problem or task
  - Assumes reader has basic knowledge
  - Focused on achieving a goal
- [ ] **Practical and actionable**
  - Clear steps to solve the problem
  - Minimal explanation of concepts
  - Real-world scenarios
- [ ] **Alternative approaches mentioned (if applicable)**
  - Trade-offs are discussed
  - Multiple solutions shown when appropriate

### Reference
If this is reference documentation:
- [ ] **Information-oriented approach**
  - Factual, dry, technical descriptions
  - Complete API/CLI documentation
  - No tutorials or explanations mixed in
- [ ] **Comprehensive and accurate**
  - All functions/options documented
  - Parameters, types, defaults specified
  - Return values and exceptions listed
- [ ] **Consistent structure**
  - Follows reference documentation template
  - Same format across similar items

### Explanation
If this is an explanation document:
- [ ] **Understanding-oriented approach**
  - Discusses concepts and design
  - Explains "why" rather than "how"
  - Provides background and context
- [ ] **Conceptual clarity**
  - Complex ideas are broken down
  - Analogies or examples clarify concepts
  - Design decisions are explained
- [ ] **Neutral and objective**
  - Presents trade-offs fairly
  - Acknowledges alternatives
  - Not promotional or prescriptive

---

## 5. Structure and Organization

### Document Structure
- [ ] **Clear hierarchy**
  - Headings follow logical order (h1 → h2 → h3)
  - No skipped heading levels
  - Table of contents (if long document)
- [ ] **Appropriate length**
  - Not too long or too short for the topic
  - Can be split into multiple docs if too long
  - Sufficient detail for the topic
- [ ] **Scannable and readable**
  - Good use of headings and subheadings
  - Bullet points for lists
  - Code blocks properly formatted
  - Visual breaks between sections

### Navigation
- [ ] **Navigation aids are present**
  - "See also" sections where appropriate
  - Links to related documentation
  - Breadcrumbs or context (where applicable)
- [ ] **Document is discoverable**
  - Listed in appropriate index files
  - Linked from relevant documents
  - Mentioned in README or main docs index

---

## 6. Technical Formatting

### Markdown Formatting
- [ ] **Markdown syntax is correct**
  - Headings use proper syntax (#, ##, ###)
  - Code blocks use triple backticks with language
  - Lists are properly formatted
  - Tables are well-formed
- [ ] **Code highlighting is appropriate**
  - Language specifier for code blocks (```python, ```bash, etc.)
  - Inline code uses backticks
  - Output is distinguished from commands

### Consistency
- [ ] **Formatting is consistent**
  - Heading capitalization is consistent
  - Code block style is consistent
  - List formatting is consistent
  - Terminology is used consistently
- [ ] **Style guide compliance**
  - Follows project style guide
  - CLI commands formatted correctly
  - File paths use correct conventions
  - Environment variable names are correct

---

## 7. Accessibility and Inclusivity

### Accessibility
- [ ] **Images have alt text (if applicable)**
  - Descriptive alt text for all images
  - Diagrams are described in text
- [ ] **Tables are accessible**
  - Header rows are marked
  - Complex tables have captions
- [ ] **Color is not the only indicator**
  - Color-blind friendly
  - Information conveyed through text as well

### Inclusivity
- [ ] **Language is inclusive**
  - Gender-neutral pronouns (they/them)
  - Avoids assumptions about reader
  - Culturally neutral examples
- [ ] **Accessibility considerations mentioned**
  - Command-line accessibility noted where relevant
  - Alternative approaches for different needs

---

## 8. Version and Maintenance

### Version Information
- [ ] **Version information is correct**
  - Document specifies applicable version(s)
  - Deprecated features are marked
  - New features are identified
- [ ] **Changelog references are included (if applicable)**
  - Links to relevant CHANGELOG entries
  - Migration guides for breaking changes

### Maintenance
- [ ] **Document is up-to-date**
  - Reflects current codebase
  - No references to removed features
  - Matches current best practices
- [ ] **Date stamps are appropriate**
  - "Last updated" date (if applicable)
  - Version-specific dates

---

## 9. Security and Privacy

### Security
- [ ] **No security vulnerabilities introduced**
  - No hardcoded credentials
  - No insecure practices demonstrated
  - Security warnings are included where needed
- [ ] **Secure defaults are used**
  - Examples follow security best practices
  - Production examples use strong crypto
  - API keys/tokens are shown as placeholders

### Privacy
- [ ] **No personal information exposed**
  - No real usernames, emails, or paths
  - Example data is fictional
  - No sensitive configuration shown

---

## 10. Specific to pytest-jux

### Cryptography
- [ ] **Cryptographic examples are secure**
  - Key generation uses strong algorithms (RSA-2048+, ECDSA-P256+)
  - Production examples use appropriate key sizes (RSA-4096, ECDSA-P384)
  - Self-signed vs CA-signed is explained
  - Key storage security is mentioned

### Configuration
- [ ] **Configuration examples are realistic**
  - Uses XDG-compliant paths
  - Environment variables are documented
  - Configuration precedence is clear
  - Multi-environment setup is explained

### CLI Commands
- [ ] **CLI examples match actual commands**
  - Command names are correct (jux-keygen, jux-sign, etc.)
  - Options match actual implementation
  - Short and long forms are both shown
  - Exit codes are documented

### pytest Integration
- [ ] **pytest integration is accurate**
  - pytest hook usage is correct
  - pytest.ini examples are valid
  - Plugin options are documented
  - Interaction with other plugins is noted

---

## Review Summary

### Overall Assessment
- [ ] **Documentation meets quality standards**
- [ ] **No blockers identified**
- [ ] **Ready to merge/publish**

### Required Changes
List any required changes before approval:

1. _____________________
2. _____________________
3. _____________________

### Suggested Improvements
List any optional improvements:

1. _____________________
2. _____________________
3. _____________________

### Reviewer Notes

_____________________
_____________________
_____________________

---

## Checklist Completion

**Review completed by**: _____________________
**Date**: _____________________
**Result**: ☐ Approved  ☐ Approved with changes  ☐ Changes required

---

## Related Resources

- **Diátaxis Framework**: https://diataxis.fr/
- **pytest-jux Style Guide**: See CONTRIBUTING.md
- **Markdown Guide**: https://www.markdownguide.org/
- **ADR-0002**: Development best practices (includes documentation standards)

---

*This checklist is maintained as part of Sprint 5: Documentation & User Experience. For improvements to this checklist, please open a GitHub issue.*
