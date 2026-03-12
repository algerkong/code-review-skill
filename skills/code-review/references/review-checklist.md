# Code Review Checklist — 40 Questions

Read this reference when you need the full detailed checklist for thorough reviews. Organized by dimension, each question includes what to look for and common pitfalls.

---

## Dimension 1: Logic & Correctness (Questions 1-10)

### 1. Does the code correctly implement all stated requirements?
- Trace each requirement to specific code paths
- Check that acceptance criteria are met, not just the happy path

### 2. Are loop boundaries correct?
- Off-by-one errors in iteration
- Infinite loop potential (missing break conditions, incorrect convergence)
- Empty collection handling (does the loop body assume ≥1 element?)

### 3. What happens if a variable or object is null/undefined at runtime?
- Trace nullable references through call chains
- Check for optional chaining where needed (`?.` in JS/TS, `?` in Kotlin)
- Null checks before dereferencing

### 4. Are all user inputs validated comprehensively?
- Type validation, range checks, format validation
- Length limits on strings and collections
- Whitelist vs blacklist approaches (prefer whitelist)

### 5. What implicit assumptions does this code make?
- Ordering assumptions (events arriving in sequence)
- Uniqueness assumptions (IDs, usernames)
- Availability assumptions (external services always responding)

### 6. Could thread interleaving cause unexpected behavior?
- Shared mutable state accessed from multiple threads
- Check-then-act patterns without synchronization
- Atomic operation assumptions

### 7. Are shared resources protected by appropriate synchronization?
- Database transactions with correct isolation levels
- Distributed locks where needed
- Deadlock potential in lock ordering

### 8. What happens when an operation fails midway through?
- Partial state mutations before an error
- Cleanup/rollback logic
- Idempotency for retryable operations

### 9. How does the code handle time-related edge cases?
- Timezone handling (UTC vs local)
- Daylight saving time transitions
- Clock skew in distributed systems
- Date arithmetic (months with different lengths, leap years)

### 10. Can the system reach invalid states through unexpected operation sequences?
- State machine completeness (all transitions defined)
- Concurrent request handling (double-submit, race conditions)
- Initialization order dependencies

---

## Dimension 2: Security — OWASP-Aligned (Questions 11-20)

### 11. Are inputs validated and sanitized before use in SQL, OS, or LDAP operations?
- Parameterized queries (not string concatenation)
- OS command arguments escaped or avoided entirely
- LDAP filter encoding

### 12. Are passwords/credentials stored with strong hashing?
- Acceptable: bcrypt, Argon2, PBKDF2 with sufficient rounds
- Unacceptable: MD5, SHA-1, SHA-256 without salt, plaintext
- Salt uniqueness per credential

### 13. Is authorization checked on every request, including direct object references?
- IDOR (Insecure Direct Object Reference) prevention
- Server-side authorization (not relying on client-side checks)
- Consistent use of middleware/decorators for auth

### 14. Is sensitive data encrypted in transit (TLS 1.2+) and at rest?
- HTTPS enforcement (no mixed content)
- Database encryption for PII
- Encryption key management (not hardcoded)

### 15. Are security headers configured?
- Content-Security-Policy (CSP)
- Strict-Transport-Security (HSTS)
- X-Frame-Options, X-Content-Type-Options
- Referrer-Policy

### 16. Is user data encoded/escaped for its rendering context?
- HTML entity encoding for HTML output
- JavaScript string escaping for inline scripts
- CSS encoding for style contexts
- URL encoding for URL parameters

### 17. Are external dependencies scanned for known vulnerabilities?
- `npm audit`, `pip-audit`, `cargo audit`, Dependabot, Snyk
- Dependency pinning (lockfiles present and committed)
- License compatibility

### 18. Are security-relevant events logged with adequate detail?
- Authentication attempts (success and failure)
- Authorization failures
- Input validation failures
- No sensitive data in logs (passwords, tokens, PII)

### 19. Are user-supplied URLs validated with allowlists to prevent SSRF?
- URL scheme restriction (only http/https)
- Domain allowlisting
- Internal network range blocking (169.254.x.x, 10.x.x.x, etc.)

