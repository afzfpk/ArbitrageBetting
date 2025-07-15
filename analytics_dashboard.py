"""
Dashboard de analytics profissional para arbitragem
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import database as db
from typing import Dict, List, Optional

class AnalyticsDashboard:
    """Dashboard de análise de performance de arbitragem."""
    
    @staticmethod
    def get_user_stats(user_id: int, days: int = 30) -> Dict:
        """
        Obtém estatísticas do utilizador.
        
        Args:
            user_id: ID do utilizador
            days: Número de dias para análise
            
        Returns:
            Dicionário com estatísticas
        """
        conn = db.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor()
            
            # Estatísticas básicas
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_opportunities,
                    SUM(profit) as total_profit,
                    AVG(profit_percent) as avg_profit_percent,
                    MAX(profit) as max_profit,
                    MIN(profit) as min_profit,
                    SUM(total_stake) as total_wagered
                FROM arbitrage_opportunities 
                WHERE date_created >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            stats = cursor.fetchone()
            
            # Lucro por dia
            cursor.execute("""
                SELECT 
                    DATE(date_created) as date,
                    SUM(profit) as daily_profit,
                    COUNT(*) as daily_count
                FROM arbitrage_opportunities 
                WHERE date_created >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(date_created)
                ORDER BY date
            """, (days,))
            
            daily_data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "total_opportunities": stats[0] or 0,
                "total_profit": float(stats[1] or 0),
                "avg_profit_percent": float(stats[2] or 0),
                "max_profit": float(stats[3] or 0),
                "min_profit": float(stats[4] or 0),
                "total_wagered": float(stats[5] or 0),
                "daily_data": daily_data
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {}
    
    @staticmethod
    def create_profit_chart(daily_data: List) -> go.Figure:
        """
        Cria gráfico de lucro diário.
        
        Args:
            daily_data: Dados diários
            
        Returns:
            Figura Plotly
        """
        if not daily_data:
            return go.Figure()
        
        dates = [row[0] for row in daily_data]
        profits = [float(row[1]) for row in daily_data]
        cumulative_profit = [sum(profits[:i+1]) for i in range(len(profits))]
        
        fig = go.Figure()
        
        # Lucro diário
        fig.add_trace(go.Bar(
            x=dates,
            y=profits,
            name="Lucro Diário",
            marker_color='rgba(51, 102, 255, 0.7)',
            yaxis="y"
        ))
        
        # Lucro acumulado
        fig.add_trace(go.Scatter(
            x=dates,
            y=cumulative_profit,
            mode='lines+markers',
            name="Lucro Acumulado",
            line=dict(color='#4CAF50', width=3),
            yaxis="y2"
        ))
        
        fig.update_layout(
            title="Performance de Lucros",
            xaxis_title="Data",
            yaxis=dict(title="Lucro Diário (€)", side="left"),
            yaxis2=dict(title="Lucro Acumulado (€)", side="right", overlaying="y"),
            hovermode='x unified',
            template="plotly_dark",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_opportunities_heatmap(daily_data: List) -> go.Figure:
        """
        Cria heatmap de oportunidades por dia da semana e hora.
        
        Args:
            daily_data: Dados de oportunidades
            
        Returns:
            Figura Plotly
        """
        # Simular dados de heatmap (em produção viria da base de dados)
        import numpy as np
        
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        hours = list(range(24))
        
        # Gerar dados simulados baseados em padrões reais
        np.random.seed(42)
        data = np.random.poisson(2, (7, 24))
        
        # Adicionar padrões realistas
        for day in range(7):
            for hour in range(24):
                if day < 5:  # Dias úteis
                    if 9 <= hour <= 17:  # Horário comercial
                        data[day][hour] += 3
                    elif 19 <= hour <= 22:  # Noite
                        data[day][hour] += 2
                else:  # Fim de semana
                    if 14 <= hour <= 18:  # Tarde
                        data[day][hour] += 4
                    elif 20 <= hour <= 23:  # Noite
                        data[day][hour] += 3
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=[f"{h:02d}:00" for h in hours],
            y=days,
            colorscale='Viridis',
            hoverongaps=False,
            colorbar=dict(title="Oportunidades")
        ))
        
        fig.update_layout(
            title="Mapa de Calor: Oportunidades por Hora/Dia",
            xaxis_title="Hora do Dia",
            yaxis_title="Dia da Semana",
            template="plotly_dark",
            height=300
        )
        
        return fig
    
    @staticmethod
    def create_bookmaker_analysis() -> go.Figure:
        """
        Cria análise de performance por casa de apostas.
        
        Returns:
            Figura Plotly
        """
        # Dados simulados para demonstração
        bookmakers = ['Betano.pt', '888Starz', 'Placard.pt', 'Betclic.pt']
        opportunities = [45, 38, 22, 15]
        avg_profit = [2.3, 2.8, 1.9, 2.1]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=bookmakers,
            y=opportunities,
            name="Oportunidades",
            marker_color='rgba(51, 102, 255, 0.7)',
            yaxis="y"
        ))
        
        fig.add_trace(go.Scatter(
            x=bookmakers,
            y=avg_profit,
            mode='lines+markers',
            name="Lucro Médio (%)",
            line=dict(color='#FF5722', width=3),
            marker=dict(size=10),
            yaxis="y2"
        ))
        
        fig.update_layout(
            title="Performance por Casa de Apostas",
            xaxis_title="Casa de Apostas",
            yaxis=dict(title="Número de Oportunidades", side="left"),
            yaxis2=dict(title="Lucro Médio (%)", side="right", overlaying="y"),
            template="plotly_dark",
            height=400
        )
        
        return fig

def show_analytics_dashboard(user_data: Dict):
    """
    Mostra dashboard de analytics completo.
    
    Args:
        user_data: Dados do utilizador
    """
    st.markdown("## 📊 Dashboard de Performance")
    
    # Filtros de tempo
    col1, col2 = st.columns([3, 1])
    with col1:
        time_period = st.selectbox(
            "Período de análise",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Último ano"],
            index=1
        )
    
    # Mapear período
    days_map = {
        "Últimos 7 dias": 7,
        "Últimos 30 dias": 30,
        "Últimos 90 dias": 90,
        "Último ano": 365
    }
    days = days_map[time_period]
    
    # Obter estatísticas
    stats = AnalyticsDashboard.get_user_stats(user_data["id"], days)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Lucro Total",
            f"€{stats.get('total_profit', 0):.2f}",
            delta=f"+{stats.get('total_profit', 0)/days:.2f}/dia"
        )
    
    with col2:
        st.metric(
            "Oportunidades",
            stats.get('total_opportunities', 0),
            delta=f"+{stats.get('total_opportunities', 0)/days:.1f}/dia"
        )
    
    with col3:
        st.metric(
            "Lucro Médio",
            f"{stats.get('avg_profit_percent', 0):.2f}%",
            delta=None
        )
    
    with col4:
        roi = (stats.get('total_profit', 0) / stats.get('total_wagered', 1)) * 100 if stats.get('total_wagered', 0) > 0 else 0
        st.metric(
            "ROI Total",
            f"{roi:.2f}%",
            delta=f"€{stats.get('total_wagered', 0):.0f} apostado"
        )
    
    # Gráficos
    st.markdown("### 📈 Análise Temporal")
    
    if stats.get('daily_data'):
        profit_chart = AnalyticsDashboard.create_profit_chart(stats['daily_data'])
        st.plotly_chart(profit_chart, use_container_width=True)
    else:
        st.info("Sem dados suficientes para gráfico temporal. Faça alguns cálculos primeiro!")
    
    # Dois gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🕒 Mapa de Oportunidades")
        heatmap = AnalyticsDashboard.create_opportunities_heatmap(stats.get('daily_data', []))
        st.plotly_chart(heatmap, use_container_width=True)
    
    with col2:
        st.markdown("### 🏢 Performance por Casa")
        bookmaker_chart = AnalyticsDashboard.create_bookmaker_analysis()
        st.plotly_chart(bookmaker_chart, use_container_width=True)
    
    # Insights automáticos
    st.markdown("### 🎯 Insights Inteligentes")
    
    insights = []
    
    if stats.get('avg_profit_percent', 0) > 2:
        insights.append("🟢 Excelente performance! Lucro médio acima de 2%")
    elif stats.get('avg_profit_percent', 0) > 1:
        insights.append("🟡 Boa performance. Considere procurar oportunidades com maior margem")
    else:
        insights.append("🔴 Performance baixa. Reveja a estratégia de seleção de odds")
    
    if stats.get('total_opportunities', 0) < days * 0.5:
        insights.append("📊 Poucas oportunidades identificadas. Considere usar a funcionalidade de API")
    
    if len(insights) > 0:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Execute alguns cálculos para obter insights personalizados")

def export_data_to_csv(user_data: Dict) -> str:
    """
    Exporta dados do utilizador para CSV.
    
    Args:
        user_data: Dados do utilizador
        
    Returns:
        Dados CSV como string
    """
    try:
        history = db.get_arbitrage_history(1000)  # Últimas 1000 entradas
        df = pd.DataFrame(history)
        return df.to_csv(index=False)
    except Exception:
        return "Erro ao exportar dados"