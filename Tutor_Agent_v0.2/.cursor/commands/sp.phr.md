---
description: Record an AI exchange as a Prompt History Record (PHR) for learning and traceability.
---

# COMMAND: Record this AI exchange as a structured PHR artifact

## CONTEXT

The user has just completed work (or is requesting work) and needs to capture this exchange as a Prompt History Record (PHR) for:

- Learning and pattern recognition (spaced repetition)
- Team knowledge sharing and traceability
- Compliance and audit requirements
- Building a searchable corpus of effective prompts

**User's input to record:**

$ARGUMENTS

**CRITICAL**: The complete text above is the PROMPT to preserve verbatim. Do NOT truncate to first line only.

## YOUR ROLE

Act as a meticulous documentation specialist with expertise in:

- Knowledge management and organizational learning
- Software development lifecycle documentation
- Metadata extraction and classification
- Creating structured, searchable technical records

## QUICK OVERVIEW

After completing ANY work, automatically create a PHR:

1. **Detect work type**: constitution|spec|plan|tasks|implementation|debugging|refactoring|discussion|general
2. **Generate title**: 3-7 word descriptive title summarizing the work
3. **Capture context**: COMPLETE conversation (never truncate to summaries)
4. **Route correctly**:
   - Pre-feature work → `docs/prompts/`
   - Feature-specific work → `specs/<feature>/prompts/`
5. **Confirm**: Show "📝 PHR-NNNN recorded"

## OUTPUT STRUCTURE

Execute this workflow in 5 sequential steps, reporting progress after each:

## Step 1: Execute User's Request (if not already done)

If the user provided a task/question in $ARGUMENTS:

- Complete the requested work first
- Provide full response to user
- Then proceed to Step 2 to record the exchange

If you already completed work and user just wants to record it:

- Skip to Step 2

## Step 2: Determine Stage

Select ONE stage that best describes the work:

**Pre-feature stages** (→ `docs/prompts/`):

- `constitution` - Defining quality standards, project principles (ALWAYS docs/prompts/)

**Feature stages** (→ `specs/<feature>/prompts/` - requires feature context):

- `spec` - Creating feature specifications
- `plan` - Architecture design and technical approach
- `tasks` - Implementation breakdown with test cases
- `red` - Debugging, fixing errors, test failures
- `green` - Implementation, new features, passing tests
- `refactor` - Code cleanup, optimization
- `explainer` - Code explanations, documentation
- `misc` - Other feature work
- `general` - General work within feature (falls back to docs/prompts/ if no specs/ exist)

## Step 3: Create PHR File

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json` to get repository metadata (FEATURE_DIR, BRANCH, etc.).

Generate a concise title (3-7 words) summarizing what was accomplished.

Call the PHR creation script with title and stage:

```bash
.specify/scripts/bash/create-phr.sh \
  --title "<your-generated-title>" \
  --stage <selected-stage> \
  --json
```

Parse the JSON output to get: `id`, `path`, `context`, `stage`, `feature`

## Step 4: Fill ALL Template Placeholders

Read the file at `path` from JSON output. Replace ALL {{PLACEHOLDERS}}:

**YAML Frontmatter:**

- `{{ID}}` → ID from JSON output
- `{{TITLE}}` → Your generated title
- `{{STAGE}}` → Selected stage
- `{{DATE_ISO}}` → Today (YYYY-MM-DD format)
- `{{SURFACE}}` → "agent"
- `{{MODEL}}` → Your model name or "unspecified"
- `{{FEATURE}}` → Feature from JSON or "none"
- `{{BRANCH}}` → Current branch name
- `{{USER}}` → Git user name or "unknown"
- `{{COMMAND}}` → "/sp.phr" or the command that triggered this
- `{{LABELS}}` → Extract key topics as ["topic1", "topic2", ...]
- `{{LINKS_SPEC}}`, `{{LINKS_TICKET}}`, `{{LINKS_ADR}}`, `{{LINKS_PR}}` → Relevant links or "null"
- `{{FILES_YAML}}` → List files modified/created, one per line with " - " prefix, or " - none"
- `{{TESTS_YAML}}` → List tests run/created, one per line with " - " prefix, or " - none"

**Content Sections:**

- `{{PROMPT_TEXT}}` → **THE COMPLETE $ARGUMENTS TEXT VERBATIM** (do NOT truncate to first line!)
- `{{RESPONSE_TEXT}}` → Brief summary of your response (1-3 sentences)
- `{{OUTCOME_IMPACT}}` → What was accomplished
- `{{TESTS_SUMMARY}}` → Tests run or "none"
- `{{FILES_SUMMARY}}` → Files modified or "none"
- `{{NEXT_PROMPTS}}` → Suggested next steps or "none"
- `{{REFLECTION_NOTE}}` → One key insight

**CRITICAL**: `{{PROMPT_TEXT}}` MUST be the FULL multiline user input from $ARGUMENTS above, not just the title or first line.

## Step 5: Report Completion

## FORMATTING REQUIREMENTS

Present results in this exact structure:

```
✅ Exchange recorded as PHR-{id} in {context} context
📁 {relative-path-from-repo-root}

Stage: {stage}
Feature: {feature or "none"}
Files modified: {count}
Tests involved: {count}
```

## ERROR HANDLING

If create-phr.sh fails:

1. Display the exact error message from script
2. Explain what went wrong in plain language
3. Provide specific corrective action with commands
4. Do NOT fail silently or hide errors

## TONE

Be professional, concise, and action-oriented. Focus on what was accomplished and what's next.

---

After completing the main command, automatically create a PHR: (1) Detect stage: constitution|spec|architect|green|red|refactor|explainer|general, (2) Generate 3-7 word title, (3) Load `.**/commands/sp.phr.md` and execute with $ARGUMENTS (FULL multiline input, NOT truncated), detected stage, implicit mode, (4) On error: warn but don't block. CRITICAL: Preserve complete user input in PHR. Skip only for /sp.phr itself.

**Architecture Decisions**: When significant architectural decisions are made (typically during /sp.plan), suggest documenting with: "📋 Architecture decisions identified. Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`" Wait for user consent.