### 20. Are anti-CSRF tokens present on every state-changing request?
- Token generation and validation
- SameSite cookie attribute
- Double-submit cookie pattern (if applicable)

---

## Dimension 3: Performance (Questions 21-30)

### 21. Does this code execute queries inside a loop?
- The classic N+1 problem
- Look for ORM lazy-loading in loops
- Batch or eager-load alternatives

### 22. Can multiple DB calls be combined into one bulk or JOIN query?
- Sequential reads that could be a single query
- Separate insert/update calls that could be batched
- Transaction scope (too broad = contention, too narrow = inconsistency)

### 23. Are all allocated resources released in every code path?
- try-finally / using / defer / with patterns
- Connection pool returns
- File handle and stream closing

### 24. Do any in-memory collections grow without bounds?
- Caches without eviction policy (LRU, TTL)
- Event listener accumulation
- Logging buffers

### 25. Are unnecessary object allocations happening in hot paths?
- Object creation inside tight loops
- String concatenation vs StringBuilder
- Autoboxing in numeric-intensive code (Java)

### 26. Is the algorithmic complexity acceptable for expected data volumes?
- O(n²) or worse on potentially large datasets
- Unindexed database queries on large tables
- Recursive algorithms without depth limits

### 27. Could repeated calculations be cached?
- Pure functions called with same arguments
- Expensive computations in render loops (React useMemo)
- Database queries with stable results

### 28. Could linear searches be replaced with indexed lookups?
- Array.find() where a Map/Set would be O(1)
- Database full table scans where an index exists or should
- Repeated filtering of the same collection

### 29. Are synchronization bottlenecks limiting horizontal scale?
- Global locks, single-threaded queues
- Database row-level vs table-level locks
- Shared mutable state that prevents sharding

### 30. Does the code make blocking calls that could be asynchronous?
- Synchronous HTTP requests in an async runtime
- File I/O blocking the event loop
- Database queries that don't need to be awaited sequentially

---

## Dimension 4: Maintainability & Readability (Questions 31-40)

### 31. Does this change improve overall code health, even if imperfect?
- The "boy scout rule" — leave the campground cleaner
- Incremental improvement over perfection
- Don't block good changes demanding great ones

### 32. Are names meaningful and intention-revealing?
- Variable names that describe content, not type (`userAge` not `int1`)
- Function names that describe behavior (`calculateShippingCost` not `process`)
- Boolean names that read naturally (`isEnabled`, `hasPermission`)

### 33. Are functions small, single-purpose, and at one abstraction level?
- Functions doing too many things (> 1 clear responsibility)
- Mixed abstraction levels (HTTP parsing next to business logic)
- Extract-method opportunities

### 34. Do function names describe behavior without peeking at implementation?
- Name describes the "what" not the "how"
- No implementation details leaking into names
- Consistent naming patterns across the codebase

### 35. Do comments explain "why" not "what"? Is dead code removed?
- Comments explaining business rules or non-obvious decisions
- Commented-out code that should be deleted (it's in git history)
- TODO/FIXME/HACK comments with tracking (issue numbers)

### 36. Is related code kept together with clear separation?
- Cohesion: related logic in the same module
- Separation: unrelated concerns in different modules
- Vertical ordering: caller above callee, or public above private

### 37. Does this change reduce coupling and increase flexibility?
- Dependency injection over hard dependencies
- Interface/protocol usage for polymorphism
- Configuration over hardcoded values

### 38. Are errors handled explicitly with useful, secure messages?
- User-facing errors: helpful without exposing internals
- Developer-facing errors: stack traces, context, correlation IDs
- No swallowed exceptions (empty catch blocks)

### 39. Does the change include tests verifying behavior?
- Unit tests for new logic
- Integration tests for new integrations
- Edge case coverage (not just happy path)
- Test quality: do they test behavior or implementation details?

### 40. Does the code follow established style guidelines consistently?
- Project's own style guide (if exists)
- Language idioms and conventions
- Consistent patterns with the rest of the codebase
