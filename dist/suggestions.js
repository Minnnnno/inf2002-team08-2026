'use strict';
window.ClaritySuggestions = (() => {
  let api, activeId=null;
  const $=s=>document.querySelector(s);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const key=f=>JSON.stringify([f.category,f.value.toLowerCase()]);
  const ignored=()=>api?.state().ignoredSuggestions||[];
  const isIgnored=f=>ignored().some(x=>x.key===key(f));
  const action=(label,name,id='',primary=false)=>`<button type="button" class="btn compact ${primary?'primary':''}" data-suggestion-action="${name}" data-id="${esc(id)}">${label}</button>`;
  function close(refocus=false){
    const id=activeId;activeId=null;$('#suggestion-popover')?.remove();
    document.querySelectorAll('.suggestion-selected').forEach(el=>el.classList.remove('suggestion-selected'));
    if(refocus){const flag=[...document.querySelectorAll('[data-flag]')].find(el=>el.dataset.flag===id);(flag||$('#composer'))?.focus();}
  }
  function position(){
    const pop=$('#suggestion-popover');if(!pop)return;
    const anchor=[...document.querySelectorAll('[data-flag]')].find(el=>el.dataset.flag===activeId)||[...document.querySelectorAll('[data-suggestion-card]')].find(el=>el.dataset.suggestionCard===activeId);
    if(!anchor){close();return;}
    const r=anchor.getBoundingClientRect(),v=window.visualViewport;
    const left=v?.offsetLeft||0,top=v?.offsetTop||0,width=v?.width||innerWidth,height=v?.height||innerHeight;
    pop.style.maxHeight=Math.max(120,height-24)+'px';
    pop.style.width=Math.min(350,width-24)+'px';
    const h=pop.getBoundingClientRect().height,w=pop.getBoundingClientRect().width;
    pop.style.left=Math.max(left+12,Math.min(r.left,left+width-w-12))+'px';
    pop.style.top=Math.max(top+12,Math.min(r.bottom+8+h<top+height?r.bottom+8:r.top-h-8,top+height-h-12))+'px';
  }
  function open(id){
    const f=api.issues().find(x=>x.id===id);if(!f)return;
    close();activeId=id;api.select(id);
    document.querySelectorAll('[data-flag]').forEach(el=>el.classList.toggle('suggestion-selected',el.dataset.flag===id));
    const card=[...document.querySelectorAll('[data-suggestion-card]')].find(el=>el.dataset.suggestionCard===id);
    card?.classList.add('suggestion-selected');
    const meta=ClarityCore.categories[f.category],pop=document.createElement('section');
    pop.id='suggestion-popover';pop.className='suggestion-popover';pop.setAttribute('role','dialog');pop.setAttribute('aria-labelledby','suggestion-title');
    pop.innerHTML=`<div class="suggestion-popover-heading"><h2 id="suggestion-title">${esc(meta.singular)}</h2><button type="button" class="icon-btn" data-suggestion-action="close" aria-label="Close suggestion">×</button></div><p>${esc(meta.reason)}</p><div class="suggestion-replacement"><del>${esc(f.value)}</del><span aria-hidden="true"> → </span><strong>${esc(f.replacement)}</strong></div><div class="suggestion-actions">${action('Apply','apply',id,true)}${action('Ignore once','once',id)}${action('Ignore always','always',id)}</div><p class="suggestion-hint">Ignore once keeps this occurrence. Ignore always stops warnings for this exact detail in this browser.</p>`;
    document.body.append(pop);position();pop.querySelector('[data-suggestion-action="apply"]').focus();
  }
  function render(){
    close();
    const sidebar=$('#suggestions-sidebar');
    if(sidebar){
      const flags=api.pending();
      sidebar.innerHTML=`<div class="suggestions-heading"><div><span class="eyebrow">LIVE REVIEW</span><h2>Privacy suggestions <span class="suggestions-count">${flags.length}</span></h2></div></div><p class="suggestion-hint">Review details before sharing your prompt.</p>${flags.length?action('Apply all masking suggestions','all','',true):'<div class="suggestions-empty"><strong>No suggestions to review</strong><p>Keep writing. Detection is limited; check your wording before sending.</p></div>'}${Object.entries(ClarityCore.categories).map(([category,meta])=>{
        const group=flags.filter(f=>f.category===category);if(!group.length)return '';
        return `<section class="suggestion-group"><h3>${esc(meta.label)} <span>${group.length}</span></h3>${group.map(f=>`<article class="suggestion-card" data-suggestion-card="${f.id}"><button type="button" class="suggestion-select" data-suggestion-action="select" data-id="${f.id}" aria-label="Review ${esc(meta.singular)}: ${esc(f.value)}"><span class="suggestion-original">${esc(f.value)}</span><span class="suggestion-proposed">${esc(f.replacement)}</span></button><div class="suggestion-actions">${action('Apply','apply',f.id,true)}${action('Ignore once','once',f.id)}${action('Ignore always','always',f.id)}</div></article>`).join('')}</section>`;
      }).join('')}`;
    }
    const form=$('#preferences-form');
    if(form){
      $('#ignored-suggestions')?.remove();
      const section=document.createElement('section');section.id='ignored-suggestions';section.className='setting-card';
      section.innerHTML=`<h2>Ignored details</h2><p>Ignore always suppresses warnings for an exact detail in this browser, across conversations. Restoring warnings takes effect immediately.</p>${ignored().length?ignored().map((x,i)=>`<div class="ignored-detail"><span>${esc(x.value)} <small>(${esc(ClarityCore.categories[x.category]?.label||x.category)})</small></span>${action('Restore warnings','restore',String(i))}</div>`).join(''):'<p>No details are always ignored.</p>'}`;
      form.insertBefore(section,form.querySelector('.save-bar'));
    }
  }
  document.addEventListener('click',e=>{
    const b=e.target.closest('[data-suggestion-action]');if(!b||!api)return;
    const {suggestionAction:a,id}=b.dataset;
    if(a==='close'){close(true);return;}
    if(a==='select'){const flag=[...document.querySelectorAll('[data-flag]')].find(el=>el.dataset.flag===id);flag?.scrollIntoView({block:'nearest'});open(id);return;}
    close();
    if(a==='apply'||a==='once'){api.change(id,a==='apply'?'mask':'keep');$('#composer')?.focus();}
    if(a==='always'){
      const f=api.issues().find(x=>x.id===id);if(!f)return;
      api.state().ignoredSuggestions=[...ignored(),{key:key(f),category:f.category,value:f.value}];api.save();api.refresh();$('#composer')?.focus();api.announce('Warnings disabled for this exact detail. Restore them in Privacy preferences.');
    }
    if(a==='restore'){api.state().ignoredSuggestions=ignored().filter((_,i)=>i!==Number(id));api.save();render();$('#ignored-suggestions h2').tabIndex=-1;$('#ignored-suggestions h2').focus();api.announce('Warnings restored for this detail.');}
    if(a==='all'){
      const flags=api.pending();if(!flags.length)return;
      api.snapshot('Undo masking');api.replace(flags);api.save();api.refresh();$('#composer')?.focus();api.announce(`${flags.length} masking suggestions applied. Use Undo to restore them.`);
    }
  });
  document.addEventListener('pointerdown',e=>{if(activeId&&!e.target.closest('#suggestion-popover, [data-flag], [data-suggestion-card]'))close();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&activeId){e.preventDefault();e.stopImmediatePropagation();close(true);}},true);
  window.addEventListener('resize',position);
  window.addEventListener('scroll',position,true);
  window.visualViewport?.addEventListener('resize',position);
  window.visualViewport?.addEventListener('scroll',position);
  return {configure:config=>api=config,isIgnored,render,open,close};
})();
