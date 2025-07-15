"""
Optimizações avançadas para web app e desktop
"""
import streamlit as st

def inject_desktop_features():
    """Injeta funcionalidades específicas para desktop."""
    
    desktop_features = """
    <style>
    /* Optimizações específicas para desktop */
    @media (min-width: 1024px) {
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Melhor uso do espaço em desktop */
        .main .block-container {
            padding: 2rem 3rem;
        }
        
        /* Sidebar mais larga em desktop */
        .css-1d391kg {
            width: 320px !important;
        }
        
        /* Tooltips avançados */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 220px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -110px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Keyboard shortcuts visual */
        .shortcut-key {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 3px;
            padding: 2px 6px;
            font-family: monospace;
            font-size: 11px;
            margin: 0 2px;
        }
    }
    
    /* Multi-monitor support */
    @media (min-width: 1920px) {
        .stApp {
            max-width: 1600px;
        }
        
        .main .block-container {
            padding: 2rem 4rem;
        }
    }
    
    /* Dark/Light theme detection */
    @media (prefers-color-scheme: light) {
        .card {
            background: rgba(0, 0, 0, 0.05) !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            color: #333 !important;
        }
        
        .tooltip .tooltiptext {
            background-color: #f9f9f9;
            color: #333;
            border: 1px solid #ddd;
        }
    }
    
    /* Print styles for desktop */
    @media print {
        .stSidebar, .stButton, .stSelectbox {
            display: none !important;
        }
        
        .card {
            border: 1px solid #000 !important;
            break-inside: avoid;
            margin-bottom: 1rem;
        }
        
        body {
            background: white !important;
            color: black !important;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(51, 102, 255, 0.6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(51, 102, 255, 0.8);
    }
    </style>
    
    <script>
    // Keyboard shortcuts para desktop
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K para quick actions
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Focus no primeiro input
            const firstInput = document.querySelector('.stNumberInput input');
            if (firstInput) firstInput.focus();
        }
        
        // Ctrl/Cmd + Enter para calcular
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            // Trigger calculation (simular click no botão calcular)
            const calculateBtn = document.querySelector('.stButton button');
            if (calculateBtn) calculateBtn.click();
        }
        
        // Escape para limpar
        if (e.key === 'Escape') {
            // Clear all inputs
            document.querySelectorAll('.stNumberInput input').forEach(input => {
                input.value = '';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            });
        }
    });
    
    // Auto-save para desktop
    let autoSaveInterval;
    function startAutoSave() {
        autoSaveInterval = setInterval(() => {
            const data = {
                timestamp: new Date().toISOString(),
                odds: Array.from(document.querySelectorAll('.stNumberInput input')).map(i => i.value)
            };
            localStorage.setItem('arbitrage_autosave', JSON.stringify(data));
        }, 30000); // Save every 30 seconds
    }
    
    // Restore from auto-save
    function restoreAutoSave() {
        const saved = localStorage.getItem('arbitrage_autosave');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                const inputs = document.querySelectorAll('.stNumberInput input');
                data.odds.forEach((value, index) => {
                    if (inputs[index] && value) {
                        inputs[index].value = value;
                        inputs[index].dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            } catch (e) {
                console.log('Auto-save restore failed:', e);
            }
        }
    }
    
    // Initialize desktop features
    setTimeout(() => {
        startAutoSave();
        // restoreAutoSave(); // Uncomment to enable auto-restore
    }, 1000);
    
    // Full screen mode para desktop
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    // Add fullscreen button
    function addFullscreenButton() {
        const button = document.createElement('button');
        button.innerHTML = '⛶';
        button.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            background: rgba(51, 102, 255, 0.8);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            cursor: pointer;
            font-size: 16px;
        `;
        button.onclick = toggleFullscreen;
        document.body.appendChild(button);
    }
    
    // Initialize on desktop
    if (window.innerWidth >= 1024) {
        setTimeout(addFullscreenButton, 2000);
    }
    </script>
    """
    
    st.markdown(desktop_features, unsafe_allow_html=True)

def create_sharing_features():
    """Cria funcionalidades de partilha avançadas."""
    
    sharing_js = """
    <script>
    // Web Share API para dispositivos modernos
    async function shareCalculation(data) {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'Calculadora de Arbitragem',
                    text: data,
                    url: window.location.href
                });
            } catch (err) {
                console.log('Error sharing:', err);
                fallbackShare(data);
            }
        } else {
            fallbackShare(data);
        }
    }
    
    // Fallback para browsers sem Web Share API
    function fallbackShare(data) {
        // Copy to clipboard
        navigator.clipboard.writeText(data).then(() => {
            // Show notification
            showNotification('Texto copiado para área de transferência!');
        });
    }
    
    // Notification system
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        // Add slide animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
            style.remove();
        }, 3000);
    }
    
    // QR Code generation para partilha fácil
    function generateQRCode(data) {
        const qrData = encodeURIComponent(data);
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${qrData}`;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="color: #333; margin-bottom: 15px;">Partilhar via QR Code</h3>
                <img src="${qrUrl}" alt="QR Code" style="border: 1px solid #ddd;">
                <p style="color: #666; margin: 10px 0; font-size: 12px;">Digitaliza com o telemóvel</p>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: #3366ff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Fechar
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
    }
    
    // URL shortener simulation (in production, use real service)
    function shortenUrl(longUrl) {
        const hash = btoa(longUrl).slice(0, 8);
        return `https://arb.ly/${hash}`;
    }
    
    window.shareCalculation = shareCalculation;
    window.generateQRCode = generateQRCode;
    window.showNotification = showNotification;
    </script>
    """
    
    st.markdown(sharing_js, unsafe_allow_html=True)

