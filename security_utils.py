import re
import html
import streamlit as st
from typing import Any, Union
import time
from functools import wraps

class SecurityUtils:
    """Utilitários de segurança para a aplicação."""
    
    @staticmethod
    def sanitize_input(user_input: Union[str, float, int]) -> Union[str, float, int]:
        """
        Sanitiza entrada do usuário para prevenir XSS e injeção.
        
        Args:
            user_input: Entrada do usuário para sanitizar
            
        Returns:
            Entrada sanitizada
        """
        if isinstance(user_input, str):
            # Remover scripts maliciosos
            user_input = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', user_input, flags=re.IGNORECASE)
            # Escapar HTML
            user_input = html.escape(user_input)
            # Remover caracteres de controle
            user_input = ''.join(char for char in user_input if ord(char) >= 32 or char in '\t\n\r')
            # Limitar tamanho
            user_input = user_input[:1000]  # Máximo 1000 caracteres
        
        return user_input
    
    @staticmethod
    def validate_numeric_input(value: Any, min_val: float = 0, max_val: float = float('inf')) -> bool:
        """
        Valida entrada numérica.
        
        Args:
            value: Valor para validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            
        Returns:
            True se válido, False caso contrário
        """
        try:
            num_val = float(value)
            return min_val <= num_val <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_odds(odd: Any) -> bool:
        """
        Valida se uma odd está dentro de limites razoáveis.
        
        Args:
            odd: Valor da odd para validar
            
        Returns:
            True se válido, False caso contrário
        """
        return SecurityUtils.validate_numeric_input(odd, 1.01, 1000.0)
    
    @staticmethod
    def validate_stake(stake: Any) -> bool:
        """
        Valida se um valor de aposta está dentro de limites razoáveis.
        
        Args:
            stake: Valor da aposta para validar
            
        Returns:
            True se válido, False caso contrário
        """
        return SecurityUtils.validate_numeric_input(stake, 0.01, 1000000.0)
    
    @staticmethod
    def secure_display_text(text: str) -> str:
        """
        Prepara texto para exibição segura sem HTML.
        
        Args:
            text: Texto para exibir
            
        Returns:
            Texto seguro para exibição
        """
        if not isinstance(text, str):
            text = str(text)
        return SecurityUtils.sanitize_input(text)

class RateLimiter:
    """Controle de taxa de requisições para APIs."""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        """
        Inicializa o limitador de taxa.
        
        Args:
            max_calls: Número máximo de chamadas permitidas
            time_window: Janela de tempo em segundos
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def is_allowed(self) -> bool:
        """
        Verifica se uma nova chamada é permitida.
        
        Returns:
            True se permitido, False caso contrário
        """
        now = time.time()
        # Remove chamadas antigas
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def get_wait_time(self) -> int:
        """
        Retorna o tempo de espera até a próxima chamada permitida.
        
        Returns:
            Tempo de espera em segundos
        """
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        wait_time = self.time_window - (time.time() - oldest_call)
        return max(0, int(wait_time))

def rate_limit_decorator(limiter: RateLimiter):
    """
    Decorator para aplicar rate limiting a funções.
    
    Args:
        limiter: Instância do RateLimiter
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                wait_time = limiter.get_wait_time()
                st.warning(f"Muitas requisições. Aguarde {wait_time} segundos.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_environment_variables():
    """Valida se todas as variáveis de ambiente necessárias estão presentes."""
    required_vars = ["DATABASE_URL"]
    optional_vars = ["ODDS_API_KEY"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.environ.get(var):
            missing_optional.append(var)
    
    if missing_required:
        st.error(f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing_required)}")
        st.stop()
    
    if missing_optional:
        st.warning(f"Variáveis de ambiente opcionais ausentes: {', '.join(missing_optional)}")

import os