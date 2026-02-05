function loadSites() {
    fetch('sites.html')
        .then(response => {
            if (!response.ok) throw new Error('sites html not found: ' + response.status);
            return response.text();
        })
        .then(text => {
            const container = document.getElementById('loadSites');
            if (container) {
                container.innerHTML = text;
            }
        })
        .catch(err => console.error('Error al cargar el HTML:', err)); // Eliminado el "." extra
}

loadSites();