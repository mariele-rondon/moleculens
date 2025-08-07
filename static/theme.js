// Função para aplicar o tema e o ícone do botão.
// Deixamos a função no escopo global para ser acessível por todos os scripts.
function applyTheme(theme) {
    const themeToggleButton = document.getElementById('theme-toggle');
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        if (themeToggleButton) themeToggleButton.textContent = '☀️';
    } else {
        document.documentElement.classList.remove('dark-mode');
        if (themeToggleButton) themeToggleButton.textContent = '🌙';
    }
}

// Lógica de clique que será usada em todas as páginas
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle');

    // Adiciona o evento de clique ao botão
    themeToggleButton.addEventListener('click', () => {
        const newTheme = document.documentElement.classList.contains('dark-mode') ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);

        // Dispara um evento customizado para que outras partes da página (como o 3Dmol) possam reagir
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
    });

    // Garante que o ícone do botão esteja correto no carregamento da página
    const currentTheme = localStorage.getItem('theme') || 'light';
    if(currentTheme === 'dark') {
        if (themeToggleButton) themeToggleButton.textContent = '☀️';
    } else {
        if (themeToggleButton) themeToggleButton.textContent = '🌙';
    }
});
