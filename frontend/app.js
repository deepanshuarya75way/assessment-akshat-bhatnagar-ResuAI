/* =====================================================
   RESUAI DASHBOARD – CLIENT-SIDE APPLICATION LOGIC
   Connects to FastAPI backend · Pure Vanilla JS
===================================================== */

'use strict';

/* ===================================================
   STATE
=================================================== */
let allJobs = [];
let allUsers = [];
let currentTab = 'dashboard';

/* ===================================================
   INIT
=================================================== */
document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 1000);
  checkSystemStatus();
  loadDashboard();
  loadJobs();
  loadUsers();
  loadResumes();
  loadLogs();
  initDragDrop();
});

/* ===================================================
   CLOCK
=================================================== */
function updateClock() {
  const el = document.getElementById('topbar-time');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-IN', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
  }) + ' · ' + now.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

/* ===================================================
   NAVIGATION
=================================================== */
function switchTab(tab, el) {
  if (el && el.tagName === 'A') {
    el.preventDefault ? el.preventDefault() : (event.returnValue = false);
  }

  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

  const navEl = document.getElementById(`nav-${tab}`);
  if (navEl) navEl.classList.add('active');

  const tabEl = document.getElementById(`tab-${tab}`);
  if (tabEl) tabEl.classList.add('active');

  const titles = {
    dashboard: 'Dashboard', jobs: 'Job Board', ats: 'ATS Matcher',
    resumes: 'Resume Vault', users: 'Users', logs: 'System Logs'
  };
  const bp = document.getElementById('breadcrumb-page');
  if (bp) bp.textContent = titles[tab] || tab;

  currentTab = tab;

  // Close sidebar on mobile
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.remove('open');
  }

  return false;
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

/* ===================================================
   SYSTEM STATUS
=================================================== */
async function checkSystemStatus() {
  try {
    const res = await fetch('/health');
    const data = await res.json();
    const chip = document.getElementById('status-chip');
    const txt  = document.getElementById('status-text');
    if (data.status === 'ok') {
      chip.style.background = 'rgba(16,185,129,0.08)';
      chip.style.border = '1px solid rgba(16,185,129,0.2)';
      chip.style.color = '#34d399';
      txt.textContent = 'System Online';
    }
  } catch {
    const chip = document.getElementById('status-chip');
    const txt  = document.getElementById('status-text');
    chip.style.background = 'rgba(239,68,68,0.08)';
    chip.style.border = '1px solid rgba(239,68,68,0.2)';
    chip.style.color = '#ef4444';
    txt.textContent = 'Offline';
    document.querySelectorAll('.stage-status').forEach(s => {
      s.classList.remove('online');
      s.classList.add('offline');
    });
  }
}

/* ===================================================
   DASHBOARD
=================================================== */
async function loadDashboard() {
  try {
    const [jobsRes, usersRes, resumesRes] = await Promise.allSettled([
      fetch('/jobs/latest?limit=6'),
      fetch('/users'),
      fetch('/resumes/')
    ]);

    // Stats
    const jobs    = jobsRes.status === 'fulfilled' && jobsRes.value.ok ? await jobsRes.value.json() : [];
    const users   = usersRes.status === 'fulfilled' && usersRes.value.ok ? await usersRes.value.json() : [];
    const resumes = resumesRes.status === 'fulfilled' && resumesRes.value.ok ? await resumesRes.value.json() : [];

    animateCount('stat-jobs-val', jobs.length);
    animateCount('stat-users-val', users.length);
    animateCount('stat-resumes-val', resumes.length);

    const calSynced = jobs.filter(j => j.calendar_synced).length;
    animateCount('stat-cal-val', calSynced);

    // Update badge
    const badge = document.getElementById('jobs-count-badge');
    if (badge) badge.textContent = jobs.length;

    // Dashboard job feed
    renderDashboardFeed(jobs.slice(0, 5));

  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

function animateCount(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  let current = 0;
  const step = Math.max(1, Math.floor(target / 25));
  const interval = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current;
    if (current >= target) clearInterval(interval);
  }, 40);
}

