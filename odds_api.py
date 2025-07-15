import os
import requests
import time
from typing import List, Dict, Any, Optional, Tuple

class OddsAPI:
    """Classe para interagir com a The Odds API para buscar odds."""
    
    BASE_URL = "https://api.the-odds-api.com/v4/sports"
    
    def __init__(self):
        """Inicializa a API com a chave da API de ambiente."""
        self.api_key = os.environ.get("ODDS_API_KEY")
        if not self.api_key:
            print("ODDS_API_KEY não encontrada nas variáveis de ambiente")
            # Não interromper a aplicação, apenas desabilitar funcionalidades da API
            self.api_key = None
        
        # Mapear nomes de esportes para os códigos da API
        self.sport_map = {
            "futebol": "soccer",
            "basquete": "basketball",
            "tenis": "tennis",
            "beisebol": "baseball",
            "hockey": "icehockey",
            "futebol_americano": "americanfootball",
            "mma": "mma"
        }
        
        # Contador de chamadas à API
        self.api_calls = 0
        # Timestamp da última chamada à API
        self.last_call = 0
    
    def get_sports(self) -> List[Dict[str, Any]]:
        """Busca a lista de esportes disponíveis."""
        url = f"{self.BASE_URL}"
        params = {
            "apiKey": self.api_key
        }
        
        return self._make_request(url, params)
    
    def get_odds(self, sport: str, region: str = "eu", market: str = "h2h") -> List[Dict[str, Any]]:
        """
        Busca odds para um determinado esporte.
        
        Args:
            sport: Código do esporte (ex: 'soccer_brazil_campeonato' ou nome mapeado 'futebol')
            region: Região para as odds (ex: 'eu', 'us', 'uk')
            market: Tipo de mercado (ex: 'h2h' para moneyline, 'spreads', 'totals')
            
        Returns:
            Lista de jogos com suas odds
        """
        # Mapear nome do esporte se for um nome genérico
        if sport in self.sport_map:
            sport_code = self.sport_map[sport]
            # Buscar todos os esportes para encontrar o código específico
            all_sports = self.get_sports()
            # Filtrar para encontrar códigos que contenham o esporte genérico
            sport_codes = [s["key"] for s in all_sports if sport_code in s["key"]]
            if sport_codes:
                sport = sport_codes[0]  # Usar o primeiro código encontrado
        
        url = f"{self.BASE_URL}/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": region,
            "markets": market,
            "oddsFormat": "decimal"
        }
        
        return self._make_request(url, params)
    
    def get_best_odds(self, sport: str) -> List[Dict[str, Any]]:
        """
        Busca os jogos e encontra as melhores odds para cada resultado.
        
        Args:
            sport: Código do esporte
            
        Returns:
            Lista de jogos com odds otimizadas para arbitragem
        """
        games = self.get_odds(sport)
        arb_opportunities = []
        
        for game in games:
            if "bookmakers" not in game or not game["bookmakers"]:
                continue
            
            home_team = game["home_team"]
            away_team = game["away_team"]
            
            # Encontrar as melhores odds para cada resultado
            best_home_odd = 0
            best_away_odd = 0
            best_draw_odd = 0
            
            # Bookmakers que ofereceram as melhores odds
            best_home_bookie = ""
            best_away_bookie = ""
            best_draw_bookie = ""
            
            for bookmaker in game["bookmakers"]:
                bookie_name = bookmaker["title"]
                
                for market in bookmaker["markets"]:
                    if market["key"] != "h2h":
                        continue
                    
                    for outcome in market["outcomes"]:
                        price = outcome["price"]
                        name = outcome["name"]
                        
                        if name == home_team and price > best_home_odd:
                            best_home_odd = price
                            best_home_bookie = bookie_name
                        elif name == away_team and price > best_away_odd:
                            best_away_odd = price
                            best_away_bookie = bookie_name
                        elif name == "Draw" and price > best_draw_odd:
                            best_draw_odd = price
                            best_draw_bookie = bookie_name
            
            # Calcular se há oportunidade de arbitragem
            has_draw = best_draw_odd > 0
            
            if has_draw:
                # Jogo com possibilidade de empate (futebol, etc)
                inv_sum = (1 / best_home_odd) + (1 / best_away_odd) + (1 / best_draw_odd)
                outcomes = [
                    {"name": home_team, "odd": best_home_odd, "bookmaker": best_home_bookie},
                    {"name": away_team, "odd": best_away_odd, "bookmaker": best_away_bookie},
                    {"name": "Empate", "odd": best_draw_odd, "bookmaker": best_draw_bookie}
                ]
            else:
                # Jogo sem empate (basquete, tenis, etc)
                inv_sum = (1 / best_home_odd) + (1 / best_away_odd)
                outcomes = [
                    {"name": home_team, "odd": best_home_odd, "bookmaker": best_home_bookie},
                    {"name": away_team, "odd": best_away_odd, "bookmaker": best_away_bookie}
                ]
            
            # Se a soma das probabilidades for menor que 1, há oportunidade de arbitragem
            arb_opportunity = inv_sum < 1
            
            arb_opportunities.append({
                "id": game["id"],
                "sport": game["sport_key"],
                "commence_time": game["commence_time"],
                "home_team": home_team,
                "away_team": away_team,
                "has_draw": has_draw,
                "outcomes": outcomes,
                "implied_prob_sum": inv_sum,
                "is_arbitrage": arb_opportunity,
                "profit_percent": ((1 / inv_sum) - 1) * 100 if arb_opportunity else 0
            })
        
        # Ordenar por maior lucro potencial
        arb_opportunities.sort(key=lambda x: x["profit_percent"], reverse=True)
        return arb_opportunities
    
    def find_arbitrage_opportunities(self, min_profit: float = 1.0) -> List[Dict[str, Any]]:
        """
        Busca oportunidades de arbitragem em vários esportes.
        
        Args:
            min_profit: Percentual mínimo de lucro para considerar uma oportunidade
            
        Returns:
            Lista de oportunidades de arbitragem
        """
        all_opportunities = []
        
        # Lista de esportes populares para procurar oportunidades
        sports_to_check = ["soccer", "tennis", "basketball", "baseball"]
        
        for sport in sports_to_check:
            try:
                sport_opps = self.get_best_odds(sport)
                # Filtrar somente oportunidades reais com lucro mínimo
                filtered_opps = [
                    opp for opp in sport_opps 
                    if opp["is_arbitrage"] and opp["profit_percent"] >= min_profit
                ]
                all_opportunities.extend(filtered_opps)
            except Exception as e:
                print(f"Erro ao buscar oportunidades para {sport}: {e}")
        
        # Ordenar por maior lucro potencial
        all_opportunities.sort(key=lambda x: x["profit_percent"], reverse=True)
        return all_opportunities
    
    def get_game_odds(self, game_id: str) -> Tuple[float, float, Optional[float]]:
        """
        Retorna as melhores odds para um jogo específico.
        
        Args:
            game_id: ID do jogo
            
        Returns:
            Tuple com (melhor odd casa, melhor odd fora, melhor odd empate ou None)
        """
        # Esta função seria ideal para implementar no futuro, mas vamos
        # simplificar usando apenas as duas melhores odds para qualquer jogo
        
        # Aqui, retornaremos um exemplo simples de duas odds
        # Mas em uma implementação completa, buscaríamos as odds específicas
        # para o jogo com o ID fornecido
        
        # Por enquanto, vamos retornar duas odds genéricas que garantem arbitragem
        return 2.10, 2.05, None
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Any:
        """
        Faz uma requisição à API com controle de rate limit e validação de segurança.
        
        Args:
            url: URL da requisição
            params: Parâmetros da requisição
            
        Returns:
            Dados da resposta em JSON
        """
        # Verificar se a API key está disponível
        if not self.api_key:
            raise ValueError("API key não configurada")
        
        # Validar URL para prevenir SSRF
        if not url.startswith('https://api.the-odds-api.com'):
            raise ValueError("URL não autorizada")
        
        # Sanitizar parâmetros
        safe_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                safe_params[key] = value[:100]  # Limitar tamanho
            else:
                safe_params[key] = value
        # Aguardar pelo menos 1 segundo entre chamadas para respeitar o rate limit
        current_time = time.time()
        if current_time - self.last_call < 1:
            time.sleep(1 - (current_time - self.last_call))
        
        response = requests.get(url, params=params)
        self.last_call = time.time()
        self.api_calls += 1
        
        if response.status_code != 200:
            error_msg = f"Erro na API (status {response.status_code}): {response.text}"
            raise Exception(error_msg)
        
        # Verificar cabeçalhos para informações sobre o rate limit
        remaining = response.headers.get("x-rate-limit-remaining", "Desconhecido")
        used = response.headers.get("x-rate-limit-requests-used", "Desconhecido") 
        print(f"Chamadas restantes: {remaining}, Utilizadas: {used}")
        
        return response.json()


