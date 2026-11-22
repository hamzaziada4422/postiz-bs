# Agent Report reel pipeline

Makes a vertical news reel (voiceover, captions, number cards) from a short JSON spec.

1. `./setup.sh` once per session (installs kokoro-onnx, downloads voice models).
2. Write `specs/<id>.json`. The `id` field must equal the file name. See `specs/r2.json` and `specs/r3.json`.
   Line types: `big` (kicker, big, sub, optional color), `text` (text, sub), `bars` (title, rows [label, value, display, word index to reveal on]), `end`.
   Write `say` as spoken words (numbers spelled out) and `show` as the caption text.
3. `python3 gen_news.py <id>` builds the HyperFrames project at `/home/claude/hf/<id>`.
4. In that folder run `npx --yes hyperframes@0.9.81 check --json` and fix errors, then
   `npx --yes hyperframes@0.9.81 render --quality looks --output ../<id>.mp4` (about 1 to 2 minutes for 20 seconds).
5. Copy the mp4 to `reels/<date>-<id>.mp4` in this repo, commit and push to main, then upload it to Postiz with
   uploadFromUrlTool using `https://raw.githubusercontent.com/hamzaziada4422/postiz-bs/main/reels/<file>.mp4`
   and attach the returned path to an Instagram post (becomes a Reel) and an X post.

Keep text inside x 120 to 888 and y 288 to 1248, at least 28 px type, no all caps, no em dashes.

## Image cards
`python3 gen_cards.py cards.json outdir` renders unique 1080x1350 PNG cards (kicker, big number, subline, source). Use them for X images and as Instagram carousel slides when no other image source works. Commit PNGs to `media/<date>/` and upload by raw URL like the reels.