def add_accessibility_features():
    """Adiciona funcionalidades de acessibilidade."""
    
    accessibility_css = """
    <style>
    /* High contrast mode */
    @media (prefers-contrast: high) {
        .card {
            border: 2px solid currentColor !important;
        }
        
        .stButton button {
            border: 2px solid currentColor !important;
        }
    }
    
    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Focus indicators */
    .stButton button:focus,
    .stNumberInput input:focus,
    .stSelectbox select:focus {
        outline: 3px solid #3366ff !important;
        outline-offset: 2px !important;
    }
    
    /* Screen reader only text */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    /* Skip link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: #3366ff;
        color: white;
        padding: 8px;
        border-radius: 4px;
        text-decoration: none;
        z-index: 10000;
    }
    
    .skip-link:focus {
        top: 6px;
    }
    </style>
    
    <script>
    // Add skip link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Saltar para conteúdo principal';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content landmark
    const mainContent = document.querySelector('.main');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }
    
    // Voice commands (experimental)
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'pt-PT';
        
        recognition.onresult = function(event) {
            const command = event.results[0][0].transcript.toLowerCase();
            console.log('Voice command:', command);
            
            // Simple voice commands
            if (command.includes('calcular')) {
                const btn = document.querySelector('.stButton button');
                if (btn) btn.click();
            } else if (command.includes('limpar')) {
                document.querySelectorAll('.stNumberInput input').forEach(input => {
                    input.value = '';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                });
            }
        };
        
        // Add voice control button (optional)
        function addVoiceButton() {
            const voiceBtn = document.createElement('button');
            voiceBtn.innerHTML = '🎤';
            voiceBtn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                font-size: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 9999;
            `;
            voiceBtn.onclick = () => recognition.start();
            voiceBtn.title = 'Comando de voz (diz "calcular" ou "limpar")';
            document.body.appendChild(voiceBtn);
        }
        
        // Uncomment to enable voice control
        // setTimeout(addVoiceButton, 3000);
    }
    </script>
    """
    
    st.markdown(accessibility_css, unsafe_allow_html=True)

def inject_performance_monitoring():
    """Adiciona monitorização de performance."""
    
    performance_js = """
    <script>
    // Performance monitoring
    let performanceData = {
        pageLoadTime: 0,
        calculationTimes: [],
        errors: []
    };
    
    // Measure page load time
    window.addEventListener('load', () => {
        performanceData.pageLoadTime = performance.now();
        console.log(`Página carregada em ${performanceData.pageLoadTime.toFixed(2)}ms`);
    });
    
    // Monitor calculation performance
    function monitorCalculation(startTime) {
        const duration = performance.now() - startTime;
        performanceData.calculationTimes.push(duration);
        
        if (duration > 1000) { // Slow calculation
            console.warn(`Cálculo lento: ${duration.toFixed(2)}ms`);
        }
        
        // Keep only last 10 measurements
        if (performanceData.calculationTimes.length > 10) {
            performanceData.calculationTimes.shift();
        }
    }
    
    // Error tracking
    window.addEventListener('error', (e) => {
        performanceData.errors.push({
            message: e.message,
            filename: e.filename,
            line: e.lineno,
            timestamp: new Date().toISOString()
        });
        
        console.error('App error tracked:', e.message);
    });
    
    // Memory usage monitoring (Chrome only)
    function checkMemoryUsage() {
        if (performance.memory) {
            const memory = performance.memory;
            const usage = {
                used: Math.round(memory.usedJSHeapSize / 1048576),
                total: Math.round(memory.totalJSHeapSize / 1048576),
                limit: Math.round(memory.jsHeapSizeLimit / 1048576)
            };
            
            if (usage.used > 50) { // Over 50MB
                console.warn(`Uso de memória elevado: ${usage.used}MB`);
            }
            
            return usage;
        }
        return null;
    }
    
    // Check memory every 30 seconds
    setInterval(checkMemoryUsage, 30000);
    
    // Performance report function
    window.getPerformanceReport = function() {
        const avgCalculationTime = performanceData.calculationTimes.length > 0 
            ? performanceData.calculationTimes.reduce((a, b) => a + b) / performanceData.calculationTimes.length 
            : 0;
            
        return {
            pageLoadTime: performanceData.pageLoadTime,
            avgCalculationTime: avgCalculationTime.toFixed(2),
            totalCalculations: performanceData.calculationTimes.length,
            totalErrors: performanceData.errors.length,
            memoryUsage: checkMemoryUsage()
        };
    };
    </script>
    """
    
    st.markdown(performance_js, unsafe_allow_html=True)