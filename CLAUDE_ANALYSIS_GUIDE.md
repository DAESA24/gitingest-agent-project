# GitIngest Agent - Analysis Generation Guide

This guide documents the analysis types and workflow for analyzing extracted repository content.

## Analysis Types

### 1. Installation Analysis

**Focus:**
- Prerequisites (Python version, system dependencies, tools required)
- Step-by-step installation instructions
- Configuration requirements (environment variables, config files)
- Verification steps (how to test installation worked)
- Common installation issues and troubleshooting

**Quality Criteria:**
- Numbered step-by-step format for clarity
- Command examples for each installation step
- Clear explanation of what each step accomplishes
- Links to relevant documentation sections if available
- Practical troubleshooting tips

**Example Output Structure:**
```markdown
# [Repository Name] - Installation Guide

## Prerequisites
- List all required tools, versions, and system requirements

## Installation Steps
1. **Step Name**
   ```bash
   command here
   ```
   Explanation of what this step does

2. **Next Step**
   ...

## Configuration
- Environment variables needed
- Config file locations and settings

## Verification
- How to verify installation was successful
- Test commands to run

## Troubleshooting
- Common issues and solutions
```

### 2. Workflow Analysis

**Focus:**
- Quick start example to get started quickly
- Common use cases with practical code examples
- API or CLI usage patterns and conventions
- Best practices for using the library/tool effectively
- Tips and tricks from the documentation

**Quality Criteria:**
- Practical, runnable code examples
- Real-world usage scenarios
- Explanation of why and when to use specific patterns
- References to documentation for deeper exploration
- Clear progression from basic to advanced usage

**Example Output Structure:**
```markdown
# [Repository Name] - Workflow Guide

## Quick Start
- Minimal example to get running immediately

## Common Use Cases

### Use Case 1: [Name]
```python
# Code example
```
Explanation of when and why to use this pattern

### Use Case 2: [Name]
...

## Best Practices
- Recommended patterns and conventions
- Performance tips
- Common pitfalls to avoid

## Advanced Usage
- More complex scenarios
- Customization options
```

### 3. Architecture Analysis

**Focus:**
- High-level system overview and main components
- Component relationships and how parts interact
- Data flow through the system (input → processing → output)
- Key design patterns and architectural decisions
- Extension points for customization and integration

**Quality Criteria:**
- Clear text-based component diagrams or descriptions
- Explanation of each component's responsibilities
- Identification of core abstractions and interfaces
- Discussion of why architectural decisions were made
- Guide to where different functionality lives in codebase

**Example Output Structure:**
```markdown
# [Repository Name] - Architecture Overview

## System Overview
- High-level description of what the system does
- Main components and their purposes

## Component Architecture
### Component 1: [Name]
- Responsibility
- Key files/modules
- Interfaces provided

### Component 2: [Name]
...

## Data Flow
- How data moves through the system
- Input sources → Processing steps → Output destinations

## Design Patterns
- Key patterns used and why
- Architectural decisions explained

## Extension Points
- How to customize or extend the system
- Plugin interfaces
- Configuration options
```

### 4. Custom Analysis

**Focus:**
- User-specified focus based on their specific question
- Examples: "How does authentication work?", "Explain the CLI architecture", "What testing framework is used?", "How do I extend feature X?"

**Quality Criteria:**
- Directly addresses the user's specific question
- Uses extracted content as evidence and examples
- Cites specific files, functions, or code sections when relevant
- Provides actionable guidance tailored to the question
- Suggests related areas to explore if applicable

**Example Flow:**
```
User selects "custom" → Prompted: "What would you like to analyze?"
User responds: "How does the CLI argument parsing work?"

Analysis focuses specifically on:
- CLI framework used
- Argument definition patterns
- Validation logic
- Help text generation
- Examples from the codebase
```

## Analysis Workflow

### Step 6: Analysis Generation

After extraction is complete and content is verified under token limit:

1. **Prompt user for analysis type:**
   ```
   What type of analysis would you like?
   1. Installation - Step-by-step setup guide
   2. Workflow - Usage patterns and examples
   3. Architecture - System design and components
   4. Custom - Specific focus (you will be prompted)

   Your choice:
   ```

2. **If custom selected:**
   Prompt: "What would you like to analyze?"
   Accept free-form user input describing their specific need

3. **Read extracted content:**
   - File path available from extraction step
   - Read entire file content into memory
   - Content already verified under 200k token limit

4. **Generate analysis:**
   - Focus analysis on selected type using guidelines above
   - Extract specific details from the repository content
   - Include relevant code examples from the extracted content
   - Format output as markdown with clear section headings
   - Be actionable, specific, and concise
   - Prioritize quality and usefulness over speed

5. **Display analysis:**
   - Present complete analysis to user
   - Use markdown formatting (headers, code blocks, lists)
   - Clear section organization
   - Syntax-highlighted code blocks where applicable

6. **Proceed to Step 7: Optional Analysis Storage**

### Step 7: Optional Analysis Storage

After analysis is displayed to user:

1. **Prompt user to save:**
   ```
   Save this analysis to analyze/ folder? (yes/no)
   ```

2. **If user confirms yes:**
   - Call `storage.save_analysis(analysis_content, repo_name, analysis_type)`
   - Display confirmation: "✓ Saved to: [absolute_path]"
   - Analysis file includes metadata header with date and analysis type

3. **If user declines:**
   - Display: "Analysis not saved (displayed only)"
   - Analysis remains available in conversation but not persisted

4. **Proceed to workflow completion**

## Analysis Quality Guidelines

**General Principles:**
- Use specific details from the extracted repository content
- Provide actionable recommendations and clear next steps
- Include code examples where relevant and helpful
- Be concise but comprehensive (avoid overwhelming detail)
- Cite specific files or code sections when referencing implementation
- Format for readability with clear section organization
- Consider the user's likely intent for each analysis type

**Content Organization:**
- Start with overview/context
- Progress from simple to complex concepts
- Use consistent heading hierarchy
- Separate concerns into logical sections
- Include practical examples throughout
- End with next steps or further resources

**Code Examples:**
- Use proper syntax highlighting (language tags in code blocks)
- Include context comments for clarity
- Show complete, runnable examples when possible
- Explain what the code demonstrates
- Reference where in the codebase the example comes from

## Storage Schema

Analysis files are saved to:
```
analyze/
  installation/           # Installation guides
    [repo-name].md
  workflow/              # Workflow documentation
    [repo-name].md
  architecture/          # Architecture analyses
    [repo-name].md
  custom/                # Custom analyses
    [repo-name].md
```

Each saved analysis includes a metadata header:
```markdown
# [repo-name] - [Analysis Type] Analysis

**Repository:** https://github.com/[owner]/[repo-name]
**Analyzed:** YYYY-MM-DD
**Analysis Type:** [installation|workflow|architecture|custom]

---

[Analysis content follows...]
```

## Notes for Claude Code

- Analysis generation is your core capability - leverage your understanding of code and documentation
- The extracted content is already curated and under token limits - analyze it thoroughly
- Each analysis type serves a different user need - tailor your focus accordingly
- Quality matters more than speed - take time to provide thoughtful, useful insights
- When in doubt about what to include, err on the side of being practical and actionable