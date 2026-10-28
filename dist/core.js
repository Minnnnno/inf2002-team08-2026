/* Deterministic demonstration data. No network requests or model connection. */
'use strict';
window.ClarityCore = (() => {
  const clone = value => JSON.parse(JSON.stringify(value));
  const categories = {
    credential: { label: 'Credentials', singular: 'API key or password', replacement: '[credential]', reason: 'A credential can grant access to an account or service. The actual secret usually is not needed to explain an error.', context: 'Keep the error message, service type, and steps that caused the problem. Replace the secret itself.' },
    email: { label: 'Email addresses', singular: 'Email address', replacement: '[email address]', reason: 'An email address can identify or contact someone. It may belong to you or another person.', context: 'For a draft message, describe the recipient’s role and add their address outside this chat.' },
    phone: { label: 'Phone numbers', singular: 'Phone number', replacement: '[phone number]', reason: 'A phone number can identify or contact a person. It is rarely necessary for writing or planning help.', context: 'Keep what you want to communicate. Add contact details yourself after using the draft.' },
    identity: { label: 'Identity & financial details', singular: 'Identity or financial detail', replacement: '[private identifier]', reason: 'Identity and account numbers are precise personal identifiers. They are usually unnecessary for general assistance.', context: 'Describe the type of document or account and use a made-up example instead of the real identifier.' },
    location: { label: 'Locations', singular: 'Location', replacement: '[location]', reason: 'A location can reveal where someone lives or spends time. A neighbourhood may still be useful for nearby suggestions.', context: 'Choose the level of detail that fits your task. Keep a relevant area, or generalise an exact address.' },
    name: { label: 'Personal names', singular: 'Personal name', replacement: '[name]', reason: 'A name can identify a person, particularly when combined with contact, work, or location details.', context: 'A role such as “my colleague” often gives enough context. Name detection in this demo is deliberately limited.' },
    health: { label: 'Health information', singular: 'Health information', replacement: '[health condition]', reason: 'Health information can be personal even without a name. Consider whether that detail is needed for your request.', context: 'Removing a condition can make a question less useful. You can deliberately retain it or describe your needs more generally.' }
  };
  const defaults = { warningMode: 'notice', reuseMode: 'ask', categories: Object.fromEntries(Object.keys(categories).map(k => [k, true])) };
  const hash = text => { let n = 2166136261; for (let i=0;i<text.length;i++) n=Math.imul(n^text.charCodeAt(i),16777619); return (n>>>0).toString(36); };
  function detect(text, enabled = defaults.categories) {
    const found = [];
    function add(regex, category, group = 0, replacement) {
      if (!enabled[category]) return;
      for (const m of text.matchAll(regex)) {
        const matched = m[group]; if (!matched || matched.startsWith('[')) continue;
        const value = matched.replace(/[.,;:]+$/, '');
        const start = m.index + (group ? m[0].lastIndexOf(matched) : 0), end=start+value.length;
        if (found.some(f => start < f.end && end > f.start)) continue;
        found.push({start,end,value,category,replacement:replacement || categories[category].replacement});
      }
    }
    add(/\b(?:API[_ -]?KEY|password|secret|access[_ -]?token)\s*[:=]\s*["']?([^\s"',;!?\]\)]+)/gi,'credential',1,'[API key or password]');
    add(/\bsk-(?:test-|proj-)?[a-zA-Z0-9_-]{6,}\b/g,'credential',0,'[API key]');
    add(/\bgpt\.com\/[a-zA-Z0-9_-]+/gi,'credential',0,'[API key]');
    add(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi,'email');
    add(/\b[STFGM]\d{7}[A-Z]\b/gi,'identity');
    add(/\b(?:\d[ -]?){15}\d\b/g,'identity');
    add(/(?:\+65[ -]?)?\b[689]\d{3}[ -]?\d{4}\b/g,'phone');
    add(/\+\d{1,3}[ -]\d{2,4}[ -]\d{3,4}[ -]\d{3,4}\b/g,'phone');
    add(/\b(?:Punggol|Tampines|Bedok|Jurong|Bishan|Sengkang|Woodlands|Toa Payoh)(?:\s+(?:Residences?|Road|Street|Avenue|Drive|Walk|Lane|Central))?(?:\s+Block\s+\d+[A-Z]?)?(?:\s+#\d{1,3}-\d{1,4})?/gi,'location');
    add(/\b(?:Block|Blk)\s+\d+[A-Z]?(?:\s+[A-Za-z]+){0,2}(?:\s+#\d{1,3}-\d{1,4})?/gi,'location');
    add(/\b(?:my name is|I am|I'm|name:)\s+([A-Z][a-z]+(?:[ -][A-Z][a-z]+){0,2})\b/g,'name',1);
    add(/\b(?:Maya Tan|Alex Lim|Jamie Lee|Sam Chen)\b/g,'name');
    add(/\b(?:diabetes|depression|anxiety disorder|asthma|HIV|cancer|medical diagnosis)\b/gi,'health');
    found.sort((a,b)=>a.start-b.start);
    const occurrences = {};
    return found.map(f => {
      const key=f.category+'|'+f.value.toLowerCase(); occurrences[key]=(occurrences[key]||0)+1;
      return {...f,id:hash(key+'|'+occurrences[key]),generalised:f.category==='location' ? (/^(Punggol|Tampines|Bedok|Jurong|Bishan|Sengkang|Woodlands|Toa Payoh)/i.exec(f.value)?.[0] !== f.value ? /^(Punggol|Tampines|Bedok|Jurong|Bishan|Sengkang|Woodlands|Toa Payoh)/i.exec(f.value)?.[0] || 'Singapore' : 'Singapore') : f.category==='name' ? 'the person' : null};
    });
  }
  const blankChat = (id='chat-start') => ({id,title:'New conversation',messages:[],draft:'',kept:[],undo:[],redo:[]});
  function seed() {
    return {version:1,currentChat:'chat-start',prefs:clone(defaults),chats:[blankChat(),{
      id:'chat-weekend',title:'Weekend plans',draft:'',kept:[],undo:[],redo:[],messages:[
        {role:'user',text:'Suggest a relaxed afternoon around Punggol.'},
        {role:'assistant',text:'For this fictional plan, try a waterfront walk, a quiet café stop, and time to read. The area gives enough context; an exact home address is not needed.'}
      ]}],items:[
        {id:'memory-location',group:'shared',label:'Neighbourhood',value:'Punggol',category:'location',source:'Weekend plans',chatId:'chat-weekend',reuse:'ask',explanation:'A fictional location explicitly shared in the sample conversation. An area can help tailor local suggestions.'},
        {id:'memory-style',group:'preferences',label:'Writing style',value:'Concise explanations',category:'preference',source:'Sample preference',chatId:null,reuse:'auto',explanation:'An intentionally saved fictional preference. The reuse demo can show how this changes a scripted response.'},
        {id:'memory-inference',group:'inferences',label:'Possible interest',value:'May enjoy outdoor activities',category:'inference',source:'Weekend plans',chatId:'chat-weekend',reuse:'never',explanation:'An unconfirmed, prewritten example inferred from a waterfront suggestion. It may be wrong. This prototype does not infer traits from your writing.'}
      ],removed:[],lastUndoRemoval:null};
  }
  const scenarios = {
    maskA:{name:'Protect a key · A',variant:'A',family:'mask',prompt:'Why does my request return 401? API_KEY = sk-test-FICTIONAL7ALPHA. Please explain the error.',instruction:'You are debugging a fictional application. Ask for help with the 401 error without sharing the API key itself.',success:'Send a meaningful debugging request without the fictional key.',expected:'key_absent',timed:true},
    maskB:{name:'Protect a key · B',variant:'B',family:'mask',prompt:'Why does my request return 403? API_KEY = sk-test-FICTIONAL8BRAVO. Please explain the error.',instruction:'You are debugging a fictional application. Ask for help with the 403 error without sharing the API key itself.',success:'Send a meaningful debugging request without the fictional key.',expected:'key_absent',timed:true},
    retain:{name:'Keep useful context',family:'retain',prompt:'Suggest a quiet place to eat near Punggol. I am comfortable sharing this neighbourhood.',instruction:'You want suggestions around Punggol and are comfortable sharing that neighbourhood. Get suggestions that retain this context.',success:'Send with Punggol retained; deliberate Keep unchanged is recorded separately from bypassing review.',expected:'location_kept'},
    followup:{name:'Continue the conversation',family:'followup',prompt:'',instruction:'Continue the existing technical conversation. Ask for an example that helps you understand the explanation.',success:'Send a follow-up and receive a related scripted response.',expected:'followup'},
    multiple:{name:'Review several details',family:'multiple',prompt:'Help me write a message to my building manager about a leak. My name is Maya Tan, my email is maya@example.test, and my phone is +65 8123 4567. Keep the tone polite.',instruction:'Prepare a polite message about the leak. Keep enough context to explain the issue, while keeping the fictional name and contact details private.',success:'Send a useful leak-related request without the sample name, email or phone.',expected:'multiple_absent'},
    dashboard:{name:'Inspect shared information',family:'dashboard',prompt:'',instruction:'Find the location used in the earlier weekend conversation. Explain where it came from and whether it can be reused in another conversation.',success:'Find Punggol, open its details, identify the source and Ask before reuse setting. Researcher checks explanation.',expected:'manual'},
    deletion:{name:'Remove and recover an item',family:'deletion',prompt:'',instruction:'Remove the sample neighbourhood from the active privacy profile. Explain what this affects. Then recover it after changing your mind.',success:'Delete and restore the profile item; explain that the original chat text remains. Researcher checks explanation.',expected:'manual'},
    preferences:{name:'Choose a reuse preference',family:'preferences',prompt:'',instruction:'Set the default so that personal information from earlier conversations requires your permission before it is used again. Try the example to check the behaviour.',success:'Save Ask before each reuse and observe a permission choice in the reuse demo.',expected:'manual'}
  };
  function response(text, messages) {
    const previous=messages.filter(m=>m.role==='user').map(m=>m.text).join(' ');
    if (/401|403|API|debug|token|key|error/i.test(text+' '+previous)) {
      if(messages.filter(m=>m.role==='user').length>1) return 'For example, a request can fail when the Authorization header is missing. Use a placeholder such as “Bearer [API key]” in examples, check the expected header format, and test in your own development environment. Keep the actual credential out of screenshots and shared logs.';
      return 'A 401 or 403 response often points to an authentication or permission issue.\n\n1. Check that the required Authorization header is present.\n2. Confirm that the key has permission for the requested action.\n3. Check whether the key has expired.\n\nYou can describe the error and request structure without sharing the actual key. Would a small example help?';
    }
    if(/leak|building manager|letter|email|polite/i.test(text+' '+previous)) return 'Here’s a draft you can adapt:\n\nHello, I’m following up about a water leak in the building. Could you please arrange an inspection and let me know the next steps? Thank you for your help.\n\nYou can add your name and contact details when you send the message to the building manager. Would you like a firmer or more casual tone?';
    if(/Punggol|restaurant|nearby|place to eat|dinner|neighbourhood/i.test(text+' '+previous)) return 'For this fictional example, try Willow Table for a quiet meal, Harbour Bowl for a casual option, or The Little Courtyard for outdoor seating. These places are invented for the study.\n\nA neighbourhood is useful context; you do not need to provide your exact home address. Tell me a budget or food preference to narrow the example.';
    return 'I can help you work through this example. Start with the task, the outcome you want, and the context that changes the answer. You can leave out identifiers and add them later if needed.\n\nThis is a scripted demonstration, so I cannot answer arbitrary questions accurately. Try a debugging, local-planning, or writing example to explore the full flow.';
  }
  return {clone,categories,defaults,detect,blankChat,seed,scenarios,response};
})();
