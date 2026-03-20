/* Job Hunter — hlavní JavaScript aplikace */

const DATA_URL  = 'data/offers.json';
const CFG_URL   = 'data/config.json';
const LS_STATUS = 'jh_status';       // { id: 'prihlasena' | 'zamer' | 'cekam' | 'nerelevantni' }
const LS_SETTINGS = 'jh_settings';   // přepsání config.json uživatelem
const LS_PROMPT   = 'jh_prompt';     // vlastní AI prompt
const LS_OPENROUTER = 'jh_openrouter_key';

let allOffers  = [];
let serverConfig = {};
let currentTab = 'offers';

/* ── INIT ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {
  setupTabs();
  await loadData();
  renderOffers();
  renderStats();
  setupFilters();
  loadSettingsUI();
  loadPromptUI();
  loadCoverLetterUI();
});

/* ── TABS ─────────────────────────────────────────── */
function setupTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.tab === tab));
  document.querySelectorAll('.tab-panel').forEach(p =>
    p.classList.toggle('active', p.id === 'tab-' + tab));
}

/* ── DATA LOADING ─────────────────────────────────── */
async function loadData() {
  try {
    const [offersResp, cfgResp] = await Promise.all([
      fetch(DATA_URL + '?v=' + Date.now()),
      fetch(CFG_URL  + '?v=' + Date.now()),
    ]);
    const offersData = await offersResp.json();
    serverConfig     = await cfgResp.json();

    allOffers = offersData.offers || [];

    // Zobraz datum aktualizace
    if (offersData.updated) {
      const d = new Date(offersData.updated);
      document.getElementById('last-updated').textContent =
        'Aktualizováno: ' + d.toLocaleDateString('cs-CZ') + ' ' + d.toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit' });
    }
  } catch (e) {
    console.error('Chyba načítání dat:', e);
    document.getElementById('offers-grid').innerHTML =
      '<div class="empty-state"><div class="icon">⚠️</div><p>Nepodařilo se načíst nabídky. Zkontroluj GitHub Pages nastavení.</p></div>';
  }
}

/* ── STATUS ───────────────────────────────────────── */
function getStatuses() {
  try { return JSON.parse(localStorage.getItem(LS_STATUS) || '{}'); } catch { return {}; }
}

function getStatus(id) {
  return getStatuses()[id] || '';
}

function setStatus(id, value) {
  const s = getStatuses();
  if (value) s[id] = value; else delete s[id];
  localStorage.setItem(LS_STATUS, JSON.stringify(s));
}

/* ── RENDER OFFERS ────────────────────────────────── */
function renderOffers(filters = {}) {
  const grid = document.getElementById('offers-grid');
  if (!allOffers.length) {
    grid.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>Zatím žádné nabídky. GitHub Actions je spustí každý den ráno.</p></div>';
    return;
  }

  let offers = allOffers.slice();

  // Filtr hledání
  if (filters.search) {
    const q = filters.search.toLowerCase();
    offers = offers.filter(o =>
      o.title.toLowerCase().includes(q) ||
      (o.company || '').toLowerCase().includes(q));
  }

  // Filtr stavu
  if (filters.status) {
    const statuses = getStatuses();
    offers = offers.filter(o => {
      const st = statuses[o.id] || '';
      if (filters.status === '_none') return !st;
      return st === filters.status;
    });
  }

  // Filtr portálu
  if (filters.source) {
    offers = offers.filter(o => o.source === filters.source);
  }

  // Filtr skóre
  if (filters.minScore) {
    offers = offers.filter(o => (o.ai_score || 0) >= parseInt(filters.minScore));
  }

  if (!offers.length) {
    grid.innerHTML = '<div class="empty-state"><div class="icon">🔍</div><p>Žádné nabídky neodpovídají filtru.</p></div>';
    return;
  }

  grid.innerHTML = offers.map(o => renderCard(o)).join('');

  // Přidej event listenery
  grid.querySelectorAll('.status-select').forEach(sel => {
    sel.addEventListener('change', e => {
      const id = e.target.dataset.id;
      setStatus(id, e.target.value);
      updateSelectStyle(e.target);
      renderStats();
    });
  });

  grid.querySelectorAll('.btn-cover').forEach(btn => {
    btn.addEventListener('click', e => {
      const id = e.target.dataset.id;
      const offer = allOffers.find(o => o.id === id);
      if (offer) openCoverLetterModal(offer);
    });
  });
}

