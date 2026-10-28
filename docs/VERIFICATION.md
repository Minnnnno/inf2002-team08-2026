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

## Changes made against INF2002 lecture guidance

| Lecture point | WCAG | Change in the prototype | How it is checked |
|---|---|---|---|
| Human Abilities: presbyopia, x-height ("zooming alone may not solve it") | 1.4.4, 1.4.12 | Minimum visible text raised from 9–11 px to 12 px (57 rules). All-caps label letter-spacing reduced to 0.6 px. | `edge_checks.py` fails if any visible text on the four main routes is under 12 px |
| Human Abilities: sarcopenia, fine motor precision | 2.5.8 Target Size (Minimum) | Inline text links (for example "How it works", the researcher link) have at least 24 px of clickable height | Manual audit script (all interactive targets at least 24 px, or wrapped in a full-row label) |
| Human Abilities: contrast ratio at least 4.5:1 | 1.4.3 | No change needed. All text measured at least 4.5:1 on all four routes | Audit script, plus axe `color-contrast` |
| Human Abilities: colour deficiency | 1.4.1 Use of Color | Flag state is carried by underline shape: wavy means needs review, dotted means kept. Both are now 2px thick in darker colours, because the 1px dotted "kept" line almost disappeared in greyscale. The active dashboard filter also gets an underline bar. Warnings use an icon and text. | Chrome vision emulation (deuteranopia, protanopia, achromatopsia), standard and strong modes |
| Human Abilities: colour deficiency, presbyopia | 1.4.1, 1.4.11 Non-text Contrast | Optional **Stronger visual cues** setting under Privacy preferences, saved in this browser. It adds 3px underlines, dashed or dotted outlines on flags, darker card and button borders, and a 3px focus ring. The same rules apply automatically when the operating system requests more contrast (`prefers-contrast: more`). | `browser_smoke.py` (preview, save, persist, revert), axe on chat with strong cues on |
| Human Abilities: protanopia, deuteranopia (red-green); low blue sensitivity | 1.4.1, 1.4.3 | Status colours (accent, warning, danger) are tuned to differ in **lightness**, not only hue, in both themes. Simulated worst-case colour difference (CIELAB ΔE, Machado 2009) improved from 9.3 to 16.3 in light mode and from 11.5 to 25.8 in dark mode, with every status colour still at least 4.5:1. Destructive confirm buttons carry a trash icon. In dark mode, kept details use a neutral tint (dotted underline) and flagged details an amber tint (wavy underline). | `edge_checks.py` simulates protanopia, deuteranopia and tritanopia for both themes and requires ΔE ≥ 15 and 4.5:1. Chrome vision emulation screenshots. |
| Human Abilities: recognition over recall | 3.3.2 | Send button shows its shortcut as a tooltip ("Send (Ctrl+Enter)") and exposes `aria-keyshortcuts` | Manual |
| Human Abilities: peripheral motion distracts | 2.3.3, 2.2.2 | Motion runs only in response to the user's action (nothing loops or pulses), and `prefers-reduced-motion` is respected | Code comment in the Motion block of `styles.css`, reduced-motion emulation |
| Visual Design: F-pattern scanning, guide | none | The "Prototype" status badge moved from the far top-right to next to the page title | Screenshots |
| Visual Design: proximity (Gestalt) | none | More space between a dashboard item's title group and its reuse/source row; review pill raised to 13 px | Screenshots |
| Web Interaction: evaluate with industry tools | none | axe-core WCAG 2 A/AA scan on seven page states | `edge_checks.py` (axe file in the OS temp directory) |

The W3C Nu HTML validator (validator.w3.org) has not been run yet. Run it by hand on `index.html`, `researcher.html` and `study-guide.html`, and record the result here.

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
