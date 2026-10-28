"""Regression checks for editing, deletion, research setup, offline use and accessibility."""
import pathlib,sys,tempfile,json
try:
    from playwright.sync_api import sync_playwright,expect
except ImportError:
    sys.path.insert(0,str(pathlib.Path(tempfile.gettempdir())/'hci-browser-tools'))
    from playwright.sync_api import sync_playwright,expect

base='http://127.0.0.1:4173'
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
    st=page.evaluate('ClarityStore.state()')
    assert not any(x['id']=='memory-location' for x in st['items']+st['removed'])
    assert 'Punggol' in st['chats'][1]['messages'][0]['text']
    page.goto(base+'/#preferences')
    page.locator('[name=category][value=email]').uncheck()
    page.get_by_role('button',name='Save preferences').click()
    page.get_by_role('link',name='Back to chat').click()
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
        assert not violations,json.dumps(violations)
        print('PASS axe WCAG A/AA checks across seven routes (does not establish conformance)')

    page.goto(base)
    for width,height in [(320,568),(390,844),(768,1024)]:
        page.set_viewport_size({'width':width,'height':height})
        for route in ['chat','dashboard','preferences','help']:
            page.goto(base+'/#'+route)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route)
    print('PASS no horizontal page overflow at 320, 390 and 768 CSS pixels')

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
