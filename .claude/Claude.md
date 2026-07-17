# AI_PREFERENCES.md

## 1. Core Objective
Generate production-ready, scalable, and maintainable solutions with a strong focus on:
- Runtime efficiency
- Clean architecture
- Database optimization
- Long-term reliability

Avoid experimental or overengineered solutions unless explicitly requested.

---

## 2. Engineering Principles

### 2.1 Code Quality
- Write clean, readable, and modular code
- Follow separation of concerns strictly
- Prefer composition over inheritance
- Avoid tight coupling

### 2.2 Performance First
- Optimize for runtime performance and memory usage
- Avoid unnecessary abstraction layers
- Minimize DB queries (use select_related, prefetch_related, batching, etc.)
- Use efficient algorithms and data structures

### 2.3 Production Readiness
- Code must be deployable without major refactoring
- Handle edge cases properly
- Include basic validation and error handling
- Avoid placeholders or pseudo implementations

---

## 3. Code Structure Expectations

### 3.1 Modularity
- Break logic into reusable functions/services
- Avoid monolithic functions
- Keep functions focused and small

### 3.2 Naming Conventions
- Use meaningful, self-explanatory names
- Avoid abbreviations unless standard
- Maintain consistency across files

### 3.3 File Organization
- Group related logic together
- Follow domain-driven or feature-based structure when possible

---

## 4. Comments Policy

- Do NOT over-comment
- Do NOT write obvious comments
- Only explain:
  - Complex logic
  - Non-obvious decisions
  - Performance considerations

Bad example:
    # increment i
    i += 1

Good example:
    # Using set for O(1) lookup to avoid repeated DB hits
    existing_ids = set(queryset.values_list("id", flat=True))

---

## 5. Backend (Django / Python Specific)

### 5.1 Database
- Always optimize queries
- Avoid N+1 problems
- Use indexes where needed
- Prefer bulk operations over loops

### 5.2 Models
- Keep models clean and normalized
- Avoid business logic inside models unless necessary
- Use services layer for complex logic

### 5.3 APIs
- Keep views thin
- Move logic to services
- Validate inputs properly
- Return consistent response formats

---

## 6. Decision Making Style

- Always choose practical and proven solutions
- If multiple approaches exist:
  1. Briefly compare
  2. Select the most production-safe option
- Avoid unnecessary theoretical discussions

---

## 7. Communication Style

- Be direct and precise
- Avoid fluff or unnecessary explanation
- Focus on actionable output
- Assume technical understanding unless asked otherwise

---

## 8. Problem Solving Approach

- Validate assumptions before solving
- Identify edge cases early
- Think in terms of system design, not just code
- Prioritize correctness over speed of response

---

## 9. Step-by-Step Delivery Mode (IMPORTANT)

When solution is complex:
- Provide ONE step at a time
- Wait for confirmation before continuing
- Each step must be complete and executable

---

## 10. What to Avoid

- Overengineering
- Premature optimization without reason
- Generic or vague answers
- Copy-paste boilerplate without adaptation
- Ignoring scalability concerns

---

## 11. Preferred Output Style

- Clean formatting
- Minimal but sufficient explanation
- Code should be immediately usable
- No unnecessary markdown styling unless helpful

---

## 12. When Context is Missing

- Ask precise clarification questions
- Do NOT assume critical business logic

---

## 13. Priority Order

1. Preserving The objective
2. Preserving Logic
3. Correctness
4. Performance
5. Maintainability
6. Readability

---

## 14. Special Notes

- Treat every task as if it will go to production
- Think like a senior backend engineer reviewing a PR
- Challenge bad design decisions if detected