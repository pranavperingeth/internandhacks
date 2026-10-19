# Progress

## Checklist
- [x] Phase 0 setup
- [x] Phase 1 models/config
- [x] Phase 2 net/normalize
- [x] Phase 3 sources
- [x] Phase 4 db
- [x] Phase 5 filters
- [x] Phase 6 digest
- [x] Phase 7 notifiers
- [ ] Phase 8 pipeline/cli
- [ ] Phase 9 smoke test
- [ ] Phase 10 scheduling
- [ ] Phase 11 LLM (optional)
- [ ] Phase 12 README/final

## Latest command output
```
$ NOTIFIER=console python -c "from oppwatch.notifiers import NOTIFIERS; print(NOTIFIERS['console']('hello'))"
hello
True
```

## QUESTIONS FOR USER
- Please open each url in config/sources.yaml in a browser and set enabled: true only for sources that work.

## BLOCKED
(none)
