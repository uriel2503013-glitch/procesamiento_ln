const tabs = Array.from(document.querySelectorAll('.tab'));
const fields = document.getElementById('fields');
const form = document.getElementById('assistantForm');
const result = document.getElementById('result');
const statusPill = document.getElementById('statusPill');
const clearBtn = document.getElementById('clearBtn');

const templates = {
  generate_text: document.getElementById('template-generate_text'),
  improve_text: document.getElementById('template-improve_text'),
  summarize_text: document.getElementById('template-summarize_text'),
  formal_email: document.getElementById('template-formal_email'),
};

let currentMode = 'generate_text';

function setStatus(text, tone = 'neutral') {
  statusPill.textContent = text;
  statusPill.dataset.tone = tone;
}

function renderFields(mode) {
  fields.innerHTML = '';
  const fragment = templates[mode].content.cloneNode(true);
  fields.appendChild(fragment);
}

function switchMode(mode) {
  currentMode = mode;
  tabs.forEach((tab) => tab.classList.toggle('active', tab.dataset.mode === mode));
  renderFields(mode);
  setStatus('Listo');
  result.textContent = 'Aquí aparecerá la respuesta generada.';
}

tabs.forEach((tab) => {
  tab.addEventListener('click', () => switchMode(tab.dataset.mode));
});

clearBtn.addEventListener('click', () => {
  form.reset();
  renderFields(currentMode);
  result.textContent = 'Aquí aparecerá la respuesta generada.';
  setStatus('Limpio');
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = { action: currentMode };

  for (const [key, value] of formData.entries()) {
    payload[key] = value.trim();
  }

  setStatus('Pensando...', 'loading');
  result.textContent = 'Generando respuesta...';

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || 'No se pudo generar la respuesta.');
    }

    result.textContent = data.result;
    setStatus('Listo', 'success');
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
    setStatus('Error', 'error');
  }
});

switchMode(currentMode);
