# Clarity — INF2002 Team 08

A static HCI prototype for reviewing personal information before sharing a chat prompt. The application runs entirely in the browser with scripted responses and local storage. No build step, backend, API key or actual GPT connection is required.

## Run locally

From the repository root, start a local server:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open **http://127.0.0.1:4173/** and keep that terminal running. Press **Ctrl+C** in the terminal to stop the server. If `python` is unavailable but the Python launcher is installed, use `py` instead.

You can also open [dist/index.html](dist/index.html) directly in a browser. Use the HTTP server for browser tests and repeatable research sessions across tabs. Keep the participant and researcher tabs on the same address, including the port.

| Page | Local address |
|---|---|
| Participant application | `http://127.0.0.1:4173/` |
| Researcher console | `http://127.0.0.1:4173/researcher.html` |
| Testing guide, consent and task sheets | `http://127.0.0.1:4173/study-guide.html` |
| Design rationale | `http://127.0.0.1:4173/design-notes.html` |

For a static hosting service, use **`dist/` as the publish directory** and include all its files. The application assets are local; using the application does not contact a model or other external service.

## Using the prototype

1. **How it works** opens on every fresh page load, except during a prepared study task. Complete it or choose **Skip tour**. Reopen it using **How it works** below the prompt box. Navigating between application screens does not reopen it automatically.
2. Type a supplied example into **Your prompt**. There are no preset prompt cards.
3. Select an underlined detail or the **Review** control near Send. Choose **Mask information**, **Generalise** where available, **Keep unchanged**, or **Edit manually**. Multiple details can be reviewed together.
4. Use **Undo** to reverse a draft change, then select **Send**. Sending adds the prompt and a scripted response to the conversation.
5. Open the top-left menu or floating shield to access the privacy dashboard, privacy preferences, settings and help. Drafts and conversations survive navigation and reload.

The dashboard supports searching and filtering profile entries, inspecting their source, correcting values, changing reuse rules, deleting, restoring and permanently removing recoverable profile copies. Removing a profile entry leaves its original conversation text intact. Privacy preferences include notice/pause behaviour, detection categories, default reuse and an interactive reuse example; choose **Save preferences** to apply them.

### Example prompts to type

All details below are fictional. With the default detection categories enabled, the examples flag one credential, one neighbourhood, and three name/contact details respectively.

**Debugging an error**

```text
Why does my request return 401? API_KEY = sk-test-FICTIONAL7ALPHA. Please explain the error.
```

After the debugging response, try this follow-up:

```text
Could you show an example?
```

**Finding a place nearby**

```text
Suggest a quiet place to eat near Punggol. I am comfortable sharing this neighbourhood.
```

**Drafting a message**

```text
Help me write a message to my building manager about a leak. My name is Maya Tan, my email is maya@example.test, and my phone is +65 8123 4567. Keep the tone polite.
```

Replies use whole-word keywords for debugging (`401`, `403`, `API`, `error`), local planning (`Punggol`, `nearby`, `restaurant`) and writing (`leak`, `building manager`, `draft`, `message`). A new request takes priority over earlier chat topics. Recognised follow-ups can use the previous prompt; unmatched questions receive a demonstration fallback. Sensitive-detail detection is separate from response selection and follows the category preferences.

The [testing guide](dist/study-guide.html) includes the alternate debugging prompt and full study instructions. The researcher console can print the selected task's exact prompt.

## Display and accessibility controls

- **Dark mode:** use the switch in the top-left navigation menu.
- **Colour accessibility:** open **Settings** and choose **Red–green (protan/deutan)**, **Blue–yellow (tritan)** or **High-contrast neutral**. These display changes apply immediately and are saved in this browser. Use **Reset colour preset** to restore the default palette.
- **Stronger visual cues:** choose this option in **Privacy preferences**, then save. Pending details use wavy underlines; kept details use dotted underlines, so their meaning does not depend on colour alone.
- **Navigation position:** use the direction buttons in **Settings** to move the floating shield. Dragging and **Alt+arrow keys** are also supported.
- **Keyboard:** Tab moves between controls; Enter activates a focused flagged detail; **Ctrl/⌘+Enter** sends; **Alt+R** opens review; **Ctrl/⌘+Z** undoes a composer change; Esc closes a dialog or panel. Enter in the prompt inserts a new line.

The welcome heading, introduction, conversation and prompt use a shared left reading edge to support F-pattern scanning. The [accessibility audit](docs/ACCESSIBILITY-AUDIT.md) records contrast results, colour-vision simulations, layout checks and verification limits. Automated checks support the WCAG 2.2 AA target; they do not certify full conformance.