function renderDashboardFeed(jobs) {
  const feed = document.getElementById('dashboard-job-feed');
  if (!feed) return;

  if (!jobs || jobs.length === 0) {
    feed.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:10px 0">No jobs ingested yet. The scheduler will pick them up shortly.</p>';
    return;
  }

  feed.innerHTML = jobs.map(j => `
    <div class="job-feed-item" onclick="openJobModal(${j.id})" tabindex="0" role="button" aria-label="${j.company} – ${j.role}">
      <div class="company-avatar" style="${avatarStyle(j.company)}">${initials(j.company)}</div>
      <div class="job-feed-body">
        <div class="job-feed-company">${esc(j.company || 'Unknown')}</div>
        <div class="job-feed-role">${esc(j.role || '—')}</div>
      </div>
      <div class="job-feed-meta">
        <span class="job-type-chip ${chipClass(j.job_type)}">${esc(j.job_type || 'Job')}</span>
        <span style="font-size:11px;color:var(--text-muted)">${j.location || ''}</span>
      </div>
    </div>
  `).join('');
}

/* ===================================================
   JOBS
=================================================== */
async function loadJobs() {
  try {
    const res = await fetch('/jobs/');
    if (!res.ok) throw new Error('Failed');
    allJobs = await res.json();
    renderJobs(allJobs);

    const badge = document.getElementById('jobs-count-badge');
    if (badge) badge.textContent = allJobs.length;
  } catch (err) {
    document.getElementById('jobs-grid').innerHTML =
      '<p style="color:#ef4444;padding:20px;grid-column:1/-1">Failed to load jobs. Is the server running?</p>';
  }
}

function renderJobs(jobs) {
  const grid  = document.getElementById('jobs-grid');
  const empty = document.getElementById('jobs-empty');
  if (!grid) return;

  if (!jobs || jobs.length === 0) {
    grid.innerHTML = '';
    grid.classList.add('hidden');
    empty.classList.remove('hidden');
    return;
  }

  grid.classList.remove('hidden');
  empty.classList.add('hidden');

  grid.innerHTML = jobs.map(j => `
    <div class="job-card" onclick="openJobModal(${j.id})" tabindex="0" role="button" aria-label="Open ${j.company} job details">
      <div class="job-card-header">
        <div class="company-avatar" style="${avatarStyle(j.company)}">${initials(j.company)}</div>
        <div>
          <div class="job-company-name">${esc(j.company || 'Unknown Company')}</div>
          <div class="job-role-name">${esc(j.role || 'Role not specified')}</div>
        </div>
      </div>
      <div class="job-card-chips">
        ${j.job_type ? `<span class="job-type-chip ${chipClass(j.job_type)}">${esc(j.job_type)}</span>` : ''}
        ${j.location ? `<span class="job-type-chip chip-default">📍 ${esc(j.location)}</span>` : ''}
        ${j.batch    ? `<span class="job-type-chip chip-default">Batch ${esc(j.batch)}</span>` : ''}
      </div>
      <div class="job-card-meta">
        <div class="meta-item">
          <span class="meta-key">CTC / Stipend</span>
          <span class="meta-val">${esc(j.ctc || j.stipend || '—')}</span>
        </div>
        <div class="meta-item">
          <span class="meta-key">Min. CGPA</span>
          <span class="meta-val">${esc(j.minimum_cgpa || '—')}</span>
        </div>
      </div>
      <div class="job-card-deadline">
        <span>Deadline</span>
        <span class="deadline-val">${esc(j.application_deadline || 'Not specified')}</span>
      </div>
    </div>
  `).join('');
}

