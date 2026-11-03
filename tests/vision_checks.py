"""Colour-vision emulation, reading alignment, and optional WebAIM cross-check.

Serve dist on port 4173. --webaim sends only public colour hex pairs to WebAIM's
documented contrast-checker API; it sends no page contents or user data.
"""
import argparse, json, pathlib, sys, tempfile, time, urllib.request

try:
    from playwright.sync_api import sync_playwright, expect
except ImportError:
    sys.path.insert(0, str(pathlib.Path(tempfile.gettempdir())/'hci-browser-tools'))
    from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:4173')
parser.add_argument('--webaim', action='store_true')
args = parser.parse_args()
out = pathlib.Path(tempfile.gettempdir())/'clarity-accessibility'
out.mkdir(exist_ok=True)
report = {'vision':[], 'alignment':[], 'presets':[], 'webaim':[]}
colour_pairs = []

PAIR = '''selector=>{
 const e=document.querySelector(selector),s=getComputedStyle(e);
 const rgb=s=>s.match(/[\\d.]+/g).map(Number);
 const blend=(a,b)=>{const t=a.length>3?a[3]:1;return a.slice(0,3).map((v,i)=>v*t+b[i]*(1-t))};
 const bg=e=>e?blend(rgb(getComputedStyle(e).backgroundColor),bg(e.parentElement)):[255,255,255];
 const hex=c=>c.map(v=>Math.round(v).toString(16).padStart(2,'0')).join('').toUpperCase();
 return {foreground:hex(blend(rgb(s.color),bg(e))),background:hex(bg(e))};
}'''

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    context.add_init_script("document.addEventListener('DOMContentLoaded',()=>document.querySelector('.guided-tour[open] [data-tour=close]')?.click(),{once:true})")
    page=context.new_page()
    cdp=context.new_cdp_session(page)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(args.url+'/#settings')
    options=page.locator('#colour-preset option').evaluate_all('(items)=>items.map(e=>e.value)')
    assert options==['default','protan','tritan','neutral'],options

    for theme in ['light','dark']:
        page.evaluate('(t)=>localStorage.setItem("clarity.theme",t)',theme)
        for preset in options:
            page.goto(args.url+'/#settings');page.reload()
            page.get_by_label('Colour-vision support preset').select_option(preset)
            page.reload()
            expect(page.locator('#colour-preset')).to_have_value(preset)
            assert page.evaluate('document.documentElement.dataset.colourPreset')==preset
            report['presets'].append({'theme':theme,'preset':preset,'selectionAndPersistence':'pass'})
            page.goto(args.url+'/#chat')
            page.locator('#composer').fill('')
            page.locator('#composer').fill('Ask alex@example.test and alex@example.test about the leak.')
            page.locator('.flag').nth(1).click()
            page.get_by_role('button',name='Keep unchanged',exact=True).click()
            expect(page.locator('.flag.kept')).to_have_count(1)
            expect(page.locator('.flag:not(.kept)')).to_have_count(1)
            for mode in ['protanopia','deuteranopia','tritanopia','achromatopsia']:
                cdp.send('Emulation.setEmulatedVisionDeficiency',{'type':mode})
                styles=page.evaluate('''()=>({pending:getComputedStyle(document.querySelector('.flag:not(.kept)')).textDecorationStyle,kept:getComputedStyle(document.querySelector('.flag.kept')).textDecorationStyle})''')
                assert styles=={'pending':'wavy','kept':'dotted'},(theme,preset,mode,styles)
                assert 'kept unchanged' in page.locator('.flag.kept').get_attribute('aria-label')
                expect(page.get_by_role('button',name='1 detail to review')).to_be_visible()
                expect(page.get_by_role('button',name='Mask information',exact=True)).to_be_visible()
                expect(page.get_by_role('button',name='Keep unchanged',exact=True)).to_be_visible()
                page.screenshot(path=str(out/f'vision-{theme}-{preset}-{mode}.png'),full_page=True)
                report['vision'].append({'theme':theme,'preset':preset,'simulation':mode,'nonColourCues':'pass'})
            cdp.send('Emulation.setEmulatedVisionDeficiency',{'type':'none'})
            for name,selector in [('Primary action','.review-actions .btn.primary'),('Supporting text','.review-copy p'),('Warning label','.badge.amber')]:
                pair=page.evaluate(PAIR,selector)
                colour_pairs.append({'theme':theme,'preset':preset,'element':name,**pair})
            page.get_by_role('button',name='Open Clarity navigation').click()
            expect(page.get_by_role('menuitem',name='Settings',exact=True)).to_be_visible()
            page.keyboard.press('Escape')

        # A real left-to-right reading column, not an ornamental letter F.
        page.evaluate("localStorage.setItem('clarity.colourPreset','default');localStorage.removeItem(ClarityStore.STATE)")
        for width in [1440,768,390,320]:
            page.set_viewport_size({'width':width,'height':1000})
            page.goto(args.url+'/#chat');page.reload()
            boxes={name:page.locator(selector).bounding_box() for name,selector in [('heading','.welcome h2'),('lead','.welcome > p'),('prompt','.composer-box')]}
            assert abs(boxes['heading']['x']-boxes['lead']['x'])<2,(theme,width,boxes)
            assert abs(boxes['heading']['x']-boxes['prompt']['x'])<2,(theme,width,boxes)
            assert page.locator('.welcome').evaluate('(e)=>getComputedStyle(e).textAlign')=='left'
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            if width==1440:
                lengths=page.evaluate('''()=>['.welcome h2','.welcome > p'].map(s=>{const r=document.createRange();r.selectNodeContents(document.querySelector(s));return r.getBoundingClientRect().width})''')
                assert lengths[0]>lengths[1],lengths
                page.screenshot(path=str(out/f'scanning-{theme}-desktop.png'),full_page=True)
            if width==320:
                page.screenshot(path=str(out/f'scanning-{theme}-mobile.png'),full_page=True)
            report['alignment'].append({'theme':theme,'width':width,'sharedLeftEdge':'pass','overflow':False})
        page.set_viewport_size({'width':1440,'height':1000})
    assert not errors,errors
    browser.close()

if args.webaim:
    cache={}
    for pair in colour_pairs:
        fg,bg=pair['foreground'],pair['background']
        key=fg+'/'+bg
        if key not in cache:
            url=f'https://webaim.org/resources/contrastchecker/?fcolor={fg}&bcolor={bg}&api'
            with urllib.request.urlopen(url,timeout=30) as response:
                cache[key]=json.load(response)
            time.sleep(1)
        result=cache[key]
        report['webaim'].append({**pair,'result':result})
        print('WebAIM',pair['theme'],pair['preset'],pair['element'],result,flush=True)

(out/'vision-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert all(row['result']['AA']=='pass' for row in report['webaim']),report['webaim']
print('PASS',len(report['vision']),'vision states,',len(report['alignment']),'layout checks,',len(report['presets']),'preset persistence checks,',len(report['webaim']),'WebAIM pairs')
