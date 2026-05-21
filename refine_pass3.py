#!/usr/bin/env python3
"""Third-pass refinements — fix remaining same-start distractor issues."""
import sys
sys.path.insert(0, '.')
from apply_improvements import apply, q

REPLACEMENTS = {

# Q176 line=232 — wrong options all start with "Only", correct is "All categories"
232: q(
    "High false-positive rates in one category undermine trust in:",
    [
        "All categories — high FP in one category erodes developer confidence in the whole review pipeline, causing them to dismiss even accurate findings from other categories",
        "Just that one category — developers are highly calibrated reviewers who apply skepticism selectively and continue trusting well-performing categories independently",
        "Exclusively the severity classification for that category — high FP suggests severity labeling is miscalibrated, not that the entire pipeline loses developer trust",
        "Categories tuned in the same prompt-improvement session — co-tuned categories share a prompt history, but changes to one don't directly affect detection logic in others",
    ],
    "Trust erosion from high-FP categories is not contained — developers who encounter frequent false alarms apply skepticism to all findings, not just the noisy category. 'If the tool cried wolf on security, why trust the performance findings?' Options B, C, D all propose that skepticism stays isolated, which contradicts how developer trust degrades in practice."
),

# Q275 line=357 — wrong options all start with "Uniformly"
357: q(
    "In a synthesis output, financial data and news content should be rendered:",
    [
        "According to content type — financial data as structured tables (for comparison), news as prose narrative (for context), technical findings as code or structured lists",
        "In a single prose narrative regardless of content type — simplifies downstream text processing but makes financial comparisons unreadable and obscures tabular relationships",
        "As machine-readable JSON for all content — aids programmatic processing but produces unreadable synthesis for human reviewers and loses the narrative flow of news articles",
        "As bullet lists for everything — loses the relational structure of financial tables (where row/column position carries meaning) and the narrative thread of news content",
    ],
    "Rendering by content type preserves each category's natural structure: financial data as tables for comparison, news as prose for narrative, technical findings as structured lists. A single format — prose, JSON, or bullets — either loses structure or produces unreadable output for at least one content type."
),

}

if __name__ == '__main__':
    apply(REPLACEMENTS)