function filterJobs() {
  const search    = (document.getElementById('job-search')?.value || '').toLowerCase();
  const batch     = (document.getElementById('job-batch')?.value || '').toLowerCase();
  const typeFilter = (document.getElementById('job-type-filter')?.value || '').toLowerCase();

  const filtered = allJobs.filter(j => {
    const matchSearch = !search ||
      (j.company || '').toLowerCase().includes(search) ||
      (j.role    || '').toLowerCase().includes(search);
    const matchBatch  = !batch  || (j.batch || '').toLowerCase().includes(batch);
    const matchType   = !typeFilter || (j.job_type || '').toLowerCase().includes(typeFilter);
    return matchSearch && matchBatch && matchType;
  });

  renderJobs(filtered);
}

function clearJobFilters() {
  ['job-search', 'job-batch'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const sel = document.getElementById('job-type-filter');
  if (sel) sel.value = '';
  renderJobs(allJobs);
}

function handleGlobalSearch(val) {
  if (currentTab !== 'jobs') {
    switchTab('jobs', null);
  }
  const el = document.getElementById('job-search');
  if (el) { el.value = val; filterJobs(); }
}

/* ===================================================
   JOB MODAL
=================================================== */
async function openJobModal(jobId) {
  const job = allJobs.find(j => j.id === jobId);
  if (!job) {
    try {
      const res = await fetch(`/jobs/${jobId}`);
      if (!res.ok) { showToast('Job not found', 'error'); return; }
      const j = await res.json();
      renderJobModal(j);
    } catch { showToast('Failed to load job', 'error'); return; }
  } else {
    renderJobModal(job);
  }
  document.getElementById('job-modal').classList.remove('hidden');
}

function renderJobModal(j) {
  document.getElementById('job-modal-title').textContent = j.role || 'Job Details';
  document.getElementById('job-modal-company').textContent = j.company || '';

  const skills = (j.skills_required || []).map(s => `
    <span style="display:inline-block;background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.2);
    color:var(--blue-300);font-size:12px;padding:3px 10px;border-radius:20px;margin:3px;">${esc(s)}</span>
  `).join('');

  const branches = (j.eligible_branches || []).join(', ') || '—';
  const process  = (j.selection_process || []).map((p,i) => `
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)">
      <span style="width:22px;height:22px;border-radius:50%;background:rgba(37,99,235,0.15);color:var(--blue-300);
      font-size:11px;font-weight:700;display:grid;place-items:center;flex-shrink:0">${i+1}</span>
      <span style="font-size:13px;color:var(--text-secondary)">${esc(p)}</span>
    </div>
  `).join('');

  document.getElementById('job-modal-body').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px">
      ${metaBlock('Job Type',    j.job_type)}
      ${metaBlock('Location',    j.location)}
      ${metaBlock('CTC',         j.ctc)}
      ${metaBlock('Stipend',     j.stipend)}
      ${metaBlock('Min. CGPA',   j.minimum_cgpa)}
      ${metaBlock('Batch',       j.batch)}
      ${metaBlock('Eligible Branches', branches)}
      ${metaBlock('Deadline',    j.application_deadline)}
      ${metaBlock('Calendar',    j.calendar_synced ? '✅ Synced' : '⏳ Pending')}
    </div>
    ${j.job_description ? `
      <div style="margin-bottom:18px">
        <div class="ats-detail-label">Job Description</div>
        <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;
        padding:14px;font-size:13px;color:var(--text-secondary);line-height:1.7;max-height:200px;overflow-y:auto">
          ${esc(j.job_description)}
        </div>
      </div>` : ''}
    ${skills ? `<div style="margin-bottom:18px"><div class="ats-detail-label">Skills Required</div><div style="margin-top:8px">${skills}</div></div>` : ''}
    ${process ? `<div><div class="ats-detail-label">Selection Process</div><div style="margin-top:8px">${process}</div></div>` : ''}
    ${j.apply_url ? `
      <div style="margin-top:18px;padding-top:14px;border-top:1px solid var(--border)">
        <a href="${esc(j.apply_url)}" target="_blank" class="btn-primary" style="text-decoration:none;display:inline-flex">
          Apply Now ↗
        </a>
      </div>` : ''}
  `;
}

function metaBlock(label, val) {
  if (!val) return '';
  return `
    <div class="ats-detail-item">
      <div class="ats-detail-label">${esc(label)}</div>
      <div class="ats-detail-val">${esc(String(val))}</div>
    </div>`;
}

function closeJobModal() {
  document.getElementById('job-modal').classList.add('hidden');
}

/* ===================================================
   ATS MATCHER
=================================================== */
async function runAtsMatch() {
  const userId = document.getElementById('ats-user-id')?.value?.trim();
  const jobId  = document.getElementById('ats-job-id')?.value?.trim();

  if (!userId || !jobId) { showToast('Please enter both User ID and Job ID', 'error'); return; }

  const btn = document.getElementById('ats-match-btn');
  btn.disabled = true;
  btn.textContent = 'Analysing… (AI may take ~30s)';

  const controller = new AbortController();
  const timeoutId  = setTimeout(() => controller.abort(), 90_000);

  try {
    const res = await fetch(`/ats/match/${userId}/${jobId}`, { method: 'POST', signal: controller.signal });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Match failed');
    }
    const data = await res.json();
    clearTimeout(timeoutId);
    renderAtsResult(data);
    showToast('ATS match computed!', 'success');
  } catch (err) {
    clearTimeout(timeoutId);
    const msg = err.name === 'AbortError' ? 'Request timed out. Try again.' : err.message;
    showToast(msg, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/></svg> Analyze Match`;
  }
}