function renderCard(o) {
  const score = o.ai_score || 0;
  const scoreCls = score >= 8 ? 'high' : score >= 5 ? 'mid' : score > 0 ? 'low' : 'none';
  const cardCls  = score >= 8 ? 'score-high' : score >= 5 ? 'score-mid' : score > 0 ? 'score-low' : '';
  const status = getStatus(o.id);
  const statusCls = status || '';
  const scoreLabel = score > 0 ? score : '–';

  const salary = o.salary_text
    ? `<span class="badge badge-salary">${escHtml(o.salary_text)}</span>`
    : '';

  const dateFound = o.date_found
    ? `<span class="badge badge-date">${o.date_found}</span>`
    : '';

  const comment = o.ai_comment
    ? `<div class="card-comment">"${escHtml(o.ai_comment)}"</div>`
    : '';

  return `
    <div class="offer-card ${cardCls}">
      <div class="card-header">
        <div class="score-badge ${scoreCls}">${scoreLabel}</div>
        <div class="card-title-area">
          <a class="offer-title" href="${escHtml(o.url)}" target="_blank" title="${escHtml(o.title)}">${escHtml(o.title)}</a>
          <div class="offer-meta">
            <span>${escHtml(o.company || '')}</span>
            <span class="badge badge-source">${escHtml(o.source)}</span>
            ${salary}
            ${dateFound}
          </div>
        </div>
      </div>
      ${comment}
      <div class="card-footer">
        <select class="status-select ${statusCls}" data-id="${o.id}" onchange="this.className='status-select '+this.value">
          <option value="">— stav —</option>
          <option value="zamer"       ${status==='zamer'       ?'selected':''}>Mám zájem</option>
          <option value="prihlasena"  ${status==='prihlasena'  ?'selected':''}>Přihlásila jsem se</option>
          <option value="cekam"       ${status==='cekam'       ?'selected':''}>Čekám na odpověď</option>
          <option value="nerelevantni"${status==='nerelevantni'?'selected':''}>Nerelevantní</option>
        </select>
        <button class="btn btn-secondary btn-cover" data-id="${o.id}">Průvodní dopis</button>
        <a class="btn btn-primary" href="${escHtml(o.url)}" target="_blank">Otevřít</a>
      </div>
    </div>`;
}

function updateSelectStyle(sel) {
  sel.className = 'status-select ' + (sel.value || '');
}

/* ── STATS ────────────────────────────────────────── */
function renderStats() {
  const statuses = getStatuses();
  const total       = allOffers.length;
  const zamer       = allOffers.filter(o => statuses[o.id] === 'zamer').length;
  const prihlasena  = allOffers.filter(o => statuses[o.id] === 'prihlasena').length;
  const cekam       = allOffers.filter(o => statuses[o.id] === 'cekam').length;
  const highScore   = allOffers.filter(o => (o.ai_score || 0) >= 8).length;

  document.getElementById('stat-total').textContent    = total;
  document.getElementById('stat-zamer').textContent    = zamer;
  document.getElementById('stat-prihlas').textContent  = prihlasena;
  document.getElementById('stat-cekam').textContent    = cekam;
  document.getElementById('stat-high').textContent     = highScore;
}

/* ── FILTERS ──────────────────────────────────────── */
function setupFilters() {
  const searchEl    = document.getElementById('filter-search');
  const statusEl    = document.getElementById('filter-status');
  const sourceEl    = document.getElementById('filter-source');
  const minScoreEl  = document.getElementById('filter-score');

  // Naplň portály
  const sources = [...new Set(allOffers.map(o => o.source))].sort();
  sources.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s; opt.textContent = s;
    sourceEl.appendChild(opt);
  });

  const getFilters = () => ({
    search:   searchEl.value.trim(),
    status:   statusEl.value,
    source:   sourceEl.value,
    minScore: minScoreEl.value,
  });

  [searchEl, statusEl, sourceEl, minScoreEl].forEach(el =>
    el.addEventListener('change', () => renderOffers(getFilters())));
  searchEl.addEventListener('input', () => renderOffers(getFilters()));
}

