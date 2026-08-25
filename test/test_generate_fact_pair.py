from scripts.generate_fact_pair import build_commands, compact_fact_sheet, format_prompt


FACTS = "Claim: Octopuses have three hearts. Source: https://example.test/source"


def _value_after(command, flag):
    return command[command.index(flag) + 1]


def test_builds_short_and_long_commands_from_one_fact_sheet():
    commands = build_commands(
        subject="Why octopuses have three hearts",
        fact_sheet=FACTS,
        python="python",
        video_source="pexels",
        voice_name="en-US-AriaNeural-Female",
    )

    assert [name for name, _ in commands] == ["short", "long"]
    short = commands[0][1]
    long_form = commands[1][1]
    assert _value_after(short, "--video-aspect") == "9:16"
    assert _value_after(long_form, "--video-aspect") == "16:9"
    assert FACTS in _value_after(short, "--video-script-prompt")
    assert FACTS in _value_after(long_form, "--video-script-prompt")


def test_prompts_prohibit_unverified_claims():
    prompt = format_prompt("Use only verified claims.", FACTS)
    assert "VERIFIED FACT SHEET" in prompt
    assert FACTS in prompt


def test_compact_fact_sheet_omits_source_metadata():
    sheet = "Claim: Three hearts.\nSource: https://example.test\nAccessed: 2026-08-25"
    compact = compact_fact_sheet(sheet)
    assert "Claim: Three hearts." in compact
    assert "https://example.test" not in compact
    assert "Accessed:" not in compact
