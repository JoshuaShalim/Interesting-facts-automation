"""Build or execute paired Short and long-form fact-video commands."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "cli.py"
MAX_FACT_SHEET_CHARS = 5_000
MAX_SCRIPT_PROMPT_CHARS = 2_000

SHORT_REQUIREMENTS = """
Create a 35-50 second YouTube Short for curious English-speaking viewers.
Open with a specific curiosity gap in the first sentence. Use only the verified
claims supplied below. Explain one connected idea with brisk, natural pacing.
Do not invent statistics, quotations, dates, rankings, or scientific certainty.
End with a satisfying payoff, not a generic subscribe request.
""".strip()

LONG_REQUIREMENTS = """
Create a 4-6 minute YouTube explainer for curious English-speaking viewers.
Open with a concrete surprising question, then build a clear narrative with
three to five connected sections. Use only the verified claims supplied below.
Explain necessary context and caveats in plain language. Do not invent
statistics, quotations, dates, rankings, or scientific certainty. End by
connecting the main facts into one memorable conclusion.
""".strip()


def read_fact_sheet(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("fact sheet is empty")
    if len(text) > MAX_FACT_SHEET_CHARS:
        raise ValueError(
            f"fact sheet must be at most {MAX_FACT_SHEET_CHARS} characters; "
            "keep only claims the narration needs"
        )
    return text


def compact_fact_sheet(fact_sheet: str) -> str:
    """Keep editorial guidance but omit source metadata from the LLM prompt."""
    lines = []
    for line in fact_sheet.splitlines():
        stripped = line.strip()
        if stripped.startswith(("Source:", "Accessed:")):
            continue
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def format_prompt(requirements: str, fact_sheet: str) -> str:
    prompt = (
        f"{requirements}\n\nVERIFIED FACT SHEET:\n"
        f"{compact_fact_sheet(fact_sheet)}"
    )
    if len(prompt) > MAX_SCRIPT_PROMPT_CHARS:
        raise ValueError(
            f"combined script prompt must be at most {MAX_SCRIPT_PROMPT_CHARS} "
            "characters; shorten the fact sheet"
        )
    return prompt


def build_commands(
    *,
    subject: str,
    fact_sheet: str,
    python: str,
    video_source: str,
    voice_name: str,
) -> list[tuple[str, list[str]]]:
    common = [
        python,
        str(CLI),
        "--video-subject",
        subject,
        "--video-language",
        "en-US",
        "--video-source",
        video_source,
        "--voice-name",
        voice_name,
        "--bgm-type",
        "none",
        "--match-materials-to-script",
        "--video-concat-mode",
        "sequential",
        "--video-transition-mode",
        "fade-in",
    ]

    short = common + [
        "--video-aspect",
        "9:16",
        "--paragraph-number",
        "2",
        "--video-clip-duration",
        "3",
        "--voice-rate",
        "1.08",
        "--font-size",
        "72",
        "--video-script-prompt",
        format_prompt(SHORT_REQUIREMENTS, fact_sheet),
    ]
    long_form = common + [
        "--video-aspect",
        "16:9",
        "--paragraph-number",
        "6",
        "--video-clip-duration",
        "5",
        "--voice-rate",
        "1.0",
        "--font-size",
        "54",
        "--video-script-prompt",
        format_prompt(LONG_REQUIREMENTS, fact_sheet),
    ]
    return [("short", short), ("long", long_form)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create paired Short and long-form interesting-fact videos."
    )
    parser.add_argument("--subject", required=True)
    parser.add_argument("--facts-file", required=True, type=Path)
    parser.add_argument(
        "--video-source",
        choices=["pexels", "pixabay", "coverr", "local"],
        default="pexels",
    )
    parser.add_argument("--voice-name", default="en-US-AriaNeural-Female")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subject = args.subject.strip()
    if not subject or len(subject) > 160:
        raise SystemExit("--subject must contain 1-160 characters")

    fact_sheet_path = args.facts_file.expanduser().resolve()
    try:
        fact_sheet = read_fact_sheet(fact_sheet_path)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Invalid fact sheet: {exc}") from exc

    commands = build_commands(
        subject=subject,
        fact_sheet=fact_sheet,
        python=sys.executable,
        video_source=args.video_source,
        voice_name=args.voice_name,
    )

    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": "preview",
                    "commands": [
                        {"format": name, "command": shlex.join(command)}
                        for name, command in commands
                    ],
                },
                indent=2,
            )
        )
        return 0

    for name, command in commands:
        print(f"Generating {name} video...", file=sys.stderr)
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
