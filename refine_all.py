#!/usr/bin/env python3
"""Comprehensive question refinement — fixes length imbalance, weak distractors, same-start patterns."""
import sys
sys.path.insert(0, '.')
from apply_improvements import apply, q

# Keys = 0-based line indices in questions.js
# For short-correct questions: expand the correct option to include a brief explanation
# For long-correct questions: rewrite weak/terse distractors with substantive alternatives
# For same-start distractor questions: diversify opening words

REPLACEMENTS = {

# ═══════════════════════════════════════════════════════════
# SHORT-CORRECT FIXES (ratio < 0.5, avg_wrong > 50)
# Correct option expanded to match distractor depth/length
# ═══════════════════════════════════════════════════════════

# Q89 — correct was '"any"' (5ch), distractors ~110-160ch
119: q(
    "Which <code>tool_choice</code> value guarantees the model will call SOME tool but lets it pick which?",
    [
        "<code>\"any\"</code> — forces the model to call at least one tool every turn, but does not constrain which tool it chooses",
        "<code>\"auto\"</code> — allows the model to call any available tool or respond with text if no tool call is warranted; does not guarantee a tool will be called",
        "<code>{\"type\": \"tool\", \"name\": \"search\"}</code> — forces a specific named tool call, satisfying the 'must call a tool' requirement but removing the model's freedom to choose which tool",
        "Omitting <code>tool_choice</code> entirely — without the parameter, the model defaults to <code>\"auto\"</code> behavior, making text responses equally likely",
    ],
    "\"any\" forces the model to call at least one tool every turn while still letting it select from the available set. \"auto\" allows text-only responses when the model decides no tool is needed. A named tool override forces a specific tool, removing the model's flexibility. Omitting tool_choice defaults to \"auto\" behavior."
),

# Q93 — correct was '"any"' (5ch)
123: q(
    "You want to guarantee the model calls a tool rather than returning a free-form text reply (e.g., when every request must produce structured output). Which <code>tool_choice</code> setting achieves this?",
    [
        "<code>\"any\"</code> — guarantees the model calls at least one tool on every turn, preventing conversational text responses",
        "<code>\"auto\"</code> — the model evaluates whether a tool call is warranted; structured output is not guaranteed because the model may return plain text when it judges no tool call is needed",
        "Omitting <code>tool_choice</code> entirely — the model defaults to <code>\"auto\"</code> behavior, calling a tool only when it believes it appropriate; text-only responses remain possible",
        "<code>{\"type\": \"text\"}</code> — this setting forces a plain-text response, which can be schema-shaped via prompt but does not use tool calling",
    ],
    "\"any\" is the correct setting when every request must produce a tool call — it prevents plain-text responses entirely. \"auto\" and the default both allow the model to reply with text when it decides no tool is needed. {\"type\": \"text\"} forces text and prohibits tool calls."
),

# Q97 — correct was 'tool_choice: "any"' (18ch)
127: q(
    "When you want to enforce 'always call a tool, never reply with conversational text', use:",
    [
        "<code>tool_choice: \"any\"</code> — forces the model to invoke at least one tool every turn, preventing plain-text responses entirely",
        "<code>tool_choice: \"auto\"</code> — the model evaluates whether a tool call is needed and may return conversational text when it decides no tool is relevant",
        "Omitting <code>tool_choice</code> — without the parameter, the model defaults to <code>\"auto\"</code> behavior, making text replies equally valid responses",
        "A prominent system prompt rule like 'ALWAYS invoke a tool before responding; never reply with text' — this provides guidance but does not deterministically prevent text-only responses",
    ],
    "tool_choice: \"any\" deterministically enforces tool calls on every turn. \"auto\" and the default both permit text-only responses when the model judges them appropriate. Prompt rules are probabilistic — the model may still return text under certain conditions."
),

# Q89 duplicate pattern at Q204 — correct was '"auto"' (7ch)
264: q(
    "Which <code>tool_choice</code> option might let the model return conversational text instead of calling a tool?",
    [
        "<code>\"auto\"</code> — the model decides on each turn whether to call a tool or return a text response; a tool call is not guaranteed",
        "<code>\"any\"</code> — forces the model to call at least one tool every turn, making a text-only response impossible",
        "<code>{\"type\": \"tool\", \"name\": \"summarize\"}</code> — forces a specific tool call, guaranteeing a tool invocation rather than a text response",
        "Omitting <code>tool_choice</code> is equivalent to <code>\"any\"</code> — the model always calls a tool when the parameter is absent",
    ],
    "\"auto\" (and the equivalent default of omitting tool_choice) gives the model discretion to return text when it judges no tool is needed. \"any\" and named tool overrides both guarantee a tool call occurs. The distractors' claim that omitting tool_choice equals \"any\" is incorrect — omitting it defaults to \"auto\" behavior."
),

# Q108 — correct was '<code>Grep</code>' (4ch)
142: q(
    "To search file CONTENTS for all callers of a function, the right built-in tool is:",
    [
        "<code>Grep</code> — searches file contents by text or regex pattern; the correct choice for locating all references to a function name across a codebase",
        "<code>Glob</code> — pattern-matches file paths by name, useful when the function name corresponds to a file name pattern, but does not search file contents",
        "<code>Read</code> — loads complete file contents so the model can scan the text manually, but requires reading every file individually rather than searching across all at once",
        "<code>Edit</code> — searches for a target string as part of its anchor-based replacement mechanism, not as a standalone content search tool",
    ],
    "Grep searches file contents by pattern — it's the correct tool for finding all callsites of a function across a codebase. Glob matches file names, not contents. Read loads individual files; it can't search across the codebase in one operation. Edit uses text matching as part of a replacement workflow, not as a search operation."
),

# Q109 — correct was '<code>Glob</code>' (4ch)
143: q(
    "To find all files matching a NAME pattern like <code>**/*.test.tsx</code>, you use:",
    [
        "<code>Glob</code> — matches files by path/name pattern using glob syntax; the right tool when you need a file list by name rather than by content",
        "<code>Grep</code> — while primarily a content-search tool, it can filter by filename extension with <code>--include</code> flags, but returns matching lines rather than a clean file list",
        "<code>Read</code> on the directory — this lists immediate children but does not recursively match glob patterns across subdirectories",
        "<code>Bash</code> with shell glob expansion — can enumerate files recursively but requires constructing the correct find/ls command rather than using a dedicated path-pattern tool",
    ],
    "Glob is purpose-built for matching file paths by name pattern — the right tool for \"give me all files matching **/*.test.tsx\". Grep searches contents and produces line matches, not a file list. Read on a directory lists only immediate children. Bash can do this with find/ls but requires manual shell command construction."
),

# Q112 — correct was '<code>Edit</code>' (4ch)
146: q(
    "For targeted modifications when the surrounding text is unique, the right tool is:",
    [
        "<code>Edit</code> — performs exact string replacement anchored to unique surrounding context; the right choice for isolated changes when the target text appears only once",
        "<code>Write</code> — replaces entire file contents; appropriate for complete rewrites, but unnecessarily destructive for small targeted changes",
        "<code>Bash</code> with <code>sed</code> — supports in-place substitution, but requires careful regex escaping and doesn't provide the same precision as anchor-based replacement for unique context",
        "<code>Read</code> the file first to verify the surrounding text is actually unique, then write a separate Edit call — correct approach but describes the verification step, not the modification tool itself",
    ],
    "Edit is the correct tool for targeted modifications — it matches the exact old string (using surrounding context as an anchor) and replaces it precisely. Write replaces the whole file, which is heavy-handed for a small change. Sed requires regex escaping and lacks the anchor-based uniqueness guarantee. Reading first is good practice but describes verification, not the modification tool."
),

# Q116 — correct was '<code>Bash</code>' (4ch)
150: q(
    "You need to run shell commands (e.g., build, test). The built-in tool is:",
    [
        "<code>Bash</code> — executes arbitrary shell commands, build scripts, test runners, and CLI tools; the right tool when you need to interact with the system environment",
        "<code>Edit</code> — modifies shell scripts or Makefiles in the file system, but does not execute them; changes take effect only when the scripts are run separately",
        "<code>Glob</code> — enumerates build targets or test runner scripts by filename pattern, but provides only a file list rather than executing any commands",
        "<code>Read</code> — loads build configuration files like <code>package.json</code> or <code>Makefile</code> so the model can inspect their contents, but does not run any of the commands they define",
    ],
    "Bash is the tool for executing shell commands — it invokes the system shell, runs build scripts, test commands, and CLIs. Edit modifies files but doesn't execute them. Glob finds files by name pattern but doesn't run anything. Read loads file contents for inspection only."
),

# Q121 — correct was '<code>/memory</code>' (7ch)
161: q(
    "A user wants to verify which memory files are loaded for their current session. The command is:",
    [
        "<code>/memory</code> — displays the list of CLAUDE.md files and memory files currently loaded in the session context",
        "<code>/compact</code> — compresses the current conversation to save context space, but does not display loaded memory files",
        "<code>/clear</code> — resets the current conversation history and unloads all context, rather than displaying what's loaded",
        "<code>/reload</code> — forces the session to re-read CLAUDE.md files from disk to pick up recent changes, but does not display the loaded file list",
    ],
    "/memory shows which instruction and memory files are currently in the model's context — the correct command for diagnosing what's loaded. /compact summarizes history to save tokens. /clear wipes the conversation. /reload refreshes file-based instructions from disk."
),

# Q135 — correct was '<code>context: fork</code>' (13ch)
177: q(
    "A skill that brainstorms multiple architectural alternatives should run with which frontmatter setting?",
    [
        "<code>context: fork</code> — runs the skill in an isolated copy of the session so brainstorm output and generated alternatives don't pollute the main conversation context",
        "<code>context: main</code> — runs the brainstorm inline in the current session, with all generated alternatives and reasoning added directly to the main context window",
        "No frontmatter context setting — skills default to <code>context: main</code>, so brainstorm results automatically accumulate in the current session unless overridden",
        "An external MCP server that runs brainstorming as a separate service, returning only the final recommendation through a tool call — a valid architecture but heavier than using a forked skill",
    ],
    "context: fork isolates the brainstorming session so that exploratory output — intermediate alternatives, discarded ideas, verbose reasoning — doesn't contaminate the main session's context. context: main adds all that noise directly to the working conversation. The default is main, not fork."
),

# Q149 — correct was 'Direct execution' (16ch)
195: q(
    "For a single-file bug fix with a clear stack trace, the recommended Claude Code mode is:",
    [
        "Direct execution — the approach is already clear from the stack trace; no investigation phase is needed before making the targeted change",
        "Plan mode — to verify the proposed fix doesn't introduce regressions in other files or violate architectural constraints before any code changes",
        "A forked session — to preserve the current main session state while testing the fix in isolation before merging changes back",
        "Plan mode followed immediately by direct execution — the two-phase investigation and implementation workflow for well-scoped tasks",
    ],
    "Direct execution is correct for single-file, well-scoped changes where the stack trace provides a clear diagnosis — no planning phase is needed. Plan mode is valuable when the approach is uncertain or the change touches many files. A forked session is for divergent exploration, not simple bug fixes. Plan→direct together is appropriate for more complex changes, not a clear single-file fix."
),

# Q165 — correct was '2-3 examples' (12ch)
213: q(
    "The recommended number of input/output examples for clarifying a transformation is typically:",
    [
        "2–3 examples — enough to demonstrate the pattern without consuming excessive context tokens or over-constraining the model to specific formats",
        "30 or more examples — the model needs a statistically significant sample to generalize correctly; fewer examples produce inconsistent transformations",
        "A single carefully chosen example — one precise, representative example conveys the pattern efficiently and leaves the model flexibility to handle variation",
        "No examples — clear prose instructions are sufficient; adding examples increases prompt size and may cause the model to overfit to example formats",
    ],
    "2–3 targeted examples strikes the right balance: enough to communicate the pattern clearly without wasting context or causing the model to overfit. 30+ examples are excessive for transformation guidance. A single example may be ambiguous about edge cases. No examples forces the model to rely entirely on prose, which is often less effective than showing the pattern."
),

# Q172 — correct was '<code>-p</code> (or <code>--print</code>)' (15ch)
222: q(
    "For a non-interactive CI invocation, the most important CLI flag is:",
    [
        "<code>-p</code> / <code>--print</code> — bypasses the interactive TUI and prints the model's response to stdout, which is required for CI pipelines that capture output programmatically",
        "<code>--quiet</code> — reduces log verbosity and suppresses progress messages, but the process still requires a terminal for its interactive TUI",
        "<code>--debug</code> — increases output verbosity with diagnostic information, making it unsuitable for clean CI log capture",
        "<code>--no-input</code> — while semantically intuitive, this flag does not exist in Claude Code's CLI; non-interactive operation is controlled by <code>--print</code>",
    ],
    "--print / -p is the key flag for CI: it disables the interactive terminal UI and writes output to stdout, enabling programmatic output capture in pipelines. --quiet changes verbosity but doesn't switch to non-interactive mode. --debug adds noise unsuitable for CI logs. --no-input doesn't exist."
),

# Q99 — correct was '<code>~/.claude.json</code>' (14ch)
131: q(
    "For a personal experimental MCP server you don't want to share with teammates, the config goes in:",
    [
        "<code>~/.claude.json</code> — the user-level configuration file; settings here are local to your machine and never committed to version control or shared with teammates",
        "<code>.mcp.json</code> in the project root, under a personal namespace key — this file is version-controlled and visible to all teammates who pull the repository",
        "<code>.claude/rules/</code> with a YAML frontmatter flag to activate the server only when specified — a rules file manages instruction scoping, not MCP server registration",
        "The project-level <code>CLAUDE.md</code>, since CLAUDE.md configuration and MCP server settings share the same hierarchical lookup — CLAUDE.md manages instructions, not MCP server registration",
    ],
    "~/.claude.json is the user-level config that lives on your machine and is never version-controlled — the right place for personal MCP servers you don't want shared. .mcp.json in the project root is committed to git and visible to all collaborators. Rules files and CLAUDE.md manage instruction scoping, not MCP server configuration."
),

# Q98 — correct was 'Project-level <code>.mcp.json</code>' (25ch)
130: q(
    "You want to share an MCP server configuration with your entire team via version control. Where should the config go?",
    [
        "Project-level <code>.mcp.json</code> — committed to the repository root, this file is shared with all team members who clone the project",
        "<code>~/.claude.json</code> on the lead engineer's machine, with a note in the README — this is user-level config that exists only on one machine and requires teammates to manually replicate it",
        "<code>.claude/rules/</code> with a YAML frontmatter <code>mcp: true</code> flag — rules files manage instruction scoping and path-based context loading, not MCP server registration",
        "An environment variable <code>CLAUDE_MCP_SERVER_URL</code> set in the team's CI/CD platform — environment variables are not the mechanism for registering MCP tools in Claude Code",
    ],
    "Project-level .mcp.json lives in the repository root and is committed to version control, making it automatically available to every team member who clones the project. ~/.claude.json is user-level and not shared. Rules files handle instruction scoping. Environment variables are not the MCP registration mechanism."
),

# Q129 — correct was '<code>~/.claude/commands/</code>' (19ch)
171: q(
    "A personal slash command that you don't want to share belongs in:",
    [
        "<code>~/.claude/commands/</code> — the user-level commands directory; files here are local to your machine and never version-controlled",
        "<code>.claude/commands/</code> in the project root — this creates a project-scoped command that is committed to version control and shared with all teammates who clone the repository",
        "<code>CLAUDE.md</code> at the project root — custom slash commands can be referenced in CLAUDE.md but the command file itself must live in a commands directory, not in an instruction file",
        "An environment variable like <code>CLAUDE_COMMAND_REVIEW</code> — Claude Code reads commands from directory-based files, not from environment variables",
    ],
    "~/.claude/commands/ is the user-level directory for personal slash commands — it's local to your machine and never committed. .claude/commands/ in the project root is version-controlled and shared with teammates. CLAUDE.md manages instructions, not command file storage. Environment variables don't register slash commands."
),

# Q132 — correct was '<code>argument-hint</code> in SKILL.md frontmatter' (37ch)
174: q(
    "To prompt the developer for parameters when invoking a skill without arguments, configure:",
    [
        "<code>argument-hint</code> in the SKILL.md frontmatter — this string is displayed to the developer as a prompt when the skill is invoked without arguments",
        "A required parameter in the skill's YAML schema with <code>required: true</code> — skill frontmatter uses <code>argument-hint</code> for prompting, not a required-field schema",
        "A guard clause at the top of the skill body that checks for missing arguments and outputs usage instructions — this is an output-based pattern, not the frontmatter mechanism for prompting",
        "The <code>prompt: interactive</code> frontmatter flag, which activates an interactive argument-gathering dialog before running the skill body",
    ],
    "argument-hint in the SKILL.md frontmatter is the supported mechanism for displaying a prompt to the developer when a skill is invoked without arguments. A required: true schema field describes parameter requirements but doesn't display a prompt. Guard clauses produce output after invocation, not before. prompt: interactive is not a valid frontmatter flag."
),

# Q134 — correct was '<code>~/.claude/skills/</code> with a different name' (37ch)
176: q(
    "A teammate creates a personal variant of a project skill. To avoid affecting other contributors, where should it go?",
    [
        "<code>~/.claude/skills/</code> with a different name — the user-level skills directory is local to their machine and never committed, so it won't affect other team members",
        "<code>.claude/skills/</code> in the project root with a <code>personal: true</code> frontmatter flag — project-level skills are committed to version control regardless of frontmatter flags",
        "A new branch of the repository — while branching isolates changes during development, merging or PR review exposes the personal variant to the whole team",
        "The same <code>.claude/skills/</code> location with a modified name like <code>my-review.skill.md</code> — project-level skills are version-controlled, so any file in this directory will be shared with all contributors",
    ],
    "~/.claude/skills/ is the user-level directory that exists only on the developer's machine and is never committed to version control. Any file in .claude/skills/ (project-level) is committed and shared, regardless of name or frontmatter. Branches isolate during development but not permanently."
),

# Q124 — correct was 'Project-level CLAUDE.md in version control' (43ch)
164: q(
    "For consistent behavior across team sessions, the safest place for shared coding standards is:",
    [
        "Project-level <code>CLAUDE.md</code> in version control — committed alongside the source code, it's automatically picked up by every team member's session and changes are tracked via git",
        "User-level <code>~/.claude/CLAUDE.md</code> on each developer's machine — this requires every team member to manually keep their personal file in sync with the shared standards",
        "A shared network drive that Claude Code reads at startup — Claude Code doesn't read from external network paths; context comes from the local filesystem hierarchy",
        "The team's CI/CD environment variables — environment variables provide execution context but are not the mechanism for delivering coding standards to Claude Code sessions",
    ],
    "Project-level CLAUDE.md is version-controlled with the codebase — every team member automatically inherits updates when they pull, and changes are tracked in git history. User-level files require manual synchronization per developer. Claude Code doesn't read from network drives or use environment variables for coding standards."
),

# Q126 — correct was '.claude/rules/ with YAML frontmatter glob paths' (47ch)
166: q(
    "For conventions that span MANY directories (e.g., all test files <code>**/*.test.tsx</code>), the right CLAUDE.md approach is:",
    [
        "<code>.claude/rules/</code> with YAML frontmatter <code>paths</code> glob — a dedicated rules file with a glob pattern loads only when the agent touches matching files, keeping other contexts clean",
        "A single root-level <code>CLAUDE.md</code> with all conventions inline — this always loads into every session regardless of which files are being edited, consuming context even when the conventions are irrelevant",
        "Separate <code>CLAUDE.md</code> files in each test directory — requires duplicating the same conventions N times, creating drift when standards change",
        "A user-level <code>~/.claude/CLAUDE.md</code> with the test conventions — user-level config applies globally to all projects, polluting sessions for projects that don't share these conventions",
    ],
    ".claude/rules/ with a paths glob targets the convention precisely — it loads only when matching files are in context, avoiding unnecessary token usage on unrelated tasks. Root-level CLAUDE.md always loads. Per-directory duplication causes drift. User-level config bleeds across all projects."
),

# Q131 — correct was '<code>allowed-tools</code> in the SKILL.md frontmatter' (42ch)
173: q(
    "To restrict which tools a skill can use during execution, configure:",
    [
        "<code>allowed-tools</code> in the SKILL.md frontmatter — this explicitly lists which tools the skill is permitted to invoke, enforcing least privilege during execution",
        "<code>tool_choice: \"none\"</code> in the skill's execution context — this would prevent all tool calls, not selectively restrict to a specific subset",
        "A guard prompt at the start of the skill body listing forbidden tools — prompt-based tool restrictions are probabilistic; the model may still call unlisted tools",
        "The project-level <code>.mcp.json</code> by omitting the tools you want to exclude — this controls MCP server registration, not per-skill tool access within Claude Code",
    ],
    "allowed-tools in SKILL.md frontmatter is the supported mechanism for scoping a skill's tool access — it deterministically restricts which tools the skill can invoke. tool_choice: \"none\" disables all tools. Prompt-based restrictions are probabilistic. .mcp.json manages MCP server registration, not skill-level tool permissions."
),

# Q133 — correct was 'CLAUDE.md — for always-loaded universal standards' (47ch)
175: q(
    "Which is the right choice between skills and CLAUDE.md for an universally applicable coding standard?",
    [
        "CLAUDE.md — for always-loaded universal standards that should apply to every session without explicit invocation",
        "A skill with <code>context: main</code> — skills require explicit invocation via slash command; a coding standard that must always apply cannot rely on developers remembering to invoke it",
        "A skill with <code>context: fork</code> — forked skills run in isolated sessions, which means the standard wouldn't affect the main working session at all",
        "An MCP server that responds to a <code>get_standards</code> tool call — this makes the standard opt-in per tool call rather than passively enforced across all sessions",
    ],
    "CLAUDE.md is the right vehicle for universal standards — it loads automatically on every session without requiring explicit invocation. Skills must be triggered by slash command, so critical standards that must always apply shouldn't depend on developers remembering to run them. Forked skills execute in isolation. MCP tools are opt-in per call."
),

# Q139 — correct was '.claude/rules/ with YAML frontmatter paths globs' (46ch)
183: q(
    "For files spread across many directories that share conventions (e.g., all test files <code>**/*.test.tsx</code>), the recommended approach is:",
    [
        "<code>.claude/rules/</code> with YAML frontmatter <code>paths</code> globs — a single rule file targets all matching files without duplicating content or loading the convention when unrelated files are in context",
        "Embed the convention in the root <code>CLAUDE.md</code> — this works but loads the test convention into every session, even when no test files are being touched",
        "Create a <code>CLAUDE.md</code> in each directory that contains test files — duplicates the same content in multiple places, creating maintenance drift when the convention changes",
        "Use user-level <code>~/.claude/CLAUDE.md</code> to make the convention global — applies it across all projects on the machine, not just this one repository",
    ],
    ".claude/rules/ with a paths glob is path-scoped loading: the convention loads only when matching files are in context, avoiding unnecessary context consumption. Root CLAUDE.md always loads regardless. Per-directory files duplicate content. User-level config is too broad."
),

# Q119 — correct was 'Project-level (.claude/CLAUDE.md or root CLAUDE.md)' (42ch)
159: q(
    "Which CLAUDE.md scope is shared via version control with all team members?",
    [
        "Project-level (<code>.claude/CLAUDE.md</code> or root <code>CLAUDE.md</code>) — these files live in the repository and are committed to version control, making them automatically available to every contributor",
        "User-level (<code>~/.claude/CLAUDE.md</code>) — this file lives on each developer's local machine and is never committed; changes are not propagated to teammates",
        "Subdirectory-level (<code>backend/CLAUDE.md</code>) — while these are in the repository, they apply only to sessions started within that subdirectory rather than to the whole team's workflow",
        "Enterprise-level CLAUDE.md configured in the organization's admin console — no such scope exists; Claude Code CLAUDE.md scopes are project, user, and subdirectory",
    ],
    "Project-level CLAUDE.md (at the repo root or in .claude/) is version-controlled with the source code and shared automatically with all team members. User-level is local-only. Subdirectory files are version-controlled but scoped to specific paths. There is no enterprise admin console scope."
),

# Q125 — correct was 'Run /memory to see which files are currently loaded' (52ch)
165: q(
    "You're seeing inconsistent code behavior across sessions, suspecting different memory files are loaded. First step:",
    [
        "Run <code>/memory</code> to see which CLAUDE.md files and memory files are currently loaded in the session context",
        "Delete all CLAUDE.md files in the project and recreate them — destructive; if the issue is a stale or conflicting file, this removes all project context, not just the problem",
        "Check <code>~/.claude/CLAUDE.md</code> first — while user-level config can cause cross-session inconsistencies, starting with /memory shows ALL loaded files, not just user-level ones",
        "Open a fresh session and compare behavior — useful for confirming the problem is session-specific, but doesn't reveal which files are causing the inconsistency",
    ],
    "/memory shows the complete list of loaded instruction files for the current session — it's the diagnostic first step. Deleting files is destructive without knowing which one is the problem. Checking only user-level config misses project and subdirectory files. A fresh session confirms the symptom but doesn't diagnose the cause."
),

# Q128 — correct was 'In the .claude/commands/ directory in the project repository' (59ch)
170: q(
    "You want to create a <code>/review</code> slash command that runs your team's standard code review checklist. Where does the command file go?",
    [
        "In the <code>.claude/commands/</code> directory in the project repository — project-scoped commands are version-controlled and automatically available to every team member",
        "In <code>~/.claude/commands/</code> on your personal machine — this creates a user-scoped command visible only to you; teammates must create their own copies",
        "In a <code>commands:</code> block within the root <code>CLAUDE.md</code> file — CLAUDE.md defines instructions and @imports, not executable slash command definitions",
        "As a YAML entry in <code>.mcp.json</code> under a <code>commands</code> key — .mcp.json registers MCP server configurations, not Claude Code slash commands",
    ],
    ".claude/commands/ is the project-level commands directory — files here are committed to version control and shared across the team. ~/.claude/commands/ is personal-only. CLAUDE.md manages instructions, not command files. .mcp.json registers MCP servers, not slash commands."
),

# Q65 — correct was 'claude --resume q4-payment-latency' (34ch)
85: q(
    "Your team uses Claude Code for week-long performance profiling investigations. Each investigation is named (e.g., 'q4-payment-latency'). The engineer returns after a weekend. Which is the correct approach to resume the investigation?",
    [
        "<code>claude --resume q4-payment-latency</code> — resumes the specific named session, restoring its full conversation history and accumulated tool results",
        "Save the final assistant message to a Markdown file and paste it as context at the start of a new session — this preserves only the last response, losing all intermediate tool calls and the investigative thread",
        "Start a fresh session each time — stale tool results from a week-old session may reference code that has since changed",
        "Use <code>fork_session</code> from the most recent checkpoint to create a named branch for the new week — fork_session is for divergent exploration, not for simply continuing a linear investigation after a break",
    ],
    "--resume <session-name> continues a specific named session across separate CLI invocations, restoring full context. Pasting the last message loses all prior tool results. Starting fresh discards valid prior findings. fork_session creates branches for divergent paths, not for resuming a single linear investigation."
),

# Q162 — correct was 'Address them sequentially in separate iterations' (47ch)
210: q(
    "For multiple INDEPENDENT issues, the recommended approach is:",
    [
        "Address each in a separate, focused iteration — independent issues can cause cross-contamination when combined; isolating them also makes it easier to attribute regressions",
        "Combine all issues into one comprehensive prompt and fix everything in a single pass — mixing independent issues increases context complexity and makes it harder to verify each fix individually",
        "Fix the highest-severity issue first, then re-evaluate whether the others still exist — useful for dependent issues, but independent ones don't cascade and don't require re-evaluation after each fix",
        "Open parallel sessions for each issue and merge the changes — parallel sessions risk conflicting edits to shared files; sequential isolation is the safer pattern",
    ],
    "Separate iterations for independent issues prevent cross-contamination and make each fix verifiable in isolation. Combining them into one prompt increases complexity and ambiguity. Re-evaluating after each fix makes sense for dependent issues, not independent ones. Parallel sessions risk merge conflicts."
),

# Q69 — correct was "The tool's description" (19ch)
95: q(
    "What is the primary mechanism LLMs use to decide which tool to call?",
    [
        "The tool's description — the model reads each tool's description to understand its purpose, when to use it, and what it accepts; this is the primary signal for tool selection",
        "The tool's parameter schema — while parameter types and names provide structural hints, the natural language description is the primary selection signal",
        "The order of tools in the tools array — research shows no reliable positional bias in tool selection; descriptions dominate over position",
        "The tool's name alone — names provide a coarse signal but are insufficient when multiple tools have semantically similar names; descriptions carry the deciding weight",
    ],
    "Tool descriptions are the primary mechanism LLMs use for selection — they provide the semantic context for when, why, and how to use each tool. Parameter schemas provide structural constraints. Tool position in the array has no reliable effect. Names are helpful but insufficient when tools are semantically similar."
),

# Q96 — correct was 'A dozen+ tools — selection degrades as decision complexity grows' (66ch)
126: q(
    "The number of tools that degrades selection reliability often kicks in around:",
    [
        "A dozen or more tools — as the decision space grows, the model's ability to consistently select the right tool degrades; beyond ~10-12 tools, reliability drops noticeably",
        "Two or three tools — selection is reliable with any number above two; the issue only appears when tools have identical names",
        "Exactly 20 tools — selection reliability is a step function: perfect below 20, unreliable above it",
        "The number of tools has no effect on selection reliability — the model's tool-selection quality depends entirely on description quality, not on the count",
    ],
    "Tool selection reliability degrades as count grows beyond roughly 10-12 — the model's decision space becomes too large for consistent disambiguation. Two or three tools don't degrade selection. There's no exact 20-tool cliff. Count matters; description quality alone can't compensate for an extremely large tool set."
),

# Q123 — correct was 'It references external files so CLAUDE.md stays modular' (57ch)
163: q(
    "Which is true about <code>@import</code> in CLAUDE.md?",
    [
        "@import references an external file — the referenced content is loaded into context; it keeps the main CLAUDE.md concise while allowing modular organization of instructions",
        "@import embeds the content of the referenced file inline at the import statement location during authoring — @import is a runtime reference, not a build-time embedding",
        "@import only works for files within the same directory as the CLAUDE.md that contains the import statement — @import can reference files at any path within the repository",
        "@import is processed by the Claude API during request handling, adding the referenced file's tokens to the system prompt — @import is processed by Claude Code, not the Anthropic API",
    ],
    "@import is a runtime reference: when Claude Code loads the CLAUDE.md, it reads the referenced file and includes its content in context. It's not inline embedding at authoring time. @import can reference files at paths beyond the current directory. Processing happens in Claude Code, not in the Anthropic API."
),

# Q167 — correct was '--output-format json together with --json-schema' (50ch)
217: q(
    "To enforce machine-parseable structured output for automated PR comments, the right CLI flag combination is:",
    [
        "<code>--output-format json</code> together with <code>--json-schema</code> — these flags together instruct Claude Code to output a JSON object conforming to the provided schema",
        "<code>--json</code> alone — this flag exists but only requests JSON formatting without a schema, so the output structure is not enforced",
        "<code>--format structured --schema pr-comments.json</code> — not valid Claude Code CLI flags; the correct flags are <code>--output-format</code> and <code>--json-schema</code>",
        "<code>--print</code> combined with a system prompt instruction to output JSON — the system prompt can request JSON but doesn't enforce schema compliance the way the CLI schema flag does",
    ],
    "--output-format json combined with --json-schema enforces schema-conformant structured output. --json alone requests JSON without schema enforcement. --format and --schema are not valid Claude Code flags. System prompt JSON requests are probabilistic; schema flags are enforced."
),

# Q152 — correct was 'Plan mode (to investigate, decide, and design)' (45ch)
198: q(
    "A library migration touches 45 files and has two viable integration strategies. The first step is:",
    [
        "Plan mode — to investigate the codebase, evaluate both strategies, and decide on the approach before any files are modified",
        "Direct execution on a sample file — start with one file to see which approach works before committing to a strategy across all 45",
        "Fork the session and run both strategies in parallel to compare outcomes — fork_session is for exploring divergent paths, not for deciding between strategies before acting",
        "Ask the model to estimate which strategy is better from the description alone, then directly execute that strategy across all 45 files",
    ],
    "Plan mode is correct when you need to investigate the codebase and decide between strategies before committing to changes across 45 files — it prevents costly rework. Direct execution on a sample is reasonable but skips the strategy-evaluation phase. Forking is for parallel exploration, not upfront decision-making. Asking for an estimate without investigation risks choosing the wrong strategy."
),

# Q156 — correct was 'It enables safe exploration and design comparison before committing' (69ch)
202: q(
    "You're choosing between integration approaches with different infrastructure requirements. Why is plan mode valuable here?",
    [
        "It enables safe exploration of both approaches and comparison of trade-offs before any infrastructure changes are made or code is modified",
        "It prevents Claude from consuming API tokens on implementation details before the approach is confirmed — plan mode uses fewer tokens than direct execution",
        "It forces the model to produce a spec document before writing code, ensuring downstream engineers understand the rationale",
        "It automatically forks the session so both approaches can be evaluated in parallel without affecting the main context",
    ],
    "Plan mode's core value is enabling exploration and comparison before commitment — especially important when approaches have different infrastructure requirements and the wrong choice is costly to reverse. Plan mode doesn't inherently use fewer tokens. It doesn't produce spec documents unless instructed. It doesn't automatically fork sessions."
),

# Q155 — correct was 'Direct execution — the scope is clear and limited' (44ch)
201: q(
    "For a date validation conditional being added to one function, the right mode is:",
    [
        "Direct execution — the scope is limited to one function in one file and the implementation is straightforward; no planning phase is needed",
        "Plan mode — to confirm the validation logic is consistent with other date validations in the codebase before implementing",
        "Plan mode followed by direct execution — use the planning phase to draft the conditional logic, then execute to insert it into the function",
        "A forked session — to test the conditional logic without affecting the main session's file state",
    ],
    "Direct execution is correct for small, well-scoped additions like a single function's validation logic — the task is clear and bounded. Plan mode is valuable for changes with uncertain scope or multiple viable approaches, not routine additions. Plan→direct adds unnecessary overhead for a known simple change. Forking is for divergent exploration."
),

# Q157 — correct was 'Spawn an Explore subagent that returns summaries to the main session' (69ch)
203: q(
    "In a multi-phase task, how can you avoid filling the main context with verbose codebase exploration output?",
    [
        "Spawn an Explore subagent that returns concise summaries to the main session — the subagent's verbose exploration stays in its isolated context; only the summary enters the main session",
        "Use <code>/compact</code> after each exploration phase to summarize and compress accumulated context before starting the next phase",
        "Write all exploration findings to a file and instruct the main session to read only the file rather than the raw tool output",
        "Increase <code>max_tokens</code> on each exploration call so the model finishes exploration before the main session fills",
    ],
    "Spawning an Explore subagent isolates verbose exploration output in the subagent's context — only the summary it returns enters the main session. /compact summarizes after the fact but loses precision. Writing to files adds round-trips and doesn't prevent the main session from processing the exploration output. max_tokens controls output length, not context accumulation."
),

# Q304 — correct was 'Subdirectory CLAUDE.md → Project CLAUDE.md → User CLAUDE.md' (52ch)
393: q(
    "In what order does CLAUDE.md scope apply (most specific to least)?",
    [
        "Subdirectory CLAUDE.md → Project CLAUDE.md → User CLAUDE.md — more specific (closer to the edited file) overrides less specific (farther away or global)",
        "User CLAUDE.md → Project CLAUDE.md → Subdirectory CLAUDE.md — applying global settings first before progressively narrowing to project-specific rules",
        "Project CLAUDE.md → User CLAUDE.md → Subdirectory CLAUDE.md — project rules take precedence over both user preferences and subdirectory overrides",
        "All scopes are applied simultaneously with equal priority; conflicts are resolved by the model based on relevance to the current task",
    ],
    "CLAUDE.md scope is hierarchical: subdirectory (most specific, closest to the file) → project root → user-level (most general). More specific scopes override less specific ones. The order is not reversed; global settings don't take precedence over project-specific ones. Scopes are not equal-priority."
),

# Q181 — correct was 'Inconsistent classification across runs on the same input' (58ch)
237: q(
    "Which is the strongest indicator that a prompt's specificity is insufficient?",
    [
        "Inconsistent classification on identical inputs across separate runs — when the same input produces different outputs, it signals the prompt leaves too much room for model interpretation",
        "The model produces longer outputs than expected — verbosity is often a sign of over-specification (too many instructions) rather than under-specification",
        "Claude asks clarifying questions before answering — questions typically indicate genuine ambiguity in the input, not a prompt design defect",
        "The model occasionally declines to answer — refusals are driven by safety guidelines or missing context, not by prompt specificity gaps",
    ],
    "Inconsistent outputs on identical inputs is the clearest signal that a prompt lacks specificity — the model fills the ambiguous space differently each run. Longer outputs suggest over-instruction. Clarifying questions reflect input ambiguity, not prompt design. Refusals are safety-driven, not specificity-driven."
),

# Q191 — correct was '2-4 examples' (12ch)
249: q(
    "The recommended number of targeted few-shot examples for an ambiguous scenario is roughly:",
    [
        "2–4 examples — enough to establish the boundary condition with representative positive and negative cases without overwhelming the prompt",
        "5–8 examples — fewer than 5 examples leaves too much ambiguity for boundary cases; more than 8 is still manageable and improves precision",
        "1–2 examples — a minimal example set is sufficient to demonstrate the pattern while preserving context budget for other instructions",
        "10 or more examples — the more examples, the more reliably the model generalizes the desired behavior and avoids edge cases",
    ],
    "2–4 targeted examples is the recommended range for clarifying ambiguous scenarios — enough to show positive and negative cases without consuming excessive context. 5–8 is more than needed for targeted boundary clarification. 1–2 may be insufficient to define boundaries. 10+ is overkill for targeted clarification and risks context waste."
),

# Q194 — correct was 'Tool use (tool_use) with a JSON schema as the input parameter' (68ch)
254: q(
    "For guaranteed schema-compliant structured output that eliminates JSON syntax errors, use:",
    [
        "Tool use (<code>tool_use</code>) with a JSON schema defined as the input parameter — the API enforces schema conformance on tool call arguments, making syntax errors impossible",
        "A system prompt instruction: 'Always output valid JSON conforming to this schema: ...' — provides guidance but doesn't enforce conformance; the model can still produce malformed JSON",
        "Setting <code>response_format: {\"type\": \"json_object\"}</code> in the request — requests JSON format but does not validate the output against a specific schema",
        "Post-processing the model's output with a JSON parser and retrying on parse failures — correct as a fallback but adds latency and doesn't prevent syntax errors at generation time",
    ],
    "Tool use with a JSON schema enforces schema compliance at the API level — tool call arguments are validated against the schema, making JSON syntax errors impossible. System prompt instructions are probabilistic. response_format: json_object requests JSON without schema validation. Post-processing is a fallback, not a prevention mechanism."
),

# Q150 — correct was 'Microservice restructuring across 45+ files' (47ch)
196: q(
    "Which task is best suited for plan mode?",
    [
        "Microservice restructuring across 45+ files — high complexity, broad impact, and multiple viable approaches make plan mode essential before committing to changes",
        "Adding a null check to a single function — well-scoped, unambiguous, and confined to one location; direct execution is appropriate",
        "Renaming a local variable within a method — single-file, atomic, no architectural decisions needed; no planning value",
        "Fixing a typo in a string constant — trivial scope with zero ambiguity; plan mode would add unnecessary overhead with no benefit",
    ],
    "Microservice restructuring benefits from plan mode: the scope is broad, the impact is high, and the approach may not be obvious upfront. Null checks, variable renames, and typo fixes are all bounded, unambiguous tasks where plan mode adds overhead without benefit."
),

# Q251 — correct was 'What was attempted, partial results, and potential alternatives' (65ch)
327: q(
    "Subagents should implement local recovery for transient failures and propagate only:",
    [
        "What was attempted, partial results obtained, and potential alternative approaches — giving the coordinator the information it needs to decide next steps without re-running work already done",
        "A generic error code and status field — minimal error payloads force the coordinator to re-run the subagent entirely without the context needed to adapt the approach",
        "The full exception stack trace and raw tool output — useful for debugging but too verbose for coordinator decision-making; structured summaries are more actionable",
        "Nothing — coordinators should implement their own health checks and detect subagent failures by timeout rather than waiting for subagent error reports",
    ],
    "Propagating what was attempted, partial results, and alternatives gives the coordinator actionable context for recovery decisions — it can retry differently, use the partial results, or skip the failed task. Generic error codes lose context. Raw stack traces are too verbose. Silent failures by timeout prevent informed recovery."
),

# Q254 — correct was 'An anti-pattern — partial recovery and annotated gaps are preferable' (68ch)
330: q(
    "Terminating an entire multi-agent workflow on a single subagent failure is:",
    [
        "An anti-pattern — coordinators should attempt partial recovery, annotate gaps, and continue where possible rather than discarding all completed work",
        "Best practice — a workflow with any failure is unreliable; it's better to restart from scratch with a clean state than to synthesize partial results",
        "Required by the Agent SDK — the SDK automatically terminates a coordinator when any spawned subagent returns an error status",
        "Appropriate only for financial workflows — non-critical pipelines should tolerate partial failures, but monetary operations must terminate on any subagent error",
    ],
    "Aborting the full workflow on a single failure discards all completed subagents' work unnecessarily. The recommended pattern is partial recovery: annotate which parts failed, use available results, and retry only the failed components. The SDK doesn't enforce termination. Blanket termination for financial workflows ignores the availability of partial recovery with appropriate safeguards."
),

# Q291 — correct was 'Address each in a separate iteration to isolate cause/effect' (65ch)
379: q(
    "You have three independent bugs to fix. The recommended pattern is:",
    [
        "Fix each bug in a separate iteration so changes are isolated — this makes it easy to attribute any unexpected behavior to the specific fix that introduced it",
        "Fix all three in a single pass to reduce the number of API calls and review cycles",
        "Fix them in order of estimated difficulty, combining the two simplest into one pass to save time",
        "Delegate all three bugs to parallel subagents that each make their own changes, then merge the results",
    ],
    "Separate iterations isolate cause and effect — if an unexpected regression appears, you know exactly which fix introduced it. Combining independent fixes in a single pass makes attribution ambiguous. Difficulty-based batching still mixes changes. Parallel subagents risk conflicting edits to shared code."
),

# Q298 — correct was '<code>Grep</code> — search file contents for the function name' (52ch)
387: q(
    "For finding all callers of a specific function, the recommended built-in tool is:",
    [
        "<code>Grep</code> — searches file contents across the codebase for the function name by pattern, returning all matching locations",
        "<code>Glob</code> — matches files by name pattern, useful for finding files named after the function but not for finding where it's called within file contents",
        "<code>Read</code> on each file — loads complete file contents for manual inspection, but requires iterating through every file individually rather than searching in one pass",
        "<code>Edit</code> — uses text matching as part of replacement operations; not designed for search-only operations across a codebase",
    ],
    "Grep searches file contents by pattern — the right tool for locating all callers of a function across a codebase. Glob matches filenames, not content. Read loads individual files; it can't efficiently search across many files. Edit uses matching for replacement, not as a standalone search."
),

# Q299 — correct was '**/*.tsx (or **/components/**/*.tsx depending on layout)' (57ch)
388: q(
    "A rule should apply to React component files anywhere in the repo. The path glob pattern is:",
    [
        "<code>**/*.tsx</code> (or <code>**/components/**/*.tsx</code> if components are in dedicated directories) — these patterns match .tsx files at any directory depth",
        "<code>/*.tsx</code> — this matches only .tsx files at the repository root; the leading <code>*</code> without <code>**</code> doesn't recurse into subdirectories",
        "<code>src/**</code> — this matches all files under src/ but doesn't filter to .tsx extension; it would load the rule for non-component files too",
        "<code>components/*.tsx</code> — this matches .tsx files only in a top-level components/ directory, missing nested or differently organized component trees",
    ],
    "**/*.tsx matches all .tsx files at any depth in the repository. /*.tsx matches only at the root. src/** is too broad (no extension filter). components/*.tsx is too narrow (no recursive matching for nested structures)."
),

# Q170 — correct was 'Provide existing test files in context so generation avoids duplication' (79ch)
220: q(
    "Test generation in CI keeps suggesting scenarios already covered. The recommended fix is:",
    [
        "Provide existing test files in context so the agent can identify covered scenarios before generating new ones",
        "Set the temperature to 0 to make generation more deterministic and reduce the chance of suggesting duplicate scenarios",
        "Use a post-processing deduplication step to filter out scenarios that match existing test descriptions",
        "Regenerate the test suite from scratch to ensure a coherent, non-redundant set of scenarios",
    ],
    "Providing existing test files in context gives the agent the information it needs to avoid duplication — it can see what's covered before generating. Temperature 0 reduces variance but doesn't prevent duplication if the model lacks context about existing tests. Post-processing deduplication is a fallback, not a root-cause fix. Regenerating from scratch discards valid existing tests."
),

# Q235 — correct was 'Trim verbose tool outputs to only the relevant fields before they accumulate' (80ch)
307: q(
    "A tool returns 40+ fields per order lookup, but only 5 are relevant. What should the architect do?",
    [
        "Trim the tool output to the 5 relevant fields before returning results to the model — prevents the irrelevant data from accumulating in context across repeated calls",
        "Increase the context window by upgrading to a higher-tier model — more context capacity allows the verbose output to fit, but doesn't prevent context degradation from irrelevant tokens",
        "Ask the model to ignore the irrelevant fields in its reasoning — the model still processes all 40 fields even when told to ignore them; the tokens still consume context",
        "Cache the tool result and reuse it across turns to avoid repeated context accumulation from multiple lookup calls",
    ],
    "Trimming at the tool layer removes irrelevant data before it enters context — the correct architectural fix. A larger context window accommodates the noise but doesn't eliminate it. Instructing the model to ignore fields doesn't prevent those tokens from consuming context. Caching reduces the number of calls but doesn't fix the per-call context overhead."
),

# Q303 — correct was 'Unreliable tool selection — especially when similar tools exist' (63ch)
392: q(
    "A vague tool description leads to:",
    [
        "Unreliable tool selection — especially when similar tools coexist; without clear descriptions, the model cannot consistently choose the right tool",
        "Slower API response times — the model spends more inference time reasoning about tool choices when descriptions are ambiguous",
        "Higher hallucination rates in tool outputs — vague descriptions affect tool selection, not the accuracy of the data tools return",
        "Schema validation failures — tool descriptions don't affect parameter validation; schema errors come from incorrect parameter types, not description quality",
    ],
    "Vague descriptions cause unreliable tool selection — the model picks the wrong tool when it can't differentiate similar tools by description. API response time is not meaningfully affected by description quality. Hallucinations in outputs are driven by model and data issues, not description clarity. Schema validation is independent of descriptions."
),

# Q73 — correct was 'Keyword-sensitive instructions in the system prompt that bias tool selection' (78ch)
99: q(
    "Even with well-written tool descriptions, your model still sometimes ignores the right tool. The next most common cause is:",
    [
        "Keyword-sensitive instructions in the system prompt that bias the model toward general or conversational responses over tool calls",
        "The order of tools in the tools array — the model systematically prefers tools listed first and ignores later entries",
        "Token budget limits in the API request — when max_tokens is low, the model skips tool calls to conserve output space",
        "A mismatch between the tool's parameter types and the model's internal type inference for the request",
    ],
    "System prompt keyword sensitivity is the next most common cause after description quality — instructions like 'be helpful and conversational' can bias the model away from structured tool calls. Tool order in the array has no reliable effect on selection. Token budget constraints don't cause tool selection failures. Parameter type mismatches cause tool call errors, not tool selection failures."
),

# Q154 — correct was 'Costly rework due to making changes before understanding the codebase' (69ch)
200: q(
    "Plan mode primarily prevents which class of problem?",
    [
        "Costly rework from committing to changes before the codebase structure and implications are understood",
        "API timeout errors from long-running direct execution sessions that exceed request limits",
        "Context window overflow from accumulating too many tool results during implementation",
        "Model hallucinations about code that doesn't exist — plan mode verifies assumptions before any file reads occur",
    ],
    "Plan mode's primary purpose is preventing costly rework — it allows the agent to map the codebase and evaluate approaches before modifying any files. API timeouts are unrelated to mode. Context accumulation is managed by other mechanisms. Plan mode doesn't prevent hallucinations; it prevents premature changes."
),

# Q90 — correct was '{"type": "tool", "name": "extract_metadata"} — forced selection' (72ch)
120: q(
    "To ensure <code>extract_metadata</code> is the FIRST tool called in a workflow, which <code>tool_choice</code> setting guarantees this on the first API call?",
    [
        "<code>{\"type\": \"tool\", \"name\": \"extract_metadata\"}</code> — forces the model to call this specific tool and no other on this request, guaranteeing it runs first",
        "<code>\"any\"</code> — forces a tool call but lets the model choose which tool; it might call an enrichment tool instead of <code>extract_metadata</code>",
        "<code>\"auto\"</code> — the model decides which tool to call based on context; it may or may not call <code>extract_metadata</code> first",
        "A system prompt instruction: 'Always call <code>extract_metadata</code> before any other tool' — probabilistic compliance; the model may deviate under complex inputs",
    ],
    "{\"type\": \"tool\", \"name\": \"extract_metadata\"} forces exactly that tool on that request — guaranteed first call. \"any\" forces some tool but doesn't specify which. \"auto\" gives the model full discretion. System prompt instructions are probabilistic."
),

# ═══════════════════════════════════════════════════════════
# LONG-CORRECT / SHORT-DISTRACTOR FIXES
# Distractors rewritten to be substantive and plausible
# ═══════════════════════════════════════════════════════════

# Q208 — distractors were 'A random UUID', 'Author name', 'Filename only'
270: q(
    "To enable systematic analysis of false-positive triggers, the structured findings should include:",
    [
        "A <code>detected_pattern</code> field describing the code construct that triggered the finding — this enables engineers to aggregate and analyze which patterns drive false positives",
        "A <code>confidence_score</code> field from 0.0 to 1.0 — numeric confidence helps route findings for review but doesn't explain which patterns are causing misclassifications",
        "A <code>suggested_fix</code> field with an auto-generated remediation — actionable but doesn't help diagnose why the finding was triggered in the first place",
        "A <code>line_count</code> field for the affected code block — contextual metadata but doesn't capture the semantic construct that caused the false positive",
    ],
    "A detected_pattern field records what the model observed that triggered the finding — this is the key to systematic false-positive analysis. Without knowing what code construct fired, you can't identify which patterns produce noise. Confidence scores route findings but don't explain triggers. Suggested fixes and line counts are supplementary, not diagnostic."
),

# Q268 — distractors were 'Random sampling', 'Document size', 'Document language'
348: q(
    "You want to route ambiguous or contradictory source documents to human review. What's the best signal?",
    [
        "A model-emitted <code>conflict_detected</code> or <code>low_confidence</code> indicator at the field or document level — the model that processed the document is best positioned to flag its own uncertainty",
        "A word-count threshold — routing all documents above a certain length assumes longer documents are more ambiguous, which is not reliably true",
        "Presence of numeric data — flagging all documents with numbers for human review is too broad and would route most financial or scientific documents regardless of clarity",
        "Processing timestamp — using time of day or document age as a routing signal has no relationship to document ambiguity or contradictions",
    ],
    "Model-emitted uncertainty flags (conflict_detected, low_confidence) are the most reliable routing signal — the model that processed the document is best positioned to report where it encountered contradictions or lacked confidence. Word count, numeric data presence, and timestamps are unrelated to actual document ambiguity."
),

# Q275 — distractors were 'Always as prose', 'Always as JSON', 'Always as bullet lists'
357: q(
    "In a synthesis output, financial data and news content should be rendered:",
    [
        "According to content type — financial data as structured tables, news as prose narrative, technical findings as code or structured lists",
        "Always as prose narrative — uniform prose format simplifies downstream parsing but obscures the structure of financial data and makes tables unreadable",
        "Always as machine-readable JSON — consistent JSON output aids programmatic processing but produces unreadable synthesis reports for human reviewers",
        "Always as bullet lists regardless of content type — uniform bullet formatting loses the relational structure of financial tables and the narrative flow of news content",
    ],
    "Rendering by content type preserves the natural structure of each content category: financial data as tables (for comparison), news as prose (for narrative), technical findings as structured lists. Forcing all content into a single format — prose, JSON, or bullets — either loses structure or produces unreadable outputs for at least one content type."
),

# Q290 — distractors were 'tool_choice: "any"', 'Force-call a summary tool', 'Use plan mode'
378: q(
    "For a synthesis subagent that should produce text and never call tools (output only), the correct constraint is:",
    [
        "Restrict <code>allowedTools</code> to an empty set — removing all tools from the subagent's definition makes it impossible to call any tools, regardless of what the system prompt requests",
        "<code>tool_choice: \"any\"</code> — this forces the model to call at least one tool every turn, which is the opposite of what's needed for a text-only output subagent",
        "A system prompt instruction: 'Only produce text output; never call tools' — probabilistic; the model may still emit tool calls under certain inputs if tools are available",
        "Use plan mode — plan mode controls whether files are modified before planning, not whether tool calls can be made during execution",
    ],
    "An empty allowedTools set is the deterministic constraint — with no tools registered, the model cannot call any tools regardless of instructions. tool_choice: \"any\" mandates tool calls, the opposite of the goal. System prompt prohibitions are probabilistic. Plan mode controls execution safety, not tool availability."
),

# Q218 — distractors were 'By order of arrival', 'By IP address', 'By message hash'
282: q(
    "How do you correlate a batch response back to its original request?",
    [
        "By the <code>custom_id</code> field — included in each request and returned with each response, enabling reliable mapping between submissions and results",
        "By response order — batch results are not guaranteed to return in submission order; relying on position would silently misassign responses when the order shifts",
        "By response timestamp — multiple requests in a batch may complete at the same millisecond, making timestamp-based correlation ambiguous",
        "By content similarity — matching responses to requests by semantic similarity introduces errors when requests have similar content and is not a reliable programmatic approach",
    ],
    "custom_id is the supported correlation mechanism: you assign a unique ID to each request when submitting, and the batch API returns that same ID with the corresponding result. Response order is not guaranteed. Timestamps are not unique within a batch. Content similarity is error-prone and non-deterministic."
),

# Q219 — distractors were vague single phrases
283: q(
    "You have an SLA requiring 30-hour processing for a large batch. How should you schedule submissions?",
    [
        "Submit batches on a staggered schedule (e.g., every 4 hours) so each batch's 24-hour processing window completes before its downstream deadline",
        "Submit all requests in a single batch at the start of the window — a single large batch maximizes throughput but risks missing the SLA if the 24-hour window starts late",
        "Submit requests only during business hours — the batch API processes continuously; restricting to business hours wastes the processing window and reduces effective throughput",
        "Submit small batches every hour to ensure freshness — very frequent small batches fragment work unnecessarily and don't leverage the batch API's cost efficiency for large volumes",
    ],
    "Staggered submission ensures each batch's worst-case 24-hour window fits within the 30-hour SLA. One large batch risks SLA failure if processing starts near the deadline. Business-hours-only submission wastes the available processing window. Hourly micro-batches fragment the workload without improving latency."
),

# Q220 — distractors were 'Resubmit the entire batch', 'Drop the failed items', 'Switch to synchronous'
284: q(
    "Some batch requests fail. What's the right recovery?",
    [
        "Identify failed items by <code>custom_id</code> and resubmit only those, with appropriate modifications if the failure was due to invalid inputs",
        "Resubmit the entire batch — re-running successful requests wastes API budget and potentially inflates costs for results you already have",
        "Drop failed items and proceed with partial results — acceptable for non-critical pipelines but not for cases where complete coverage is required",
        "Switch the failed items to synchronous API calls for immediate retry — synchronous calls have different rate limits and higher per-token cost, making this inefficient for batch-scale recovery",
    ],
    "Targeted resubmission by custom_id is the correct recovery pattern — retry only what failed, preserving the work already completed. Resubmitting the full batch wastes budget on successes. Dropping failed items produces incomplete results. Switching to synchronous for recovery loses batch pricing advantages."
),

# Q221 — distractors were 'Submit everything at once for speed', 'Run a load test', 'Disable retries'
285: q(
    "Before batch-processing large volumes, what's the recommended preparation step?",
    [
        "Refine prompts on a small sample first — maximizing first-pass success rates avoids costly iterative resubmissions across the full volume",
        "Submit the full volume immediately — faster time-to-start, but prompt issues discovered mid-batch require reprocessing large numbers of items",
        "Run a synthetic load test against the batch endpoint — load testing verifies throughput but doesn't validate prompt quality or output correctness on real inputs",
        "Disable retries to measure the raw first-pass success rate — disabling retries produces a metric but at the cost of failing items that would otherwise recover",
    ],
    "Prompt refinement on a small sample catches issues before they compound across large volumes. Submitting immediately risks discovering prompt problems after many items have been processed incorrectly. Load testing validates infrastructure, not prompt quality. Disabling retries provides a quality metric but unnecessarily fails recoverable items."
),

# Q260 — distractors were 'Start with empty context', 'Re-read every file', 'Reset the session'
338: q(
    "Before spawning sub-agents for a new exploration phase, what's the recommended preparation step?",
    [
        "Summarize key findings from the prior phase and inject the summary into the sub-agents' initial context — prevents redundant re-exploration and gives sub-agents a coherent starting point",
        "Start sub-agents with completely empty context — clean state avoids bias from prior findings, but also requires each sub-agent to re-discover baseline facts already established",
        "Pass the entire prior session transcript as each sub-agent's context — comprehensive but likely to overflow context limits and dilute the sub-agent's focus with irrelevant intermediate steps",
        "Let sub-agents inherit context automatically from the coordinator — sub-agents in Claude Code have isolated context; they do not automatically inherit the coordinator's conversation history",
    ],
    "Injecting a targeted summary of prior findings gives sub-agents the essential context they need without re-running previous work or overloading context with verbose exploration output. Empty context wastes exploration capacity on re-discovery. Full transcripts overflow context. Sub-agent context inheritance is not automatic."
),

# Q187 — distractors were 'Only flagged issues', 'Only acceptable patterns', 'Random samples'
245: q(
    "You're providing few-shot examples to reduce false positives. What should the examples include?",
    [
        "Both acceptable patterns AND genuine issues, with reasoning — so the model learns the distinction, not just one side of the boundary",
        "Only confirmed flagged issues — the model learns what to flag but not what to accept; it will over-flag because it has no representation of acceptable patterns",
        "Only acceptable patterns — the model learns what to pass through but not what to flag; it will under-flag because it has no representation of genuine issues",
        "A random sample from the dataset regardless of label — random samples may not include examples near the decision boundary where the model needs the most guidance",
    ],
    "Both positive (genuine issues) and negative (acceptable patterns) examples with reasoning teach the model the decision boundary — not just one side. Only flagged examples produce over-flagging. Only acceptable examples produce under-flagging. Random samples may not include the boundary cases that most need illustration."
),

# Q210 — distractors were 'A free-text notes field only', 'No special handling', 'A priority field'
272: q(
    "For inconsistent source data, a useful schema addition is:",
    [
        "A <code>conflict_detected: boolean</code> field that the model sets when it finds inconsistencies in the source — enables automated routing and downstream reconciliation without losing either conflicting value",
        "A free-text <code>notes</code> field where the model describes the inconsistency — captures the issue but in an unstructured form that's hard to process programmatically",
        "A <code>confidence: float</code> field without a conflict flag — numeric confidence indicates uncertainty but doesn't explicitly signal that two conflicting values exist in the source",
        "A <code>source_count: int</code> field recording how many sources were consulted — quantifies coverage but doesn't indicate whether sources agree or conflict",
    ],
    "A machine-actionable conflict_detected boolean enables automated routing of inconsistent records for human review without losing either conflicting value. Free-text notes are unstructured and hard to process programmatically. A confidence float indicates uncertainty but doesn't explicitly flag contradictions. Source count measures coverage, not consistency."
),

# Q212 — distractors were 'They are easier to detect', 'They cannot be retried', 'They are caused by max_tokens'
274: q(
    "Semantic validation errors (e.g., wrong field placement, totals not summing) differ from syntax errors in that:",
    [
        "They require business-logic validation; strict JSON schemas via tool use eliminate syntax errors but cannot verify that a total field actually matches the sum of its line items",
        "They are easier to detect than syntax errors — semantic errors are harder to detect because they require understanding business rules, not just parsing structure",
        "They cannot be retried with a corrected prompt — semantic errors can be addressed by retry with specific error context; the retry pattern applies to both types",
        "They only occur when the model exceeds its token limit — token limits cause truncation, not semantic mismatches between related fields",
    ],
    "Semantic errors require business-logic validation beyond what JSON schema enforcement provides — a syntactically valid JSON document can still have totals that don't sum or fields in wrong positions. Semantic errors are harder to detect than syntax errors, not easier. Both can be retried. Token limits cause truncation, not semantic inconsistencies."
),

# Q213 — distractors were 'Tokens are cheaper that way', 'It satisfies API requirements', 'It enables logging'
275: q(
    "Why is including the original document in a retry request important?",
    [
        "The model needs the source to re-extract correctly — a retry with only the failed extraction result lacks the ground truth the model needs to identify and correct the error",
        "The batch API requires the original document in retry requests — the API doesn't enforce this; it's a best practice, not a technical requirement",
        "Retrying without the original document counts against rate limits differently — rate limits are based on tokens and request counts, not on whether source documents are included",
        "Including the document provides the model with more tokens to work with, improving extraction quality — it's not the token increase but the source reference that matters",
    ],
    "The model needs the original source document to re-extract correctly — the failed extraction result alone doesn't contain the source text the model needs to correct the error. The API doesn't technically require the original document. Rate limits are not affected by document inclusion. It's the source reference, not the added tokens, that improves retry quality."
),

# Q202 — distractors were 'Semantic errors', 'Model from hallucinating', 'Network failures'
262: q(
    "Strict JSON schemas via tool use prevent:",
    [
        "Syntax errors in the JSON output — missing braces, wrong value types, malformed strings, and structural issues are prevented at the API level by schema enforcement",
        "Semantic errors where field values are logically incorrect — a schema can enforce that a field is a number, but not that it equals the sum of other fields",
        "Model hallucinations in extracted content — schema enforcement validates structure, not factual accuracy; the model can still return a valid-schema response with fabricated values",
        "Downstream application crashes from unexpected field names — schema enforcement at generation time prevents undefined fields, but this is a consequence of preventing syntax/structure errors, not a distinct category",
    ],
    "Strict schemas via tool use prevent syntax and structural errors — the API validates that the model's output matches the defined schema. They don't prevent semantic errors (logically wrong values), factual hallucinations (structurally valid but invented content), or network failures."
),

# Q209 — distractors were 'Force the model to recompute', 'Reject the document silently', 'Hide the discrepancy'
271: q(
    "A document has a stated total of $1000 but line items sum to $950. The model fills in both fields. What's the right extraction approach?",
    [
        "Extract both <code>calculated_total</code> and <code>stated_total</code>, and flag the discrepancy — preserves both values and surfaces the inconsistency for downstream reconciliation",
        "Force the model to recompute and resolve the discrepancy before returning — the model performing arithmetic on source data introduces the risk of choosing the wrong value or hallucinating a reconciliation",
        "Return only the stated total, treating the document's explicit value as authoritative — discards the discrepancy signal and the calculated figure, which may be the correct one",
        "Return only the calculated total as the more reliable value — the stated total is explicit source data; discarding it loses potentially important provenance information",
    ],
    "Extracting both values and flagging the discrepancy preserves all source data and enables human reconciliation. Forcing the model to resolve the discrepancy risks choosing the wrong value. Returning only the stated or only the calculated total discards a value that may be correct and loses the inconsistency signal."
),

# Q272 — distractors were 'Strip all dates', 'Use only the most recent data', 'Use only the oldest data'
354: q(
    "To prevent temporal differences (e.g., 2023 vs 2024 data) from being misinterpreted in synthesis:",
    [
        "Include publication or collection dates in structured outputs — downstream agents can then filter, compare, or contextualize findings by time period",
        "Strip all dates from the output and present findings as timeless facts — removes temporal context needed for correct interpretation; a 2023 regulatory finding may no longer be valid",
        "Filter to only the most recent data before synthesis — newer data is not always more relevant; older authoritative sources may carry more weight for certain analyses",
        "Merge all sources into a single time-aggregated summary — aggregation without temporal tracking is precisely what causes temporal misinterpretation",
    ],
    "Including dates preserves temporal provenance so downstream agents can correctly interpret findings relative to time periods. Stripping dates removes the context needed to identify temporal conflicts. Filtering to only recent data discards potentially valid older sources. Time-aggregated summaries without date tracking cause the misinterpretation problem this pattern is designed to prevent."
),

# Q274 — distractors were 'Plain prose summaries', 'Only the source URLs', 'Only the citations'
356: q(
    "For multi-source synthesis, subagents should be required to output:",
    [
        "Structured claim-source mappings — each finding paired with its source document, URL, or excerpt so the synthesis agent can verify provenance and detect contradictions across sources",
        "Plain prose summaries — human-readable but unstructured; the synthesis agent cannot programmatically match claims to sources or detect when two prose summaries contradict each other",
        "Source URLs only without content — provides attribution but not the claim content or excerpt needed for the synthesis agent to evaluate relevance or identify conflicts",
        "A single consolidated paragraph per subagent — discards the source-level structure needed for cross-source verification and makes contradiction detection impossible",
    ],
    "Structured claim-source mappings give the synthesis agent verifiable provenance: it can match claims to sources, detect contradictions between sources, and produce attributed outputs. Plain prose, URL-only lists, and consolidated paragraphs all lose the claim-level structure needed for reliable multi-source synthesis."
),

# Q284 — distractors were 'Switch to batch', 'Use both APIs simultaneously', 'Use no API and run locally'
371: q(
    "You're considering switching pre-merge linting from synchronous to batch API for cost savings. Should you?",
    [
        "No — pre-merge checks are blocking; developers wait for results before merging, and the batch API's 24-hour processing window violates the latency requirements of a blocking workflow",
        "Yes — the batch API costs 50% less per token, so switching linting to batch reduces CI costs without affecting developers",
        "Yes, but only for style checks — security and correctness checks remain synchronous since they're blocking, while style is informational",
        "Yes — run both APIs in parallel and return whichever responds first, combining the batch cost savings with synchronous latency guarantees",
    ],
    "Pre-merge linting is a blocking workflow: developers need results before they can merge. The batch API processes requests within 24 hours — incompatible with this latency requirement. Cost savings are irrelevant if the workflow breaks. Splitting by check type still blocks on some checks, and 'run both' doesn't work since batch responses aren't immediate."
),

# Q278 — distractors were 'isError: true', 'An exception', 'An empty string'
364: q(
    "For an MCP tool that returns information about a single record, what's the right response when no record is found?",
    [
        "A successful response with an explicit empty result — a null or empty structured object signals 'not found' as a normal outcome without triggering the model's error-handling path",
        "An <code>isError: true</code> response with a 'record not found' message — treating absence as an error causes the model to enter error-recovery mode for a normal, expected outcome",
        "Raise an exception in the tool implementation — unhandled exceptions surface as tool errors to the model, again triggering error-recovery behavior for what should be a normal case",
        "Return a dummy record with placeholder values — fabricating data prevents the model from knowing the record doesn't exist, leading to downstream reasoning on invented content",
    ],
    "A successful empty result correctly signals 'not found' as a normal, expected outcome — the model can handle it with normal logic rather than entering error recovery. isError: true and exceptions both trigger error handling for a situation that isn't an error. Returning dummy data fabricates facts the model will reason on."
),

# Q230 — distractors were placeholder phrases
296: q(
    "Requiring developers to manually split their PRs into smaller submissions to fit review context limits is:",
    [
        "An architectural anti-pattern — it shifts review-system complexity onto developers who must manually restructure their work; a well-designed review pipeline should handle decomposition internally",
        "The recommended approach — smaller PRs improve review quality and are a standard software engineering best practice regardless of the reviewing system",
        "Required by the Claude Code review API — the API doesn't mandate PR size; context limits can be managed through multi-pass review architecture without developer intervention",
        "Equivalent to a multi-pass review — multi-pass review splits analysis across multiple API calls; requiring developers to split PRs is a workflow burden, not an equivalent technical solution",
    ],
    "Manual PR splitting is an anti-pattern because it imposes architectural constraints on developers rather than solving the problem at the review system level. Multi-pass review handles large PRs internally through per-file passes plus integration passes. Smaller PRs are a general best practice but not the right solution to review system context limits."
),

# Q241 — distractors were placeholder phrases
315: q(
    "A customer is frustrated about a return that the agent CAN process within policy. What's the right response?",
    [
        "Acknowledge the frustration, offer to resolve the return since it's within policy, and escalate only the emotional component if the customer remains upset after resolution",
        "Silently process the return without acknowledging the frustration — resolves the issue but ignores the customer's emotional state, which is an escalation trigger",
        "Escalate immediately to a human agent — appropriate if the return were outside policy, but escalating a solvable in-policy request wastes human resources unnecessarily",
        "Process the return and send a satisfaction survey afterward — deferring acknowledgment to a post-interaction survey doesn't address the frustration during the interaction",
    ],
    "The right response combines resolution (the return is solvable) with acknowledgment (the customer is frustrated). Silent processing ignores the emotional trigger. Immediate escalation is appropriate for out-of-policy requests, not solvable ones. Post-interaction surveys don't address frustration in the moment."
),

# Q229 — distractors were too vague
295: q(
    "Which is true about multi-pass review architectures?",
    [
        "Splitting large reviews into per-file passes plus a separate cross-file integration pass produces more consistent depth than reviewing the full changeset in one pass",
        "Running a single comprehensive pass always produces higher quality than splitting — a single pass maintains context about the full changeset, whereas splits lose cross-file relationships",
        "Running identical passes five times and majority-voting the results is more accurate than a targeted multi-pass approach — repetition without structure amplifies noise rather than improving precision",
        "Static analysis tools make multi-pass review redundant — static analysis handles syntax and pattern detection; multi-pass review adds semantic and architectural review that static tools can't perform",
    ],
    "Per-file passes plus a cross-file integration pass consistently outperform single-pass review because each pass can focus attention fully — local issues don't compete with cross-file concerns. A single pass suffers from attention dilution across large changesets. Majority voting on identical passes doesn't fix the dilution problem. Static analysis complements but doesn't replace LLM review for semantic issues."
),

# Q269 — distractors were too vague
349: q(
    "For calibrating field-level confidence scores, you should:",
    [
        "Map model confidence to actual accuracy using a labeled validation set — raw model confidence is uncalibrated; calibration reveals the true accuracy at each confidence level",
        "Use the model's raw confidence output directly as a routing threshold — raw confidence is systematically biased and doesn't reliably reflect actual accuracy without calibration",
        "Apply a fixed threshold of 0.5 across all field types — a universal threshold ignores that different fields have different base rates and error distributions",
        "Set the threshold based on business risk tolerance alone without measuring empirical accuracy — risk tolerance informs the decision but must be applied to calibrated accuracy curves, not raw scores",
    ],
    "Calibration against a labeled validation set converts raw model confidence into meaningful accuracy estimates — without calibration, 0.9 confidence might correspond to 70% actual accuracy. Raw confidence is unreliable. A fixed 0.5 threshold ignores field-level accuracy variance. Risk tolerance sets the policy but requires calibrated accuracy data to apply correctly."
),

# Q273 — distractors were too short
355: q(
    "Synthesis reports should:",
    [
        "Distinguish well-established findings from contested ones, preserving original source context and confidence levels rather than presenting all findings as equally certain",
        "Present all findings as equally certain to avoid confusing readers with uncertainty qualifications — flattening confidence differences hides important reliability distinctions",
        "Drop contested findings to maintain a coherent, definitive narrative — contested findings often represent the most important areas of uncertainty and should be surfaced, not suppressed",
        "Drop well-established findings to focus the report on unresolved questions — established findings provide the baseline context needed to interpret contested ones",
    ],
    "Synthesis reports should preserve the confidence hierarchy from the source data — well-established findings versus contested ones carry different weights. Presenting all findings as equally certain flattens important distinctions. Dropping contested or established findings both lose critical information: contested findings reveal uncertainty, established findings provide context."
),

# Q297 — distractors were too short
386: q(
    "Your synthesis output erases publication dates from individual findings to create a cleaner report. Why is this a problem?",
    [
        "Downstream agents and readers cannot tell whether a finding reflects 2023 or 2024 conditions — temporal context is often essential for correctly interpreting regulatory, market, or scientific claims",
        "Publication dates are required metadata under most data retention policies — compliance is a valid concern, but the core problem is interpretability, not regulatory compliance",
        "Removing dates increases the synthesis report's token count because the model must add caveats — date removal actually reduces token count; the issue is loss of provenance, not token efficiency",
        "The synthesis model needs dates to sort findings chronologically in the output — sorting is a presentation concern; the deeper issue is that readers can't assess whether findings are still current",
    ],
    "Erasing publication dates removes temporal context that's essential for correct interpretation — a regulatory finding from 2023 may be superseded by 2024 changes. Compliance and sorting are secondary concerns. The core issue is that readers and downstream systems cannot assess the currency or validity of findings without knowing when they were produced."
),

# Q296 — distractors were too short
385: q(
    "A junior engineer creates a fixed five-step pipeline for debugging unknown errors. What's the architectural problem?",
    [
        "Fixed pipelines cannot adapt to what's discovered — in open-ended debugging, each finding should reshape the next step; a hardcoded sequence continues regardless of what the prior step revealed",
        "Five steps is too few for thorough debugging — the number of steps is not the core problem; the issue is that steps are fixed rather than adaptive",
        "Fixed pipelines are slower than dynamic ones — performance isn't the concern; a fixed pipeline may reach a wrong conclusion quickly rather than a right one slowly",
        "The model cannot follow more than three sequential instructions reliably — sequential instructions are not inherently unreliable; the problem is the inability to branch based on findings",
    ],
    "Fixed pipelines can't adapt to intermediate discoveries — in debugging, what you find in step 2 determines what step 3 should be, not a predetermined sequence. The problem isn't the number of steps, speed, or instruction-following reliability; it's the inability to reshape the investigation based on findings."
),

# Q265 — distractors were too short
345: q(
    "To detect novel error patterns in high-confidence extractions, the recommended approach is:",
    [
        "Stratified random sampling of high-confidence extractions for periodic human review — novel errors concentrate in this tier precisely because the model's confidence prevents them from reaching review through standard routing",
        "Reviewing only low-confidence extractions — novel errors in high-confidence extractions are invisible to low-confidence routing; sampling only the uncertain tier misses the silent failure mode",
        "Reviewing a fixed 1% random sample regardless of confidence level — flat random sampling can work but doesn't specifically target the high-confidence tier where novel errors hide",
        "Skipping review of high-confidence extractions entirely — 'high confidence' reflects model self-assessment, not ground truth; systematic errors can persist undetected without any sampling",
    ],
    "Stratified sampling specifically covers the high-confidence tier where novel errors are most likely to go undetected — standard routing never sends these to human review. Low-confidence-only review creates a blind spot. Flat random sampling is better than nothing but less targeted. Skipping high-confidence review entirely allows novel systematic errors to compound undetected."
),

# Q302 — distractors were too short
391: q(
    "You want to reduce human review workload while maintaining quality. The recommended approach is:",
    [
        "Calibrate confidence using a validation set and route only low-confidence or flagged extractions to human review — high-confidence items are skipped only after confirming their accuracy through calibration",
        "Reduce review uniformly by reviewing every other item regardless of confidence — uniform reduction ignores the signal in confidence scores; high-confidence items are treated identically to uncertain ones",
        "Skip reviewing high-confidence extractions entirely without calibration — without calibration, 'high confidence' is the model's self-reported certainty, not an empirically validated accuracy level",
        "Have humans review only items flagged by a secondary validation rule — rule-based flags catch known error patterns but miss novel errors that haven't been codified into rules yet",
    ],
    "Calibrated confidence-based routing is the right balance: validate confidence scores against labeled data, then confidently skip the high-confidence tier while reviewing uncertain or flagged items. Uniform reduction wastes review on obvious cases and skips uncertain ones equally. Uncalibrated skipping trusts self-reported confidence. Rule-based flags catch known errors but miss novel patterns."
),

# Q301 — distractors were too short
390: q(
    "You worked on a refactor yesterday in session <code>refactor-2024-11-01</code>. Today, several engineers changed the affected files while you were away. How do you continue effectively?",
    [
        "Resume with <code>--resume refactor-2024-11-01</code>, then explicitly tell the agent which prior findings are still valid given yesterday's changes before continuing",
        "Resume and let the agent figure out which prior context is still valid — the model will use prior tool results without knowing which files changed; it may reason from stale information without explicit guidance",
        "Start completely fresh with no summary — loses all valid prior analysis unnecessarily; prior findings about unchanged parts of the codebase are still useful",
        "Wait for the other engineers to finish their changes before resuming — collaboration requires resuming with awareness of changes, not pausing until all changes stop",
    ],
    "Resume with the named session but proactively inform the agent about which prior findings are stale due to yesterday's changes. Resuming without guidance risks reasoning from outdated tool results. Starting fresh discards valid analysis. Waiting is impractical; engineers need to work concurrently."
),

# Q312 — distractors were too short
401: q(
    "In the loop, you accidentally append the model's assistant text to history without a corresponding <code>tool_result</code>. What happens?",
    [
        "The next request is malformed — the API requires a <code>tool_result</code> message following any <code>tool_use</code> block; an assistant message without it creates an invalid conversation structure",
        "Nothing observable — the API silently ignores orphaned tool_use blocks and treats the conversation as if the tool was never called",
        "The model automatically generates a placeholder tool result — the API does not fabricate tool results; missing results cause an error, not auto-completion",
        "The conversation silently resets to before the tool call — the API does not implement implicit rollback; it returns an error for the malformed request",
    ],
    "Missing a tool_result after a tool_use block creates a malformed request — the API requires paired tool_use/tool_result messages. The API doesn't silently ignore orphaned blocks, fabricate results, or silently roll back the conversation."
),

# Q175 — distractors were too short
231: q(
    "Which review instruction is more likely to produce precise, actionable findings?",
    [
        "'Flag comments only when the claimed behavior contradicts the actual code behavior' — a specific, testable criterion the model can apply consistently",
        "'Check that comments are accurate' — too vague; 'accurate' is open to interpretation and produces inconsistent results depending on how the model interprets the standard",
        "'Be thorough about comments' — a behavioral instruction without a specific criterion; thoroughness varies per model interpretation and produces no consistent standard",
        "'Identify any comment-related issues' — the broadest possible framing; without defining what constitutes an issue, the model applies its own judgment inconsistently",
    ],
    "'Flag when the claimed behavior contradicts the actual code' is precise and testable — the model has a specific criterion to apply. 'Check for accuracy', 'be thorough', and 'identify issues' are increasingly vague formulations that rely on the model's interpretation of what counts as a problem, producing inconsistent results across runs."
),

# Q190 — distractors were too short
248: q(
    "You see empty/null extraction for required fields when the source format varies. The fix is:",
    [
        "Add few-shot examples demonstrating correct extraction from documents with varied formats — shows the model how to handle each format variation rather than leaving it to guess",
        "Make all fields required in the schema — required fields enforce that the model outputs something, but force it to hallucinate values when the source doesn't contain the data",
        "Require uniform input formatting before extraction — normalizing inputs reduces variance but adds preprocessing complexity and doesn't help with inherently varied source documents",
        "Drop the failing fields from the schema — removing fields avoids the extraction problem but also loses the data those fields were designed to capture",
    ],
    "Few-shot examples with varied source formats teach the model how to handle each variation explicitly. Making fields required forces hallucination for missing data. Requiring uniform input adds preprocessing complexity. Dropping fields loses the data entirely — none of these address the root cause."
),

# ═══════════════════════════════════════════════════════════
# SAME-START DISTRACTOR FIXES
# Wrong options all begin with same word — diversify openings
# ═══════════════════════════════════════════════════════════

# Q3 — all wrong options start with "agentic"
10: q(
    "Your DevOps team is automating incident response. One proposal uses a hardcoded runbook executor: detect alert → look up runbook → execute step 1 → execute step 2 → notify. A colleague proposes replacing it with a Claude-powered agentic loop. A junior engineer argues both call the same tools in roughly the same order, so the difference is cosmetic. What is the fundamental architectural distinction?",
    [
        "In an agentic loop, the model reasons about which tool to call next based on accumulated context; a decision tree follows fixed, pre-configured tool sequences regardless of intermediate results",
        "Both approaches are equivalent when tool lists and descriptions are identical — the selection mechanism (LLM vs. tree) doesn't affect tool execution outcomes",
        "A hardcoded runbook is more reliable for compliance because every step is auditable and pre-approved; agentic loops introduce non-determinism that compliance teams must re-certify",
        "The main difference is latency: agentic loops add LLM inference time to each step while decision trees execute tool calls directly without a reasoning pass",
    ],
    "The defining distinction is adaptive, context-informed decision-making. After each step the agentic loop uses all accumulated results to decide the next action — it may retry differently, skip steps, or branch based on what it found. A decision tree executes a fixed sequence regardless of intermediate results. Equivalence (B) ignores this fundamental difference. Reliability (C) conflates auditability with correctness. Latency (D) is an operational consideration, not the architectural distinction."
),

# Q43 — all wrong options start with "when"
59: q(
    "Your team is architecting a healthcare scheduling agent that can book procedures, override waiting lists, and flag cases as urgent. Legal has identified three rules: clinician review token for urgent flags, supervisor approval for wait-list overrides, guardian consent for minor bookings. A senior engineer argues these should be system prompt rules since they're 'clearly stated.' When are hooks definitively required instead?",
    [
        "Whenever business rules require guaranteed compliance — financial, legal, or safety-critical constraints cannot tolerate a non-zero failure rate from probabilistic prompt enforcement",
        "Only after prompt-based enforcement has failed in production at least once — hooks are a remediation tool, not a proactive safeguard, and should be added only after observed violations",
        "Exclusively for post-execution validation, not pre-execution blocking — hooks run after the fact to detect violations; pre-execution enforcement belongs in the prompt",
        "Primarily when compliance rules are too complex for the model to evaluate correctly — simple binary rules like 'token required' can always be enforced reliably via prompt alone",
    ],
    "Hooks are required from the start whenever rules demand guaranteed compliance — the exam guide is explicit: don't wait for failures before switching to deterministic enforcement. Treating hooks as post-failure remediation (B) is backwards. Hooks can run pre-execution for blocking (C). Simple rules still require hooks if compliance-critical (D)."
),

# Q49 — all wrong options start with "hooks"
65: q(
    "An audit of your healthcare scheduling agent finds that over 18 months, 7 out of 140,000 procedure bookings violated the guardian consent rule — a system prompt instruction. Your VP of Engineering argues 99.995% compliance is 'effectively perfect.' What is the strongest argument for hooks?",
    [
        "Hooks fire deterministically every time — prompt instructions have a non-zero failure rate that is unacceptable when each violation represents a patient safety or legal incident",
        "Hooks eliminate token overhead from compliance instructions in the system prompt, reducing per-request cost — a secondary benefit, not the primary argument for hooks in a safety-critical context",
        "Hooks are version-controlled separately from the system prompt, enabling compliance logic to be audited and updated without touching the agent's instructions — true but not the binding argument",
        "Hooks can enforce the rule for specific tools while allowing the prompt to remain general, simplifying system prompt maintenance — accurate but not the reason hooks are required here",
    ],
    "Determinism is the binding argument. In healthcare, each of 7 violations represents a potential patient harm or lawsuit — 99.995% is not acceptable. The other options describe real benefits of hooks (cost, auditability, scoping) but they're optimization arguments, not the core reason hooks are required for compliance-critical rules."
),

# Q59 — all wrong options start with "tasks"
77: q(
    "You are architecting a Claude-powered system to modernize a 15-year-old e-commerce platform's database layer. The codebase has no architecture diagram, inconsistent naming, and several layers of legacy abstractions. A junior engineer suggests starting with the most-changed files from git history. A senior engineer insists on an upfront analysis phase. Which decomposition approach applies here?",
    [
        "Tasks where the structure is unknown until exploration is done benefit from an upfront analysis phase before adaptive subtask generation",
        "Fixed-sequence pipelines are more appropriate — database migrations always follow the same schema → data → index pattern regardless of codebase state",
        "Parallel decomposition is preferable — each database table can be migrated independently once the schema is mapped, so upfront analysis is unnecessary overhead",
        "The junior engineer's git history approach is correct — code change frequency is a reliable proxy for both business criticality and coupling, making it sufficient as a decomposition basis",
    ],
    "Unknown-structure exploration tasks require an upfront analysis phase before decomposing into subtasks — without mapping the legacy abstractions and dependencies, any implementation plan risks breaking hidden couplings. Fixed-sequence pipelines assume structural knowledge that doesn't exist. Parallel table migration is possible eventually but requires discovery first. Git history frequency is a heuristic, not a complete decomposition basis for an unknown codebase."
),

# Q142 — all wrong options start with "paths:"
186: q(
    "Which YAML frontmatter <code>paths</code> pattern would match all TypeScript source files under <code>src/</code> but exclude test files?",
    [
        '<code>paths: ["src/**/*.ts", "!src/**/*.test.ts"]</code> — the glob matches all .ts files under src/ and the negation pattern excludes test files',
        '<code>paths: ["src/**/*.ts"]</code> — this matches all .ts files including test files; there is no negation to exclude the test file pattern',
        '<code>paths: ["src/"]</code> — a bare directory path is not a valid glob pattern for matching files; it would match the directory name, not files within it',
        '<code>paths: ["**/*.ts", "src/"]</code> — combining a broad glob with a directory pattern creates an overly broad match that includes .ts files outside src/ and duplicates src/ matching',
    ],
    "The correct pattern uses a glob for source files combined with a negation pattern to exclude test files. A glob without the negation includes test files. A bare directory path doesn't match files. Combining an unrestricted glob with a directory entry is overly broad and doesn't achieve the exclusion."
),

# Q145 — all wrong options start with "paths:"
189: q(
    "For Terraform files: which is the recommended frontmatter?",
    [
        '<code>paths: ["**/*.tf", "**/*.tfvars"]</code> — matches both Terraform configuration files and variable files at any directory depth',
        '<code>paths: ["*.tf"]</code> — matches only .tf files in the root directory; doesn\'t recurse into subdirectories like <code>modules/</code> or <code>environments/</code>',
        '<code>paths: ["terraform/"]</code> — a bare directory name is not a valid file-matching glob; it would match the directory itself, not the files inside it',
        '<code>paths: ["**/*"]</code> — matches every file in the repository, making this rule apply regardless of file type rather than targeting Terraform files specifically',
    ],
    "The recommended pattern covers both .tf and .tfvars extensions with recursive matching (**) to handle typical Terraform directory structures. *.tf without ** misses nested modules. A bare directory path doesn't match files. **/* is too broad and applies the rule to all files."
),

# Q146 — all wrong options start with "path-scoped"
190: q(
    "Why is path-scoped loading more efficient than always-loaded rules?",
    [
        "Rules load only when matching files are in context — irrelevant conventions don't consume token budget when the agent is working on unrelated files",
        "Path-scoped rules are parsed faster by Claude Code — the efficiency gain is about context relevance, not parsing speed; both rule types parse at the same speed",
        "Path-scoped rules bypass the CLAUDE.md hierarchy check — all CLAUDE.md files are discovered through the same hierarchy regardless of path scoping",
        "Path-scoped rules apply before always-loaded rules, giving them precedence — rule priority is determined by specificity in the hierarchy, not by whether a rule is path-scoped",
    ],
    "Path-scoped rules are efficient because they load only when relevant files are in context — they don't consume token budget on sessions where the agent is editing files outside the scope. Parsing speed, hierarchy bypassing, and precedence order are all incorrect reasons; the benefit is context token efficiency."
),

# Q0 — all wrong options start with "whether"
7: q(
    "You are implementing an agentic loop with the Claude Agent SDK. After each API response, what is the correct signal to determine whether the loop should continue executing tool calls?",
    [
        "The value of <code>stop_reason</code> — continue when it is <code>\"tool_use\"</code>, terminate when it is <code>\"end_turn\"</code>",
        "Parsing the assistant's response text for phrases like 'I'm done' or 'task complete' — natural language signals are non-deterministic and an explicit anti-pattern",
        "An arbitrary maximum iteration count (e.g., 10 iterations) as the primary stopping criterion — a fixed cap used as the primary stop condition terminates tasks prematurely or wastes iterations",
        "The status code returned by the most recent tool call — tool execution success does not indicate whether the model has finished reasoning",
    ],
    "stop_reason drives the loop: 'tool_use' means the model wants to call tools and continue; 'end_turn' means the model has finished. Parsing natural language for completion signals is an explicit anti-pattern. Using iteration caps as the primary stop mechanism truncates legitimate work. Tool return status reflects execution success, not model completion."
),

}  # end REPLACEMENTS


if __name__ == '__main__':
    apply(REPLACEMENTS)
