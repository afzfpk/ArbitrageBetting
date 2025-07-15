"""
Helpers específicos para casas de apostas populares em Portugal
"""
import re
from typing import Dict, List, Tuple, Optional
from security_utils import SecurityUtils

class BookmakerHelpers:
    """Utilitários específicos para casas de apostas populares."""
    
    # Dados das principais casas de apostas portuguesas
    BOOKMAKERS = {
        "betano": {
            "name": "Betano.pt",
            "url": "https://betano.pt",
            "commission_rate": 0.05,  # 5% de margem típica
            "min_bet": 0.10,
            "max_bet": 10000.0,
            "specialty": ["futebol", "tenis", "basquete"],
            "features": ["cash_out", "live_betting", "quick_bet"]
        },
        "888starz": {
            "name": "888Starz",
            "url": "https://888starz.bet",
            "commission_rate": 0.04,  # 4% de margem típica
            "min_bet": 0.20,
            "max_bet": 50000.0,
            "specialty": ["futebol", "tenis", "esports"],
            "features": ["high_limits", "crypto_betting", "live_streaming"]
        },
        "placard": {
            "name": "Placard.pt",
            "url": "https://placard.pt",
            "commission_rate": 0.06,
            "min_bet": 0.05,
            "max_bet": 5000.0,
            "specialty": ["futebol_portugues", "multiplas"],
            "features": ["local_expertise", "promotions"]
        },
        "betclic": {
            "name": "Betclic.pt",
            "url": "https://betclic.pt",
            "commission_rate": 0.055,
            "min_bet": 0.10,
            "max_bet": 15000.0,
            "specialty": ["futebol", "tenis", "formula1"],
            "features": ["super_odds", "combo_boost"]
        }
    }
    
    @staticmethod
    def get_bookmaker_info(bookmaker_name: str) -> Optional[Dict]:
        """
        Obtém informações sobre uma casa de apostas.
        
        Args:
            bookmaker_name: Nome da casa de apostas
            
        Returns:
            Dicionário com informações da casa de apostas ou None
        """
        bookmaker_key = bookmaker_name.lower().replace(" ", "").replace(".", "")
        
        # Mapeamentos comuns
        mappings = {
            "betano": "betano",
            "betanopt": "betano",
            "888starz": "888starz",
            "888": "888starz",
            "placard": "placard",
            "placardpt": "placard",
            "betclic": "betclic",
            "betclicpt": "betclic"
        }
        
        key = mappings.get(bookmaker_key)
        return BookmakerHelpers.BOOKMAKERS.get(key)
    
    @staticmethod
    def calculate_optimal_stakes_with_limits(odd1: float, odd2: float, total_stake: float, 
                                           bookmaker1: str, bookmaker2: str) -> Dict:
        """
        Calcula apostas ótimas considerando limites das casas de apostas.
        
        Args:
            odd1, odd2: Odds dos dois resultados
            total_stake: Montante total disponível
            bookmaker1, bookmaker2: Nomes das casas de apostas
            
        Returns:
            Dicionário com informações detalhadas das apostas
        """
        # Obter informações das casas de apostas
        bm1_info = BookmakerHelpers.get_bookmaker_info(bookmaker1)
        bm2_info = BookmakerHelpers.get_bookmaker_info(bookmaker2)
        
        # Calcular apostas ótimas básicas
        implied_prob1 = 1 / odd1
        implied_prob2 = 1 / odd2
        total_implied = implied_prob1 + implied_prob2
        
        optimal_stake1 = total_stake * implied_prob1 / total_implied
        optimal_stake2 = total_stake * implied_prob2 / total_implied
        
        # Aplicar limites das casas de apostas
        warnings = []
        
        if bm1_info:
            if optimal_stake1 < bm1_info["min_bet"]:
                warnings.append(f"Aposta na {bm1_info['name']} é inferior ao mínimo (€{bm1_info['min_bet']:.2f})")
                optimal_stake1 = bm1_info["min_bet"]
            elif optimal_stake1 > bm1_info["max_bet"]:
                warnings.append(f"Aposta na {bm1_info['name']} excede o máximo (€{bm1_info['max_bet']:.2f})")
                optimal_stake1 = bm1_info["max_bet"]
        
        if bm2_info:
            if optimal_stake2 < bm2_info["min_bet"]:
                warnings.append(f"Aposta na {bm2_info['name']} é inferior ao mínimo (€{bm2_info['min_bet']:.2f})")
                optimal_stake2 = bm2_info["min_bet"]
            elif optimal_stake2 > bm2_info["max_bet"]:
                warnings.append(f"Aposta na {bm2_info['name']} excede o máximo (€{bm2_info['max_bet']:.2f})")
                optimal_stake2 = bm2_info["max_bet"]
        
        # Recalcular lucro com os ajustes
        adjusted_total = optimal_stake1 + optimal_stake2
        profit1 = (optimal_stake1 * odd1) - adjusted_total
        profit2 = (optimal_stake2 * odd2) - adjusted_total
        guaranteed_profit = min(profit1, profit2)
        profit_percent = (guaranteed_profit / adjusted_total) * 100 if adjusted_total > 0 else 0
        
        return {
            "stake1": optimal_stake1,
            "stake2": optimal_stake2,
            "total_adjusted": adjusted_total,
            "guaranteed_profit": guaranteed_profit,
            "profit_percent": profit_percent,
            "warnings": warnings,
            "bm1_info": bm1_info,
            "bm2_info": bm2_info,
            "is_profitable": guaranteed_profit > 0
        }
    
    @staticmethod
    def get_betting_tips(bookmaker1: str, bookmaker2: str) -> List[str]:
        """
        Fornece dicas específicas para as casas de apostas.
        
        Args:
            bookmaker1, bookmaker2: Nomes das casas de apostas
            
        Returns:
            Lista de dicas úteis
        """
        tips = []
        
        bm1_info = BookmakerHelpers.get_bookmaker_info(bookmaker1)
        bm2_info = BookmakerHelpers.get_bookmaker_info(bookmaker2)
        
        if bm1_info and "betano" in bookmaker1.lower():
            tips.extend([
                "🟢 Betano: Usa 'Aposta Rápida' para colocares apostas mais rapidamente",
                "🟢 Betano: Ativa notificações para mudanças de odds importantes",
                "🟢 Betano: Cash out disponível se quiseres sair antecipadamente"
            ])
        
        if bm2_info and "888" in bookmaker2.lower():
            tips.extend([
                "🔵 888Starz: Limites mais altos - ideal para apostas grandes",
                "🔵 888Starz: Aceita criptomoedas para depósitos mais rápidos",
                "🔵 888Starz: Streaming ao vivo disponível para alguns eventos"
            ])
        
        # Dicas gerais de arbitragem
        tips.extend([
            "⚡ Coloca as apostas o mais rapidamente possível para evitar mudanças de odds",
            "📱 Usa apps móveis de ambas as casas para maior velocidade",
            "🎯 Verifica sempre se tens saldo suficiente em ambas as contas antes de calcular",
            "📊 Considera usar alertas de odds para encontrar mais oportunidades"
        ])
        
        return tips
    
    @staticmethod
    def format_bet_instructions(stake1: float, stake2: float, odd1: float, odd2: float,
                               bookmaker1: str, bookmaker2: str, event_name: str = None) -> str:
        """
        Formata instruções claras para colocar as apostas.
        
        Args:
            stake1, stake2: Valores das apostas
            odd1, odd2: Odds correspondentes
            bookmaker1, bookmaker2: Casas de apostas
            event_name: Nome do evento (opcional)
            
        Returns:
            Texto formatado com instruções
        """
        event_text = f" no evento {event_name}" if event_name else ""
        
        instructions = f"""
🎯 INSTRUÇÕES DE APOSTAS{event_text}

📋 APOSTA 1 - {bookmaker1.upper()}
   💰 Apostar: €{stake1:.2f}
   📊 Odd: {odd1:.2f}
   🎯 Resultado: Resultado 1
   
📋 APOSTA 2 - {bookmaker2.upper()}
   💰 Apostar: €{stake2:.2f}
   📊 Odd: {odd2:.2f}
   🎯 Resultado: Resultado 2

⏱️ IMPORTANTE:
- Coloca ambas as apostas RAPIDAMENTE
- Verifica as odds antes de confirmar
- Garante que tens saldo suficiente em ambas as contas
"""
        return instructions.strip()

