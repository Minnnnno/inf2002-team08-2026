# Accessibility and web standards review

Reviewed on **3 November 2026** using isolated fictional data in Google Chrome through Python Playwright. The target is **WCAG 2.2 Level AA**.

## Changes

- Removed the three preset prompt cards. Participants type the supplied fictional prompts; live sensitive-detail detection remains available as they type.
- Prepared study tasks also start with an empty composer. The researcher console and printable task sheets supply the existing prompts. Timing now includes typing, so these trials must be analysed separately from older prefilled-draft trials.
- Scripted replies use whole-word keywords and give the current request priority over earlier chat topics. Unmatched questions receive the demonstration fallback.
- Replaced dark idle button fills with pale or lighter theme surfaces, contrasting labels, visible borders, distinct hover states and focus rings. Primary and destructive actions retain their semantic colours.
- Corrected invalid inline/block nesting, the unattached composer label, missing group roles, skipped headings, the invalid `main` inside `noscript`, and empty tour name/description references.
- Kept hidden floating-menu items inert and preserved keyboard focus on the review-complete heading after masking.
- Included each flagged value's visible text in its accessible name for speech-input targeting (2.5.3).
- Added **Settings → Navigation position** buttons as a single-pointer alternative to dragging the floating shield.
- Adjusted muted text in light colour presets, removed fading from tab-counter text and mapped high-contrast mode to system colours.

## Contrast checker

`tests/accessibility_audit.py` reads Chrome's computed foreground, fill, border and outline colours. It composites transparent fills, applies the WCAG sRGB relative-luminance formula and compares the unrounded ratios with the thresholds. axe-core separately checks rendered page text. This measures actual theme/preset combinations, rather than assuming that token colours alone establish contrast.

