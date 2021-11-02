window.addEventListener('load', function() {
    //Handles loading screen
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.cssText += 'animation: fade-out 1s;';
    loadingScreen.innerHTML = '';
    setTimeout(() => loadingScreen.remove(), 1000);
});