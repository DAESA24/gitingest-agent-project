# TOON Testing Container

A Docker container for experimenting with the TOON (Token-Oriented Object Notation) format and measuring actual token savings compared to JSON.

## Purpose

- Learn Docker container basics
- Test TOON CLI tool in isolated environment
- Measure real-world token savings on GitHub API data
- Validate TOON's claimed 46.3% token reduction

## What's Installed

- **Node.js 20** (Alpine Linux base)
- **TOON CLI** (`@toon-format/cli`) - Convert between JSON and TOON
- **tokenx** - Count tokens using various encoders
- **curl** - Fetch API data
- **jq** - Process JSON
- **bash** - Nicer shell than sh

## Quick Start

### Build the Image

```bash
cd docker/toon-test
docker build -t toon-test .
```

### Run Interactive Shell

```bash
docker run -it toon-test
```

### Run with Volume Mount (access local files)

```bash
# From project root
docker run -it -v $(pwd)/docker/toon-test/test-data:/workspace/test-data toon-test
```

## Testing Workflow

### 1. Fetch GitHub API Data

```bash
# Inside container
curl https://api.github.com/repos/toon-format/toon > test-data/github-api.json
```

### 2. Convert to TOON

```bash
toon test-data/github-api.json --stats -o test-data/github-api.toon
```

### 3. Compare Token Counts

```bash
# Count tokens in JSON
tokenx count test-data/github-api.json

# Count tokens in TOON
tokenx count test-data/github-api.toon

# Or use TOON's built-in stats
toon test-data/github-api.json --stats
```

### 4. Verify Accuracy

```bash
# Decode TOON back to JSON
toon test-data/github-api.toon --decode -o test-data/decoded.json

# Compare with original (should be identical)
diff <(jq -S . test-data/github-api.json) <(jq -S . test-data/decoded.json)
```

## Example Commands

```bash
# Test with different delimiters
toon input.json --delimiter "\t" --stats       # Tab-separated (often most efficient)
toon input.json --delimiter "|" --stats        # Pipe-separated
toon input.json --delimiter "," --stats        # Comma-separated (default)

# Add length markers
toon input.json --length-marker --stats

# Output to stdout
toon input.json --stats
```

## Docker Commands Reference

```bash
# Build
docker build -t toon-test .

# Run interactive
docker run -it toon-test

# Run with volume
docker run -it -v $(pwd)/test-data:/workspace/test-data toon-test

# Run specific command
docker run toon-test toon --help

# List running containers
docker ps

# Stop container
docker stop <container-id>

# Remove container
docker rm <container-id>

# Remove image
docker rmi toon-test

# View logs
docker logs <container-id>
```

## File Structure

```
docker/toon-test/
├── Dockerfile           # Container definition
├── README.md           # This file
├── test-data/          # Downloaded JSON files (not committed)
│   └── .gitkeep
└── scripts/            # Helper scripts (future)
    └── compare.sh      # Automated comparison script
```

## Learning Goals

- [x] Create a Dockerfile
- [x] Build a Docker image
- [ ] Run containers interactively
- [ ] Mount volumes for data persistence
- [ ] Execute commands in running containers
- [ ] Clean up containers and images

## Next Steps

After mastering this container:
1. Create `docker/gitingest-dev/` - Development environment for GitIngest Agent
2. Add multi-stage builds for smaller images
3. Use Docker Compose for multi-service setups
4. Deploy containers to production

## Resources

- **TOON Format:** https://toonformat.dev
- **TOON CLI:** https://www.npmjs.com/package/@toon-format/cli
- **Docker Docs:** https://docs.docker.com
- **Node.js Images:** https://hub.docker.com/_/node

---

- **Created:** 2025-11-03
- **Purpose:** Docker learning + TOON testing
- **Status:** Active
