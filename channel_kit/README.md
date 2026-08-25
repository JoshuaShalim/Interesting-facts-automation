# Interesting Facts Channel Kit

This starter profile adapts MoneyPrinterTurbo for an English-language
"interesting facts" channel that publishes both Shorts and longer videos.

## Guardrails

- Verify every factual claim before rendering.
- Keep a source URL and access date for every claim in the fact sheet.
- Use only licensed stock footage or assets you created.
- Review the finished video before uploading.
- Keep automatic cross-platform publishing disabled during the pilot.
- Do not reuse the same script, title, hook, or edit structure across videos.

## Free-first stack

- Script model: Google Gemini free tier
- Narration: Microsoft Edge TTS (`en-US-AriaNeural-Female`)
- Footage: Pexels free API, or locally supplied licensed media
- Rendering: FFmpeg through MoneyPrinterTurbo
- Music: disabled initially to avoid copyright and attribution mistakes

## First-run setup

1. Start the WebUI with `sh webui.sh` on macOS/Linux or `webui.bat` on Windows.
2. In Basic Settings, select Google Gemini and add a Gemini API key.
3. Select Pexels as the video source and add a free Pexels API key.
4. Keep Upload-Post and automatic publishing disabled.
5. Copy `fact-sheet-template.md`, fill it from reliable sources, and save it
   outside this template file.
6. Preview the two commands:

   ```bash
   .venv/bin/python scripts/generate_fact_pair.py \
     --subject "Why octopuses have three hearts" \
     --facts-file channel_kit/my-first-fact-sheet.md
   ```

7. When the preview is correct, add `--execute`.

The wrapper creates two separate MoneyPrinterTurbo jobs: a portrait Short and
a landscape long-form video. Both jobs receive the same verified fact sheet,
but use format-specific pacing and storytelling instructions.

## Pilot publishing plan

- Weeks 1-2: three Shorts and one long video per week.
- Weeks 3-4: repeat only the topics and hooks that earn strong retention.
- Upload privately first, review captions and visuals, then publish manually.
- Do not judge the channel from one video; review at least 12 Shorts and four
  long videos before changing the niche.

