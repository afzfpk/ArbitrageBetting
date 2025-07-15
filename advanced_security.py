"""
Medidas de segurança avançadas para aplicação de apostas
"""
import hashlib
import hmac
import time
import random
import string
from typing import Dict, List, Optional
import streamlit as st

class AdvancedSecurity:
    """Funcionalidades de segurança avançadas."""
    
    @staticmethod
    def generate_session_token() -> str:
        """Gera um token de sessão seguro."""
        timestamp = str(int(time.time()))
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return hashlib.sha256(f"{timestamp}{random_str}".encode()).hexdigest()[:32]
    
    @staticmethod
    def validate_bet_amount(amount: float, max_daily_limit: float = 10000.0) -> Dict:
        """
        Valida montantes de aposta com limites de segurança.
        
        Args:
            amount: Montante da aposta
            max_daily_limit: Limite diário máximo
            
        Returns:
            Resultado da validação
        """
        # Verificar limites básicos
        if amount < 0.01:
            return {"valid": False, "reason": "Montante mínimo é €0.01"}
        
        if amount > max_daily_limit:
            return {"valid": False, "reason": f"Montante excede limite diário (€{max_daily_limit:.2f})"}
        
        # Verificar padrões suspeitos
        if amount > 1000 and amount % 1 == 0:  # Valores redondos altos
            return {
                "valid": True, 
                "warning": "Montante alto e redondo - confirma se é intencional",
                "requires_confirmation": True
            }
        
        return {"valid": True}
    
    @staticmethod
    def detect_suspicious_patterns(odds_history: List[Dict]) -> List[str]:
        """
        Detecta padrões suspeitos nas odds para prevenir manipulação.
        
        Args:
            odds_history: Histórico de odds inseridas
            
        Returns:
            Lista de alertas de segurança
        """
        alerts = []
        
        if len(odds_history) < 2:
            return alerts
        
        # Verificar odds muito baixas (possível erro ou manipulação)
        for entry in odds_history[-5:]:  # Últimas 5 entradas
            if entry.get('odd1', 0) < 1.01 or entry.get('odd2', 0) < 1.01:
                alerts.append("⚠️ Odds muito baixas detectadas - verifica se estão corretas")
        
        # Verificar padrões repetitivos
        recent_odds = [(entry.get('odd1', 0), entry.get('odd2', 0)) for entry in odds_history[-3:]]
        if len(set(recent_odds)) == 1 and len(recent_odds) > 1:
            alerts.append("⚠️ Odds idênticas repetidas - pode ser erro de entrada")
        
        # Verificar lucros irrealisticamente altos
        for entry in odds_history[-3:]:
            if entry.get('profit_percent', 0) > 10:
                alerts.append("⚠️ Lucro muito alto (>10%) - confirma as odds com as casas de apostas")
        
        return alerts
    
    @staticmethod
    def create_secure_backup(data: Dict) -> str:
        """
        Cria backup seguro dos dados com hash de integridade.
        
        Args:
            data: Dados para backup
            
        Returns:
            Hash de integridade dos dados
        """
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def mask_sensitive_data(text: str) -> str:
        """
        Mascara dados sensíveis em logs.
        
        Args:
            text: Texto para mascarar
            
        Returns:
            Texto com dados sensíveis mascarados
        """
        # Mascarar possíveis emails
        import re
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '***@***.***', text)
        
        # Mascarar possíveis IBANs
        text = re.sub(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b',
                     'PT***************', text)
        
        return text

