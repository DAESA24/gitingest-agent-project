# TOON Token Savings Test Results

**Date:** 2025-11-03
**Container:** toon-test (Node.js 20 Alpine + TOON CLI 0.7.3)
**Data Source:** GitHub API (toon-format/toon repository)

## Summary

Tested TOON format conversion on real GitHub API responses to validate claimed token savings.

**Key Finding:** TOON achieves **16.6% to 22.8% token reduction** on GitHub API data, which is **lower than the claimed 46.3%** average but still significant.

## Test Cases

### Test 1: Repository Metadata

**Source:** `https://api.github.com/repos/toon-format/toon`

**Results:**
- **JSON:** 4,044 tokens
- **TOON:** 3,374 tokens
- **Savings:** 670 tokens (**-16.6%**)

**Data characteristics:**
- Single repository object
- Deeply nested structure (owner, organization, license objects)
- Many URL fields (long strings)
- Flat key-value pairs

### Test 2: Commit History

**Source:** `https://api.github.com/repos/toon-format/toon/commits`

**Results:**
- **JSON:** 76,348 tokens
- **TOON:** 58,906 tokens
- **Savings:** 17,442 tokens (**-22.8%**)

**Data characteristics:**
- Array of 30 commit objects
- Highly repetitive structure (same fields per commit)
- Nested author/committer objects
- PGP signatures (large string blobs)

## Analysis

### Why Lower Than 46.3%?

The TOON benchmarks showed 46.3% average token reduction, but our GitHub API tests showed 16-23%. Possible reasons:

1. **Field Name Length**
   - GitHub API uses long, descriptive field names (`avatar_url`, `subscriptions_url`, `followers_url`)
   - TOON doesn't compress field names, only structure
   - Longer field names = smaller percentage savings

2. **URL-Heavy Data**
   - GitHub API responses contain many long URL strings
   - URLs don't compress well with TOON's structural optimizations
   - TOON optimizes *data structure*, not *string content*

3. **Deep Nesting vs Arrays**
   - GitHub API uses deeply nested objects (owner → properties)
   - TOON's best savings come from arrays with uniform schemas
   - The commit history (array-based) showed better savings (22.8%) than single object (16.6%)

4. **Benchmark Dataset Characteristics**
   - TOON's 46.3% benchmark used datasets optimized for TOON's strengths:
     - Employee records (uniform arrays)
     - Analytics data (numeric-heavy)
     - Orders/transactions (repetitive structure)
   - GitHub API data is more heterogeneous

### When TOON Performs Best

Based on these tests, TOON saves the most tokens on data that has:

✅ **Arrays of uniform objects** (commit history: 22.8% savings)
✅ **Repetitive field structures**
✅ **Numeric or short string values**
✅ **Shallow nesting**

TOON saves less on data with:

❌ **Long field names**
❌ **URL-heavy content**
❌ **Deeply nested single objects**
❌ **Large string blobs** (signatures, descriptions)

## Practical Implications

### For GitIngest Agent

**Repository Metadata:**
- 16.6% savings is modest
- 4,044 → 3,374 tokens (670 saved)
- Only useful if analyzing many repositories

**Commit/Issue/PR Arrays:**
- 22.8% savings is more significant
- 76,348 → 58,906 tokens (17,442 saved)
- **Good use case:** Analyzing repository history or large API responses

### Break-Even Analysis

**When is TOON worth it?**

- **Small responses (<5k tokens):** Overhead not worth it
- **Medium responses (5-50k tokens):** Marginal benefit (15-20% savings)
- **Large responses (>50k tokens):** Significant benefit, especially if array-based

### Recommended Strategy

1. **Use TOON for:**
   - Arrays of commits, issues, PRs
   - Caching large API responses
   - Storing structured metadata for multiple repositories

2. **Skip TOON for:**
   - Single repository metadata
   - Small API responses
   - Text-heavy content (README, documentation)

## Docker Learnings

This project successfully demonstrated:

### Docker Skills Acquired

- ✅ Created a Dockerfile from scratch
- ✅ Used multi-package installations (apk + npm)
- ✅ Built an image with `docker build`
- ✅ Ran interactive containers
- ✅ Used stdin/stdout for data pipelines
- ✅ Mounted volumes (attempted, learned Windows/WSL challenges)
- ✅ Verified installed tools in containers

### Workflow Pattern

```bash
# Build once
docker build -t toon-test .

# Run many times with different data
cat data.json | docker run --rm -i toon-test toon --stats
```

This pattern is **perfect for testing tools** without installing them locally.

## Conclusions

### TOON Performance

- **Real savings:** 16-23% on GitHub API data
- **Below benchmark:** Less than claimed 46.3%, but expected given data characteristics
- **Still valuable:** For large array-based API responses (>50k tokens)

### Docker Experience

- **Success:** Built and tested a real tool in isolated environment
- **Learning:** Practical experience with Dockerfile, build, run workflow
- **Next steps:** Ready to containerize GitIngest Agent for development/deployment

### Honest Token Estimates

**For GitIngest Agent + GitHub API data:**
- Expect **15-25% token savings**, not 46%
- Best use case: Large commit/issue/PR history
- Marginal benefit for single repository metadata

---

## Appendix: Test Data Files

```
docker/toon-test/test-data/
├── toon-repo.json       # 6.7 KB - Repository metadata
├── toon-repo.toon       # Converted TOON format
├── toon-commits.json    # 134 KB - Commit history (30 commits)
└── toon-commits.toon    # Converted TOON format (not saved)
```

## Commands Used

```bash
# Build container
docker build -t toon-test .

# Fetch test data
curl -s https://api.github.com/repos/toon-format/toon > toon-repo.json
curl -s https://api.github.com/repos/toon-format/toon/commits > toon-commits.json

# Convert with stats
cat toon-repo.json | docker run --rm -i toon-test toon --stats
cat toon-commits.json | docker run --rm -i toon-test toon --stats
```

---

- **Test Date:** 2025-11-03
- **TOON CLI Version:** 0.7.3
- **Container Base:** Node.js 20 Alpine
- **Status:** ✅ Complete
