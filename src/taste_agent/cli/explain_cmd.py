"""taste explain — mentor mode: explain WHY an issue matters."""
from __future__ import annotations

import click


@click.command()
@click.argument("issue", required=False)
@click.option("--dimension", default=None, help="Filter by dimension (e.g. aesthetic, ux, copy).")
@click.pass_context
def explain(ctx: click.Context, issue: str | None, dimension: str | None) -> None:
    """Explain WHY an issue matters — mentor mode.

    Run without arguments for general guidance, or pass an issue description
    for specific mentorship on that problem.
    """
    if not issue:
        _print_general_guidance()
        return

    _explain_issue(issue, dimension)


def _explain_issue(issue_text: str, dimension: str | None) -> None:
    """Provide mentor guidance for a specific issue."""
    dim = dimension or _infer_dimension(issue_text)
    explanations = {
        "aesthetic": {
            "placeholder copy": "Placeholder copy (Lorem Ipsum, 'Insert text here') signals that the writer hasn't thought about who the audience is. Enterprise buyers in particular read every word — vague copy erodes trust immediately.",
            "inconsistent color": "Color deviations from the spec mean the design system isn't being enforced. This compounds over time into visual debt that's expensive to fix later.",
            "typography": "Typography choices directly affect readability and perceived quality. Deviating from the spec's font choices breaks the intended visual rhythm.",
        },
        "ux": {
            "missing error state": "Error states aren't optional — they're the moment users need most. Invisible errors cause users to distrust the system entirely.",
            "no loading state": "Without loading indicators, users don't know if their action registered. They click again, causing duplicate operations.",
            "unclear affordance": "If users can't tell something is clickable, they won't click it. Every interactive element must communicate its affordance.",
        },
        "copy": {
            "generic": "Generic copy like 'Welcome to our platform' could describe any product. Specific copy signals that you understand your audience and have intentionally chosen every word.",
            "hedging": "Words like 'maybe', 'might', 'could' undermine authority. Enterprise buyers need confidence, not qualifiers.",
            "jargon": "Overuse of jargon excludes people who don't share your context. Aim for the smartest person in the room who isn't a specialist.",
        },
        "adherence": {
            "spec violation": "The spec exists so the human doesn't have to repeat themselves. Violating it wastes the design investment.",
        },
        "architecture": {
            "circular import": "Circular imports are a tax on the entire team. Every developer who touches this file pays it, forever, until the cycle is broken.",
            "god module": "A file that does too many things is a file that will be broken by the next change. Break it down to single-responsibility units.",
        },
        "naming": {
            "generic name": "Names like 'data', 'info', 'temp' carry no meaning. They force readers to read the implementation to understand what's stored. A good name is the first form of documentation.",
        },
        "api_design": {
            "inconsistent response shape": "API consumers build against your response shapes. Changing them silently breaks their integration. Version or maintain consistency.",
        },
        "code_style": {
            "magic number": "A magic number like 'if x > 86400' requires everyone to decode it. Name it: 'SESSION_TTL_SECONDS = 86400' is self-documenting.",
        },
        "coherence": {
            "naming inconsistency": "Using 'user' in one file and 'account' in another for the same concept forces readers to maintain a mental map of your inconsistencies.",
        },
    }

    dim_explanations = explanations.get(dim, {})
    explanation = dim_explanations.get(issue_text.lower(), None)

    if explanation:
        click.echo(f"[{dim.upper()}] WHY THIS MATTERS:\n")
        click.echo(f"  {explanation}\n")
    else:
        # Generic guidance
        click.echo(f"[{dim.upper()}] MENTOR GUIDANCE:\n")
        click.echo(f"  The issue '{issue_text}' suggests a deviation from established standards.")
        click.echo("  The reason these standards exist is to prevent small inconsistencies from")
        click.echo("  compounding into a system that's hard to maintain and trust.\n")


def _infer_dimension(text: str) -> str:
    """Infer which dimension an issue belongs to from its text."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["color", "font", "typography", "spacing", "layout", "visual"]):
        return "aesthetic"
    if any(k in text_lower for k in ["button", "input", "error", "loading", "hover", "state", "ux", "interaction"]):
        return "ux"
    if any(k in text_lower for k in ["copy", "text", "headline", "label", "tone", "voice", "placeholder", "generic"]):
        return "copy"
    if any(k in text_lower for k in ["import", "layer", "module", "architecture", "circular", "god"]):
        return "architecture"
    if any(k in text_lower for k in ["naming", "name", "snake", "camel", "pascal", "generic"]):
        return "naming"
    if any(k in text_lower for k in ["api", "endpoint", "response", "status", "route"]):
        return "api_design"
    if any(k in text_lower for k in ["function length", "magic number", "comment", "style"]):
        return "code_style"
    if any(k in text_lower for k in ["consistent", "coherence", "duplicate", "inconsistent"]):
        return "coherence"
    return "adherence"


def _print_general_guidance() -> None:
    """Print general mentor guidance."""
    guidance = """
# Taste Mentor - General Guidance

The Taste Agent enforces standards that exist for three reasons:

1. Trust - Consistent systems are predictable. Predictability builds trust.
   Every deviation from spec is a small lie to future maintainers.

2. Efficiency - Clear conventions let developers move fast without
   consulting a human. Naming a function is not a creative act - it is
   a documentation act.

3. Onboarding - A new developer joining a project with strong taste
   standards can contribute meaningfully in day one. A project with no
   standards requires weeks of reading to understand.

## Severity Quick Reference

  P0 (BLOCKER):    Violates a stated non-negotiable -> immediate REJECT
  P1 (MAJOR):      Significant deviation from spec -> 2+ leads to REVISE
  P2 (MINOR):      Drift that accumulates debt -> 4+ leads to REVISE
  P3 (SUGGESTION): Opportunity to exceed spec -> APPROVE with note

## The Mentor Question

When evaluating, ask: "Would a senior practitioner recognize this as
the work of someone who understands what they're doing?"

If the answer is uncertain, that's a REVISE.
If the answer is clearly no, that's a REJECT.
If the answer is clearly yes, that's an APPROVE.

Run 'taste explain <issue>' for specific guidance on an issue.
"""
    click.echo(guidance)
