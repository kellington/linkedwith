# GSD Readme - /gsd:help

## GSD Command Reference

  GSD (Get Shit Done) creates hierarchical project plans optimized for solo agentic development with Claude Code.

  Quick Start

  1. /gsd:new-project - Initialize project (includes research, requirements, roadmap)
  2. /gsd:plan-phase 1 - Create detailed plan for first phase
  3. /gsd:execute-phase 1 - Execute the phase

  Staying Updated

  GSD evolves fast. Update periodically:

  npx get-shit-done-cc@latest

  Core Workflow

  /gsd:new-project → /gsd:plan-phase → /gsd:execute-phase → repeat

  Project Initialization

  /gsd:new-project
  Initialize new project through unified flow.

  One command takes you from idea to ready-for-planning:
  - Deep questioning to understand what you're building
  - Optional domain research (spawns 4 parallel researcher agents)
  - Requirements definition with v1/v2/out-of-scope scoping
  - Roadmap creation with phase breakdown and success criteria

  Creates all .planning/ artifacts:
  - PROJECT.md — vision and requirements
  - config.json — workflow mode (interactive/yolo)
  - research/ — domain research (if selected)
  - REQUIREMENTS.md — scoped requirements with REQ-IDs
  - ROADMAP.md — phases mapped to requirements
  - STATE.md — project memory

  Usage: /gsd:new-project

  /gsd:map-codebase
  Map an existing codebase for brownfield projects.

  - Analyzes codebase with parallel Explore agents
  - Creates .planning/codebase/ with 7 focused documents
  - Covers stack, architecture, structure, conventions, testing, integrations, concerns
  - Use before /gsd:new-project on existing codebases

  Usage: /gsd:map-codebase

  Phase Planning

  /gsd:discuss-phase <number>
  Help articulate your vision for a phase before planning.

  - Captures how you imagine this phase working
  - Creates CONTEXT.md with your vision, essentials, and boundaries
  - Use when you have ideas about how something should look/feel
  - Optional --batch asks 2-5 related questions at a time instead of one-by-one

  Usage: /gsd:discuss-phase 2
  Usage: /gsd:discuss-phase 2 --batch
  Usage: /gsd:discuss-phase 2 --batch=3

  /gsd:research-phase <number>
  Comprehensive ecosystem research for niche/complex domains.

  - Discovers standard stack, architecture patterns, pitfalls
  - Creates RESEARCH.md with "how experts build this" knowledge
  - Use for 3D, games, audio, shaders, ML, and other specialized domains
  - Goes beyond "which library" to ecosystem knowledge

  Usage: /gsd:research-phase 3

  /gsd:list-phase-assumptions <number>
  See what Claude is planning to do before it starts.

  - Shows Claude's intended approach for a phase
  - Lets you course-correct if Claude misunderstood your vision
  - No files created - conversational output only

  Usage: /gsd:list-phase-assumptions 3

  /gsd:plan-phase <number>
  Create detailed execution plan for a specific phase.

  - Generates .planning/phases/XX-phase-name/XX-YY-PLAN.md
  - Breaks phase into concrete, actionable tasks
  - Includes verification criteria and success measures
  - Multiple plans per phase supported (XX-01, XX-02, etc.)

  Usage: /gsd:plan-phase 1
  Result: Creates .planning/phases/01-foundation/01-01-PLAN.md

  PRD Express Path: Pass --prd path/to/requirements.md to skip discuss-phase entirely. Your PRD becomes locked decisions in CONTEXT.md. Useful when you already have clear
   acceptance criteria.

  Execution

  /gsd:execute-phase <phase-number>
  Execute all plans in a phase, or run a specific wave.

  - Groups plans by wave (from frontmatter), executes waves sequentially
  - Plans within each wave run in parallel via Task tool
  - Optional --wave N flag executes only Wave N and stops unless the phase is now fully complete
  - Verifies phase goal after all plans complete
  - Updates REQUIREMENTS.md, ROADMAP.md, STATE.md

  Usage: /gsd:execute-phase 5
  Usage: /gsd:execute-phase 5 --wave 2

  Smart Router

  /gsd:do <description>
  Route freeform text to the right GSD command automatically.

  - Analyzes natural language input to find the best matching GSD command
  - Acts as a dispatcher — never does the work itself
  - Resolves ambiguity by asking you to pick between top matches
  - Use when you know what you want but don't know which /gsd:* command to run

  Usage: /gsd:do fix the login button
  Usage: /gsd:do refactor the auth system
  Usage: /gsd:do I want to start a new milestone

  Quick Mode

  /gsd:quick [--full] [--discuss] [--research]
  Execute small, ad-hoc tasks with GSD guarantees but skip optional agents.

  Quick mode uses the same system with a shorter path:
  - Spawns planner + executor (skips researcher, checker, verifier by default)
  - Quick tasks live in .planning/quick/ separate from planned phases
  - Updates STATE.md tracking (not ROADMAP.md)

  Flags enable additional quality steps:
  - --discuss — Lightweight discussion to surface gray areas before planning
  - --research — Focused research agent investigates approaches before planning
  - --full — Adds plan-checking (max 2 iterations) and post-execution verification

  Flags are composable: --discuss --research --full gives the complete quality pipeline for a single task.

  Usage: /gsd:quick
  Usage: /gsd:quick --research --full
  Result: Creates .planning/quick/NNN-slug/PLAN.md, .planning/quick/NNN-slug/SUMMARY.md

  ---
  /gsd:fast [description]
  Execute a trivial task inline — no subagents, no planning files, no overhead.

  For tasks too small to justify planning: typo fixes, config changes, forgotten commits, simple additions. Runs in the current context, makes the change, commits, and
  logs to STATE.md.

  - No PLAN.md or SUMMARY.md created
  - No subagent spawned (runs inline)
  - ≤ 3 file edits — redirects to /gsd:quick if task is non-trivial
  - Atomic commit with conventional message

  Usage: /gsd:fast "fix the typo in README"
  Usage: /gsd:fast "add .env to gitignore"

  Roadmap Management

  /gsd:add-phase <description> — Add new phase to end of current milestone.
  /gsd:insert-phase <after> <description> — Insert urgent work as decimal phase between existing phases.
  /gsd:remove-phase <number> — Remove a future phase and renumber subsequent phases.

  Milestone Management

  /gsd:new-milestone <name> — Start a new milestone through unified flow.
  /gsd:complete-milestone <version> — Archive completed milestone and prepare for next version.

  Progress Tracking

  /gsd:progress — Check project status and intelligently route to next action.

  Session Management

  /gsd:resume-work — Resume work from previous session with full context restoration.
  /gsd:pause-work — Create context handoff when pausing work mid-phase.

  Debugging

  /gsd:debug [issue description] — Systematic debugging with persistent state across context resets.

  Quick Notes

  /gsd:note <text> — Zero-friction idea capture — one command, instant save, no questions.

  Todo Management

  /gsd:add-todo [description] — Capture idea or task as todo.
  /gsd:check-todos [area] — List pending todos and select one to work on.

  User Acceptance Testing

  /gsd:verify-work [phase] — Validate built features through conversational UAT.

  Ship Work

  /gsd:ship [phase] — Create PR from completed phase work.
  /gsd:review --phase N [--gemini] [--claude] [--codex] [--all] — Cross-AI peer review.
  /gsd:pr-branch [target] — Create clean PR branch filtering out .planning/ commits.

  Other

  /gsd:plant-seed [idea] — Capture forward-looking idea with trigger conditions.
  /gsd:audit-uat — Cross-phase audit of all outstanding UAT items.
  /gsd:audit-milestone [version] — Audit milestone completion against original intent.
  /gsd:plan-milestone-gaps — Create phases to close gaps identified by audit.
  /gsd:settings — Configure workflow toggles and model profile.
  /gsd:set-profile <profile> — Quick switch model profile (quality/balanced/budget/inherit).
  /gsd:cleanup — Archive accumulated phase directories.
  /gsd:update — Update GSD to latest version.
  /gsd:join-discord — Join the GSD Discord community.

  Common Workflows

  Starting a new project:
  /gsd:new-project → /clear → /gsd:plan-phase 1 → /clear → /gsd:execute-phase 1

  Resuming work: /gsd:progress

  Adding urgent work: /gsd:insert-phase 5 "Critical security fix" → plan → execute

  Completing a milestone: /gsd:complete-milestone 1.0.0 → /gsd:new-milestone

  Debugging: /gsd:debug "issue" → /clear → /gsd:debug (resume)

  Getting Help

  - Read .planning/PROJECT.md for project vision
  - Read .planning/STATE.md for current context
  - Check .planning/ROADMAP.md for phase status
  - Run /gsd:progress to check where you're up to

✻ Crunched for 1m 1s