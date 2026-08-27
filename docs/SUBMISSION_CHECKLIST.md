# Submission Checklist

## Code

- [x] Official `Agent` interface implemented
- [x] Standalone `submission/agent.py` entry file
- [x] Frozen catalog remains unmodified and excluded from Git
- [x] Official evaluator and public labels remain unmodified
- [x] No API keys, credentials, or network dependency
- [x] Python dependency manifest included
- [x] Unit and contract tests pass
- [x] Public result reproduced with the official evaluator
- [x] Method, limitations, latency, tokens, and cost disclosed

## Devpost

- [x] Draft description prepared in `docs/DEVPOST_DESCRIPTION.md`
- [ ] Add team/member names if applicable
- [ ] Replace the demo-video placeholder with the public YouTube URL
- [ ] Add the public GitHub repository URL
- [ ] Verify project title and Track 4 selection

## Demo video

- [x] Three-minute narration and command sequence prepared
- [ ] Record the terminal walkthrough
- [ ] Confirm audio and text are readable
- [ ] Upload to YouTube with public visibility
- [ ] Confirm no unlicensed third-party media appears

## Final verification

```bash
python -m unittest discover -v
python -m evaluator.local_evaluator --output results.json
python -m scripts.trace_session public_0001
```

The remaining unchecked items require the participant's identity, GitHub
account, and YouTube/Devpost access; they cannot be completed by the local agent.
