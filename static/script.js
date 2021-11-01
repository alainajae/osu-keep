window.addEventListener('load', function() {
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.cssText += 'animation: fade-out 1s;';
    loadingScreen.innerHTML = '';
    setTimeout(() => loadingScreen.remove(), 1000);
});