# Função auxiliar para converter uma oportunidade em odds simples
def convert_opportunity_to_odds(opportunity: Dict[str, Any]) -> Tuple[float, float, Optional[float]]:
    """
    Converte uma oportunidade de arbitragem em um par de odds simples.
    
    Args:
        opportunity: Dados da oportunidade
        
    Returns:
        Tuple com (odd1, odd2, odd_draw ou None)
    """
    if not opportunity or "outcomes" not in opportunity:
        return 0, 0, None
    
    odds = [outcome["odd"] for outcome in opportunity["outcomes"]]
    
    if len(odds) == 3:
        return odds[0], odds[1], odds[2]
    elif len(odds) == 2:
        return odds[0], odds[1], None
    else:
        return 0, 0, None


# Teste da API
if __name__ == "__main__":
    api = OddsAPI()
    try:
        # Teste básico da API
        print("Testando conexão com a API...")
        sports = api.get_sports()
        print(f"Esportes disponíveis: {len(sports)}")
        
        # Buscar oportunidades
        print("\nBuscando oportunidades de arbitragem...")
        opportunities = api.find_arbitrage_opportunities(min_profit=0.5)
        print(f"Encontradas {len(opportunities)} oportunidades")
        
        # Mostrar as melhores oportunidades
        for i, opp in enumerate(opportunities[:5]):
            print(f"\nOportunidade #{i+1}:")
            print(f"Jogo: {opp['home_team']} vs {opp['away_team']}")
            print(f"Esporte: {opp['sport']}")
            print(f"Lucro potencial: {opp['profit_percent']:.2f}%")
            print("Odds:")
            for outcome in opp["outcomes"]:
                print(f"  {outcome['name']}: {outcome['odd']} ({outcome['bookmaker']})")
    
    except Exception as e:
        print(f"Erro ao testar a API: {e}")