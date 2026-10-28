# Clarity — INF2002 Team 08

Static, frontend-only HCI prototype based on the supplied paper screens. No build, backend, API keys, authentication code, actual GPT connection, or installable extension.

Open `dist/index.html` directly in a modern browser. For repeatable cross-tab research testing, serve `dist/` over local HTTP:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Then open `http://127.0.0.1:4173/`. The researcher console is `researcher.html`, the testing/consent guide is `study-guide.html`, and the design-to-research mapping is `design-notes.html`. All assets are local; the app makes no external requests.

## Main flows

- Chat: type or load an example; select underlined text or Review; mask, generalise, keep, manually edit or batch-apply; undo; send and follow up.
- Dashboard: search/filter shared details, saved preferences and unconfirmed inferences; inspect source; edit values and reuse choices; delete with explicit scope; restore from Removed; permanently erase the recoverable profile copy.
- Preferences: notice/pause mode, detection categories, default reuse and a working permission example. Save changes to apply them.
- Help: simulated capabilities, detector limits, local storage, deletion scope, keyboard shortcuts and researcher link.
- Research: consent-gated anonymous task recording, resettable scenarios, two controlled conditions, task outcomes/assistance, JSON/CSV exports. No raw prompt or profile values enter the study export.

## Storage

`clarity.prototype.v1` holds chats/drafts/profile/preferences in browser localStorage. `clarity.study.v1` holds anonymous study records. They are separate stores on each origin. Clear all local data in the researcher console to reset both; downloaded exports remain outside the application.

## Verification

JavaScript syntax: `node --check dist/app.js` (also core.js, store.js and researcher.js).

Browser suite: install Python Playwright (`python -m pip install playwright`) and have Google Chrome installed, then serve `dist/` and run `python tests/browser_smoke.py`. The test uses the standard Windows Chrome path; adjust it if your Chrome is elsewhere. Test screenshots/exports are written to the OS temporary folder, not the website. See `docs/VERIFICATION.md` for the actual validation record.

## Limits

Rules and vocabulary are intentionally bounded; false positives/negatives are expected. No image/document detection. Responses and possible inferences are scripted. Profile reuse is demonstrated through an explicit preview rather than a real memory system. No actual GPT data is accessed or deleted. Automated browser checks do not replace user studies or assistive-technology evaluation. The supplied PDFs and personal interview details are not copied into the website.

The app runs locally or on a static file host. No hosting setup is required to open `dist/index.html`.