async function loadUserMatches() {
  const userId = document.getElementById('ats-view-user')?.value?.trim();
  if (!userId) { showToast('Enter a User ID', 'error'); return; }

  try {
    const res = await fetch(`/ats/resume/${userId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed');
    }
    const matches = await res.json();
    renderMatchList(matches);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderAtsResult(data) {
  const placeholder = document.getElementById('ats-result-placeholder');
  const content     = document.getElementById('ats-result-content');

  placeholder.classList.add('hidden');
  content.classList.remove('hidden');

  const score   = parseFloat(data.match_score || data.score || 0);
  const pct     = Math.round(score * (score <= 1 ? 100 : 1));
  const cls     = pct >= 70 ? 'score-good' : pct >= 45 ? 'score-mid' : 'score-low';
  const label   = pct >= 70 ? '🎯 Strong Match' : pct >= 45 ? '⚡ Moderate Match' : '⚠️ Weak Match';

  content.innerHTML = `
    <div class="ats-result-card">
      <div class="ats-score-banner ${cls}">
        <div class="score-number">${pct}%</div>
        <div class="score-label">${label}</div>
      </div>
      <div class="ats-detail-grid">
        ${metaBlock('User ID',  data.user_id)}
        ${metaBlock('Job ID',   data.job_id)}
        ${metaBlock('Match ID', data.id)}
        ${metaBlock('Computed', data.created_at ? new Date(data.created_at).toLocaleString('en-IN') : '—')}
      </div>
      ${data.matched_skills?.length ? `
        <div class="ats-detail-label" style="margin-bottom:8px">Matched Skills</div>
        <div>${data.matched_skills.map(s =>
          `<span style="display:inline-block;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);
          color:#34d399;font-size:12px;padding:3px 10px;border-radius:20px;margin:3px;">${esc(s)}</span>`
        ).join('')}</div>` : ''}
      ${data.missing_skills?.length ? `
        <div class="ats-detail-label" style="margin-top:14px;margin-bottom:8px">Missing Skills</div>
        <div>${data.missing_skills.map(s =>
          `<span style="display:inline-block;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
          color:#ef4444;font-size:12px;padding:3px 10px;border-radius:20px;margin:3px;">${esc(s)}</span>`
        ).join('')}</div>` : ''}
      ${data.suggestions ? `
        <div class="ats-detail-label" style="margin-top:14px;margin-bottom:6px">AI Suggestions</div>
        <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;
        padding:14px;font-size:13px;color:var(--text-secondary);line-height:1.7">${esc(data.suggestions)}</div>` : ''}
    </div>
  `;
}

function renderMatchList(matches) {
  const placeholder = document.getElementById('ats-result-placeholder');
  const content     = document.getElementById('ats-result-content');
  placeholder.classList.add('hidden');
  content.classList.remove('hidden');

  if (!matches || matches.length === 0) {
    content.innerHTML = `<div class="ats-placeholder"><p class="empty-title">No matches found for this user.</p></div>`;
    return;
  }

  content.innerHTML = `
    <div class="ats-result-card">
      <div class="card-header">
        <h3 class="card-title">All Matches — ${matches.length} result${matches.length !== 1 ? 's' : ''}</h3>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px">
        ${matches.map(m => {
          const score = parseFloat(m.match_score || m.score || 0);
          const pct   = Math.round(score * (score <= 1 ? 100 : 1));
          const cls   = pct >= 70 ? 'score-good' : pct >= 45 ? 'score-mid' : 'score-low';
          return `
            <div style="display:flex;align-items:center;gap:14px;padding:14px;border-radius:10px;
            border:1px solid var(--border);background:rgba(255,255,255,0.02)">
              <div class="ats-score-banner ${cls}" style="padding:10px 18px;margin:0;min-width:70px;text-align:center">
                <div style="font-size:22px;font-weight:800;font-family:'Space Grotesk',sans-serif">${pct}%</div>
              </div>
              <div>
                <div style="font-size:14px;font-weight:600;color:var(--text-primary)">Job #${m.job_id}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:3px">Match ID: ${m.id}</div>
              </div>
            </div>`;
        }).join('')}
      </div>
    </div>`;
}

/* ===================================================
   RESUMES
=================================================== */
async function loadResumes() {
  try {
    const res = await fetch('/resumes/');
    if (!res.ok) throw new Error('Failed');
    const resumes = await res.json();
    renderResumeList(resumes);
    animateCount('stat-resumes-val', resumes.length);
  } catch {
    const el = document.getElementById('resumes-list');
    if (el) el.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:10px">Could not load resumes.</p>';
  }
}

function renderResumeList(resumes) {
  const el = document.getElementById('resumes-list');
  if (!el) return;

  if (!resumes || resumes.length === 0) {
    el.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:10px 0">No resumes uploaded yet.</p>';
    return;
  }

  el.innerHTML = resumes.map(r => `
    <div class="resume-item">
      <div class="resume-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="20" height="20">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
      </div>
      <div class="resume-info">
        <div class="resume-filename">${esc(r.file_name || r.filename || 'resume.pdf')}</div>
        <div class="resume-meta">User #${r.user_id} · ${r.created_at ? new Date(r.created_at).toLocaleDateString('en-IN') : ''}</div>
      </div>
      <button class="action-btn" title="Delete" onclick="deleteResume(${r.id})">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="16" height="16">
          <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
          <path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
        </svg>
      </button>
    </div>
  `).join('');
}

function handleFileSelect(input) {
  const hint = document.getElementById('upload-filename');
  if (input.files && input.files[0]) {
    hint.textContent = input.files[0].name;
    hint.style.color = 'var(--blue-300)';
  }
}

function initDragDrop() {
  const dz = document.getElementById('dropzone');
  if (!dz) return;
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.style.borderColor = 'var(--blue-400)'; });
  dz.addEventListener('dragleave', () => { dz.style.borderColor = ''; });
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.style.borderColor = '';
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      const input = document.getElementById('resume-file');
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      handleFileSelect(input);
    } else {
      showToast('Please drop a PDF file', 'error');
    }
  });
}

async function uploadResume() {
  const file   = document.getElementById('resume-file')?.files?.[0];
  const userId = document.getElementById('upload-user-id')?.value?.trim();
  const status = document.getElementById('upload-status');

  if (!file)   { showToast('Select a PDF file first', 'error'); return; }
  if (!userId) { showToast('Enter a User ID', 'error'); return; }

  const btn = document.getElementById('upload-btn');
  btn.disabled = true;
  status.className = 'upload-status hidden';

  // Rotating status messages — Groq can take 20-40s when rate-limited
  const stages = [
    '📤 Uploading file…',
    '🤖 AI is parsing your resume…',
    '⏳ Groq LLM processing (may take ~30s)…',
    '🔄 Computing ATS scores…',
    '🧠 Still working — almost there…',
  ];
  let stageIdx = 0;
  btn.textContent = stages[0];
  const stageTimer = setInterval(() => {
    stageIdx = Math.min(stageIdx + 1, stages.length - 1);
    btn.textContent = stages[stageIdx];
  }, 7000);

  // 90-second hard timeout so the button never freezes forever
  const controller = new AbortController();
  const timeoutId  = setTimeout(() => controller.abort(), 90_000);

  try {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`/resumes/upload/${userId}`, {
      method: 'POST',
      body: form,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    status.className = 'upload-status success';
    status.textContent = '✅ Resume uploaded, parsed and ATS updated successfully!';
    showToast('Resume uploaded & parsed!', 'success');
    loadResumes();
  } catch (err) {
    clearTimeout(timeoutId);
    const msg = err.name === 'AbortError'
      ? 'Request timed out after 90s. The server may still be processing — check Resumes list in a moment.'
      : err.message;
    status.className = 'upload-status error';
    status.textContent = `❌ ${msg}`;
    showToast(msg, 'error');
  } finally {
    clearInterval(stageTimer);
    btn.disabled = false;
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> Upload &amp; Parse`;
  }
}

