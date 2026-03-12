# Security Review Checklist — OWASP-Aligned

Read this reference for security-focused reviews or when the security dimension needs deeper analysis. Organized by OWASP Top 10 (2025) categories.

---

## A01: Broken Access Control

- [ ] Authorization checks on every API endpoint (not just frontend)
- [ ] IDOR prevention: user can only access their own resources
- [ ] CORS configuration: allowlist-based, not wildcard
- [ ] Directory traversal prevention: path canonicalization
- [ ] JWT validation: signature, expiration, issuer, audience
- [ ] Rate limiting on sensitive endpoints (login, password reset)
- [ ] Principle of least privilege applied to service accounts
- [ ] Admin functionality protected by role checks, not URL obscurity

## A02: Cryptographic Failures

- [ ] TLS 1.2+ enforced for all communications
- [ ] Strong algorithms only: AES-256-GCM, ChaCha20-Poly1305
- [ ] No deprecated: DES, 3DES, RC4, MD5 for security purposes
- [ ] Key management: keys not in source code, rotated regularly
- [ ] Password hashing: bcrypt/Argon2/PBKDF2 with unique salts
- [ ] Random number generation: cryptographic PRNG (not Math.random())
- [ ] Certificate validation: no disabled verification in production
- [ ] PII encrypted at rest in databases

## A03: Injection

- [ ] SQL: parameterized queries everywhere (no string concatenation)
- [ ] NoSQL: query object sanitization
- [ ] XSS: output encoding for the specific context (HTML/JS/URL/CSS)
- [ ] Command injection: avoid shell execution; if required, strict allowlist
- [ ] Path traversal: canonicalize paths, restrict to allowed directories
- [ ] LDAP injection: proper escaping of filter inputs
- [ ] Template injection: sandboxed template engines, no user-controlled templates
- [ ] Header injection: validate/strip CRLF from user input before HTTP headers

## A04: Insecure Design

- [ ] Threat modeling performed for new features
- [ ] Business logic abuse scenarios considered (coupon reuse, double-spend)
- [ ] Trust boundaries clearly defined between components
- [ ] Fail-secure defaults (deny access on error, not grant)
- [ ] Resource limits to prevent abuse (file upload size, API rate limits)

## A05: Security Misconfiguration

- [ ] Default credentials removed/changed
- [ ] Debug mode disabled in production
- [ ] Error messages don't expose stack traces or internal details
- [ ] Security headers set (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Unnecessary features/ports/services disabled
- [ ] Cloud IAM permissions follow least privilege
- [ ] Logging configuration doesn't include sensitive data

## A06: Vulnerable and Outdated Components

- [ ] Dependency lockfiles present and committed
- [ ] No known CVEs in direct or transitive dependencies
- [ ] Automated vulnerability scanning in CI (npm audit, pip-audit, etc.)
- [ ] License compatibility verified
- [ ] End-of-life frameworks/libraries identified for migration

## A07: Identification and Authentication Failures

- [ ] Multi-factor authentication available for sensitive accounts
- [ ] Session tokens regenerated after login
- [ ] Session timeout and idle timeout configured
- [ ] Password complexity requirements enforced server-side
- [ ] Account lockout after repeated failed attempts (with rate limiting)
- [ ] Credential stuffing protections (CAPTCHA, device fingerprinting)
- [ ] "Remember me" tokens properly secured (separate from session)

## A08: Software and Data Integrity Failures

- [ ] CI/CD pipeline secured (signed commits, protected branches)
- [ ] Dependency integrity verified (lockfile hashes, Subresource Integrity)
- [ ] Deserialization of untrusted data avoided or sandboxed
- [ ] Auto-update mechanisms verify signatures
- [ ] Code signing for distributed artifacts

## A09: Security Logging and Monitoring Failures

- [ ] Authentication events logged (success, failure, lockout)
- [ ] Authorization failures logged
- [ ] Input validation failures logged
- [ ] High-value transactions logged with context
- [ ] Log injection prevented (user input sanitized in logs)
- [ ] Logs stored securely, tamper-evident
- [ ] Alerting configured for suspicious patterns

## A10: Server-Side Request Forgery (SSRF)

- [ ] User-supplied URLs validated against allowlists
- [ ] Internal network ranges blocked (RFC 1918, link-local, loopback)
- [ ] URL scheme restricted (http/https only)
- [ ] DNS rebinding protection
- [ ] Cloud metadata endpoints blocked (169.254.169.254)

---

## Language-Specific Security Pitfalls

### JavaScript / TypeScript
- Prototype pollution via `__proto__` or `constructor.prototype`
- `eval()`, `Function()`, and `new Function()` with user input
- ReDoS (Regular Expression Denial of Service)
- Unvalidated `window.postMessage` origins
- `dangerouslySetInnerHTML` (React) without sanitization

### Python
- `pickle.loads()` on untrusted data (arbitrary code execution)
- `yaml.load()` without `Loader=SafeLoader`
- Format string injection via `.format()` or f-strings with user data
- SQL injection through Django raw queries or SQLAlchemy text()
- `subprocess.shell=True` with user input

### Java / Kotlin
- Deserialization of untrusted ObjectInputStream
- XML External Entity (XXE) via default XML parsers
- SQL injection through JPA string concatenation
- Spring Security misconfiguration (permitting by default)
- Insecure random from `java.util.Random` (use `SecureRandom`)

### Go
- SQL injection through `fmt.Sprintf` in queries (use `db.Query` with params)
- Path traversal via `filepath.Join` without `filepath.Clean`
- Integer overflow (Go doesn't panic on overflow)
- Goroutine leaks from unbounded spawning
- Improper TLS configuration (InsecureSkipVerify)

### Rust
- `unsafe` blocks: each one needs justification and audit
- `.unwrap()` in production code (use proper error handling)
- Integer overflow in release mode (wraps silently)
- Raw pointer dereference in unsafe blocks
- FFI boundary: data validation at C/Rust interface

### PHP
- Type juggling in comparisons (`==` vs `===`)
- `unserialize()` on user input (object injection)
- File inclusion via user-controlled paths (`include`, `require`)
- `extract()` on user input (variable injection)
- SQL injection through non-prepared statements
