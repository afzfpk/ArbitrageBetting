// Função para copiar texto para a área de transferência
function copyToClipboard(text) {
  const el = document.createElement('textarea');
  el.value = text;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
}

// Função para configurar botões de cópia em toda a página
function setupCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const textToCopy = this.getAttribute('data-clipboard-text');
      if (textToCopy) {
        copyToClipboard(textToCopy);
        
        // Feedback visual temporário
        const originalText = this.innerHTML;
        this.innerHTML = "✓ Copiado!";
        
        setTimeout(() => {
          this.innerHTML = originalText;
        }, 2000);
      }
    });
  });
}

// Executar quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', setupCopyButtons);

// Verificar e configurar periodicamente novos botões (para elementos dinâmicos)
setInterval(setupCopyButtons, 2000);