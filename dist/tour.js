'use strict';
(() => {
  const steps = [
    ['Your message, your choice', 'Write your request here. Clarity checks for potentially personal information as you type. This tour uses a fictional email; nothing is sent or saved.', 'prompt'],
    ['Notice a personal detail', 'Underlined text is a detail worth reviewing. Select the example email to see why it was flagged. No matches does not mean a message is safe.', 'detail'],
    ['Choose what to share', 'An email address may be unnecessary for drafting a message. Try Mask information below. Keep unchanged is also your choice in a real chat.', 'review'],
    ['Change your mind', 'Masking replaces the detail in your draft. Try Undo masking to restore it. Draft changes can be reversed before sending.', 'undo'],
    ['Find your privacy dashboard', 'Open Privacy dashboard from navigation or the floating shield. It shows details recorded by this prototype and controls for reuse. It cannot access actual AI account data.', 'dashboard']
  ];
  const dialog = document.createElement('dialog');
  dialog.className = 'guided-tour';
  dialog.setAttribute('aria-labelledby', 'tour-title');
  dialog.setAttribute('aria-describedby', 'tour-description');
  document.body.append(dialog);
  let step = 0, masked = false, returnFocus;
  const SEEN_KEY = 'clarity.guidedTour.seen.v1';
  let shownThisVisit = false;
  function startTour(trigger) {
    if (dialog.open) return;
    returnFocus = trigger; step = 0; masked = false;
    dialog.showModal(); render();
    shownThisVisit = true;
    try { localStorage.setItem(SEEN_KEY, 'true'); } catch { /* Still show only once in this tab if storage is unavailable. */ }
  }
  function offerFirstVisitTour() {
    if (shownThisVisit || (location.hash && location.hash !== '#chat') || ClarityStore.study().active) return;
    try { if (localStorage.getItem(SEEN_KEY) === 'true') return; } catch { /* Practice can run without storage. */ }
    startTour(document.querySelector('[data-action="start-tour"]') || document.querySelector('#composer'));
  }
  function render() {
    const [title, description, target] = steps[step];
    const spot = name => target === name ? ' tour-spotlight' : '';
    dialog.innerHTML = `<div class="tour-layout"><div class="tour-demo" aria-label="Fictional practice screen">
      <div class="tour-demo-header"><strong>Clarity</strong><span class="badge">Practice only</span></div>
      <div class="tour-demo-body"><div class="tour-dashboard${spot('dashboard')}"><strong>Privacy dashboard</strong><p>Shared in chats · Saved preferences · Possible inferences</p></div>
      <h2>What would you like help with?</h2><p class="muted">Learn the controls with a fictional example.</p>
      <section class="tour-review${spot('review')}" ${step < 2 ? 'hidden' : ''}><strong>Email address detected</strong><p>A draft usually does not need your email. You can add it yourself later.</p><div class="tour-example-actions"><button type="button" class="btn primary" data-tour="mask">Mask information</button><button type="button" class="btn" data-tour="keep">Keep unchanged</button></div></section>
      <div class="tour-prompt${spot('prompt')}"><strong>Your prompt</strong><p>My email is ${masked ? '<span class="tour-replacement">[email]</span>' : `<button type="button" class="tour-detail${spot('detail')}" data-tour="detail">alex@example.com</button>`}. Help me write a job application.</p><span class="muted">Example only — sending is disabled during practice.</span></div>
      <div class="tour-undo${spot('undo')}" ${step < 3 ? 'hidden' : ''}><button type="button" class="btn" data-tour="undo" ${masked ? '' : 'disabled'}>Undo masking</button><span>${masked ? 'Your email has been replaced with a placeholder.' : 'The original email is restored.'}</span></div>
      <p id="tour-result" role="status"></p></div></div>
      <section class="tour-card"><span class="eyebrow">Guided tour · ${step + 1} of ${steps.length}</span><h2 id="tour-title" tabindex="-1">${title}</h2><p id="tour-description">${description}</p><div class="tour-progress" aria-hidden="true">${steps.map((_, i) => `<span class="${i === step ? 'current' : ''}"></span>`).join('')}</div><div class="tour-controls"><button type="button" class="btn ghost" data-tour="close">Skip tour</button><button type="button" class="btn" data-tour="back" ${step === 0 ? 'disabled' : ''}>Back</button><button type="button" class="btn primary" data-tour="next">${step === 4 ? 'Finish' : 'Next'}</button></div><small class="muted">Press Esc to leave. Your original draft stays unchanged.</small></section></div>`;
    dialog.querySelector('#tour-title').focus();
  }
  function close() { dialog.close(); if (returnFocus?.isConnected) returnFocus.focus(); }
  document.addEventListener('click', event => {
    const start = event.target.closest('[data-action="start-tour"]');
    if (!start) return;
    // Practice must not coach participants in the middle of a prepared study.
    if (ClarityStore.study().active) { window.alert('Finish or clear the study task before starting the practice tour.'); return; }
    startTour(start);
  });
  dialog.addEventListener('click', event => {
    const action = event.target.closest('[data-tour]')?.dataset.tour;
    if (!action) return;
    if (action === 'close' || (action === 'next' && step === 4)) { close(); return; }
    if (action === 'next') { step++; if (step === 3) masked = true; }
    if (action === 'back') { step--; masked = step === 3; }
    if (action === 'detail') step = 2;
    if (action === 'mask') { masked = true; step = 3; }
    if (action === 'undo') masked = false;
    if (action === 'keep') { dialog.querySelector('#tour-result').textContent = 'Kept unchanged. You can decide which details are useful for your request.'; return; }
    render();
  });
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  // Keep app-wide shortcuts from changing the real draft behind the tour.
  window.addEventListener('keydown', event => { if (dialog.open) event.stopPropagation(); }, true);
  window.addEventListener('hashchange', () => { if (dialog.open) close(); offerFirstVisitTour(); });
  offerFirstVisitTour();
})();
