import streamlit as st
import math
import pandas as pd
from datetime import datetime
import database as db
import base64
import random
from pathlib import Path
import odds_api
import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from security_utils import SecurityUtils, RateLimiter, rate_limit_decorator, validate_environment_variables
from bookmaker_helpers import BookmakerHelpers, ArbitrageAnalyzer
from advanced_security import AdvancedSecurity, PerformanceOptimizer, UserExperience, init_advanced_features
from user_management import init_authentication, require_authentication, show_pricing_page, SubscriptionManager
from mobile_optimization import inject_mobile_optimizations, add_ios_meta_tags
from analytics_dashboard import show_analytics_dashboard, export_data_to_csv
from webapp_optimizer import inject_desktop_features, create_sharing_features, add_accessibility_features, inject_performance_monitoring
from payment_system import PaymentSystem, show_pricing_page, init_payment_system

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Arbitragem",
    page_icon="🎯",
    layout="wide"
)

# Validar variáveis de ambiente na inicialização
validate_environment_variables()

# Inicializar rate limiter para API
api_rate_limiter = RateLimiter(max_calls=30, time_window=60)

# Inicializar funcionalidades avançadas
init_advanced_features()

# Inicializar autenticação e pagamentos
init_authentication()
init_payment_system()

# Adicionar optimizações móveis e desktop
inject_mobile_optimizations()
add_ios_meta_tags()
inject_desktop_features()
create_sharing_features()
add_accessibility_features()
inject_performance_monitoring()

# Verificar autenticação (comentar para testar sem login)
# require_authentication()

# Carregar CSS personalizado com segurança
def load_css(css_file):
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
            # Sanitizar CSS para remover possíveis scripts maliciosos
            css_content = SecurityUtils.sanitize_input(css_content)
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo CSS não encontrado: {css_file}")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

# Carrega JavaScript personalizado com segurança
def load_js(js_file):
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
            # Validar que o JavaScript não contém código malicioso
            if 'eval(' in js_content or 'document.write(' in js_content:
                st.error("JavaScript contém código potencialmente perigoso")
                return
            st.markdown(f'<script>{js_content}</script>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo JavaScript não encontrado: {js_file}")
    except Exception as e:
        st.error(f"Erro ao carregar JavaScript: {e}")

try:
    load_css("styles.css")
    load_css("mobile_layout.css")
    load_css("universal_layout.css")
    
    # Incluir o script JavaScript para funcionalidade de cópia
    load_js("clipboard.js")
    
    # Adicionar JavaScript para exclusão de oportunidades
    st.markdown("""
    <script>
    function deleteOpportunity(id) {
        if (confirm('Tem certeza que deseja excluir esta oportunidade?')) {
            // Usar o mecanismo de comunicação do Streamlit com o backend
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: {
                    action: 'delete',
                    id: id
                }
            }, '*');
        }
    }
    </script>
    """, unsafe_allow_html=True)
except Exception as e:
    st.write(f"Erro ao carregar recursos: {e}")

# Função para criar fundo de gradiente suave
def add_bg_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0a0a14, #121220, #151525, #121220);
            background-size: 400% 400%;
            animation: gradient 20s ease infinite;
        }
        
        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_bg_style()

# Inicializar sessão de estado para odds API
if 'api_odds' not in st.session_state:
    st.session_state.api_odds = []
if 'last_api_check' not in st.session_state:
    st.session_state.last_api_check = 0
if 'selected_opportunity' not in st.session_state:
    st.session_state.selected_opportunity = None
if 'api_loading' not in st.session_state:
    st.session_state.api_loading = False
# Valores temporários para odds da API
if 'temp_odd1' not in st.session_state:
    st.session_state.temp_odd1 = 2.10
if 'temp_odd2' not in st.session_state:
    st.session_state.temp_odd2 = 1.90

# Função para carregar oportunidades de arbitragem da API com rate limiting
@rate_limit_decorator(api_rate_limiter)
def load_arbitrage_opportunities():
    try:
        st.session_state.api_loading = True
        api = odds_api.OddsAPI()
        opportunities = api.find_arbitrage_opportunities(min_profit=0.5)
        st.session_state.api_odds = opportunities
        st.session_state.last_api_check = time.time()
        st.session_state.api_loading = False
        return opportunities
    except Exception as e:
        st.error(f"Erro ao carregar oportunidades: {SecurityUtils.secure_display_text(str(e))}")
        st.session_state.api_loading = False
        return []

# Função para selecionar uma oportunidade específica
def select_opportunity(opportunity_index):
    opportunity = st.session_state.api_odds[opportunity_index]
    st.session_state.selected_opportunity = opportunity
    # Extrair as odds para o formulário - armazenar em variáveis temporárias
    # (não podemos modificar diretamente os widgets já instanciados)
    odds = [outcome["odd"] for outcome in opportunity["outcomes"]]
    if len(odds) >= 2:
        st.session_state.temp_odd1 = odds[0]
        st.session_state.temp_odd2 = odds[1]
    
    # Certificar que estamos na primeira aba
    st.session_state.active_tab = 0
    st.rerun()

# Inicializar aba ativa
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
    
# Inicializar estado para ações de exclusão
if 'delete_action' not in st.session_state:
    st.session_state.delete_action = None

# Processar ação de exclusão se houver
if st.session_state.delete_action:
    opportunity_id = st.session_state.delete_action
    if db.delete_arbitrage_opportunity(opportunity_id):
        st.success(f"Oportunidade {opportunity_id} excluída com sucesso!")
    else:
        st.error(f"Erro ao excluir oportunidade {opportunity_id}.")
    st.session_state.delete_action = None
    st.rerun()

# Usaremos botões do Streamlit para exclusão em vez de JavaScript
# Isso simplifica a implementação e garante compatibilidade

# Callback para mudar de aba
def set_active_tab(tab_index):
    st.session_state.active_tab = tab_index
    st.rerun()

