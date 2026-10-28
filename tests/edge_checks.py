"""Regression checks for editing, deletion, research setup, offline use and accessibility."""
import pathlib,sys,tempfile,json
try:
    from playwright.sync_api import sync_playwright,expect
except ImportError:
    sys.path.insert(0,str(pathlib.Path(tempfile.gettempdir())/'hci-browser-tools'))
    from playwright.sync_api import sync_playwright,expect

base='http://127.0.0.1:4173'

# Colour-vision deficiency check (Machado et al. 2009, severity 1.0). Status colours must stay
# distinguishable (CIELAB dE >= 15) for protanopia, deuteranopia and tritanopia, and keep 4.5:1.
import math
CVD={'normal':[[1,0,0],[0,1,0],[0,0,1]],
     'protanopia':[[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
     'deuteranopia':[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
     'tritanopia':[[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
def _lin(c):c/=255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def _gam(c):c=min(1,max(0,c));return 255*(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055)
def _hex(h):
    h=h.strip().lstrip('#')
    if len(h)==3:h=''.join(c*2 for c in h)
    return [int(h[i:i+2],16) for i in (0,2,4)]
def _sim(rgb,t):return [_gam(sum(CVD[t][i][j]*_lin(rgb[j]) for j in range(3))) for i in range(3)]
def _lab(rgb):
    r,g,b=[_lin(x) for x in rgb];X=(.4124*r+.3576*g+.1805*b)/.95047;Y=.2126*r+.7152*g+.0722*b;Z=(.0193*r+.1192*g+.9505*b)/1.08883
    f=lambda t:t**(1/3) if t>.008856 else 7.787*t+16/116
    return 116*f(Y)-16,500*(f(X)-f(Y)),200*(f(Y)-f(Z))
def _contrast(a,b):
    L=lambda c:.2126*_lin(c[0])+.7152*_lin(c[1])+.0722*_lin(c[2]);x,y=L(a),L(b);return (max(x,y)+.05)/(min(x,y)+.05)
def cvd_worst(tokens):
    names=list(tokens);return min(math.dist(_lab(_sim(tokens[a],t)),_lab(_sim(tokens[b],t))) for t in CVD for i,a in enumerate(names) for b in names[i+1:])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    ctx=b.new_context(viewport={'width':1440,'height':1000})
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base)
    page.locator('#composer').fill('Ask alex@example.test and alex@example.test about the leak.')
    page.locator('.flag').nth(1).click()
    page.get_by_role('button',name='Keep unchanged',exact=True).click()
    page.get_by_role('button',name='Mask information',exact=True).click()
    expect(page.locator('.flag')).to_have_count(1)
    expect(page.locator('.flag.kept')).to_have_count(1)
    assert '[email address] and alex@example.test' in page.locator('#composer').inner_text()
    page.get_by_role('button',name='Edit manually',exact=True).click()
    page.locator('#composer').press('Home')
    page.locator('#composer').press('Control+Home')
    page.locator('#composer').press_sequentially('Hello. ')
    expect(page.locator('.flag.kept')).to_have_count(1)
    print('PASS repeated identical details retain the correct keep decision after edits')

    page.locator('#composer').fill('Popular restaurants near Punggol Residences Block 5.')
    expect(page.locator('.flag')).to_have_count(1)
    page.locator('.flag').click()
    page.get_by_role('button',name='Generalise to').click()
    assert page.locator('#composer').inner_text()=='Popular restaurants near Punggol.'
    expect(page.locator('.flag.kept')).to_have_count(1)
    page.get_by_role('button',name='Undo generalisation',exact=True).click()
    assert 'Residences Block 5.' in page.locator('#composer').inner_text()
    page.get_by_role('button',name='Edit manually',exact=True).click()
    page.locator('#composer').fill('First line')
    page.locator('#composer').press('End');page.locator('#composer').press('Enter')
    page.locator('#composer').press_sequentially('Second line')
    assert 'First line\nSecond line'==page.locator('#composer').inner_text()
    page.locator('#composer').fill('<img src=x onerror="window.injected=true"> My email is alex@example.test')
    assert page.locator('#composer img').count()==0
    page.get_by_role('button',name='Send',exact=True).click()
    assert not page.evaluate('!!window.injected')
    print('PASS generalisation, punctuation, multiline input and safe text rendering')

    page.goto(base+'/#dashboard')
    page.get_by_role('button',name='Delete Neighbourhood',exact=True).click()
    page.get_by_role('button',name='Delete',exact=True).click()
    page.get_by_role('button',name='Removed 1',exact=True).click()
    page.get_by_role('button',name='Delete permanently',exact=True).click()
    page.locator('#modal').get_by_role('button',name='Delete permanently',exact=True).click()
    expect(page.get_by_role('button',name='Removed 0',exact=True)).to_be_visible()
    st=page.evaluate('ClarityStore.state()')
    assert not any(x['id']=='memory-location' for x in st['items']+st['removed'])
    assert 'Punggol' in st['chats'][1]['messages'][0]['text']
    page.goto(base+'/#preferences')
    page.locator('[name=category][value=email]').uncheck()
    page.get_by_role('button',name='Save preferences').click()
    page.get_by_role('button',name='Open Clarity navigation').click()
    page.get_by_role('menuitem',name='Chat').click()
    page.locator('#composer').fill('Contact alex@example.test')
    expect(page.locator('.flag')).to_have_count(0)
    print('PASS permanent profile deletion preserves source chat; category toggles work')

    research=ctx.new_page();research.goto(base+'/researcher.html')
    research.locator('#consent').check();research.get_by_role('button',name='Save session setup').click()
    research.get_by_role('button',name='Prepare task',exact=True).click()
    research.locator('#modal').get_by_role('button',name='Prepare task',exact=True).click()
    expect(page.get_by_role('button',name='Begin task')).to_be_visible()
    assert page.locator('#main').evaluate('(e)=>e.inert')
    assert not page.evaluate('ClarityStore.study().events.length')
    page.get_by_role('button',name='Begin task').click()
    assert not page.locator('#main').evaluate('(e)=>e.inert')
    research.get_by_role('button',name='Stop recording',exact=True).click()
    assert not page.evaluate('ClarityStore.study().consent')
    print('PASS task controls gated until Begin; stopping logging closes the task')

    violations=[]
    axe=pathlib.Path(tempfile.gettempdir())/'clarity-axe.min.js'
    if axe.exists():
        for path in ['/#chat','/#dashboard','/#preferences','/#help','/researcher.html','/study-guide.html','/design-notes.html']:
            page.goto(base+path)
            page.add_script_tag(path=str(axe))
            v=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}));}')
            if v: violations.append({'path':path,'violations':v})
        page.goto(base+'/#chat');page.evaluate("document.documentElement.classList.add('cues-strong')")
        page.get_by_role('button',name='Draft a message').click()
        page.add_script_tag(path=str(axe))
        v=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return r.violations.map(v=>v.id)}')
        if v: violations.append({'path':'chat (stronger cues)','violations':v})
        page.evaluate("localStorage.setItem('clarity.theme','dark')")
        for path in ['/#chat','/#dashboard','/#preferences','/#help']:
            page.goto(base+path);page.reload();page.wait_for_timeout(400)
            page.add_script_tag(path=str(axe))
            v=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}});return r.violations.map(v=>v.id)}')
            if v: violations.append({'path':path+' (dark)','violations':v})
        page.evaluate("localStorage.removeItem('clarity.theme')")
        assert not violations,json.dumps(violations)
        print('PASS axe WCAG A/AA checks across seven routes (does not establish conformance)')

    page.set_viewport_size({'width':1440,'height':1000})
    for route in ['chat','dashboard','preferences','help']:
        page.goto(base+'/#'+route)
        tiny=page.evaluate('''()=>[...document.querySelectorAll('body *')].filter(e=>[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&e.getClientRects().length&&parseFloat(getComputedStyle(e).fontSize)<12).map(e=>e.textContent.trim().slice(0,30))''')
        assert not tiny,(route,tiny)
    print('PASS no visible text below 12px on the four main routes')

    page.goto(base)
    for width,height in [(320,568),(390,844),(768,1024)]:
        page.set_viewport_size({'width':width,'height':height})
        for route in ['chat','dashboard','preferences','help']:
            page.goto(base+'/#'+route)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route)
    print('PASS no horizontal page overflow at 320, 390 and 768 CSS pixels')

    for theme in ['light','dark']:
        page.goto(base+'/#chat');page.evaluate(f"localStorage.setItem('clarity.theme','{theme}')");page.reload()
        v=page.evaluate("()=>{const c=getComputedStyle(document.documentElement);return ['--accent','--warning','--danger','--surface','--bg'].map(k=>c.getPropertyValue(k).trim())}")
        tokens={'accent':_hex(v[0]),'warning':_hex(v[1]),'danger':_hex(v[2])};surface=_hex(v[3] or v[4])
        worst=cvd_worst(tokens)
        assert worst>=15,(theme,'status colours too similar under colour-vision deficiency',round(worst,1))
        for k,c in tokens.items():assert _contrast(c,surface)>=4.5,(theme,k,round(_contrast(c,surface),2))
        print(f'PASS {theme}: status colours distinguishable for protanopia/deuteranopia/tritanopia (worst dE {worst:.1f}), all >= 4.5:1')
    page.evaluate("localStorage.removeItem('clarity.theme')")

    for f in ['index.html','researcher.html','study-guide.html','design-notes.html','styles.css','docs.css','core.js','store.js','app.js','researcher.js','favicon.svg']:
        assert ctx.request.get(base+'/'+f).status==200,f
    local=(pathlib.Path(__file__).resolve().parents[1]/'dist'/'index.html').as_uri()
    page.goto(local)
    page.get_by_role('button',name='Debug an error').click()
    page.get_by_role('button',name='1 detail to review').click()
    page.get_by_role('button',name='Mask information',exact=True).click()
    page.get_by_role('button',name='Send',exact=True).click()
    expect(page.locator('.message.assistant')).to_have_count(1)
    assert not errors,errors
    print('PASS all static resources, direct file opening and zero browser errors')
    b.close()
