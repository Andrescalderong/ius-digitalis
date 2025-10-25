document.addEventListener('DOMContentLoaded', async () => {
  try {
    const r = await fetch('blockchain_registry/outputs/anchors.json', { cache: 'no-store' });
    const data = await r.json();
    const resultsEl = document.getElementById('results') || document.body;

    function showResults() {
      const container = document.getElementById('transactions') || resultsEl;
      container.innerHTML = '';
      if (!data?.anchors?.length) {
        container.innerHTML = '<div style="color:#f55">Sin datos de transacciones</div>';
        return;
      }
      data.anchors.forEach((anchor, i) => {
        const dateStr = new Date(anchor.timestamp * 1000).toLocaleString('es-ES');
        container.insertAdjacentHTML('beforeend', `
          <div class="transaction">
            <h3 style="color:#4ecdc4;margin-bottom:15px;">📄 Transacción #${i+1}</h3>
            <div class="tx-row"><span class="tx-label">Expediente:</span><span class="tx-value">${anchor.expediente_id}</span></div>
            <div class="tx-row"><span class="tx-label">Categoría:</span><span class="tx-value">${anchor.categoria}</span></div>
            <div class="tx-row"><span class="tx-label">SHA-256:</span><span class="hash">${anchor.sha256}</span></div>
            <div class="tx-row"><span class="tx-label">TX ID:</span><span class="hash">${anchor.txid}</span></div>
            <div class="tx-row"><span class="tx-label">Network:</span><span class="tx-value">${anchor.network}</span></div>
            <div class="tx-row"><span class="tx-label">Timestamp:</span><span class="tx-value" style="color:#4ecdc4;">${dateStr}</span></div>
          </div>
        `);
      });
      resultsEl.classList?.add?.('show');
    }

    showResults();
  } catch (e) {
    console.error('Error cargando anchors.json:', e);
    (document.getElementById('transactions') || document.body)
      .insertAdjacentHTML('beforeend','<div style="color:#f55">No se pudo cargar anchors.json</div>');
  }
});
