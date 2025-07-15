import streamlit as st
import math
import pandas as pd
from datetime import datetime
import database as db
import base64
import random
from pathlib import Path

# Configuração da página para mobile
st.set_page_config(
    page_title="🎯 Arbitragem Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Mobile Profissional
st.markdown("""
<style>
/* Layout Mobile Profissional */
.stApp {
    background: linear-gradient(135deg, #0a0a14, #121220);
}

/* Esconder sidebar no mobile */
.css-1d391kg {
    display: none !important;
}

/* Header mobile elegante */
.mobile-header {
    background: linear-gradient(135deg, #3366ff 0%, #667eea 100%);
    color: white;
    padding: 1.5rem;
    margin: -1rem -1rem 1rem -1rem;
    border-radius: 0 0 20px 20px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* Cards mobile */
.mobile-card {
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

/* Inputs mobile */
.stNumberInput input {
    font-size: 18px !important;
    padding: 1rem !important;
    border-radius: 15px !important;
    border: 2px solid rgba(51, 102, 255, 0.3) !important;
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    transition: all 0.3s ease !important;
}

.stNumberInput input:focus {
    border-color: #3366ff !important;
    box-shadow: 0 4px 20px rgba(51, 102, 255, 0.5) !important;
    transform: scale(1.02) !important;
}

/* Botões mobile */
.stButton button {
    width: 100% !important;
    padding: 1rem !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    border-radius: 15px !important;
    border: none !important;
    background: linear-gradient(135deg, #3366ff 0%, #667eea 100%) !important;
    color: white !important;
    box-shadow: 0 8px 24px rgba(51, 102, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(51, 102, 255, 0.4) !important;
}

/* Resultado mobile */
.result-success {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
}

.result-error {
    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(244, 67, 54, 0.3);
}

.profit-value {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0.5rem 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Animações */
.mobile-card {
    animation: slideUp 0.5s ease;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Tabela mobile */
.mobile-table {
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    overflow: hidden;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

.mobile-table table {
    width: 100%;
    border-collapse: collapse;
}

.mobile-table th {
    background: rgba(51, 102, 255, 0.8);
    color: white;
    padding: 1rem;
    font-weight: 700;
    text-align: left;
}

.mobile-table td {
    padding: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    color: white;
}

/* Selectbox mobile */
.stSelectbox select {
    font-size: 16px !important;
    padding: 1rem !important;
    border-radius: 15px !important;
    border: 2px solid rgba(51, 102, 255, 0.3) !important;
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
}

/* Text styling */
h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

p, span, div {
    color: rgba(255,255,255,0.9) !important;
}

/* Botões de ação */
.action-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.5rem;
    margin: 1rem 0;
}

.action-btn {
    padding: 0.8rem;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
    text-align: center;
}

.btn-primary {
    background: linear-gradient(135deg, #3366ff 0%, #667eea 100%);
    color: white;
}

.btn-success {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
}

.btn-warning {
    background: linear-gradient(135deg, #FF5722 0%, #f44336 100%);
    color: white;
}

/* Tabs mobile */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 15px;
    background: rgba(255,255,255,0.1);
    color: white;
    padding: 1rem;
    border: none;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3366ff 0%, #667eea 100%);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Header Mobile
st.markdown("""
<div class="mobile-header">
    <h1 style="margin: 0; font-size: 1.8rem;">🎯 Arbitragem Pro</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Calculadora Profissional de Apostas</p>
</div>
""", unsafe_allow_html=True)

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📊 Calcular", "📈 Histórico", "💡 Ajuda"])

with tab1:
    # Calculadora principal
    st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Primeira Odd")
        odd1 = st.number_input("Odd 1:", min_value=1.01, max_value=50.0, value=2.10, step=0.01, key="odd1_mobile")
        
        st.markdown("### 🏢 Casa de Apostas")
        bookmaker1 = st.selectbox("Casa 1:", ["Betano.pt", "888Starz", "Placard.pt", "Betclic.pt"], key="book1_mobile")
    
    with col2:
        st.markdown("### 🎯 Segunda Odd")
        odd2 = st.number_input("Odd 2:", min_value=1.01, max_value=50.0, value=2.05, step=0.01, key="odd2_mobile")
        
        st.markdown("### 🏢 Casa de Apostas")  
        bookmaker2 = st.selectbox("Casa 2:", ["888Starz", "Betano.pt", "Placard.pt", "Betclic.pt"], key="book2_mobile")
    
    st.markdown("### 💰 Montante Total")
    total_stake = st.number_input("Total a apostar (€):", min_value=1.0, max_value=100000.0, value=100.0, step=1.0, key="stake_mobile")
    
    st.markdown("### 📝 Nome do Evento (Opcional)")
    event_name = st.text_input("Ex: Benfica vs Porto", key="event_mobile")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão de cálculo
    if st.button("🚀 Calcular Arbitragem", key="calc_mobile"):
        # Cálculos
        prob1 = 1 / odd1
        prob2 = 1 / odd2
        total_prob = prob1 + prob2
        
        if total_prob < 1:
            # Há arbitragem
            profit_percent = (1 - total_prob) * 100
            
            # Cálculo das apostas
            stake1 = total_stake * prob1 / total_prob
            stake2 = total_stake * prob2 / total_prob
            
            profit = min(stake1 * odd1, stake2 * odd2) - total_stake
            
            # Resultado de sucesso
            st.markdown(f"""
            <div class="result-success">
                <h2 style="margin: 0; color: white;">✅ Oportunidade Encontrada!</h2>
                <div class="profit-value">€{profit:.2f}</div>
                <p style="margin: 0; color: white;">Lucro de {profit_percent:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabela de apostas
            st.markdown("""
            <div class="mobile-table">
                <table>
                    <thead>
                        <tr>
                            <th>Casa de Apostas</th>
                            <th>Odd</th>
                            <th>Apostar</th>
                            <th>Retorno</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{}</td>
                            <td>{:.2f}</td>
                            <td>€{:.2f}</td>
                            <td>€{:.2f}</td>
                        </tr>
                        <tr>
                            <td>{}</td>
                            <td>{:.2f}</td>
                            <td>€{:.2f}</td>
                            <td>€{:.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """.format(
                bookmaker1, odd1, stake1, stake1 * odd1,
                bookmaker2, odd2, stake2, stake2 * odd2
            ), unsafe_allow_html=True)
            
            # Botões de ação
            st.markdown("""
            <div class="action-buttons">
                <button class="action-btn btn-primary" onclick="shareCalculation()">
                    📋 Copiar
                </button>
                <button class="action-btn btn-success" onclick="generateQRCode()">
                    📱 QR Code
                </button>
                <button class="action-btn btn-warning" onclick="shareResult()">
                    🔗 Partilhar
                </button>
            </div>
            """, unsafe_allow_html=True)
            
            # Guardar no histórico
            try:
                db.save_arbitrage_opportunity(
                    odd1, odd2, total_stake, stake1, stake2, profit, profit_percent,
                    event_name, bookmaker1, bookmaker2
                )
                st.success("💾 Guardado no histórico!")
            except Exception as e:
                st.warning(f"Erro ao guardar: {e}")
        
        else:
            # Sem arbitragem
            st.markdown(f"""
            <div class="result-error">
                <h2 style="margin: 0; color: white;">❌ Sem Arbitragem</h2>
                <p style="margin: 0.5rem 0 0 0; color: white;">
                    Soma das probabilidades: {total_prob*100:.2f}%<br>
                    Precisa ser menor que 100%
                </p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    # Histórico
    st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Histórico de Cálculos")
    
    try:
        history = db.get_arbitrage_history(10)
        if history:
            for item in history:
                profit_color = "#4CAF50" if item['profit'] > 0 else "#f44336"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid {profit_color};">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div>
                            <strong>{item.get('event_name', 'Evento')} ({item.get('bookmaker1', 'Casa 1')} vs {item.get('bookmaker2', 'Casa 2')})</strong><br>
                            <small>Odds: {item['odd1']:.2f} / {item['odd2']:.2f}</small>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: {profit_color};">
                                €{item['profit']:.2f}
                            </div>
                            <small>{item['profit_percent']:.2f}%</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum cálculo no histórico ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    # Ajuda
    st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
    st.markdown("### 💡 Guia Rápido")
    
    st.markdown("""
    **🎯 O que é arbitragem?**
    
    Estratégia que aproveita diferenças de odds entre casas de apostas para garantir lucro independentemente do resultado.
    
    **🔍 Como funciona?**
    
    1. Encontre odds diferentes para o mesmo evento
    2. Calcule as apostas necessárias  
    3. Aposte em ambos os resultados
    4. Lucro garantido! 💰
    
    **📐 Fórmula simples**
    
    Se (1/Odds1 + 1/Odds2) < 1, então há arbitragem!
    
    **💡 Exemplo prático**
    
    - Betano: Odds 2.10 → Probabilidade 47.6%
    - 888Starz: Odds 2.05 → Probabilidade 48.8%
    - Total: 96.4% → **Lucro de 3.6%**
    
    **🏆 Dicas importantes**
    
    - Aposte rapidamente (odds mudam)
    - Verifique limites das casas
    - Tenha contas em múltiplas casas
    - Comece com valores pequenos
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# JavaScript para funcionalidades
st.markdown("""
<script>
function shareCalculation() {
    const result = document.querySelector('.result-success');
    if (result) {
        const text = result.innerText;
        if (navigator.share) {
            navigator.share({
                title: 'Oportunidade de Arbitragem',
                text: text,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(text);
            alert('Texto copiado!');
        }
    }
}

function generateQRCode() {
    const qrData = encodeURIComponent(window.location.href);
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
        <div style="background: white; padding: 20px; border-radius: 15px; text-align: center;">
            <h3 style="color: #333; margin-bottom: 15px;">Partilhar via QR Code</h3>
            <img src="${qrUrl}" alt="QR Code" style="border: 1px solid #ddd; border-radius: 10px;">
            <p style="color: #666; margin: 10px 0; font-size: 14px;">Digitaliza com o telemóvel</p>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: #3366ff; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                Fechar
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
}

function shareResult() {
    const url = window.location.href;
    if (navigator.share) {
        navigator.share({
            title: 'Calculadora de Arbitragem',
            text: 'Confere esta oportunidade de arbitragem!',
            url: url
        });
    } else {
        navigator.clipboard.writeText(url);
        alert('Link copiado!');
    }
}
</script>
""", unsafe_allow_html=True)