class PerformanceOptimizer:
    """Otimizações de performance para cálculos de arbitragem."""
    
    @staticmethod
    def cache_calculation(odd1: float, odd2: float, stake: float) -> str:
        """
        Cria chave de cache para cálculos.
        
        Args:
            odd1, odd2: Odds
            stake: Montante
            
        Returns:
            Chave de cache
        """
        return f"{odd1:.3f}_{odd2:.3f}_{stake:.2f}"
    
    @staticmethod
    def batch_calculate_opportunities(odds_list: List[tuple]) -> List[Dict]:
        """
        Calcula múltiplas oportunidades em lote para melhor performance.
        
        Args:
            odds_list: Lista de tuplas (odd1, odd2)
            
        Returns:
            Lista de resultados calculados
        """
        results = []
        
        for odd1, odd2 in odds_list:
            implied_prob1 = 1 / odd1
            implied_prob2 = 1 / odd2
            total_implied = implied_prob1 + implied_prob2
            
            is_arbitrage = total_implied < 1
            profit_percent = ((1 / total_implied) - 1) * 100 if is_arbitrage else 0
            
            results.append({
                "odd1": odd1,
                "odd2": odd2,
                "is_arbitrage": is_arbitrage,
                "profit_percent": profit_percent,
                "total_implied_prob": total_implied * 100
            })
        
        return results

class UserExperience:
    """Melhorias de experiência do usuário."""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "EUR") -> str:
        """
        Formata valores monetários.
        
        Args:
            amount: Valor
            currency: Moeda
            
        Returns:
            Valor formatado
        """
        if currency == "EUR":
            return f"€{amount:.2f}"
        return f"{amount:.2f} {currency}"
    
    @staticmethod
    def create_progress_indicator(current_profit: float, target_profit: float) -> Dict:
        """
        Cria indicador de progresso para metas de lucro.
        
        Args:
            current_profit: Lucro atual
            target_profit: Meta de lucro
            
        Returns:
            Dados do indicador
        """
        if target_profit <= 0:
            return {"progress": 0, "message": "Define uma meta de lucro"}
        
        progress = min(100, (current_profit / target_profit) * 100)
        
        if progress >= 100:
            message = "🎉 Meta alcançada! Parabéns!"
            color = "#4CAF50"
        elif progress >= 75:
            message = "🔥 Quase lá! Continua assim!"
            color = "#FF9800"
        elif progress >= 50:
            message = "💪 Meio caminho andado!"
            color = "#2196F3"
        elif progress >= 25:
            message = "📈 Bom progresso!"
            color = "#9C27B0"
        else:
            message = "🚀 Vamos começar!"
            color = "#607D8B"
        
        return {
            "progress": progress,
            "message": message,
            "color": color,
            "remaining": max(0, target_profit - current_profit)
        }
    
    @staticmethod
    def suggest_optimal_betting_times() -> List[str]:
        """
        Sugere os melhores horários para apostar baseado em padrões do mercado.
        
        Returns:
            Lista de sugestões
        """
        current_hour = time.localtime().tm_hour
        
        suggestions = []
        
        if 14 <= current_hour <= 18:
            suggestions.append("🕒 Horário nobre - mais eventos disponíveis")
        elif 20 <= current_hour <= 23:
            suggestions.append("🌙 Boa altura para eventos europeus")
        elif 2 <= current_hour <= 6:
            suggestions.append("🌍 Horário ideal para eventos americanos/asiáticos")
        else:
            suggestions.append("⏰ Verifica se há eventos ao vivo")
        
        # Sugestões por dia da semana
        weekday = time.localtime().tm_wday
        if weekday in [5, 6]:  # Fim de semana
            suggestions.append("⚽ Fins de semana têm mais eventos de futebol")
        elif weekday in [1, 2, 3]:  # Meio da semana
            suggestions.append("🎾 Meio da semana é bom para ténis e basquete")
        
        return suggestions

# Inicializar sessão de estado para funcionalidades avançadas
def init_advanced_features():
    """Inicializa funcionalidades avançadas na sessão."""
    if 'session_token' not in st.session_state:
        st.session_state.session_token = AdvancedSecurity.generate_session_token()
    
    if 'odds_history' not in st.session_state:
        st.session_state.odds_history = []
    
    if 'daily_total_bet' not in st.session_state:
        st.session_state.daily_total_bet = 0.0
    
    if 'profit_target' not in st.session_state:
        st.session_state.profit_target = 100.0  # Meta padrão de €100
    
    if 'total_profit_session' not in st.session_state:
        st.session_state.total_profit_session = 0.0