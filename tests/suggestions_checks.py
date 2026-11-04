"""Live privacy suggestions regression checks against the local server."""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(tempfile.gettempdir()) / 'hci-browser-tools'))
from playwright.sync_api import sync_playwright, expect

BASE = 'http://127.0.0.1:4173'
OUT = pathlib.Path(tempfile.gettempdir()) / 'clarity-browser-artifacts'
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.add_init_script("document.addEventListener('DOMContentLoaded',()=>document.querySelector('.guided-tour[open] [data-tour=close]')?.click(),{once:true})")
    page.goto(BASE)
    composer = page.locator('#composer')
    sidebar = page.locator('#suggestions-sidebar')
    composer.fill('Email alex@example.test or alex@example.test. My name is Maya Tan.')
    expect(sidebar.locator('.suggestion-card')).to_have_count(3)
    expect(sidebar.locator('.suggestion-group')).to_have_count(2)
    expect(page.locator('#prompt-warning')).to_be_visible()
    assert sidebar.bounding_box()['x'] >= page.locator('.chat-main').bounding_box()['width']
    page.locator('.flag').first.click()
    popover = page.get_by_role('dialog', name='Email address')
    expect(popover).to_be_visible()
    page.screenshot(path=str(OUT / 'suggestions-desktop.png'), full_page=True)
    page.keyboard.press('Escape')
    expect(popover).to_have_count(0)
    expect(page.locator('.flag').first).to_be_focused()
    page.locator('.flag').first.press('Enter')
    popover.get_by_role('button', name='Ignore once', exact=True).click()
    expect(sidebar.locator('.suggestion-card')).to_have_count(2)
    expect(page.locator('.flag.kept')).to_have_count(1)
    page.reload()
    expect(sidebar.locator('.suggestion-card')).to_have_count(2)
    sidebar.get_by_role('button', name='Apply all masking suggestions', exact=True).click()
    expect(sidebar.locator('.suggestion-card')).to_have_count(0)
    assert composer.inner_text().count('alex@example.test') == 1
    assert 'Maya Tan' not in composer.inner_text()
    page.get_by_role('button', name='Undo masking', exact=True).click()
    expect(sidebar.locator('.suggestion-card')).to_have_count(2)
    print('PASS live grouping, desktop layout, keyboard popover, occurrence ignore, apply all and undo')

    composer.fill('Email private@example.test about the error.')
    sidebar.locator('.suggestion-select').click()
    expect(page.locator('.flag.suggestion-selected')).to_have_count(1)
    popover.get_by_role('button', name='Ignore always', exact=True).click()
    expect(sidebar.locator('.suggestion-card')).to_have_count(0)
    page.reload()
    expect(sidebar.locator('.suggestion-card')).to_have_count(0)
    page.goto(BASE + '/#preferences')
    expect(page.locator('#ignored-suggestions')).to_contain_text('private@example.test')
    page.get_by_role('button', name='Restore warnings', exact=True).click()
    page.goto(BASE + '/#chat')
    expect(sidebar.locator('.suggestion-card')).to_have_count(1)
    sidebar.get_by_role('button', name='Apply', exact=True).click()
    expect(composer).to_have_text('Email [email address] about the error.')
    expect(page.locator('#prompt-warning')).to_be_hidden()
    page.get_by_role('button', name='Undo masking', exact=True).click()
    page.goto(BASE + '/#preferences')
    page.locator('[name=category][value=email]').uncheck()
    page.get_by_role('button', name='Save preferences', exact=True).click()
    page.goto(BASE + '/#chat')
    expect(sidebar.locator('.suggestion-card')).to_have_count(0)
    print('PASS persistent exact-detail ignore, restore warnings, apply, and detection preferences')

    mobile_context = browser.new_context(viewport={'width': 390, 'height': 844})
    mobile = mobile_context.new_page()
    mobile.on('pageerror', lambda e: errors.append(str(e)))
    mobile.add_init_script("document.addEventListener('DOMContentLoaded',()=>document.querySelector('.guided-tour[open] [data-tour=close]')?.click(),{once:true})")
    mobile.goto(BASE)
    mobile.locator('#composer').fill('Contact maya@example.test.')
    mobile.locator('.flag').click()
    box = mobile.locator('#suggestion-popover').bounding_box()
    assert box['x'] >= 0 and box['x'] + box['width'] <= 390
    assert box['y'] >= 0 and box['y'] + box['height'] <= 844
    mobile.screenshot(path=str(OUT / 'suggestions-mobile.png'), full_page=True)
    mobile.get_by_role('dialog').get_by_role('button', name='Apply', exact=True).click()
    expect(mobile.locator('#suggestions-sidebar .suggestion-card')).to_have_count(0)
    assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
    mobile.set_viewport_size({'width': 320, 'height': 740})
    assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors, errors
    print('PASS mobile popover placement, apply, 320px reflow and no browser errors')
    browser.close()