# Header profissional universal
st.markdown("""
<div class="professional-header">
    <div class="header-content">
        <div class="logo-section">
            <div class="logo-icon">AB</div>
            <div class="title-section">
                <h1>Arbitrage Calculator Pro</h1>
                <p>Professional betting arbitrage analysis platform</p>
            </div>
        </div>
        <div class="status-section">
            <div class="status-indicator status-live">
                <span>● Live</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navegação universal profissional
st.markdown("""
<div class="universal-nav">
    <div class="nav-button active" onclick="setActiveTab(0)">
        <span class="nav-icon">📊</span>
        <span>Calculator</span>
    </div>
    <div class="nav-button" onclick="setActiveTab(1)">
        <span class="nav-icon">🎯</span>
        <span>Live Odds</span>
    </div>
    <div class="nav-button" onclick="setActiveTab(2)">
        <span class="nav-icon">📈</span>
        <span>Analytics</span>
    </div>
    <div class="nav-button" onclick="setActiveTab(3)">
        <span class="nav-icon">👤</span>
        <span>Account</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Criar tabs para entrada manual vs API vs Analytics
tab1, tab2, tab3, tab4 = st.tabs(["Calculator", "Live Odds", "Analytics", "Account"])

with tab1:
    # Criar container com estilo de card para as entradas
    st.markdown("""
    <div class="professional-card">
        <h2 style='font-size: 1.8rem; margin-bottom: 1.5rem; color: var(--accent-red); text-align: center;'>
            Enter Betting Information
        </h2>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # Adicionar um estilo de card para a seção de entrada
        st.markdown("<div class='professional-card'>", unsafe_allow_html=True)
        
        # Layout em colunas para as entradas
        col1, col2, col3 = st.columns([3, 3, 4])
        
        with col1:
            st.markdown("<p style='margin-bottom: 0.5rem; font-weight: 600;'>Casa de Apostas 1</p>", unsafe_allow_html=True)
            odd1 = st.number_input(
                "Odd para Resultado 1",
                min_value=1.01,
                max_value=1000.0,
                step=0.01,
                value=st.session_state.temp_odd1,
                format="%.2f",
                help="A odd decimal para o primeiro resultado (1.01 - 1000.0)",
                key="odd1"
            )
            
            # Validação de segurança para odd1
            if not SecurityUtils.validate_odds(odd1):
                st.error("Odd 1 inválida. Deve estar entre 1.01 e 1000.0")
            
        with col2:
            st.markdown("<p style='margin-bottom: 0.5rem; font-weight: 600;'>Casa de Apostas 2</p>", unsafe_allow_html=True)
            odd2 = st.number_input(
                "Odd para Resultado 2",
                min_value=1.01,
                max_value=1000.0,
                step=0.01,
                value=st.session_state.temp_odd2,
                format="%.2f",
                help="A odd decimal para o segundo resultado (1.01 - 1000.0)",
                key="odd2"
            )
            
            # Validação de segurança para odd2
            if not SecurityUtils.validate_odds(odd2):
                st.error("Odd 2 inválida. Deve estar entre 1.01 e 1000.0")
        
        with col3:
            st.markdown("<p style='margin-bottom: 0.5rem; font-weight: 600;'>Montante Disponível</p>", unsafe_allow_html=True)
            total_stake = st.number_input(
                "Montante Total a Apostar (€)",
                min_value=0.01,
                max_value=1000000.0,
                step=10.0,
                value=100.0,
                format="%.2f",
                help="O montante total que deseja apostar (0.01 - 1,000,000)"
            )
            
            # Validação de segurança avançada para stake
            stake_validation = AdvancedSecurity.validate_bet_amount(total_stake)
            if not stake_validation["valid"]:
                st.error(stake_validation["reason"])
            elif stake_validation.get("warning"):
                st.warning(stake_validation["warning"])
            
            # Seletor de casas de apostas
            st.markdown("<p style='margin-bottom: 0.5rem; font-weight: 600;'>Casas de Apostas</p>", unsafe_allow_html=True)
            col_bm1, col_bm2 = st.columns(2)
            with col_bm1:
                bookmaker1 = st.selectbox(
                    "Casa 1", 
                    ["Betano.pt", "888Starz", "Placard.pt", "Betclic.pt", "Outra"],
                    index=0,
                    key="bm1"
                )
            with col_bm2:
                bookmaker2 = st.selectbox(
                    "Casa 2", 
                    ["888Starz", "Betano.pt", "Placard.pt", "Betclic.pt", "Outra"],
                    index=0,
                    key="bm2"
                )
            
            # Adicionar um slider para ajuste rápido do montante
            stake_factor = st.slider(
                "Multiplicador de montante",
                min_value=0.5,
                max_value=10.0,
                value=1.0,
                step=0.5,
                help="Multiplique seu montante base para ajustar rapidamente"
            )
            
            # Atualizar o montante com base no multiplicador
            if stake_factor != 1.0:
                total_stake = total_stake * stake_factor
                
        st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card
        
        # Espaçamento 
        st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='font-size: 1.8rem; margin-bottom: 1.5rem; color: #3366ff;'>🔍 Oportunidades de Arbitragem ao Vivo</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Verificar tempo desde a última atualização
        time_since_check = time.time() - st.session_state.last_api_check
        if time_since_check > 300:  # 5 minutos
            st.info("Os dados podem estar desatualizados. Considere atualizar as oportunidades.")
    
    with col2:
        if st.button("🔄 Atualizar Odds", use_container_width=True):
            with st.spinner("Buscando oportunidades de arbitragem..."):
                load_arbitrage_opportunities()
    
    # Exibir oportunidades em formato de card
    if st.session_state.api_loading:
        st.info("Carregando oportunidades de arbitragem...")
    elif not st.session_state.api_odds:
        if st.button("🔍 Buscar Oportunidades", type="primary", use_container_width=True):
            with st.spinner("Buscando oportunidades de arbitragem..."):
                load_arbitrage_opportunities()
    else:
        # Mostrar oportunidades como cards selecionáveis
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 1rem;'>Oportunidades Disponíveis</h3>", unsafe_allow_html=True)
        
        # Criar DataFrame para exibição de oportunidades
        opportunities_data = []
        for i, opp in enumerate(st.session_state.api_odds):
            home_team = opp['home_team']
            away_team = opp['away_team']
            profit = opp['profit_percent']
            
            # Construir nomes das casas de apostas
            bookmakers = [outcome['bookmaker'] for outcome in opp['outcomes']]
            bookmakers_str = " / ".join(bookmakers[:2])  # Mostrar apenas as duas primeiras
            
            opportunities_data.append({
                "ID": i,
                "Jogo": f"{home_team} vs {away_team}",
                "Lucro": f"{profit:.2f}%",
                "Casas de Apostas": bookmakers_str
            })
        
        if opportunities_data:
            opportunities_df = pd.DataFrame(opportunities_data)
            st.dataframe(
                opportunities_df,
                hide_index=True,
                column_config={
                    "ID": st.column_config.Column(
                        "ID",
                        width="small",
                    ),
                    "Jogo": st.column_config.Column(
                        "Jogo",
                        width="medium",
                    ),
                    "Lucro": st.column_config.Column(
                        "Lucro Potencial",
                        width="small",
                    ),
                    "Casas de Apostas": st.column_config.Column(
                        "Casas de Apostas",
                        width="medium",
                    ),
                },
                use_container_width=True
            )
            
            # Seleção de oportunidade
            selected_id = st.selectbox(
                "Selecione uma oportunidade para calcular",
                options=[i for i in range(len(opportunities_data))],
                format_func=lambda x: f"{opportunities_data[x]['Jogo']} - Lucro: {opportunities_data[x]['Lucro']}"
            )
            
            if st.button("✅ Usar esta oportunidade", type="primary"):
                select_opportunity(selected_id)
        else:
            st.info("Nenhuma oportunidade de arbitragem encontrada. Tente novamente mais tarde.")
        
        st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card

    # Se uma oportunidade foi selecionada, mostrar detalhes
    if st.session_state.selected_opportunity:
        opp = st.session_state.selected_opportunity
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 1rem;'>Detalhes da Oportunidade Selecionada</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='margin-bottom: 1rem;'>
            <p><strong>Jogo:</strong> {opp['home_team']} vs {opp['away_team']}</p>
            <p><strong>Lucro potencial:</strong> {opp['profit_percent']:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar cada uma das odds com seus bookmakers
        st.markdown("<p><strong>Odds disponíveis:</strong></p>", unsafe_allow_html=True)
        for outcome in opp['outcomes']:
            st.markdown(f"""
            <div style='background: rgba(51, 102, 255, 0.1); padding: 0.5rem; margin-bottom: 0.5rem; border-radius: 4px;'>
                <p style='margin: 0;'><strong>{outcome['name']}:</strong> {outcome['odd']} ({outcome['bookmaker']})</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card

# Cálculos
st.markdown("""
<div style='text-align: center;'>
    <h2 style='font-size: 1.8rem; margin-bottom: 1.5rem; color: #FF5722;'>🔎 Análise de Arbitragem</h2>
</div>
""", unsafe_allow_html=True)

# Calcular probabilidades implícitas
implied_prob1 = 1 / odd1
implied_prob2 = 1 / odd2
total_implied_prob = implied_prob1 + implied_prob2

# Formatar percentagens para exibição
implied_prob1_pct = f"{implied_prob1 * 100:.2f}%"
implied_prob2_pct = f"{implied_prob2 * 100:.2f}%"
total_implied_prob_pct = f"{total_implied_prob * 100:.2f}%"

# Calcular a margem da casa
margin = (total_implied_prob - 1) * 100

# Adicionar um indicador visual
st.markdown("<div class='card'>", unsafe_allow_html=True)

# Exibir probabilidades implícitas com visual aprimorado
st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 1rem;'>Probabilidades Implícitas</h3>", unsafe_allow_html=True)

# Criar um layout mais atraente para as métricas
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 87, 34, 0.1);'>
        <h4 style='margin: 0; font-size: 1rem;'>Resultado 1</h4>
        <p style='font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #FF5722;'>{implied_prob1_pct}</p>
        <p style='margin: 0; opacity: 0.7; font-size: 0.9rem;'>Odd: {odd1:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 87, 34, 0.1);'>
        <h4 style='margin: 0; font-size: 1rem;'>Resultado 2</h4>
        <p style='font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: #FF5722;'>{implied_prob2_pct}</p>
        <p style='margin: 0; opacity: 0.7; font-size: 0.9rem;'>Odd: {odd2:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Determinar a cor com base na possibilidade de arbitragem
    prob_color = "#4CAF50" if total_implied_prob < 1 else "#F44336"
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba({prob_color.lstrip('#')[:2]}, {prob_color.lstrip('#')[2:4]}, {prob_color.lstrip('#')[4:]}, 0.1);'>
        <h4 style='margin: 0; font-size: 1rem;'>Probabilidade Total</h4>
        <p style='font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; color: {prob_color};'>{total_implied_prob_pct}</p>
        <p style='margin: 0; opacity: 0.7; font-size: 0.9rem;'>Margem: {margin:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Adicionar barra de progresso para visualização da probabilidade total
st.markdown("<div style='margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
st.progress(min(total_implied_prob, 1.0))

# Adicionar uma explicação condicional
if total_implied_prob < 1:
    st.markdown(f"""
    <div style='margin: 0.5rem 0; padding: 0.5rem; border-radius: 5px; background: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50;'>
        <p style='margin: 0;'>✓ As probabilidades somam <strong>{total_implied_prob_pct}</strong>, que é <strong>menor que 100%</strong>, indicando uma oportunidade de arbitragem!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style='margin: 0.5rem 0; padding: 0.5rem; border-radius: 5px; background: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336;'>
        <p style='margin: 0;'>✗ As probabilidades somam <strong>{total_implied_prob_pct}</strong>, que é <strong>maior ou igual a 100%</strong>, não indicando arbitragem.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card

# Análise avançada da oportunidade
market_analysis = ArbitrageAnalyzer.calculate_market_efficiency(odd1, odd2)

# Exibir análise de qualidade
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 1rem;'>Análise de Qualidade da Oportunidade</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    quality_color = "#4CAF50" if market_analysis["quality"] in ["Excelente", "Muito Boa"] else "#FF9800" if market_analysis["quality"] == "Boa" else "#F44336"
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05);'>
        <h4 style='margin: 0; color: {quality_color};'>{market_analysis["quality"]}</h4>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Qualidade</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    risk_color = "#4CAF50" if market_analysis["risk_level"] == "Baixo" else "#FF9800" if market_analysis["risk_level"] == "Médio" else "#F44336"
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05);'>
        <h4 style='margin: 0; color: {risk_color};'>{market_analysis["risk_level"]}</h4>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Risco</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    efficiency_color = "#4CAF50" if market_analysis["efficiency_score"] > 80 else "#FF9800" if market_analysis["efficiency_score"] > 60 else "#F44336"
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05);'>
        <h4 style='margin: 0; color: {efficiency_color};'>{market_analysis["efficiency_score"]:.1f}/100</h4>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Eficiência</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Verificar se a arbitragem é possível
if total_implied_prob < 1:
    # Arbitragem é possível - usar análise avançada
    advanced_calc = BookmakerHelpers.calculate_optimal_stakes_with_limits(
        odd1, odd2, total_stake, bookmaker1, bookmaker2
    )
    
    stake1 = advanced_calc["stake1"]
    stake2 = advanced_calc["stake2"]
    profit = advanced_calc["guaranteed_profit"]
    profit_percent = advanced_calc["profit_percent"]
    
    # Análise de urgência
    time_analysis = ArbitrageAnalyzer.estimate_time_sensitivity(profit_percent)
    
    # Criar um card com estilo moderno para a distribuição de apostas
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='font-size: 1.8rem; margin-bottom: 1.5rem; color: #4CAF50;'>💰 Oportunidade de Arbitragem Detectada!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Card para a distribuição de apostas
    st.markdown("<div class='card highlight-pulse'>", unsafe_allow_html=True)
    
    # Título dentro do card
    st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 1rem;'>Distribuição Ótima de Apostas</h3>", unsafe_allow_html=True)
    
    # Layout em colunas para as apostas
    col1, col2 = st.columns(2)
    
    # Exibir as apostas com estilo moderno e botão de cópia
    with col1:
        stake1_str = f"€{stake1:.2f}"
        st.markdown(f"""
        <div style='text-align: center; padding: 1.5rem; border-radius: 10px; background: rgba(76, 175, 80, 0.1); border: 2px solid rgba(76, 175, 80, 0.2);'>
            <h4 style='margin: 0; font-size: 1.1rem; color: #4CAF50;'>Casa de Apostas 1</h4>
            <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: #4CAF50;'>{stake1_str}</p>
            <p style='margin: 0; font-size: 1rem;'>{stake1/total_stake*100:.1f}% do total</p>
            <div style='margin-top: 0.8rem; padding: 0.5rem; background: rgba(76, 175, 80, 0.05); border-radius: 5px;'>
                <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem;'>Apostar no Resultado 1 @ {odd1:.2f}</p>
                <button class="copy-btn" data-clipboard-text="{stake1:.2f}" style="background: #4CAF50; color: white; border: none; border-radius: 4px; padding: 5px 10px; cursor: pointer; font-size: 0.8rem;">
                    <span style="margin-right: 4px;">📋</span> Copiar valor
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        stake2_str = f"€{stake2:.2f}"
        st.markdown(f"""
        <div style='text-align: center; padding: 1.5rem; border-radius: 10px; background: rgba(76, 175, 80, 0.1); border: 2px solid rgba(76, 175, 80, 0.2);'>
            <h4 style='margin: 0; font-size: 1.1rem; color: #4CAF50;'>Casa de Apostas 2</h4>
            <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: #4CAF50;'>{stake2_str}</p>
            <p style='margin: 0; font-size: 1rem;'>{stake2/total_stake*100:.1f}% do total</p>
            <div style='margin-top: 0.8rem; padding: 0.5rem; background: rgba(76, 175, 80, 0.05); border-radius: 5px;'>
                <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem;'>Apostar no Resultado 2 @ {odd2:.2f}</p>
                <button class="copy-btn" data-clipboard-text="{stake2:.2f}" style="background: #4CAF50; color: white; border: none; border-radius: 4px; padding: 5px 10px; cursor: pointer; font-size: 0.8rem;">
                    <span style="margin-right: 4px;">📋</span> Copiar valor
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar alertas de limites se existirem
    if advanced_calc["warnings"]:
        st.markdown("<br>", unsafe_allow_html=True)
        for warning in advanced_calc["warnings"]:
            st.warning(f"⚠️ {warning}")
    
    # Mostrar urgência da oportunidade
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, {time_analysis["color"]}22, {time_analysis["color"]}11); border: 2px solid {time_analysis["color"]}66;'>
        <h4 style='margin: 0; color: {time_analysis["color"]}; font-size: 1.2rem;'>URGÊNCIA: {time_analysis["urgency"]}</h4>
        <p style='margin: 0.5rem 0 0 0; font-size: 1rem;'>Janela estimada: {time_analysis["estimated_window"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar o lucro garantido
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 1rem;'>Lucro Garantido</h3>", unsafe_allow_html=True)
    
    # Visualização mais atraente do lucro
    st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; border-radius: 10px; background: rgba(76, 175, 80, 0.15); border: 2px solid rgba(76, 175, 80, 0.3);'>
        <div style='display: flex; align-items: center; justify-content: center;'>
            <div style='font-size: 3rem; font-weight: 800; color: #4CAF50; margin-right: 1rem;'>€{profit:.2f}</div>
            <div style='font-size: 1.5rem; padding: 0.3rem 0.8rem; background: #4CAF50; color: white; border-radius: 20px;'>+{profit_percent:.2f}%</div>
        </div>
        <p style='margin-top: 1rem; font-size: 1rem;'>Independentemente do resultado, ganharás este valor!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botões de ação
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([3, 3, 6])
    
    # Verificar se estamos usando dados de uma oportunidade API
    event_name = None
    bookmaker1 = None
    bookmaker2 = None
    
    if st.session_state.selected_opportunity:
        opp = st.session_state.selected_opportunity
        event_name = f"{opp['home_team']} vs {opp['away_team']}"
        
        if len(opp['outcomes']) >= 2:
            bookmaker1 = opp['outcomes'][0]['bookmaker']
            bookmaker2 = opp['outcomes'][1]['bookmaker']
    
    # Botão para salvar a oportunidade
    with cols[0]:
        if st.button("💾 Salvar oportunidade", use_container_width=True):
            # Guardar no histórico da sessão para análise de segurança
            odds_entry = {
                "odd1": odd1,
                "odd2": odd2,
                "total_stake": total_stake,
                "profit_percent": profit_percent,
                "timestamp": time.time()
            }
            st.session_state.odds_history.append(odds_entry)
            
            saved_id = db.save_arbitrage_opportunity(
                odd1, odd2, total_stake, stake1, stake2, profit, profit_percent,
                event_name=event_name, bookmaker1=bookmaker1, bookmaker2=bookmaker2
            )
            if saved_id:
                # Actualizar totais da sessão
                st.session_state.total_profit_session += profit
                st.session_state.daily_total_bet += total_stake
                
                st.success(f"Oportunidade salva com sucesso! (ID: {saved_id})")
                st.balloons()  # Celebração visual
            else:
                st.error("Erro ao salvar. Verifica a ligação à base de dados.")
    
    # Botão para compartilhar
    with cols[1]:
        # Criar texto de compartilhamento com mais detalhes se disponíveis
        if event_name:
            share_base = f"Encontrei uma oportunidade de arbitragem para {event_name} "
            if bookmaker1 and bookmaker2:
                share_base += f"entre {bookmaker1} e {bookmaker2} "
            share_text = f"{share_base}com odds {odd1:.2f} e {odd2:.2f}, gerando um lucro garantido de {profit_percent:.2f}%!"
        else:
            share_text = f"Encontrei uma oportunidade de arbitragem com odds {odd1:.2f} e {odd2:.2f}, gerando um lucro garantido de {profit_percent:.2f}%!"
        
        # Usar um componente de botão HTML com funcionalidade de copiar
        betting_instructions = BookmakerHelpers.format_bet_instructions(
            stake1, stake2, odd1, odd2, bookmaker1, bookmaker2, event_name
        )
        
        # Botões de partilha avançados
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <button class="copy-btn" onclick="shareCalculation(`{betting_instructions}`)" 
                style="width: 100%; background: var(--accent-red); color: white; border: none; border-radius: 12px; 
                padding: 0.8rem; cursor: pointer; font-weight: 600; display: flex; align-items: center; 
                justify-content: center; text-transform: uppercase; letter-spacing: 0.5px;">
                <span style="margin-right: 8px;">📋</span> Copy
            </button>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <button onclick="generateQRCode(`{betting_instructions}`)" 
                style="width: 100%; background: #4CAF50; color: white; border: none; border-radius: 4px; 
                padding: 0.5rem; cursor: pointer; font-weight: 600; display: flex; align-items: center; 
                justify-content: center;">
                <span style="margin-right: 8px;">📱</span> QR Code
            </button>
            """, unsafe_allow_html=True)
        
        with col3:
            share_url = f"https://arbitragecalc.app?odd1={odd1}&odd2={odd2}&stake={total_stake}"
            st.markdown(f"""
            <button onclick="shareCalculation('Confere esta oportunidade de arbitragem: {share_url}')" 
                style="width: 100%; background: #FF5722; color: white; border: none; border-radius: 4px; 
                padding: 0.5rem; cursor: pointer; font-weight: 600; display: flex; align-items: center; 
                justify-content: center;">
                <span style="margin-right: 8px;">🔗</span> Partilhar
            </button>
            """, unsafe_allow_html=True)
        
        # Mostrar prévia das instruções em um elemento colapsável
        with st.expander("Instruções detalhadas de apostas"):
            st.code(betting_instructions, language="text")
    
    # Mostrar dicas específicas para as casas de apostas
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 1rem;'>💡 Dicas Específicas</h3>", unsafe_allow_html=True)
    
    betting_tips = BookmakerHelpers.get_betting_tips(bookmaker1, bookmaker2)
    tips_html = ""
    for tip in betting_tips[:6]:  # Mostrar apenas 6 dicas mais relevantes
        tips_html += f"<p style='margin: 0.5rem 0; padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'>{tip}</p>"
    
    st.markdown(f"""
    <div style='padding: 1rem; border-radius: 10px; background: rgba(51, 102, 255, 0.1);'>
        {tips_html}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card
    
    # Seção de verificação com visual moderno
    with st.expander("Verificação Detalhada dos Resultados"):
        st.markdown("<div style='padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
        
        # Cenário 1
        st.markdown(f"""
        <h4 style='color: #FF5722; margin-bottom: 0.5rem;'>Cenário 1: Se o Resultado 1 vencer</h4>
        <table style='width: 100%; border-collapse: collapse;'>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.5rem;'>Ganho da Aposta 1:</td>
                <td style='padding: 0.5rem; text-align: right;'><strong>€{stake1:.2f} × {odd1:.2f} = €{stake1 * odd1:.2f}</strong></td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.5rem;'>Perda da Aposta 2:</td>
                <td style='padding: 0.5rem; text-align: right; color: #F44336;'>-€{stake2:.2f}</td>
            </tr>
            <tr>
                <td style='padding: 0.5rem;'><strong>Lucro Líquido:</strong></td>
                <td style='padding: 0.5rem; text-align: right; color: #4CAF50;'><strong>€{stake1 * odd1 - total_stake:.2f}</strong></td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Cenário 2
        st.markdown(f"""
        <h4 style='color: #FF5722; margin-bottom: 0.5rem;'>Cenário 2: Se o Resultado 2 vencer</h4>
        <table style='width: 100%; border-collapse: collapse;'>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.5rem;'>Ganho da Aposta 2:</td>
                <td style='padding: 0.5rem; text-align: right;'><strong>€{stake2:.2f} × {odd2:.2f} = €{stake2 * odd2:.2f}</strong></td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.5rem;'>Perda da Aposta 1:</td>
                <td style='padding: 0.5rem; text-align: right; color: #F44336;'>-€{stake1:.2f}</td>
            </tr>
            <tr>
                <td style='padding: 0.5rem;'><strong>Lucro Líquido:</strong></td>
                <td style='padding: 0.5rem; text-align: right; color: #4CAF50;'><strong>€{stake2 * odd2 - total_stake:.2f}</strong></td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
else:
    # Sem possibilidade de arbitragem
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='font-size: 1.8rem; margin-bottom: 1.5rem; color: #F44336;'>❌ Sem oportunidade de arbitragem</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Card para o diagnóstico
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Diagnóstico
    st.markdown(f"""
    <div style='padding: 1rem; border-radius: 8px; background: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; margin-bottom: 1rem;'>
        <h4 style='margin: 0 0 0.5rem 0; color: #F44336;'>Diagnóstico</h4>
        <p style='margin: 0;'>A soma das probabilidades implícitas é <strong>{total_implied_prob*100:.2f}%</strong>, o que é <strong>maior que 100%</strong>.</p>
        <p style='margin: 0.5rem 0 0 0;'>Não há oportunidade de arbitragem com estas odds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Fechar o card

with tab3:
    # Dashboard de Analytics
    if st.session_state.get('authenticated', False):
        show_analytics_dashboard(st.session_state.user_data)
    else:
        st.markdown("""
        ## 📊 Dashboard de Analytics
        
        O dashboard de analytics oferece:
        - 📈 Gráficos de performance detalhados
        - 🕒 Análise de padrões temporais
        - 🏢 Comparação entre casas de apostas
        - 🎯 Insights automáticos personalizados
        - 📊 Métricas de ROI e lucro
        
        **Faça login para aceder ao dashboard completo!**
        """)
        
        if st.button("Fazer Login / Registar", type="primary", key="analytics_login"):
            st.session_state.show_auth = True
            st.rerun()

with tab4:
    # Gestão de conta e configurações
    if st.session_state.get('authenticated', False):
        user_data = st.session_state.user_data
        
        st.markdown("## ⚙️ Gestão de Conta")
        
        # Informações da conta
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Perfil")
            st.write(f"**Utilizador:** {user_data['username']}")
            st.write(f"**Email:** {user_data['email']}")
            st.write(f"**Plano:** {'Premium' if user_data['is_premium'] else 'Gratuito'}")
            st.write(f"**Lucro Total:** €{user_data['total_profit']:.2f}")
        
        with col2:
            st.markdown("### 📊 Estatísticas")
            usage_status = SubscriptionManager.check_usage_limits(user_data)
            st.write(f"**Plano Actual:** {usage_status['plan_name']}")
            if usage_status['remaining'] != -1:
                st.write(f"**Cálculos Restantes:** {usage_status['remaining']}")
            else:
                st.write("**Cálculos:** Ilimitados")
        
        # Exportar dados
        st.markdown("### 📥 Exportar Dados")
        if st.button("Exportar Histórico (CSV)", key="export_csv"):
            csv_data = export_data_to_csv(user_data)
            st.download_button(
                "Descarregar CSV",
                csv_data,
                file_name=f"arbitragem_historico_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Upgrade de plano
        if not user_data['is_premium']:
            st.markdown("### 💎 Upgrade Premium")
            st.info("Desbloqueie funcionalidades avançadas com o plano Premium!")
            if st.button("Ver Planos", key="view_plans"):
                show_pricing_page()
        
        # Logout
        st.markdown("### 🚪 Sair")
        if st.button("Terminar Sessão", key="logout"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
            
    else:
        st.markdown("## 🔐 Acesso Necessário")
        st.info("Faça login para gerir a sua conta e aceder a funcionalidades avançadas.")
        
        if st.button("Fazer Login / Registar", type="primary", key="account_login"):
            st.session_state.show_auth = True
            st.rerun()

# Secção de painel avançado na sidebar
st.sidebar.markdown("<h2 style='font-size: 1.5rem; color: #FF5722; margin-bottom: 1rem;'>📊 Painel de Controlo</h2>", unsafe_allow_html=True)

# Meta de lucro e progresso
with st.sidebar.expander("🎯 Definir Meta de Lucro", expanded=True):
    profit_target = st.number_input(
        "Meta diária (€)", 
        min_value=1.0, 
        max_value=10000.0, 
        value=st.session_state.profit_target,
        step=10.0,
        key="profit_target_input"
    )
    st.session_state.profit_target = profit_target
    
    # Calcular progresso atual (baseado no histórico)
    try:
        today_history = db.get_arbitrage_history(50)  # Pegar mais registos para filtrar por hoje
        today_profit = sum([item['profit'] for item in today_history if 
                           pd.to_datetime(item['date_created']).date() == pd.Timestamp.now().date()])
        
        progress_data = UserExperience.create_progress_indicator(today_profit, profit_target)
        
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05);'>
            <p style='margin: 0; font-size: 0.8rem; opacity: 0.7;'>Progresso Hoje</p>
            <p style='font-size: 1.3rem; font-weight: 700; margin: 0.2rem 0; color: {progress_data["color"]};'>€{today_profit:.2f}</p>
            <p style='margin: 0; font-size: 0.8rem;'>{progress_data["message"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progresso
        st.progress(progress_data["progress"] / 100)
        if progress_data["remaining"] > 0:
            st.caption(f"Faltam €{progress_data['remaining']:.2f} para a meta")
            
    except Exception as e:
        st.caption("Erro ao calcular progresso")

# Sugestões de horários
with st.sidebar.expander("⏰ Melhores Horários"):
    time_suggestions = UserExperience.suggest_optimal_betting_times()
    for suggestion in time_suggestions:
        st.markdown(f"• {suggestion}")

# Alertas de segurança
if len(st.session_state.odds_history) > 0:
    security_alerts = AdvancedSecurity.detect_suspicious_patterns(st.session_state.odds_history)
    if security_alerts:
        with st.sidebar.expander("🚨 Alertas de Segurança", expanded=True):
            for alert in security_alerts:
                st.warning(alert)

# Adicionar estatísticas e histórico de oportunidades na sidebar
st.sidebar.markdown("<h2 style='font-size: 1.5rem; color: #FF5722; margin-bottom: 1rem;'>🗂️ Histórico de Oportunidades</h2>", unsafe_allow_html=True)

# Função para renderizar um item do histórico
def render_history_item(item):
    date = pd.to_datetime(item['date_created']).strftime('%d/%m/%Y %H:%M')
    profit = item['profit']
    profit_percent = item['profit_percent']
    odd1 = item['odd1']
    odd2 = item['odd2']
    item_id = item['id']
    
    # Adicionar informações do evento e casas de apostas se disponíveis
    event_info = ""
    if item.get('event_name'):
        event_info = f"""
        <div style='margin-bottom: 0.3rem; font-size: 0.9rem;'>
            <span style='color: #3366ff;'>{item['event_name']}</span>
        </div>
        """
    
    bookmaker_info = ""
    if item.get('bookmaker1') and item.get('bookmaker2'):
        bookmaker_info = f"""
        <div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem; font-size: 0.8rem;'>
            <span style='opacity: 0.8;'>{item['bookmaker1']} vs {item['bookmaker2']}</span>
        </div>
        """
    
    # Informações de cópia
    copy_text = f'Odds: {odd1:.2f}/{odd2:.2f}, Lucro: {profit_percent:.2f}%'
    if item.get('event_name'):
        copy_text = f'Evento: {item["event_name"]}, ' + copy_text
    
    return f"""
    <div style='padding: 0.8rem; margin-bottom: 0.8rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05); 
          border: 1px solid rgba(255, 255, 255, 0.1); border-left: 3px solid #3366ff;'>
        {event_info}
        <div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'>
            <span style='font-size: 0.8rem; opacity: 0.7;'>{date}</span>
            <span style='font-size: 0.8rem; font-weight: 600; color: #4CAF50;'>+{profit_percent:.2f}%</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'>
            <span style='font-weight: 600;'>€{profit:.2f}</span>
            <span style='opacity: 0.8;'>Odds: {odd1:.2f} / {odd2:.2f}</span>
        </div>
        {bookmaker_info}
        <div style='display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem;'>
            <button class='copy-btn' data-clipboard-text='{copy_text}'
                style='background: none; border: none; padding: 0; color: #3366ff; cursor: pointer; font-size: 0.75rem;'>
                📋 Copiar Detalhes
            </button>
            <div class='delete-btn-{item_id}'></div>
        </div>
    </div>
    """

# Carregar histórico de arbitragem
try:
    history = db.get_arbitrage_history(10)
    
    if history and len(history) > 0:
        # Converter para DataFrame do pandas
        df = pd.DataFrame(history)
        
        # Calcular algumas estatísticas
        total_profit = df['profit'].sum()
        avg_profit_percent = df['profit_percent'].mean()
        max_profit = df['profit'].max()
        
        # Exibir estatísticas em formato de cards
        st.sidebar.markdown("<div style='margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 0.8rem; border-radius: 10px; background: rgba(76, 175, 80, 0.1);'>
                <p style='margin: 0; font-size: 0.8rem; opacity: 0.7;'>Lucro Total</p>
                <p style='font-size: 1.3rem; font-weight: 700; margin: 0.2rem 0; color: #4CAF50;'>€{total_profit:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 0.8rem; border-radius: 10px; background: rgba(76, 175, 80, 0.1);'>
                <p style='margin: 0; font-size: 0.8rem; opacity: 0.7;'>Média de Lucro</p>
                <p style='font-size: 1.3rem; font-weight: 700; margin: 0.2rem 0; color: #4CAF50;'>{avg_profit_percent:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        # Título da lista
        st.sidebar.markdown("<h3 style='font-size: 1.1rem; margin: 1.2rem 0 0.8rem 0;'>Últimas Oportunidades</h3>", unsafe_allow_html=True)
        
        # Renderizar cada item do histórico com visual moderno
        history_html = ""
        for item in history:
            history_html += render_history_item(item)
        
        st.sidebar.markdown(history_html, unsafe_allow_html=True)
        
        # Botão para limpar histórico com estilo melhorado
        if st.sidebar.button("🗑️ Limpar Histórico", type="secondary", use_container_width=True):
            for entry in history:
                db.delete_arbitrage_opportunity(entry['id'])
            st.sidebar.success("✅ Histórico limpo com sucesso!")
            st.rerun()
    else:
        st.sidebar.markdown("""
        <div style='padding: 1rem; border-radius: 10px; background: rgba(255, 255, 255, 0.05); text-align: center;'>
            <p style='margin: 0; opacity: 0.7;'>Nenhuma oportunidade salva ainda</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Use o botão "Salvar oportunidade" quando encontrar arbitragem</p>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.sidebar.markdown(f"""
    <div style='padding: 1rem; border-radius: 10px; background: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336;'>
        <p style='margin: 0; font-size: 0.9rem;'>Erro ao carregar histórico: {e}</p>
    </div>
    """, unsafe_allow_html=True)

# Adicionar informações de ajuda em formato moderno
st.sidebar.markdown("<h2 style='font-size: 1.5rem; color: #FF5722; margin: 2rem 0 1rem 0;'>ℹ️ Guia de Arbitragem</h2>", unsafe_allow_html=True)

# Expandir/recolher as seções do guia
with st.sidebar.expander("O que é arbitragem de apostas?"):
    st.markdown("""
    <div style='padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 5px;'>
        <p>A arbitragem de apostas (ou "arbing") é uma estratégia que envolve apostar em todos os possíveis resultados de um evento, utilizando odds que garantam lucro independentemente do resultado final.</p>
        <p>É uma técnica de <strong>lucro garantido</strong> quando a matemática está a seu favor.</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar.expander("Como identificar oportunidades"):
    st.markdown("""
    <div style='padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 5px;'>
        <p>Uma oportunidade de arbitragem existe quando:</p>
        <ul>
            <li>As probabilidades implícitas de todos os resultados somam <strong>menos de 100%</strong></li>
            <li>Você consegue apostar em todos os possíveis resultados</li>
            <li>As odds não mudam antes que você consiga fazer todas as apostas</li>
        </ul>
        <p>Probabilidade implícita = 1 / Odd Decimal</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar.expander("Fórmulas utilizadas"):
    st.markdown("""
    <div style='padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 5px;'>
        <div style='margin-bottom: 0.7rem;'>
            <strong style='color: #FF5722;'>Verificando a oportunidade:</strong><br>
            Soma das probabilidades implícitas < 1
        </div>
        <div style='margin-bottom: 0.7rem;'>
            <strong style='color: #FF5722;'>Apostas ótimas:</strong><br>
            Aposta para resultado X = (Aposta total × Probabilidade X) / Soma das probabilidades
        </div>
        <div>
            <strong style='color: #FF5722;'>Lucro garantido:</strong><br>
            Lucro = (Aposta total / Soma das probabilidades) - Aposta total
        </div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar.expander("Exemplo prático"):
    st.markdown("""
    <div style='padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 5px;'>
        <p><strong>Cenário:</strong> Odds de 2.10 e 2.05</p>
        
        <p><strong>Verificação:</strong></p>
        <ul>
            <li>Probabilidade 1: 1/2.10 = 0.476 (47.6%)</li>
            <li>Probabilidade 2: 1/2.05 = 0.488 (48.8%)</li>
            <li>Soma = 0.964 (96.4%) < 100%</li>
        </ul>
        
        <p><strong>Distribuição para €100:</strong></p>
        <ul>
            <li>Aposta 1 = €100 × 0.476 / 0.964 = <strong>€49.38</strong></li>
            <li>Aposta 2 = €100 × 0.488 / 0.964 = <strong>€50.62</strong></li>
        </ul>
        
        <p><strong>Lucro:</strong> €3.73 (3.73%)</p>
    </div>
    """, unsafe_allow_html=True)

# Dica estratégica
st.sidebar.markdown("""
<div style='margin-top: 1rem; padding: 0.8rem; border-radius: 10px; background: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3;'>
    <h4 style='margin: 0 0 0.5rem 0; color: #2196F3; font-size: 1rem;'>💡 Dica Estratégica</h4>
    <p style='margin: 0; font-size: 0.9rem;'>Para maximizar seus lucros, procure eventos com alta liquidez e muitas casas de apostas concorrentes. Oportunidades de arbitragem aparecem frequentemente em mercados populares com opiniões divergentes entre bookmakers.</p>
</div>
""", unsafe_allow_html=True)

# Adicionar rodapé
st.sidebar.markdown("""
<div style='margin-top: 2rem; opacity: 0.7; text-align: center; font-size: 0.8rem;'>
    <p>Versão 2.0 - Desenvolvido com ❤️</p>
    <p>Aplicação para fins educacionais.</p>
</div>
""", unsafe_allow_html=True)

# Adicionar um rodapé personalizado com menção ao AFZF
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<footer style="margin-top: 3rem; padding: 1.2rem; background: rgba(0, 0, 0, 0.2); border-radius: 6px; text-align: center;">
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.8rem;">
        <span style="font-size: 1.2rem; margin: 0 0.8rem;">🎲</span>
        <span style="font-size: 1.2rem; margin: 0 0.8rem;">📊</span>
        <span style="font-size: 1.2rem; margin: 0 0.8rem;">💰</span>
        <span style="font-size: 1.2rem; margin: 0 0.8rem;">🎯</span>
    </div>
    <p style="margin: 0.5rem 0; font-size: 1rem;">Calculadora de Arbitragem v2.0</p>
    <p style="margin: 0.5rem 0; opacity: 0.7; font-size: 0.9rem;">Esta calculadora é apenas para fins educacionais. Aposte com responsabilidade.</p>
    <p style="margin: 0.5rem 0; opacity: 0.6; font-size: 0.8rem;">Configurado por <strong>AFZF</strong></p>
</footer>
""", unsafe_allow_html=True)
