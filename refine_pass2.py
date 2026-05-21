#!/usr/bin/env python3
"""Second-pass refinements — remaining long-correct, short-correct, and same-start issues."""
import sys
sys.path.insert(0, '.')
from apply_improvements import apply, q

# All keys are LINE NUMBERS (0-based) in questions.js

REPLACEMENTS = {

# ═══════════ SHORT-CORRECT FIXES ═══════════

# Q115 line=149 — correct='Glob for file contents; Grep for file names' (43ch), distractors ~140-150ch
149: q(
    "Which sequence is INCORRECT?",
    [
        "<code>Glob</code> for file contents; <code>Grep</code> for file names — this reversal is wrong: Grep searches file CONTENTS by pattern; Glob matches file NAMES/paths",
        "<code>Grep</code> searches within file contents using regex patterns; <code>Glob</code> matches files by name pattern — correct assignment of each tool's purpose",
        "<code>Edit</code> performs anchor-based targeted replacement within a file; <code>Write</code> replaces the entire file — correct distinction between targeted and full-file operations",
        "<code>Read</code> loads the complete contents of a file into the model's context for inspection — correct description of the Read tool's function",
    ],
    "The incorrect sequence is using Glob for content search and Grep for filename matching — these are reversed. Grep searches file contents by text/regex pattern (the right tool for finding all callers of a function). Glob matches file paths by name pattern (the right tool for finding files by extension or path structure). Options B, C, and D correctly describe each tool's purpose."
),

# Q177 line=233 — correct='Temporarily disable that category to restore developer trust' (60ch)
233: q(
    "You have a category with persistently high false positives. While improving prompt specificity, what is the most important near-term action?",
    [
        "Temporarily disable that category to stop eroding developer trust while you work on improving its precision",
        "Raise the minimum confidence threshold for only that category, routing its findings to a 'pending' queue rather than disabling it entirely — reduces noise without removing the category, but adds queue management complexity",
        "Merge it with the nearest adjacent category so its FP rate is diluted by the combined category's overall accuracy — obscures the FP problem rather than solving it, and contaminates a functioning category",
        "Add a counter-example bank to the prompt showing common FP patterns so the model avoids similar false positives — the correct long-term prompt improvement strategy, but doesn't address the trust damage in the interim",
    ],
    "Temporarily disabling the high-FP category is the most important near-term action because developer trust erodes with each false alarm — even accurate alerts from other categories get ignored once the review pipeline feels unreliable. Raising thresholds and adding counter-examples are valid long-term improvements, but the immediate priority is stopping the trust damage."
),

# ═══════════ LONG-CORRECT / SHORT-DISTRACTOR FIXES ═══════════

# Q11 line=20 — correct=134ch, distractors avg 46ch
20: q(
    "You are running a multi-agent research system. The synthesis subagent reports it has 'no data to synthesize' despite the web search subagent completing successfully. The coordinator received a tool_result confirming the search completed. What is the most likely root cause?",
    [
        "Subagents have isolated context — the coordinator did not explicitly pass the web search results to the synthesis subagent; they share no automatic context",
        "The web search results were cleared from context when the synthesis subagent was initialized — results are retained in conversation history; they're not automatically cleared between subagent invocations",
        "The synthesis subagent's system prompt is too long and crowded out the search results — system prompt size affects reasoning quality, but the search results would still be present in the tool_result message",
        "The web search subagent hallucinated a success confirmation — the coordinator received a valid tool_result; the issue is in how results were passed to synthesis, not in the search result's authenticity",
    ],
    "Subagent context isolation is the cause — each subagent starts with only what the coordinator explicitly provides. The coordinator received the search results but didn't inject them into the synthesis subagent's prompt. Results aren't automatically cleared between invocations; they're just never shared unless explicitly passed. System prompt size and hallucination are plausible-sounding but don't explain the specific failure pattern."
),

# Q15 line=24 — correct=137ch, distractors avg 42ch
24: q(
    "Why is iterative refinement (coordinator evaluates synthesis output → re-delegates with targeted feedback) superior to a single-pass synthesis?",
    [
        "A single pass cannot self-correct for missing coverage; iterative refinement lets the coordinator identify gaps and direct subagents to fill them before finalizing the output",
        "Iterative refinement is always cheaper per token — iterative loops typically cost more per output because each iteration requires additional API calls and synthesis passes",
        "Iterative refinement eliminates the need for specialized subagents — the opposite is true; it relies on subagents and makes them more effective by allowing targeted follow-up",
        "Single-pass pipelines cannot support tool use — tool use is available in any pipeline architecture; the limitation is not tool availability but the inability to incorporate feedback",
    ],
    "A single synthesis pass produces what it produces — if coverage is incomplete or a topic is shallow, there's no mechanism to correct it. Iterative refinement lets the coordinator evaluate the output and direct targeted follow-up: 'section A lacks recent data, re-research X.' Cost, subagent necessity, and tool use support are all incorrect claims."
),

# Q39 line=52 — correct=146ch, distractors avg 58ch (already at 2.5 borderline)
52: q(
    "A frustrated customer requests a human agent immediately. The issue is straightforward — within policy and solvable by the AI agent. What is the right escalation response?",
    [
        "Acknowledge the customer's frustration directly, offer to resolve the issue since it's within policy and won't require waiting for a human, and escalate only if the customer still insists after being offered resolution",
        "Silently process the resolution without acknowledging the human-agent request — resolves the transaction but ignores the stated preference, which can further escalate frustration and damage the customer relationship",
        "Immediately transfer to a human agent without attempting resolution — honors the explicit request but wastes human agent capacity on a case the AI could handle, increasing queue times for complex cases",
        "Acknowledge the frustration, complete the transaction, and then send a satisfaction survey asking the customer to rate whether they wished they'd spoken to a human — defers resolution acknowledgment to a post-interaction survey rather than addressing it in the moment",
    ],
    "The correct response acknowledges frustration (validates the customer's experience), offers immediate resolution (avoids the wait for a human), and escalates only if the customer still wants a human after hearing that the AI can solve it now. Silent processing ignores the customer's emotional state. Immediate transfer wastes capacity. Post-interaction surveys defer what should be handled in the moment."
),

# Q51 line=69 — correct=124ch, distractors avg 49ch
69: q(
    "For an open-ended task like 'add comprehensive tests to a legacy codebase', dynamic decomposition is appropriate because:",
    [
        "First mapping structure identifies high-impact, high-risk modules — without this, test generation proceeds alphabetically or arbitrarily, missing the areas that need coverage most",
        "Pre-defining every test case before any analysis works well when the codebase has complete documentation and a flat module structure — but a legacy codebase with no docs requires exploration before planning",
        "Generating tests file by file alphabetically can succeed if each file has clear docstrings explaining its purpose — but 'legacy codebase' implies missing documentation, making alphabetical generation unreliable",
        "A fixed three-step pipeline (lint → test → commit) provides enough structure for any codebase — but a pipeline without an exploration phase will commit tests for low-priority files while leaving critical modules untested",
    ],
    "Dynamic decomposition is needed here because the high-impact modules are unknown until the codebase is explored — payment and fraud detection only get discovered as critical through analysis, not alphabetical ordering. Pre-defining cases requires documentation that legacy codebases typically lack. Fixed pipelines commit to an order before knowing what's important."
),

# Q57 line=75 — correct=142ch, distractors avg 52ch
75: q(
    "Decomposing 'add comprehensive tests to a legacy codebase' requires mapping structure and prioritizing high-impact areas first. Why?",
    [
        "Without prioritization, the task balloons — by focusing on high-impact areas first, the workflow delivers the most critical coverage before context limits are reached",
        "Mapping structure is required by Claude Code's CLI before any file writes can proceed — no such requirement exists; Claude Code can write files without a prior mapping phase",
        "Tests cannot be written for a module until its full call tree has been traced as a sitemap — tests can be written for individual functions without a complete call-tree map",
        "Legacy codebases apply validation at commit time that rejects test files not placed in a pre-registered test directory — this is a hypothetical constraint; the real reason to map first is prioritization, not directory registration",
    ],
    "Prioritizing high-impact areas ensures the most critical coverage is produced before context or iteration limits are reached — alphabetical or arbitrary test generation can exhaust resources on low-priority files. The CLI doesn't require mapping, tests don't require full call trees, and legacy codebases don't reject tests by directory registration."
),

# Q76 line=102 — correct=139ch, distractors avg 29ch
102: q(
    "You want the model to reliably differentiate <code>fetch_url</code> (generic) from a constrained <code>fetch_internal_api</code>. What solves selection unreliability?",
    [
        "Replace generic tools with constrained alternatives whose descriptions clearly specify their scope, data source, and when to prefer them over semantically overlapping tools",
        "Add <code>tool_choice: \"any\"</code> — this forces the model to call some tool but does not help it choose between two semantically similar tools with overlapping names",
        "Rename both tools to start with 'fetch_' to make their shared domain explicit — a shared prefix adds visual consistency but doesn't resolve ambiguity about which tool handles which source",
        "Wrap both into a single unified <code>fetch</code> tool with a <code>source</code> parameter — merging them removes the selection problem but loses the separate validation and access-control properties of each tool",
    ],
    "Description quality is the primary mechanism for tool selection — replacing vague descriptions with scope-specific ones that explain exactly when to use each tool is the correct fix. tool_choice: \"any\" doesn't guide selection. Shared prefixes add visual structure but not semantic clarity. Merging tools eliminates the selection problem but creates a different design problem."
),

# Q197 line=257 — correct=140ch, distractors avg 36ch
257: q(
    "You want <code>extract_metadata</code> to run BEFORE any enrichment tools, every time. Best mechanism?",
    [
        "<code>tool_choice: {\"type\": \"tool\", \"name\": \"extract_metadata\"}</code> on the first API call — this forces the specific tool on that turn, guaranteeing it runs first before giving the model tool-selection freedom",
        "Rely on the model to infer the intended order from the tool descriptions and system prompt — probabilistic; the model may choose an enrichment tool first under complex or ambiguous inputs",
        "Add a system prompt rule: 'Always call <code>extract_metadata</code> before any enrichment tool' — prompt-based ordering is probabilistic and has been shown to fail under high-context scenarios",
        "Remove enrichment tools from the tool list for the first API call, then add them back on subsequent turns — this works but is more complex than using tool_choice on the first call",
    ],
    "Named tool_choice on the first call is the deterministic mechanism — it guarantees extract_metadata runs before the model gets discretion over enrichment tools. Prompt rules and description-based ordering are probabilistic. Removing/restoring tools works but adds unnecessary complexity compared to tool_choice."
),

# Q281 line=368 — correct=112ch, distractors avg 34ch
368: q(
    "A workflow requires that <code>verify_identity</code> succeeds before <code>transfer_funds</code>. Production logs show <code>transfer_funds</code> running on failed verifications. What's the fix?",
    [
        "Add a programmatic prerequisite gate that blocks <code>transfer_funds</code> unless a verified identity token from <code>verify_identity</code> is present in its parameters — deterministic enforcement at the application layer",
        "Tighten the system prompt with uppercase 'CRITICAL: verify identity MUST succeed before transfer' — system prompt ordering rules are probabilistic; this pattern has already failed in production",
        "Add few-shot examples showing the correct sequence across varied scenarios — examples improve consistency but are still probabilistic; the failure is a compliance violation requiring deterministic enforcement",
        "Set <code>tool_choice: \"any\"</code> on each turn to force tool calls — this ensures some tool is called but provides no mechanism for enforcing call ordering between specific tools",
    ],
    "A programmatic prerequisite gate is the only deterministic fix — transfer_funds is blocked at the application layer unless verify_identity's token is present. System prompt rules, few-shot examples, and tool_choice all improve model behavior probabilistically but cannot provide ordering guarantees for compliance-critical sequencing."
),

# Q310 line=399 — correct=83ch, distractors avg 27ch
399: q(
    "For a field that may have a value not present in the source document, the best schema design is:",
    [
        "Make the field nullable — allows the model to return null when no value is present rather than fabricating a placeholder or hallucinating a value",
        "Make it required — required fields pressure the model to produce a value even when none exists in the source, increasing hallucination risk",
        "Make it required with an empty-string default — an empty default still pressures the model to return something, and an empty string is ambiguous between 'not present' and 'genuinely empty'",
        "Forbid extraction of that field entirely — eliminates the field from the schema, but also removes the ability to capture the value when it IS present in some documents",
    ],
    "Nullable fields are the correct design: they allow the model to distinguish 'value exists' from 'value not present' without fabricating content. Required fields create hallucination pressure. Empty-string defaults are ambiguous. Forbidding the field works around extraction but loses the value when it does appear."
),

# ═══════════ SAME-START FIXES ═══════════

# Q49 line=65 — all options start with "Hooks"
65: q(
    "An audit of your healthcare scheduling agent finds that over 18 months, 7 out of 140,000 procedure bookings violated the guardian consent rule — a system prompt instruction. Your VP of Engineering argues 99.995% compliance is 'effectively perfect.' What is the strongest argument for hooks?",
    [
        "Hooks fire deterministically every time — prompt instructions have a non-zero failure rate that is unacceptable when each violation represents a patient safety or legal incident",
        "Eliminating the compliance instruction from the system prompt reduces per-request token costs — a secondary benefit, not the binding argument for why determinism is required",
        "Separating compliance enforcement from the system prompt makes it easier to audit and update independently — true, but maintainability is an optimization argument, not a correctness guarantee",
        "Scoping enforcement to specific tools simplifies the system prompt and reduces the chance of the instruction being overridden by persona guidance — valid concern, but still secondary to the determinism requirement",
    ],
    "Determinism is the binding argument. In healthcare, each of 7 violations represents a potential patient harm or lawsuit — 99.995% is not acceptable. The other options describe real benefits of hooks (cost reduction, auditability, scoping) but they're operational improvements, not the core reason hooks are required for safety-critical compliance."
),

# Q146 line=190 — all wrong options start with "path-scoped"
190: q(
    "Why is path-scoped loading more efficient than always-loaded rules?",
    [
        "Rules load only when matching files are in context — irrelevant conventions don't consume token budget when the agent is working on unrelated files",
        "Parse time is reduced because Claude Code skips path-scoped files that don't match — the efficiency gain is context token savings, not reduced parse time; all rule files are still discovered",
        "The CLAUDE.md hierarchy check is bypassed for path-scoped rules — all CLAUDE.md files go through the same hierarchy discovery regardless of path scoping",
        "Priority ordering gives path-scoped rules precedence over always-loaded rules — rule priority is determined by scope specificity in the hierarchy, not by whether a rule is path-scoped",
    ],
    "Path-scoped rules are efficient because they load only when relevant files are in context — they don't consume token budget on sessions where the agent is working outside the scope. The efficiency is about context token savings, not parse time, hierarchy bypassing, or priority ordering."
),

# Q176 line=232 — all wrong options start with "only"
232: q(
    "High false-positive rates in one category undermine trust in:",
    [
        "All categories — high FP in one category erodes developer confidence in the whole review pipeline, causing them to dismiss even accurate findings from other categories",
        "Only that category — developers are highly calibrated reviewers who apply skepticism selectively and continue trusting well-performing categories independently",
        "Only the severity classification attached to that category — high FP in a category suggests the severity labeling is miscalibrated, not that the whole pipeline is unreliable",
        "Only the categories that were tuned in the same prompt-improvement session — co-tuned categories share a prompt history but changes to one don't directly affect detection logic in the others",
    ],
    "Trust erosion from high-FP categories is not contained — developers who encounter frequent false alarms apply skepticism to all findings, not just the noisy category. 'If the tool cried wolf on security findings, why trust the perf findings?' Options B, C, D all propose that skepticism stays isolated, which contradicts how developer trust actually degrades."
),

# Q188 line=246 — all wrong options start with "they"
246: q(
    "How do few-shot examples enable the model to generalize?",
    [
        "They demonstrate the reasoning behind a class of decisions, helping the model apply the same logic to novel inputs that share the same underlying pattern",
        "Enumerating the complete decision boundary — the model pattern-matches new inputs against examples without reasoning; generalization comes from boundary coverage, not reasoning",
        "Encoding the desired behavior as implicit constraints that override contradictory instructions — examples demonstrate behavior but don't override explicit instructions; explicit rules take precedence",
        "Showing exactly which tools to call in the illustrated scenarios — few-shot examples influence output style and reasoning patterns, not specific tool selections in unrelated scenarios",
    ],
    "Few-shot examples work by demonstrating the reasoning pattern behind a category of decisions — the model infers the principle and applies it to novel inputs. They don't work by exhaustive boundary coverage, implicit constraint override, or tool-call prescription."
),

# Q212 line=274 — all wrong options start with "they"
274: q(
    "Semantic validation errors (e.g., wrong field placement, totals not summing) differ from syntax errors in that:",
    [
        "They require business-logic validation; strict JSON schemas via tool use eliminate syntax errors but cannot verify that a total field actually equals the sum of its line items",
        "Detection is easier for semantic errors — the opposite is true; syntax errors are caught by a parser in milliseconds, while semantic errors require domain-aware validation logic",
        "Retrying with a corrected prompt cannot fix them — incorrect; targeted retry with specific error context (e.g., 'the total field should equal the sum of line items') can address semantic errors",
        "Exceeding token limits is the primary cause — token limits cause truncation of outputs, not semantic mismatches between related fields within the response",
    ],
    "Semantic errors require business-logic validation beyond what JSON schema enforcement provides — a structurally valid JSON document can still have totals that don't sum or fields in wrong positions. Semantic errors are harder to detect than syntax errors, not easier. Both can be addressed by retry. Token limits cause truncation, not semantic inconsistencies."
),

# Q219 line=283 — all options start with "submit"
283: q(
    "You have an SLA requiring 30-hour processing for a large batch. How should you schedule submissions?",
    [
        "Use a staggered submission schedule (e.g., every 4 hours) so each batch's 24-hour processing window completes before its downstream deadline",
        "Sending everything in a single batch at the start maximizes throughput but risks missing the SLA if the 24-hour window starts late or the batch is large enough to run long",
        "Restricting submissions to business hours is tempting for operational simplicity but wastes the available processing window and reduces effective throughput",
        "Hourly micro-batches fragment the workload unnecessarily, add overhead from frequent submissions, and don't leverage the batch API's cost efficiency for large volumes",
    ],
    "Staggered submission ensures each batch's worst-case 24-hour processing window fits within the 30-hour SLA. A single large batch risks SLA failure if processing starts near the deadline. Business-hours-only submission wastes the available window. Hourly micro-batches add overhead without improving latency."
),

# Q233 line=305 — all wrong options start with "models"
305: q(
    "The 'lost in the middle' effect means:",
    [
        "Models reliably process information at the beginning and end of long inputs but may under-attend to content in the middle of the context window",
        "Uniform attention across all positions — this describes the opposite of lost-in-the-middle; research shows attention is NOT uniform and drops in the middle of long contexts",
        "Performance degradation only at the end of long contexts due to recency bias — recency bias describes the opposite pattern (favoring recent content); lost-in-the-middle specifically affects middle positions",
        "Degradation only on inputs longer than the model's training corpus average — lost-in-the-middle is an attention distribution phenomenon, not a training-length comparison effect",
    ],
    "Lost-in-the-middle describes the empirical finding that models are more reliable at the beginning and end of long inputs than in the middle. It is not uniform attention, not an end-only effect, and not a training-length comparison — it's specifically about attention distribution across position within a single context."
),

# Q267 line=347 — all wrong options start with "that"
347: q(
    "Before reducing human review, what should you verify?",
    [
        "That accuracy is consistent across document types and field segments — not just overall average accuracy, which can mask systematic failures in specific subcategories",
        "Human reviewer approval for the reduction plan — reviewer buy-in matters operationally, but it doesn't validate whether the model's accuracy is high enough to safely reduce oversight",
        "Cost savings from reduced review outweigh projected cost of residual errors — financial justification is important but secondary to verifying the accuracy baseline is actually trustworthy",
        "Model version and prompt stability since the last accuracy baseline — important for reproducibility, but accuracy consistency across document types is the more fundamental check",
    ],
    "Consistency across document types and segments is the critical check — aggregate accuracy can look high while the model systematically fails on specific document formats or edge cases. Reviewer approval, cost justification, and prompt stability are all operationally relevant but don't substitute for confirming that accuracy holds across the full distribution."
),

# Q275 line=357 — all wrong options start with "always"
357: q(
    "In a synthesis output, financial data and news content should be rendered:",
    [
        "According to content type — financial data as structured tables (for comparison), news as prose narrative (for context), technical findings as code or structured lists",
        "Uniformly as prose narrative for all content types — simplifies downstream text processing but makes financial comparisons unreadable and loses the structural relationships in tabular data",
        "Uniformly as machine-readable JSON for all content — enables programmatic processing but produces unreadable synthesis outputs for human reviewers and loses narrative flow for news content",
        "Uniformly as bullet lists regardless of content type — loses the relational structure of financial tables (where rows and columns carry meaning) and the narrative flow of news content",
    ],
    "Rendering by content type preserves the natural structure of each category: financial data needs tables for comparison, news needs prose for narrative, technical findings need structured lists for precision. Forcing a single format — prose, JSON, or bullets — either loses structure or produces unreadable output for at least one content type."
),

# Q293 line=381 — all wrong options start with "summaries"
381: q(
    "During a long exploration, you summarize each phase before moving to the next. Why is this effective for context management?",
    [
        "Phase summaries injected at the start of each new phase counteract context degradation by giving the model fresh, high-signal starting context instead of relying on attention over a long history",
        "End-of-phase summaries allow /compact to retain high-level findings while discarding verbose tool output — /compact performs its own summarization; end-of-phase summaries are for the next phase, not for /compact optimization",
        "Natural-language summaries are preserved preferentially by /compact over raw tool results — /compact doesn't apply content-type preferences; it summarizes based on recency and apparent importance",
        "Each new phase begins with a dense, targeted context block rather than a sparse context spread across many earlier turns — accurate, but the key benefit is signal quality and resistance to context degradation, not density per se",
    ],
    "Phase summaries counteract context degradation: instead of the model attending over a long, diluted history, each phase starts with a compact, high-signal summary of what was learned. Options B and C describe /compact behavior incorrectly. Option D is partially accurate but frames the benefit as 'density' rather than the actual mechanism: providing fresh accurate context that doesn't compete with a long degraded history."
),

}

if __name__ == '__main__':
    apply(REPLACEMENTS)
