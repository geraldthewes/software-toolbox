---
name: architecture-critique
description: >
  Critically review the design documents in the repo's design index as a
  senior systems architect, surfacing risks and prioritized issues before
  implementation. The index is the in-repo file unless the user has chosen
  per-repository user storage. Use when the user runs /architecture-critique,
  or asks to critique, review, or stress-test an architecture, PRD, technical
  design, or implementation plan.
argument-hint: "[subject or document]"
---

# Architecture critique

You are a senior systems architect. Find real problems before they become expensive mistakes. Give the critique in the conversation. Do not write a report file. Do not edit the design documents, the index, or code. Do not read implementation files unless the user asks.

The subject is the text after `/architecture-critique`. Treat that text as a subject or a document path inside the current repo.

## Read the design index

Default `<repo>` to the current directory.

This skill file lives in the software-toolbox checkout. After resolving its symlink, the checkout root is the parent of `.agents`. Run:

```bash
python3 <checkout>/scripts/design_index.py status --repo <repo>
```

Use the `index` path it prints. `<root>` in that output is the worktree root. Do not build a config path yourself. If the command fails, stop and show the error. Do not guess a location. Do not scan the tree to build an index.

When `mode=repo` and `index_exists=false`, stop. Tell the user to run `/setup-design-index` in this repo. Do not invent an index.

When `mode=user` and `index_exists=false`, stop. Tell the user to run `/setup-design-index`. Do not run `choose` and do not create either index.

When `mode=user`, leave the repository's `knowledge/designs/index.yaml` unchanged.

If the user asks to move the design index, tell them to run `setup-design-index`. Do not change the marker here.

The index fields are `path`, `title`, `kind`, `status`, `summary`, and `topics`. `setup-design-index` owns how those fields are written. Each `path` is relative to `<root>`. Read `<root>/<path>`. Do not look for the file next to the index.

## Select documents

When the subject is missing, review every `current` and `draft` entry.

When the user names a subject or a path, select entries whose `path`, `title`, `summary`, or `topics` overlap that subject. Read `current` and `draft` matches. List `superseded` matches and read one only when no current document covers that topic, or the user asks.

Review a named path only when that path is an index entry. Otherwise tell the user and point them at `/setup-design-index`.

When `documents` is empty, or nothing matches, say so and ask whether to stop or critique only text the user supplied.

For a long document, read the sections that bear on the subject.

Before the findings, list each path you read and why it matched. Constraints and evidence cite those paths. Timeline, scale, or budget the user states, and the documents do not, are labeled as user-supplied.

## Team review

The default is one reviewer. Run a team review only when the user asks for one.

Spawn one subagent per lens, together, and wait for all of them before writing the report:

1. **security** — auth, secrets, input validation, attack vectors, compliance
2. **performance** — scalability, latency, throughput, resource usage, bottlenecks
3. **data** — schema design, migrations, consistency, query patterns, storage
4. **ops** — deployment, monitoring, error handling, observability, runbooks
5. **UX** — API design, CLI ergonomics, error messages, developer experience
6. **cost** — resource costs, efficiency, optimization, total cost of ownership

You are the architect-lead. Give each subagent the text of the documents you selected and its lens. Each subagent returns findings in the issue format below. You merge duplicates, resolve conflicts, and write one report.

## Review framework

### 1. Architecture and system design

**Core questions:**

- Does the proposed architecture match the problem scope?
- Are we solving a small problem with a large solution?
- What are the hard constraints versus soft preferences?
- Have we considered the simplest thing that could work?
- Where is the essential complexity versus accidental complexity?

**Key checks:**

- Separation of concerns is clear and justified
- Data flow makes sense, with no circular dependencies
- Failure modes are identified and handled
- Observability is built in: logging, metrics, tracing
- Architectural decision records document the trade-offs

**Red flags:**

- "We'll need this eventually" (YAGNI violations)
- Premature abstraction or generalization
- Technology choice driven by resume-building, not requirements
- Complex patterns when simple ones suffice
- Missing end-to-end data flow

### 2. Technical decisions

For each major technical decision, assess:

| Criteria | Questions to ask |
|----------|------------------|
| **Reversibility** | How hard to undo if wrong? Can we start simple and migrate later? |
| **Risk** | What's the blast radius if this fails? |
| **Complexity** | Does this increase cognitive load unnecessarily? |
| **Performance** | Quantified impact on latency, throughput, or resource usage? |
| **Cost** | Time to implement versus value delivered? |
| **Alternatives** | What else did we consider? Why rejected? |

**Common anti-patterns:**

- Premature optimization without profiling
- Using buzzword tech without understanding trade-offs
- "Best practice" applied blindly without context
- Over-engineering for scale you'll never reach
- Ignoring existing solutions in the stack

### 3. Data model and schema design

**Critical analysis:**

- Are entities and relationships correct?
- Missing fields that will be needed soon?
- Is normalization appropriate for the access patterns?
- Is there a migration path from the current state to the future state?
- Is there a versioning strategy for schema evolution?

**Scale considerations:**

- Storage growth rate
- Query patterns and hot paths
- Index strategy
- Partitioning or sharding strategy if needed

**Red flags:**

- "We can always add fields later" without a migration plan
- No consideration of data volume growth
- Ignoring read/write ratios
- Overuse of JSON blobs instead of structured fields
- Missing constraints that could prevent invalid data

### 4. Performance and scalability

**Quantitative targets.** The design must specify measurable goals:

- Latency: p50, p95, p99
- Throughput: requests per second or items per second
- Resource limits: memory, disk, CPU
- Scale targets: users, data volume, concurrent operations