The AA thresholds are **4.5:1 for ordinary text**, **3:1 for large text**, and **3:1 for meaningful control/state indicators against adjacent colours**. The control audit conservatively requires 4.5:1 even for its icon-only controls, and checks borders against both inner and outer surfaces. See [W3C text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [W3C non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

| Default Send button state | Foreground | Fill | Text contrast | AA text result |
|---|---|---|---|---|
| Light, idle | `#1c563e` | `#e7f0e9` | 7.36:1 | Pass |
| Light, hover | `#1c563e` | `#edf5ef` | 7.72:1 | Pass |
| Dark, idle | `#9be7c4` | `#24352c` | 9.02:1 | Pass |
| Dark, hover | `#9be7c4` | `#1e2b24` | 10.25:1 | Pass |

Ratios in the table are rounded for display only. All four visible presets—default, shared red–green, blue–yellow and neutral—are checked in both themes. The older `deutan` setting is also checked for compatibility; it maps to the shared red–green preset. Disabled controls are excluded from contrast thresholds, consistent with WCAG.

## Independent colour checker and colour-vision review

The [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) was queried through its documented API using actual rendered foreground/background hex pairs. **All 24 representative text pairs passed normal-text AA**, covering primary actions, supporting text and warning labels in four visible presets and both themes. The checker independently confirms the local contrast calculations; axe checks the broader set of rendered page states. Only public colour values were sent to WebAIM.

| Theme / preset | Primary action | Supporting text | Warning label | Normal-text AA |
|---|---|---|---|---|
| Light / default | 7.36:1 | 7.00:1 | 5.00:1 | Pass |
| Light / red–green | 8.18:1 | 7.00:1 | 6.27:1 | Pass |
| Light / blue–yellow | 8.39:1 | 7.00:1 | 6.14:1 | Pass |
| Light / neutral | 15.4:1 | 11.2:1 | 13.7:1 | Pass |
| Dark / default | 9.02:1 | 7.29:1 | 9.12:1 | Pass |
| Dark / red–green | 6.97:1 | 7.29:1 | 10.3:1 | Pass |
| Dark / blue–yellow | 7.47:1 | 7.29:1 | 9.32:1 | Pass |
| Dark / neutral | 11.7:1 | 12.8:1 | 14.5:1 | Pass |

Colour-blindness support was already implemented. Settings now labels the options more clearly as **Red–green (protan/deutan)**, **Blue–yellow (tritan)** and **High-contrast neutral**. Selection and persistence passed eight theme/preset combinations.

Chrome's [vision-deficiency emulation](https://developer.chrome.com/docs/devtools/rendering/apply-effects#emulate_vision_deficiencies) was applied to all four presets in both themes: protanopia, deuteranopia, tritanopia and achromatopsia, for **32 rendered simulation states**. Each retains a wavy underline for a pending detail, a dotted underline and accessible label for a kept detail, and labelled review controls. Screenshots were captured for all combinations and representative red–green and greyscale views were inspected. The existing mathematical colour-vision regression also passes for the default palettes. Simulations support visual review; they do not establish that every person with a colour-vision difference will have the same experience.

## F-pattern scanning

The chat heading and introduction are now left-aligned with the conversation and prompt card. The heading supplies the longer first line; the shorter introduction follows; content and review headings continue down a consistent left reading edge. The bottom prompt and How it works control remain easy to revisit. Existing dashboard rows and settings/help sections retain descriptive headings and grouped content.

This applies the practical implications of [NN/g's scanning research](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/): front-load useful information and make headings and related content easy to find. F-scanning is observed reading behaviour, not a WCAG criterion or a requirement to draw a literal F. No eye-tracking outcome is claimed.

Shared heading/introduction/prompt alignment and absence of horizontal overflow passed **eight checks**: both themes at 1440, 768, 390 and 320 CSS pixels. Desktop and mobile screenshots were inspected.

## Checks and scope

| Area | Evidence |
|---|---|
| WCAG A/AA automated checks | axe-core 4.10.3, including WCAG 2.0 A/AA, 2.1 A/AA and 2.2 AA tags; 108 tested states with zero reported violations |
| States covered | Five app routes × two themes × five stored preset values (four visible presets plus the legacy deutan alias); review panels, strong cues, navigation and pause dialogs in every combination; both themes' five tour steps, deletion dialogs and multiple-detail reviews; researcher, study guide, design notes and a forced-colours chat state |
| Text, control boundary and focus contrast | Computed-colour checks pass 4.5:1 text and 3:1 boundary/focus thresholds; includes explicit checks for tab counts and flow text that axe marks for manual review |
| Keyboard and focus | Existing workflow suite checks keyboard detail review, modal close/return, shortcut sending, floating-menu navigation, deletion and undo. Review-complete heading receives focus after masking |
| Dragging alternative, 2.5.7 | Single-click direction controls move the shield; saved position survives reload. Keyboard movement remains available. See [W3C dragging guidance](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) |
| Reflow, 1.4.10 | No horizontal document overflow on all five app routes at 320, 390 and 768 CSS pixels |
| Text spacing, 1.4.12 | No document overflow on all five routes with 1.5 line height, 0.12em letter spacing, 0.16em word spacing and 2em paragraph spacing at the checked desktop width |
| Colour independence, 1.4.1 | Wavy/dotted underlines, textual labels, icons, selected-state indicators and stronger-cue preference remain available; existing colour-vision simulation regression checks pass |
| Motion | Reduced-motion preference is respected. Accessibility scans use reduced motion to measure settled colours; the main workflow suite also runs with ordinary motion |
| HTML, CSS and SVG | Current upstream Nu checker is run locally against source assets and saved rendered DOMs; see commands below |

The final Nu run reported **zero errors and zero warnings across 10 source HTML/CSS/SVG assets and 21 source/rendered HTML snapshots**. Across 920 control measurements, the lowest text contrast was **5.37:1**, the lowest inner-border contrast was **3.56:1** and the lowest outer-border contrast was **3.83:1**. The twenty measured keyboard focus rings were at least **5.18:1** against their outer background. These minimum values are truncated here; assertions use the unrounded values. Another 162 measurements cover tab counters, navigation counters and flow text.

The public W3C Nu service initially validated the source and main rendered routes, then rate-limited requests. The public CSS validator returned HTTP 500. Final standards validation uses the [official current Nu runtime](https://validator.github.io/validator/) locally, which supports HTML, CSS and SVG checking. This avoids depending on the availability of a public service. The older validator.nu hosted instance rejects the valid modern `inert` attribute; its results are not used as the final standards result.

## Reproduce

Serve the existing `dist` directory on port 4173, with the development Playwright and axe-core dependencies described in the existing verification record. The checker runtime is a development tool kept outside the repository; it is not shipped with the site.

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory dist
# In a second terminal:
python tests/browser_smoke.py
python tests/edge_checks.py
python tests/accessibility_audit.py
python tests/vision_checks.py --webaim
python tests/standards_local.py --checker 'C:\path\to\vnu-runtime-image\bin\vnu.bat'
```

The local Nu runtime used for this review is **26.11.3 (93ef029)** from the official `latest` release. Audit results, fictional DOM snapshots and screenshots are saved under the OS temporary directory `clarity-accessibility`. `audit.json` records contrast values, axe violations, checks requiring manual interpretation and browser errors; `vision-checks.json` records WebAIM responses, vision emulations, preset persistence and alignment checks; `standards-local.json` records the separate Nu result. Omit `--webaim` to run the vision/layout checks without contacting the external colour checker.

## Limits

These results support the tested implementation's AA target; they are not a certification of full WCAG conformance. axe's incomplete results are retained rather than silently treated as passes. Hidden menu control relationships are checked through the functional menu tests, and extra computed-colour checks cover the tab counters and flow text. A full assistive-technology review, including NVDA/VoiceOver, physical touch devices, other browsers, all dynamic states and user evaluation, remains necessary. Reflow and text-spacing overflow checks do not prove that every possible content variation is free of clipping.
