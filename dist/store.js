'use strict';
window.ClarityStore = (() => {
  const C=ClarityCore, STATE='clarity.prototype.v1', STUDY='clarity.study.v1';
  const memory={}; let storageProblem=false;
  function read(key,fallback) { try { const raw=localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback(); } catch { storageProblem=true; return memory[key] ? C.clone(memory[key]) : fallback(); } }
  function write(key,value) { memory[key]=C.clone(value); try { localStorage.setItem(key,JSON.stringify(value)); } catch { storageProblem=true; window.dispatchEvent(new Event('clarity-storage-error')); } }
  const emptyStudy=()=>({version:1,consent:false,participant:'P01',mode:'thinkaloud',condition:'inline',scenario:'maskA',active:null,events:[],trials:[]});
  function state(){const s=read(STATE,C.seed);if(s?.version===1&&Array.isArray(s.chats)&&s.chats.length&&s.prefs?.categories&&Array.isArray(s.items)&&Array.isArray(s.removed))return s;storageProblem=true;return C.seed();}
  function study(){const s=read(STUDY,emptyStudy);return s?.version===1&&Array.isArray(s.events)&&Array.isArray(s.trials)?s:emptyStudy();}
  const uid=()=>typeof crypto.randomUUID==='function'?crypto.randomUUID():'id-'+Date.now()+'-'+Math.random().toString(36).slice(2);
  const allowed=['category','screen','count','action','source','success','retainedCount','unreviewedCount','durationMs','reason','field','choice','disabledCount'];
  function event(name,data={}) {
    const s=study(); if(!s.consent||!s.active?.startedAt)return;
    const safe=Object.fromEntries(Object.entries(data).filter(([k,v])=>allowed.includes(k)&&['string','number','boolean'].includes(typeof v)));
    s.events.push({trialId:s.active.id,participantId:s.active.participantId,condition:s.active.condition,scenario:s.active.scenario,mode:s.active.mode,elapsedMs:Math.max(0,Date.now()-s.active.startedAt),event:name,...safe});write(STUDY,s);
  }
  function start(){const s=study();if(!s.consent||!s.active||s.active.startedAt)return false;s.active.startedAt=Date.now();write(STUDY,s);event('task_started');return true;}
  function finish(observed=null,reason='participant_finished'){
    const s=study();if(!s.active?.startedAt)return false;
    event('task_finished',{reason,...(typeof observed==='boolean'?{success:observed}:{})});
    const fresh=study(), a=fresh.active;
    fresh.trials.push({id:a.id,participantId:a.participantId,condition:a.condition,scenario:a.scenario,mode:a.mode,durationMs:Math.max(0,Date.now()-a.startedAt),observedSuccess:observed,outcome:'unrated',assistance:'unrecorded',stopReason:reason});
    fresh.active=null;write(STUDY,fresh);return true;
  }
  return {STATE,STUDY,state,study,saveState:s=>write(STATE,s),saveStudy:s=>write(STUDY,s),emptyStudy,uid,event,start,finish,get storageProblem(){return storageProblem;}};
})();
