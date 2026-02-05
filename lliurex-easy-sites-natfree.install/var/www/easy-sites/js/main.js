function loadSites() {
    fetch('sites.html')
        .then(response => {
            // Verificar si la petición fue exitosa (status 200-299)
            //if (!response.ok) throw new Error('Error de red: ' + response.status);
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