"""Rendered WCAG 2.2 AA, control contrast, reflow, and saved DOM snapshots.

Serve dist on port 4173 first. Uses the existing development Playwright/axe copies.
Artifacts go to the OS temporary directory. Follow with standards_local.py to
validate source HTML/CSS/SVG and captured fictional DOMs using the Nu checker.
"""
import argparse, json, pathlib, sys, tempfile

try:
    from playwright.sync_api import sync_playwright, expect
except ImportError:
    sys.path.insert(0, str(pathlib.Path(tempfile.gettempdir()) / 'hci-browser-tools'))
    from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:4173')
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
out = pathlib.Path(tempfile.gettempdir()) / 'clarity-accessibility'
out.mkdir(exist_ok=True)
axe = pathlib.Path(tempfile.gettempdir()) / 'clarity-axe.min.js'
assert axe.exists(), 'Install a development copy of axe-core at ' + str(axe)
report = {'axeVersion': None, 'scans': [], 'contrast': [], 'checks': []}
documents = {p.name: p.read_text(encoding='utf-8') for p in (root / 'dist').glob('*.html')}
errors = []

CONTRAST = r'''selector => {
  const rgb = s => (s.match(/[\d.]+/g)||[]).map(Number);
  const blend = (a,b) => { const t = a.length>3 ? a[3] : 1; return a.slice(0,3).map((v,i)=>v*t+b[i]*(1-t)); };
  const background = e => {
    if(!e) return [255,255,255];
    // The active filter is drawn over its absolutely positioned sliding indicator.
    const indicator=e.matches('.tabs .tab.active') ? e.parentElement.querySelector('.tab-indicator') : null;
    const under=indicator ? blend(rgb(getComputedStyle(indicator).backgroundColor),background(e.parentElement)) : background(e.parentElement);
    return blend(rgb(getComputedStyle(e).backgroundColor),under);
  };
  const luminance = c => c.map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const ratio = (a,b) => {const x=luminance(a), y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
  return [...document.querySelectorAll(selector)].filter(e=>e.getClientRects().length&&!e.disabled).map(e=>{
    const c=getComputedStyle(e), bg=background(e), outside=background(e.parentElement);
    return {name:e.getAttribute('aria-label')||e.textContent.trim(), selector:e.id?'#'+e.id:e.className,
      foreground:c.color,background:bg,border:c.borderTopColor,
      textRatio:ratio(blend(rgb(c.color),bg),bg),
      borderInside:ratio(rgb(c.borderTopColor),bg),borderOutside:ratio(rgb(c.borderTopColor),outside),
      focusRatio:ratio(rgb(c.outlineColor),outside),outlineStyle:c.outlineStyle};
  });
}'''

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    ctx.add_init_script("document.addEventListener('DOMContentLoaded',()=>document.querySelector('.guided-tour[open] [data-tour=close]')?.click(),{once:true})")
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))

    def snapshot():
        # Validate application markup, excluding scripts injected by the audit tool.
        return '<!doctype html>' + page.evaluate('''()=>{const c=document.documentElement.cloneNode(true);c.querySelectorAll('script:not([src])').forEach(e=>{if(e.textContent.includes('axe'))e.remove()});return c.outerHTML}''')

    def scan(label):
        if not page.evaluate('!!window.axe'):
            page.add_script_tag(path=str(axe))
        result = page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:r.incomplete.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}}''')
        report['axeVersion'] = result.pop('version')
        report['scans'].append({'state':label, **result})
        print('SCAN', label, 'violations:', len(result['violations']), flush=True)

    def control_check(label, state='idle'):
        # Text/icon foreground provides identification; bordered controls are additionally measured.
        for row in page.evaluate(CONTRAST, '.btn, .icon-btn, .nav-fab, .colour-primary-sample'):
            row.update(state=label, interaction=state)
            report['contrast'].append(row)
        for row in page.evaluate(CONTRAST, '.tab-count, .flow, .nav-fab-count'):
            row.update(state=label, interaction=state, textOnly=True)
            report['contrast'].append(row)

    page.goto(args.url)
    assert page.locator('.suggestion').count() == 0
    # Exercise real keystrokes so live detection and caret restoration are covered.
    page.locator('#composer').press_sequentially('API_KEY = sk-test-FICTIONAL7ALPHA', delay=5)
    expect(page.locator('.flag')).to_have_count(1)
    page.locator('#composer').fill('')
    assert page.evaluate("ClarityCore.promptTopic('My keyboard is broken')") is None
    for scenario, expected in [('maskA', 'Authorization header'), ('retain', 'Willow Table'), ('multiple', 'water leak')]:
        prompt = page.evaluate('(s)=>ClarityCore.scenarios[s].prompt', scenario)
        page.locator('#composer').fill(prompt)
        page.get_by_role('button', name='Send', exact=True).click()
        assert expected in page.locator('.message.assistant').last.inner_text()
    page.locator('#composer').fill('What is the capital of France?')
    page.locator('#composer').press('Control+Enter')
    assert 'scripted demonstration' in page.locator('.message.assistant').last.inner_text()
    report['checks'].append('Typed detection, keyword selection, topic switching and unmatched fallback passed')
    page.evaluate("localStorage.removeItem(ClarityStore.STATE)")
    page.reload()

    for theme in ['light', 'dark']:
        for preset in ['default', 'protan', 'deutan', 'tritan', 'neutral']:
            page.evaluate('([t,p])=>{localStorage.setItem("clarity.theme",t);localStorage.setItem("clarity.colourPreset",p)}', [theme,preset])
            for route in ['chat', 'dashboard', 'preferences', 'settings', 'help']:
                page.goto(args.url + '/#' + route)
                page.reload()
                label = f'{theme}/{preset}/{route}'
                scan(label)
                control_check(label)
                if theme == 'light' and preset == 'default':
                    documents['rendered-' + route + '.html'] = snapshot()
            page.goto(args.url + '/#chat')
            page.locator('#composer').fill('My email is alex@example.test. Help me write about the leak.')
            page.get_by_role('button', name='1 detail to review').click()
            scan(f'{theme}/{preset}/review')
            control_check(f'{theme}/{preset}/review')
            page.evaluate("document.documentElement.classList.add('cues-strong')")
            scan(f'{theme}/{preset}/strong-cues')
            page.evaluate("document.documentElement.classList.remove('cues-strong')")
            if preset == 'default':
                page.screenshot(path=str(out / f'review-{theme}.png'), full_page=True)
                documents[f'rendered-review-{theme}.html'] = snapshot()
            send = page.get_by_role('button', name='Send', exact=True)
            send.hover()
            page.wait_for_timeout(180)
            control_check(f'{theme}/{preset}/send', 'hover')
            send.focus()
            # Use keyboard input to make :focus-visible apply.
            page.keyboard.press('Tab')
            page.keyboard.press('Shift+Tab')
            control_check(f'{theme}/{preset}/send', 'focus')
            page.get_by_role('button', name='Open Clarity navigation').click()
            scan(f'{theme}/{preset}/navigation')
            page.keyboard.press('Escape')
            # Pause dialog exercises primary, secondary and close buttons.
            page.evaluate("(()=>{const s=ClarityStore.state();s.prefs.warningMode='pause';ClarityStore.saveState(s)})()")
            page.reload()
            page.get_by_role('button', name='Send', exact=True).click()
            scan(f'{theme}/{preset}/send-dialog')
            control_check(f'{theme}/{preset}/send-dialog')
            if theme == 'light' and preset == 'default':
                documents['rendered-send-dialog.html'] = snapshot()
            page.get_by_role('button', name='Back to draft', exact=True).click()
            page.evaluate("(()=>{const s=ClarityStore.state();s.prefs.warningMode='notice';ClarityStore.saveState(s)})()")
            page.reload()
            page.locator('#composer').fill('')

        # Guided practice and destructive actions in both themes.
        page.evaluate("localStorage.setItem('clarity.colourPreset','default')")
        page.goto(args.url + '/#help'); page.reload()
        page.get_by_role('button', name='Show me around', exact=True).click()
        for step in range(5):
            scan(f'{theme}/tour-{step+1}')
            if step == 2:
                documents[f'rendered-tour-{theme}.html'] = snapshot()
            page.get_by_role('button', name='Finish' if step == 4 else 'Next', exact=True).click()
        page.goto(args.url + '/#dashboard')
        page.get_by_role('button', name='Delete Neighbourhood', exact=True).click()
        scan(f'{theme}/delete-dialog'); control_check(f'{theme}/delete-dialog')
        documents[f'rendered-delete-{theme}.html'] = snapshot()
        page.get_by_role('button', name='Cancel', exact=True).click()
        page.goto(args.url + '/#chat')
        page.locator('#composer').fill(page.evaluate('ClarityCore.scenarios.multiple.prompt'))
        page.get_by_role('button', name='3 details to review').click()
        scan(f'{theme}/multiple-details')
        documents[f'rendered-multiple-{theme}.html'] = snapshot()

    for path in ['researcher.html', 'study-guide.html', 'design-notes.html']:
        page.goto(args.url + '/' + path)
        scan(path)
        documents['rendered-' + path] = snapshot()

    page.goto(args.url + '/#chat')
    for width in [320, 390, 768]:
        page.set_viewport_size({'width': width, 'height': 844})
        for route in ['chat', 'dashboard', 'preferences', 'settings', 'help']:
            page.goto(args.url + '/#' + route)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route)
    report['checks'].append('No document overflow on five routes at 320, 390 and 768 CSS pixels')
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto(args.url + '/#chat')
    page.add_style_tag(content='* { line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important } p {margin-bottom:2em!important}')
    for route in ['chat', 'dashboard', 'preferences', 'settings', 'help']:
        page.goto(args.url + '/#' + route)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('text spacing', route)
    report['checks'].append('WCAG text-spacing overrides cause no document overflow on five routes')
    page.reload()
    page.goto(args.url + '/#settings')
    before = page.locator('.nav-fab').bounding_box()
    page.get_by_role('button', name='Move up', exact=True).click()
    after = page.locator('.nav-fab').bounding_box()
    assert after['y'] < before['y']
    page.reload()
    assert abs(page.locator('.nav-fab').bounding_box()['y'] - after['y']) < 2
    report['checks'].append('Navigation moves with a single click and persists after reload (drag alternative)')
    page.goto(args.url + '/#chat')
    page.emulate_media(forced_colors='active')
    scan('forced-colors/chat')
    browser.close()

(out / 'documents.json').write_text(json.dumps(documents), encoding='utf-8')
report['browserErrors'] = errors
(out / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Report:', out / 'audit.json', flush=True)
failures = [r for r in report['scans'] if r['violations']]
contrast_failures = [r for r in report['contrast'] if r['textRatio'] < 4.5]
border_failures = [r for r in report['contrast'] if not r.get('textOnly') and min(r['borderInside'],r['borderOutside']) < 3]
focus_failures = [r for r in report['contrast'] if r['outlineStyle']=='solid' and r['focusRatio'] < 3]
print('FAILED STATES:', json.dumps(failures), flush=True)
print('FAILED TEXT CONTRAST:', json.dumps(contrast_failures), flush=True)
print('FAILED CONTROL BORDERS:', json.dumps(border_failures), flush=True)
print('FAILED FOCUS CONTRAST:', json.dumps(focus_failures), flush=True)
assert not errors and not failures and not contrast_failures and not border_failures and not focus_failures