/* ── SETTINGS ─────────────────────────────────────── */
function getSettings() {
  try { return JSON.parse(localStorage.getItem(LS_SETTINGS) || '{}'); } catch { return {}; }
}

function saveSettings(obj) {
  localStorage.setItem(LS_SETTINGS, JSON.stringify(obj));
}

function loadSettingsUI() {
  const s = getSettings();
  const cfg = serverConfig;

  // Sloučit: localStorage přebíjí serverConfig
  const want  = s.want_keywords  || cfg.want_keywords  || [];
  const dont  = s.dont_want_keywords || cfg.dont_want_keywords || [];
  const minSal = s.min_salary !== undefined ? s.min_salary : (cfg.min_salary || 45000);

  renderTags('want-tags', want, false);
  renderTags('dont-tags', dont, true);
  document.getElementById('min-salary').value = minSal;
  document.getElementById('cv-text').value = s.cv_text || cfg.cv_text || '';

  // OpenRouter klíč
  document.getElementById('openrouter-key').value = localStorage.getItem(LS_OPENROUTER) || '';

  // Uložení nastavení
  document.getElementById('btn-save-settings').addEventListener('click', () => {
    const settings = {
      want_keywords: getTags('want-tags'),
      dont_want_keywords: getTags('dont-tags'),
      min_salary: parseInt(document.getElementById('min-salary').value) || 45000,
      cv_text: document.getElementById('cv-text').value.trim(),
    };
    saveSettings(settings);
    const key = document.getElementById('openrouter-key').value.trim();
    if (key) localStorage.setItem(LS_OPENROUTER, key);
    else localStorage.removeItem(LS_OPENROUTER);
    showToast('Nastavení uloženo (platí pro tento prohlížeč)');
  });

  // Reset
  document.getElementById('btn-reset-settings').addEventListener('click', () => {
    if (!confirm('Smazat lokální nastavení a použít výchozí?')) return;
    localStorage.removeItem(LS_SETTINGS);
    loadSettingsUI();
    showToast('Nastavení obnoveno');
  });

  // Tag inputs
  setupTagInput('want-input', 'want-tags', false);
  setupTagInput('dont-input', 'dont-tags', true);
}

function renderTags(containerId, tags, isDont) {
  const container = document.getElementById(containerId);
  const input = container.querySelector('.tag-input');
  container.querySelectorAll('.tag').forEach(t => t.remove());
  tags.forEach(tag => {
    const el = document.createElement('span');
    el.className = 'tag' + (isDont ? ' dont' : '');
    el.innerHTML = escHtml(tag) + '<span class="tag-remove" onclick="this.parentElement.remove()">×</span>';
    container.insertBefore(el, input);
  });
}

function getTags(containerId) {
  return [...document.getElementById(containerId).querySelectorAll('.tag')]
    .map(t => t.textContent.replace('×', '').trim())
    .filter(Boolean);
}

function setupTagInput(inputId, containerId, isDont) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener('keydown', e => {
    if ((e.key === 'Enter' || e.key === ',') && input.value.trim()) {
      e.preventDefault();
      const tag = input.value.trim().replace(/,$/, '');
      if (!tag) return;
      const container = document.getElementById(containerId);
      const el = document.createElement('span');
      el.className = 'tag' + (isDont ? ' dont' : '');
      el.innerHTML = escHtml(tag) + '<span class="tag-remove" onclick="this.parentElement.remove()">×</span>';
      container.insertBefore(el, container.querySelector('.tag-input'));
      input.value = '';
    }
  });
}

/* ── PROMPT ───────────────────────────────────────── */
const DEFAULT_PROMPT = `Jsi expert na hodnocení pracovních nabídek.
Zhodnoť, zda je tato nabídka vhodná pro kandidátku a vrať:
SKÓRE: <číslo 1-10>
KOMENTÁŘ: <1-2 věty česky>

Kandidátka: {cv}

Nabídka:
Název: {title}
Firma: {company}
Popis: {description}`;

