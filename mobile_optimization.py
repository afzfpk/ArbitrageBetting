"""
Optimizações para aplicação móvel e PWA
"""
import streamlit as st

def inject_mobile_optimizations():
    """Injeta CSS e JavaScript para optimização móvel."""
    
    mobile_css = """
    <style>
    /* Optimizações para dispositivos móveis */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem !important;
        }
        
        .main .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Botões maiores para touch */
        .stButton button {
            min-height: 48px !important;
            font-size: 16px !important;
            padding: 12px 24px !important;
        }
        
        /* Inputs maiores */
        .stNumberInput input, .stTextInput input, .stSelectbox select {
            min-height: 48px !important;
            font-size: 16px !important;
        }
        
        /* Cards responsivos */
        .card {
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
        }
        
        /* Texto maior em móvel */
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }
        
        /* Sidebar em móvel */
        .css-1d391kg {
            padding: 1rem 0.5rem !important;
        }
        
        /* Tabs em móvel */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 16px !important;
            font-size: 14px !important;
        }
    }
    
    /* PWA styles */
    .pwa-install-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: center;
        z-index: 1000;
        display: none;
    }
    
    .pwa-install-banner.show {
        display: block;
    }
    
    .pwa-install-btn {
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin-left: 10px;
        cursor: pointer;
    }
    
    /* Optimizações de performance */
    * {
        -webkit-tap-highlight-color: transparent;
    }
    
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Animações suaves */
    .card, .stButton button {
        transition: all 0.2s ease;
    }
    
    /* Scroll suave */
    html {
        scroll-behavior: smooth;
    }
    
    /* Cores de tema escuro optimizadas */
    @media (prefers-color-scheme: dark) {
        .card {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    }
    </style>
    """
    
    # JavaScript para PWA e funcionalidades móveis
    mobile_js = """
    <script>
    // Detecção de dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Service Worker para PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('SW registered: ', registration);
                })
                .catch(function(registrationError) {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
    
    // Install prompt para PWA
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallBanner();
    });
    
    function showInstallBanner() {
        const banner = document.createElement('div');
        banner.className = 'pwa-install-banner show';
        banner.innerHTML = `
            <span>📱 Adicionar à tela inicial para acesso rápido</span>
            <button class="pwa-install-btn" onclick="installPWA()">Instalar</button>
            <button class="pwa-install-btn" onclick="dismissBanner()" style="background: transparent;">✕</button>
        `;
        document.body.appendChild(banner);
    }
    
    function installPWA() {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
                dismissBanner();
            });
        }
    }
    
    function dismissBanner() {
        const banner = document.querySelector('.pwa-install-banner');
        if (banner) {
            banner.remove();
        }
    }
    
    // Optimizações de touch
    if (isMobile) {
        document.addEventListener('touchstart', function() {}, true);
        
        // Prevenir zoom duplo tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Melhorar scroll em iOS
        document.body.style.webkitOverflowScrolling = 'touch';
    }
    
    // Orientação de tela
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            window.scrollTo(0, 0);
        }, 100);
    });
    
    // Vibração para feedback táctil (Android)
    function vibrate(pattern = [100]) {
        if (navigator.vibrate) {
            navigator.vibrate(pattern);
        }
    }
    
    // Adicionar vibração aos botões importantes
    document.addEventListener('click', function(e) {
        if (e.target.matches('.stButton button')) {
            vibrate([50]);
        }
    });
    </script>
    """
    
    st.markdown(mobile_css, unsafe_allow_html=True)
    st.markdown(mobile_js, unsafe_allow_html=True)

def create_pwa_manifest():
    """Cria manifest.json para PWA."""
    
    manifest = {
        "name": "Calculadora de Arbitragem Pro",
        "short_name": "ArbitrageCalc",
        "description": "Calculadora profissional de arbitragem de apostas",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a14",
        "theme_color": "#3366ff",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIHJ4PSI2NCIgZmlsbD0iIzMzNjZmZiIvPjx0ZXh0IHg9IjI1NiIgeT0iMzAwIiBmb250LXNpemU9IjIwMCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfmoI8L3RleHQ+PC9zdmc+",
                "sizes": "512x512",
                "type": "image/svg+xml"
            },
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjE5MiIgaGVpZ2h0PSIxOTIiIHJ4PSIyNCIgZmlsbD0iIzMzNjZmZiIvPjx0ZXh0IHg9Ijk2IiB5PSIxMjAiIGZvbnQtc2l6ZT0iODAiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7wn5qCPC90ZXh0Pjwvc3ZnPg==",
                "sizes": "192x192",
                "type": "image/svg+xml"
            }
        ],
        "categories": ["finance", "sports", "utilities"],
        "lang": "pt-PT"
    }
    
    return manifest

def add_ios_meta_tags():
    """Adiciona meta tags específicas para iOS."""
    
    ios_meta = """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ArbitrageCalc">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#3366ff">
    <meta name="msapplication-TileColor" content="#3366ff">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <!-- iOS Icons -->
    <link rel="apple-touch-icon" sizes="180x180" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDE4MCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjE4MCIgaGVpZ2h0PSIxODAiIHJ4PSIyMCIgZmlsbD0iIzMzNjZmZiIvPjx0ZXh0IHg9IjkwIiB5PSIxMTAiIGZvbnQtc2l6ZT0iNzAiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7wn5qCPC90ZXh0Pjwvc3ZnPg==">
    """
    
    st.markdown(ios_meta, unsafe_allow_html=True)