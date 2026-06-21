/* ===== Exam Template - Universal JS ===== */
/* 适用于所有备考站点：N1/期货/博士 */

// ===== Theme Management =====
function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') document.body.classList.add('dark');
  const btn = document.querySelector('.theme-btn');
  if (btn) {
    btn.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    });
  }
}

// ===== Back to Top =====
function initBackToTop() {
  const btn = document.createElement('button');
  btn.className = 'back-top';
  btn.innerHTML = '&#8679;';
  btn.title = '返回顶部';
  btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
  document.body.appendChild(btn);
  window.addEventListener('scroll', () => {
    btn.style.opacity = window.scrollY > 400 ? '1' : '0';
    btn.style.pointerEvents = window.scrollY > 400 ? 'auto' : 'none';
  });
}

// ===== Chapter/Section Toggle =====
function toggleChapter(el) {
  const card = el.closest('.chapter-card');
  if (card) card.classList.toggle('open');
}

function toggleSection(el) {
  const card = el.closest('.section-card');
  if (card) card.classList.toggle('open');
}

function expandAll() {
  document.querySelectorAll('.chapter-card, .section-card').forEach(c => c.classList.add('open'));
}

function collapseAll() {
  document.querySelectorAll('.chapter-card, .section-card').forEach(c => c.classList.remove('open'));
}

// ===== Search =====
function initSearch(dataKey) {
  const input = document.querySelector('.search-box');
  if (!input) return;
  input.addEventListener('input', function() {
    const query = this.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.chapter-card');
    let visible = 0;
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      const match = !query || text.includes(query);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    const counter = document.getElementById('search-count');
    if (counter) counter.textContent = visible;
  });
}

// ===== Filter =====
function setFilter(level, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const cards = document.querySelectorAll('.chapter-card');
  cards.forEach(card => {
    if (level === 'all' || card.dataset.level === level) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
}

// ===== Question Answer System =====
const examStats = { done: 0, correct: 0 };

function selectOption(btn, sel, uid) {
  if (btn.classList.contains('disabled')) return;
  const btns = btn.parentElement.querySelectorAll('.opt-btn');
  btns.forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  btn.dataset.selected = sel;
}

function revealAnswer(uid, ans) {
  const sbtn = document.getElementById('sbtn-' + uid);
  if (!sbtn || sbtn.style.display === 'none') return;

  const qblock = document.getElementById('qblock-' + uid);
  if (!qblock) return;

  const btns = qblock.querySelectorAll('.opt-btn');
  let selected = null;

  btns.forEach(b => {
    if (b.dataset.selected) selected = parseInt(b.dataset.selected);
    b.classList.add('disabled');
    b.onclick = null;
  });

  sbtn.style.display = 'none';
  examStats.done++;

  if (selected === ans) {
    btns[ans - 1].classList.add('correct');
    examStats.correct++;
  } else {
    if (selected && btns[selected - 1]) btns[selected - 1].classList.add('wrong');
    if (btns[ans - 1]) btns[ans - 1].classList.add('correct');
  }

  const exp = document.getElementById('exp-' + uid);
  if (exp) exp.classList.add('show');

  updateStats();
}

function updateStats() {
  const doneEl = document.getElementById('stat-done');
  const correctEl = document.getElementById('stat-correct');
  const rateEl = document.getElementById('stat-rate');
  if (doneEl) doneEl.textContent = examStats.done;
  if (correctEl) correctEl.textContent = examStats.correct;
  if (rateEl) rateEl.textContent = examStats.done > 0 ? Math.round(examStats.correct / examStats.done * 100) + '%' : '0%';
}

// ===== Audio Player =====
let currentAudio = null;
let currentBtn = null;

function playAudio(btn, src) {
  if (currentAudio && currentBtn === btn) {
    currentAudio.pause();
    currentAudio = null;
    currentBtn = null;
    btn.classList.remove('playing');
    btn.innerHTML = '&#9654;';
    return;
  }
  if (currentAudio) {
    currentAudio.pause();
    document.querySelectorAll('.play-btn.playing').forEach(b => {
      b.classList.remove('playing');
      b.innerHTML = '&#9654;';
    });
  }
  currentAudio = new Audio(src);
  currentBtn = btn;
  btn.classList.add('playing');
  btn.innerHTML = '&#9208;';
  currentAudio.play().catch(e => {
    console.log('Audio fail:', e);
    btn.classList.remove('playing');
    btn.innerHTML = '&#9654;';
  });
  currentAudio.onended = () => {
    btn.classList.remove('playing');
    btn.innerHTML = '&#9654;';
    currentAudio = null;
    currentBtn = null;
  };
}

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initBackToTop();
});
