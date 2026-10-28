# Verification record

Validated on 28 October 2026 with local Google Chrome through Python Playwright. Tests use fictional data and isolated browser contexts. No real participants or real GPT services were involved.

## Functional checks passed

- Single-detail detection, original/replacement review, masking, undo and sending.
- Multiple flags, selected batch replacement and batch undo.
- Explicit Keep unchanged, including keyboard activation of an underlined detail.
- Repeated identical values: retaining one occurrence survives masking another occurrence and unrelated edits.
- Context-preserving location generalisation and undo; sentence punctuation is preserved.
- Multiline editing: Enter places subsequent text on the new line. Plain-text insertion avoids injected markup.
- Initial prompt and related scripted follow-up; reload persistence.
- Draft and conversation survival across dashboard navigation.
- Searchable profile, deletion confirmation, cancel, removal, restoration and permanent removal of the recoverable profile copy.
- Source conversation text remains after profile deletion, as stated in the interface.
- Pause-before-send preference and explicit send override.
- Detection category switches and simulated reuse permission/decline.
- Separate researcher console, consent gating, preparation/reset, disabled participant controls before Begin task, task timer and stop-recording behaviour.
- Both conditions: inline + warning, and warning only. Identical masking interactions remain available through Review.
- Anonymous JSON export with task duration, outcome and assistance. Checked that fictional prompt strings, credentials, email and profile values are absent from the export.
- Direct opening of `dist/index.html` with `file://`, as well as local HTTP serving.
- All linked HTML, JavaScript, CSS and favicon files returned HTTP 200.
- No browser JavaScript errors in the checked flows.

## Visual and accessibility checks

- Inspected desktop chat, above-composer review card, dashboard and mobile review screenshots.
- Tested 1440 px desktop and 390 px mobile flows; verified no horizontal document overflow at 320, 390 and 768 CSS pixels on chat, dashboard, preferences and help.
- Keyboard review activation, sending, undo and dialog close tested. Native modal dialogs contain focus; return focus is restored or placed on a visible fallback.
- axe-core 4.10.3 reported zero WCAG 2 A/AA and WCAG 2.1 AA violations on the seven tested page states: Chat, Dashboard, Preferences, Help, Researcher, Study guide and Design notes.
- JavaScript syntax checks passed for core.js, store.js, app.js and researcher.js.

These checks do **not** establish WCAG conformance, real-world privacy protection, or improved usability. Screen-reader testing, physical touch-device testing, Safari/Firefox testing and user evaluation remain necessary. The automatic scan covers the tested states rather than every possible dynamic state.

## Test entry points

- `tests/browser_smoke.py`: main participant and researcher workflows, screenshots and sample export.
- `tests/edge_checks.py`: editing regressions, deletion scope, consent/start controls, direct-file use and optional axe checks.

Run against `http://127.0.0.1:4173`. Both use an installed Windows Google Chrome. The optional axe check uses an externally installed development copy in the OS temporary directory; no testing library is bundled into the app. Test outputs are in the OS temporary directory and are not part of the deployed site.

## Known limits

- Pattern matching is deliberately incomplete and can produce false positives/negatives. No image/document or arbitrary semantic detection.
- Replies and inference examples are prewritten. Reuse is demonstrated in an explicit preview, not a model memory system.
- Local storage is unencrypted and origin-specific; private browsing or disabled storage may prevent persistence and cross-tab researcher control. The interface reports storage failures.
- Research controls are separated by page, not secured by authentication. Use a controlled study device and keep the console away from participant view.
- Automatic success checks are simple rules; researchers must verify useful context and understanding before assigning final outcomes.
- There is no simulated connection-error journey because no connection is made; this was a secondary suggestion and is explained by the frontend-only scope.
