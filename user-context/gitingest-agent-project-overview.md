# GitIngest Agent Project Overview

**Source:** YouTube video "Bash Apps Are INSANE… A New Way To Use Claude Code"
**Video URL:** https://www.youtube.com/watch?v=1_twhMU9AxM
**Project Type:** Python CLI tool with Claude Code integration

## Project Vision

Create a direct clone of the video creator's "Git Agent" tool - an automated Claude Code agent that streamlines the process of analyzing GitHub repositories using GitIngest CLI.

## The Problem Being Solved

The video creator's original workflow had significant friction:
1. Use GitIngest to convert repositories into LLM-readable text
2. Manually check if repos exceed 200k tokens
3. If too large, manually extract just README and docs folders
4. Paste into Claude Desktop for analysis
5. Repeat process for each repository

This manual workflow creates unnecessary friction and slows down content creation.

## The Solution: Git Agent

An automated Claude Code agent that:
- **Automatically checks repository token size first** (eliminates manual checking)
- **Routes to different workflows based on size:**
  - **Under 200k tokens:** Extracts entire repository
  - **Over 200k tokens:** Examines tree structure, stores it, then intelligently fetches only needed parts (docs, specific code files) based on analysis request

## Architecture Components

### Directory Structure
- **data/** - Stores original repository extractions
- **analyze/** - Stores specific analyses (installation reports, workflow guides, etc.)
- **CLAUDE.md** - Defines the agent's behavior and workflow instructions
- **CLI.py** - Uses Click framework to create custom commands that wrap GitIngest

### Key Technical Elements
- **git-agent command:** Parent command that Claude Code automatically executes when given a GitHub URL
- **Click framework:** Python CLI framework that groups GitIngest commands with custom code
- **Token counting:** Automatic size checking to determine workflow path
- **Intelligent extraction:** Fetches only relevant content based on analysis needs

## Workflow Process

1. User provides GitHub URL to Claude Code
2. Agent runs token size check automatically
3. **If under 200k tokens:**
   - Extracts entire repository
   - Proceeds to analysis
4. **If exceeds 200k tokens:**
   - Saves repository tree structure
   - Asks user what type of analysis is needed
   - Fetches only relevant sections (docs, specific code files)
5. Claude Code analyzes the extracted content
6. Optionally saves analysis results for future reference

## Key Innovation

**Replaces Claude Desktop with Claude Code as the agent**, storing everything as structured data in the repository rather than just maintaining context in a chat session.

## Technical Implementation

### Core Framework
- **Language:** Python
- **CLI Framework:** Click (for command grouping and CLI interface)
- **Base Tool:** GitIngest CLI
- **Integration:** Claude Code via CLAUDE.md instructions

### Development Time
The video creator built this tool in approximately 2 hours, with most time spent on:
- Designing workflow logic
- Refining CLAUDE.md prompts
- Testing Claude Code command execution

## Project Goals

### Phase 1: Direct Clone
- Replicate the exact functionality shown in the video
- Implement token size checking
- Create branching workflow logic
- Set up data and analyze folder structure
- Write CLAUDE.md instructions for Claude Code integration

### Future Enhancements (Post-Clone)
- Refinements based on usage patterns
- Additional workflow improvements
- Custom features specific to our needs

## Use Cases

1. **Repository Analysis:** Quickly understand new open-source projects
2. **Documentation Extraction:** Get installation guides and workflow documentation
3. **Code Understanding:** Extract relevant code sections for learning
4. **Content Research:** Analyze repositories for video/article creation
5. **Integration Planning:** Understand how to integrate libraries into projects

## Success Criteria

- Automatic token size checking works reliably
- Workflow branches correctly based on repository size
- GitIngest integration functions seamlessly
- Claude Code responds to GitHub URLs automatically
- Analysis results are stored appropriately
- Tool eliminates manual checking and extraction steps

## Development Approach

Using BMAD methodology with GitHub integration:
- **Explore Phase:** Research GitIngest CLI, Click framework, workflow design
- **Plan Phase:** Create PRD, define architecture, design data structures
- **Execute Phase:** Implement CLI commands, test workflows, refine CLAUDE.md

## References

- **YouTube Video:** "Bash Apps Are INSANE… A New Way To Use Claude Code" (https://www.youtube.com/watch?v=1_twhMU9AxM)
- **GitIngest CLI:** Already installed via UV package manager
- **Click Framework:** Python CLI framework for building command-line tools
- **BMAD Method:** Framework for AI-assisted development

---

**Created:** 2025-09-29
**Project Status:** Initial setup with BMAD framework and GitHub integration
**Next Steps:** Begin Explore phase - research Click framework and design workflow logic