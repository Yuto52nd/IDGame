const packPicker = document.querySelector('.pack-picker');

if (packPicker) {
  const toggles = [...packPicker.querySelectorAll('.pack-toggle')];
  const summary = packPicker.querySelector('[data-pack-summary]');

  function updatePackSummary() {
    const selected = toggles.filter((toggle) => toggle.checked);
    if (!selected.length) {
      summary.textContent = 'Choose banks';
      summary.classList.add('empty');
      return;
    }

    summary.classList.remove('empty');
    summary.textContent = selected.length === toggles.length
      ? 'All banks'
      : `${selected.length} bank${selected.length === 1 ? '' : 's'} selected`;
  }

  toggles.forEach((toggle) => toggle.addEventListener('change', updatePackSummary));

  packPicker.querySelectorAll('[data-pack-action]').forEach((action) => {
    action.addEventListener('click', () => {
      const shouldSelect = action.dataset.packAction === 'all';
      toggles.forEach((toggle) => {
        toggle.checked = shouldSelect;
      });
      updatePackSummary();
    });
  });

  packPicker.closest('form').addEventListener('submit', (event) => {
    if (!toggles.some((toggle) => toggle.checked)) {
      event.preventDefault();
      packPicker.open = true;
      toggles[0].focus();
    }
  });

  updatePackSummary();
}