## Running a research session

1. Serve the application over HTTP and open the participant view and researcher console in separate tabs using the same browser profile and address. Keep the console on the researcher's screen.
2. Obtain consent, enter an anonymous participant code, select think-aloud or timed mode, and choose **Save session setup**.
3. Select the condition and scenario, then choose **Print task sheet** to provide the neutral instruction and fictional text.
4. Choose **Prepare task** and confirm the reset. This replaces the participant workspace with baseline data while preserving research records. The prompt starts empty.
5. The participant selects **Begin task**, types the supplied prompt and completes the task. Chat-task timing includes typing and stops at the first send. Other tasks use **Finish task**. Analyse these timings separately from older trials that began with a prefilled draft.
6. Record the observed outcome and assistance in the console, export JSON/task CSV/event CSV as needed, then stop recording. Reset the participant workspace between sessions.

Study exports omit raw prompt text, detected values, chat content and profile values. Conversation text is still stored separately in the participant workspace. See the [testing guide](dist/study-guide.html) for consent, counterbalancing, success criteria and analysis guidance.

## Verification

Run commands from the repository root. Browser checks require Python, Playwright and an installed Google Chrome:

```powershell
python -m pip install playwright
```

The scripts currently use `C:\Program Files\Google\Chrome\Application\chrome.exe`. If Chrome is elsewhere or you use another operating system, update `executable_path` in the browser test scripts. They launch the installed browser, so a separate Playwright browser download is not required for this configuration.

For axe accessibility scans, download the development copy to the temporary directory:

```powershell
python -c "import pathlib,tempfile,urllib.request; urllib.request.urlretrieve('https://unpkg.com/axe-core@4.10.3/axe.min.js', pathlib.Path(tempfile.gettempdir())/'clarity-axe.min.js')"
```

Keep the local server running in one terminal, then run the following in another:

```powershell
python tests/browser_smoke.py
python tests/edge_checks.py
python tests/accessibility_audit.py
python tests/vision_checks.py
```

| Script | Checks |
|---|---|
| `browser_smoke.py` | Main chat, privacy, research, keyboard, persistence and mobile workflows |
| `edge_checks.py` | Editing/deletion edge cases, research gating, optional axe scans, reflow and mathematical colour-vision checks |
| `accessibility_audit.py` | Requires axe; scans themes, presets and dynamic states, measures text/border/focus contrast, and saves rendered HTML snapshots |
| `vision_checks.py` | Chrome colour-vision simulations, preset persistence and reading alignment at desktop/mobile widths |

To independently cross-check representative rendered colours with WebAIM, run:

```powershell
python tests/vision_checks.py --webaim
```

This optional command needs internet access and sends only foreground/background colour values to WebAIM's documented contrast-checker API. The normal application and vision checks do not need this external service.

For HTML/CSS/SVG validation, download and extract the official Windows runtime from the [Nu checker release page](https://github.com/validator/validator/releases/tag/latest). Run `accessibility_audit.py` first, then point the standards script to the extracted checker:

```powershell
python tests/standards_local.py --checker 'C:\path\to\vnu-runtime-image\bin\vnu.bat'
```

If Node.js is installed, check JavaScript syntax with:

```powershell
Get-ChildItem dist/*.js | ForEach-Object { node --check $_.FullName }
```

Workflow screenshots and sample exports are written to the OS temporary directory `clarity-browser-artifacts`. Accessibility reports, rendered snapshots and colour-vision screenshots go to `clarity-accessibility` in the same temporary directory. Testing dependencies and generated artifacts are not bundled into `dist/`.

See the [verification record](docs/VERIFICATION.md) and [accessibility audit](docs/ACCESSIBILITY-AUDIT.md) for recorded results and remaining manual checks.

## Storage and limits

`clarity.prototype.v1` holds chats, drafts, profile entries and privacy preferences; `clarity.study.v1` holds anonymous study records. Theme, colour preset and shield position are also saved locally. Storage is specific to the browser profile and origin: opening the files directly, changing ports or using a hosted version creates separate stores.

Use **Clear all local study data** in the researcher console to remove study records and restore the fictional participant baseline. This does not remove downloaded files or reset the separately stored display preferences. To reset every local setting as well, clear this site's browser storage.

Detection uses a bounded set of patterns and vocabulary, so false positives and missed details are expected. There is no image/document detection, real model memory, account access or actual GPT data deletion. Responses and inference examples are scripted; reuse is demonstrated through an explicit preview. Local storage is unencrypted. Use fictional details for demonstrations and shared study devices. Automated tests do not replace user studies or manual assistive-technology testing.