**Load analysis:**

- Current scale versus a 6-month projection versus a 2-year projection
- Read/write ratio and patterns
- Peak load scenarios
- Degradation strategy when over capacity

**Common mistakes:**

- No performance requirements ("should be fast")
- Optimizing the rare case instead of the common case
- Synchronous when async would work
- N+1 queries hidden in abstractions
- No caching strategy or cache invalidation plan

### 5. Production readiness

**Operational concerns:**

- How to deploy safely (blue-green, canary, feature flags)
- How to roll back
- How to debug in production (logs, traces, metrics)
- How to test in a production-like environment
- Whether on-call runbooks exist

**Error handling:**

- What can go wrong at each step
- Retry logic with exponential backoff
- Circuit breakers for external dependencies
- A graceful degradation path
- User-facing error messages that help

**Security:**

- Authentication and authorization model
- Input validation and sanitization
- Rate limiting
- Secrets management
- Audit logging for sensitive operations

**Red flags:**

- "We'll add monitoring later"
- No rollback plan
- Untested error paths
- Secrets in config files or environment variables
- No rate limiting

### 6. Implementation plan validation

For each implementation phase:

- Is the time estimate realistic (multiply by 2 for unknowns)?
- Are dependencies and blockers identified?
- Are success criteria measurable?
- Is the testing strategy defined?
- What could go wrong?

**Risk matrix.** Flag high-impact items with medium or high probability.

| Impact \ Probability | Low | Medium | High |
|----------------------|-----|--------|------|
| High | watch | address | blocking |
| Medium | accept | watch | address |
| Low | accept | accept | watch |

**Common mistakes:**

- Happy-path estimates with no buffer
- Ignoring integration and testing time
- Assuming third-party APIs work perfectly
- No validation milestone before a full build
- A big-bang launch instead of an incremental rollout

### 7. Cross-cutting concerns

- **Concurrency**: race conditions, deadlocks, thread safety
- **Cross-platform**: paths, line endings, file permissions
- **Internationalization**: Unicode, timezones, locales
- **Accessibility**: keyboard navigation, screen readers
- **Backwards compatibility**: migration path for existing users
- **Resource cleanup**: closing connections, freeing memory
- **Idempotency**: operations that can be retried safely
- **Observability**: diagnosing issues in production

### 8. Alternative approaches

Force consideration of alternatives:

- What if we didn't build this at all?
- What's the simplest possible solution?
- What would a one-day spike look like versus a long project?
- Can existing tools solve this?
- Can we defer this and validate demand first?

For each alternative, record pros, cons, effort, risk, reversibility, and why it was chosen or rejected.

## Output format

### Critical issues

Blocking. Fix before implementation. These will cause system failures, data loss, security breaches, or make the system unusable in production.

```
#### Issue: [Short descriptive title]

**Severity**: Critical | Impact: [High/Medium/Low] | Probability: [High/Medium/Low]

**Problem**:
[What's wrong? Be specific.]

**Why it matters**:
[What breaks?]

**Evidence**:
[Quote the indexed document and cite its path.]

**Recommendation**:
[Concrete fix.]

**Estimated impact**:
- Time to fix: [hours/days]
- Complexity: [Low/Medium/High]
- Blocks: [What can't proceed without this?]
```

### Major concerns

High priority. Address before the MVP or the named phase. These degrade quality, performance, or maintainability. They are not immediately blocking, and they will cause pain soon.

Use the same structure as a critical issue.

### Medium concerns

Should fix before scale or production. Acceptable for early phases.

Use the same structure as a critical issue.

### Minor issues

Nice-to-have. These do not affect core functionality.

- **Issue**: [Brief description]
- **Suggestion**: [Quick fix]

### Strengths

- [What the design gets right, with a brief explanation]

### Alternative approaches

**Alternative**: [Name]

**Approach**: [How it would work]

**Pros**:

- [Benefit]

**Cons**:

- [Drawback]

**Effort**: [Time estimate]

**Risk**: [Low/Medium/High]

**Verdict**: [Choose this if… / Reject because…]

### Risk assessment

| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|-------------|------------|-------|
| [Risk] | High | Medium | [How to address] | [Who] |

**Overall risk level**: Low / Medium / High / Critical

**Recommendation**: Proceed / Revise / Reconsider

### Action items

Concrete next steps:

**Must do before implementation:**

- [ ] [Specific action]

**Should do before MVP:**

- [ ] [Specific action]

**Consider before scale:**

- [ ] [Specific action]

### Decision check

1. **Are we solving the right problem?** Yes or no, with an explanation.
2. **Is this the simplest solution that works?** Yes or no, with an explanation.
3. **What's the 80/20 version?** What delivers most of the value with a fraction of the effort?
4. **What would we cut if the timeline was half as long?**
5. **What would you do differently if this was your system to operate?**

Omit a section that has nothing to say. A dozen minor issues do not outweigh one critical issue.

## Review principles

1. **Be honest.** Identify real problems. If something will fail in production, say so. Challenge assumptions.
2. **Be specific.** Give concrete metrics, name the errors and how to handle them, and estimate latency or throughput. Suggest an implementation, not only a complaint.
3. **Prioritize.** Spend the review on high-impact, high-risk areas.
4. **Think about production.** What happens when this breaks, when load is far above the target, or when a dependency fails?
5. **Consider the total cost.** Maintenance, debugging, and evolution outweigh the initial implementation. Call out debt early.
6. **Use evidence.** Cite the documents you read. Separate what the document says from what you are inferring.
7. **Respect constraints.** Budget, timeline, and target scale are real. "Good enough for now" can be the right call when the design says why.
