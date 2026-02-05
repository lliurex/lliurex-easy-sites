function loadSites(){
	fetch('sites.html')
		.then(response => response.text())
		.then(text => document.getElementById('loadSites').innerHTML = text);
}
loadSites();