async function deleteResume(resumeId) {
  if (!confirm('Delete this resume?')) return;
  try {
    const res = await fetch(`/resumes/${resumeId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
    showToast('Resume deleted', 'success');
    loadResumes();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/* ===================================================
   USERS
=================================================== */
async function loadUsers() {
  try {
    const res = await fetch('/users');
    if (!res.ok) throw new Error('Failed');
    allUsers = await res.json();
    renderUsersTable(allUsers);
    animateCount('stat-users-val', allUsers.length);
  } catch {
    const tb = document.getElementById('users-tbody');
    if (tb) tb.innerHTML = '<tr><td colspan="7" class="table-loading" style="color:#ef4444">Failed to load users</td></tr>';
  }
}

function renderUsersTable(users) {
  const tbody = document.getElementById('users-tbody');
  if (!tbody) return;

  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="table-loading">No users found. Add a user to get started.</td></tr>';
    return;
  }

  tbody.innerHTML = users.map(u => `
    <tr>
      <td>${u.id}</td>
      <td class="td-primary">${esc(u.name || '—')}</td>
      <td>${esc(u.email || '—')}</td>
      <td>${esc(u.branch || '—')}</td>
      <td>${esc(u.batch || '—')}</td>
      <td>${esc(u.cgpa != null ? String(u.cgpa) : '—')}</td>
      <td>
        <button class="action-btn" title="View ATS matches" onclick="viewUserAts(${u.id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="15" height="15">
            <circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/>
          </svg>
        </button>
      </td>
    </tr>
  `).join('');
}

function viewUserAts(userId) {
  switchTab('ats', document.getElementById('nav-ats'));
  const el = document.getElementById('ats-view-user');
  if (el) { el.value = userId; loadUserMatches(); }
}

function openUserModal() {
  document.getElementById('user-modal').classList.remove('hidden');
}

function closeUserModal() {
  document.getElementById('user-modal').classList.add('hidden');
}

async function createUser() {
  const name   = document.getElementById('u-name')?.value?.trim();
  const email  = document.getElementById('u-email')?.value?.trim();
  const branch = document.getElementById('u-branch')?.value?.trim();
  const batch  = document.getElementById('u-batch')?.value?.trim();
  const cgpa   = document.getElementById('u-cgpa')?.value?.trim();

  if (!name || !email) { showToast('Name and email are required', 'error'); return; }

  try {
    const res = await fetch('/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, branch, batch, cgpa: cgpa ? parseFloat(cgpa) : null })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create user');
    }

    showToast('User created!', 'success');
    closeUserModal();
    loadUsers();

    // Clear form
    ['u-name','u-email','u-branch','u-batch','u-cgpa'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/* ===================================================
   LOGS
=================================================== */
async function loadLogs() {
  try {
    const res = await fetch('/logs-data');
    if (!res.ok) {
      // Fallback: use the HTML endpoint and parse
      loadLogsFromHtml();
      return;
    }
    const data = await res.json();
    setLog('log-out', 'out-lines', data.out || 'No output log yet.');
    setLog('log-err', 'err-lines', data.err || 'No error log yet.');
  } catch {
    loadLogsFromHtml();
  }
}

async function loadLogsFromHtml() {
  try {
    const res = await fetch('/status');
    if (!res.ok) throw new Error();
    const text = await res.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'text/html');
    const pre = doc.querySelector('pre');
    const content = pre ? pre.textContent : 'No log available.';
    setLog('log-out', 'out-lines', content);
    setLog('log-err', 'err-lines', 'See application output.');
  } catch {
    setLog('log-out', 'out-lines', 'Could not load logs. Check server.');
    setLog('log-err', 'err-lines', 'Could not load error log.');
  }
}

function setLog(logId, countId, content) {
  const el = document.getElementById(logId);
  const ct = document.getElementById(countId);
  if (!el) return;
  el.textContent = content;
  if (ct) ct.textContent = content.split('\n').length + ' lines';
  // Auto-scroll to bottom
  el.scrollTop = el.scrollHeight;
}

function clearLogs() {
  setLog('log-out', 'out-lines', '');
  setLog('log-err', 'err-lines', '');
}

/* ===================================================
   REFRESH ALL
=================================================== */
function refreshAll() {
  loadDashboard();
  loadJobs();
  loadUsers();
  loadResumes();
  loadLogs();
  checkSystemStatus();
  showToast('Refreshing all data…', 'info');
}

/* ===================================================
   TOAST NOTIFICATIONS
=================================================== */
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = {
    success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>',
    error:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    info:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  };

  toast.innerHTML = `${icons[type] || icons.info}<span>${esc(msg)}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ===================================================
   UTILITIES
=================================================== */
function esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function initials(str) {
  if (!str) return '?';
  const words = str.trim().split(/\s+/).filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

const AVATAR_PALETTES = [
  ['#1d4ed8','#3b82f6'], ['#0e7490','#06b6d4'], ['#7c3aed','#8b5cf6'],
  ['#065f46','#10b981'], ['#92400e','#f59e0b'], ['#be123c','#f43f5e'],
  ['#1e3a5f','#2563eb'], ['#134e4a','#14b8a6'],
];

function avatarStyle(company) {
  const idx = company ? (company.charCodeAt(0) + (company.charCodeAt(1) || 0)) % AVATAR_PALETTES.length : 0;
  const [from, to] = AVATAR_PALETTES[idx];
  return `background:linear-gradient(135deg,${from},${to});color:#fff;`;
}

function chipClass(type) {
  if (!type) return 'chip-default';
  const t = type.toLowerCase();
  if (t.includes('intern'))    return 'chip-internship';
  if (t.includes('full') || t.includes('fte')) return 'chip-fulltime';
  if (t.includes('ppo'))       return 'chip-ppo';
  return 'chip-default';
}

/* Close modals on overlay click */
document.addEventListener('click', e => {
  if (e.target.id === 'job-modal')  closeJobModal();
  if (e.target.id === 'user-modal') closeUserModal();
});

/* Close modals on Escape */
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeJobModal();
    closeUserModal();
  }
});