function loadPromptUI() {
  const saved = localStorage.getItem(LS_PROMPT);
  document.getElementById('prompt-textarea').value = saved || DEFAULT_PROMPT;

  document.getElementById('btn-save-prompt').addEventListener('click', () => {
    localStorage.setItem(LS_PROMPT, document.getElementById('prompt-textarea').value);
    showToast('Prompt uložen');
  });

  document.getElementById('btn-reset-prompt').addEventListener('click', () => {
    if (!confirm('Obnovit výchozí prompt?')) return;
    localStorage.removeItem(LS_PROMPT);
    document.getElementById('prompt-textarea').value = DEFAULT_PROMPT;
    showToast('Prompt obnoven');
  });

  document.getElementById('btn-copy-prompt').addEventListener('click', () => {
    navigator.clipboard.writeText(document.getElementById('prompt-textarea').value);
    showToast('Prompt zkopírován');
  });
}

/* ── COVER LETTER ─────────────────────────────────── */
function loadCoverLetterUI() {
  // Naplň select nabídkami
  const select = document.getElementById('cover-offer-select');
  allOffers.forEach(o => {
    const opt = document.createElement('option');
    opt.value = o.id;
    opt.textContent = `${o.title} @ ${o.company || '–'}`;
    select.appendChild(opt);
  });

  document.getElementById('btn-generate-cover').addEventListener('click', async () => {
    const id = select.value;
    const offer = allOffers.find(o => o.id === id);
    if (!offer) { showToast('Vyber nabídku'); return; }
    await generateCoverLetter(offer);
  });

  document.getElementById('btn-copy-cover').addEventListener('click', () => {
    const text = document.getElementById('cover-result').value;
    if (!text) { showToast('Nejprve vygeneruj průvodní dopis'); return; }
    navigator.clipboard.writeText(text);
    showToast('Zkopírováno');
  });
}

function openCoverLetterModal(offer) {
  switchTab('cover');
  const select = document.getElementById('cover-offer-select');
  select.value = offer.id;
  document.getElementById('cover-result').value = '';
}

async function generateCoverLetter(offer) {
  const key = localStorage.getItem(LS_OPENROUTER);
  if (!key) {
    showToast('Zadej OpenRouter API klíč v Nastavení');
    return;
  }

  const settings = getSettings();
  const cvText = settings.cv_text || serverConfig.cv_text || '';
  const model  = serverConfig.openrouter_model || 'openai/gpt-4o-mini';
  const style  = document.getElementById('cover-style')?.value || 'profesionální';

  const resultEl = document.getElementById('cover-result');
  resultEl.value = 'Generuji průvodní dopis…';
  document.getElementById('btn-generate-cover').disabled = true;

  const prompt = `Napiš profesionální průvodní dopis v češtině (${style} tón) na tuto pracovní nabídku.
Dopis by měl být konkrétní, přesvědčivý a maximálně 3 odstavce.

Pracovní nabídka:
Pozice: ${offer.title}
Firma: ${offer.company || 'neuvedena'}
Popis: ${offer.description || ''}

Životopis kandidátky:
${cvText}

Výstup: pouze text průvodního dopisu, bez nadpisů a meta-komentářů.`;

  try {
    const resp = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + key,
        'Content-Type': 'application/json',
        'HTTP-Referer': location.origin,
      },
      body: JSON.stringify({
        model: model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 800,
        temperature: 0.7,
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(resp.status + ': ' + err);
    }

    const data = await resp.json();
    resultEl.value = data.choices?.[0]?.message?.content?.trim() || 'Prázdná odpověď';
    showToast('Průvodní dopis vygenerován');
  } catch (e) {
    resultEl.value = 'Chyba: ' + e.message;
    showToast('Chyba generování: ' + e.message);
  } finally {
    document.getElementById('btn-generate-cover').disabled = false;
  }
}

/* ── TOAST ────────────────────────────────────────── */
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

/* ── HELPERS ──────────────────────────────────────── */
function escHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