class ArbitrageAnalyzer:
    """Analisador avançado de oportunidades de arbitragem."""
    
    @staticmethod
    def calculate_market_efficiency(odd1: float, odd2: float) -> Dict:
        """
        Calcula a eficiência do mercado e qualidade da oportunidade.
        
        Args:
            odd1, odd2: Odds dos dois resultados
            
        Returns:
            Análise detalhada da oportunidade
        """
        implied_prob1 = 1 / odd1
        implied_prob2 = 1 / odd2
        total_implied = implied_prob1 + implied_prob2
        
        margin = (total_implied - 1) * 100
        efficiency = (1 - abs(margin/10)) * 100  # Score de eficiência
        
        # Classificar a qualidade da oportunidade
        if margin < -2:
            quality = "Excelente"
            risk_level = "Baixo"
        elif margin < -1:
            quality = "Muito Boa"
            risk_level = "Baixo"
        elif margin < -0.5:
            quality = "Boa"
            risk_level = "Médio"
        elif margin < 0:
            quality = "Aceitável"
            risk_level = "Médio"
        else:
            quality = "Sem Arbitragem"
            risk_level = "Alto"
        
        return {
            "margin": margin,
            "efficiency_score": max(0, efficiency),
            "quality": quality,
            "risk_level": risk_level,
            "is_arbitrage": margin < 0,
            "implied_prob1": implied_prob1 * 100,
            "implied_prob2": implied_prob2 * 100,
            "total_implied": total_implied * 100
        }
    
    @staticmethod
    def estimate_time_sensitivity(profit_percent: float) -> Dict:
        """
        Estima a sensibilidade temporal da oportunidade.
        
        Args:
            profit_percent: Percentagem de lucro
            
        Returns:
            Análise de urgência
        """
        if profit_percent > 5:
            urgency = "CRÍTICA"
            time_estimate = "< 30 segundos"
            color = "#FF0000"
        elif profit_percent > 3:
            urgency = "ALTA"
            time_estimate = "< 2 minutos"
            color = "#FF8C00"
        elif profit_percent > 1:
            urgency = "MÉDIA"
            time_estimate = "< 5 minutos"
            color = "#FFD700"
        else:
            urgency = "BAIXA"
            time_estimate = "< 10 minutos"
            color = "#32CD32"
        
        return {
            "urgency": urgency,
            "estimated_window": time_estimate,
            "color": color,
            "priority_score": min(100, profit_percent * 20)
        }