"""
Sistema de gestão de utilizadores para aplicação de arbitragem
"""
import hashlib
import hmac
import os
import time
import secrets
import streamlit as st
from typing import Dict, Optional, List
import database as db

class UserManager:
    """Gestor de utilizadores com autenticação segura."""
    
    SECRET_KEY = os.environ.get("APP_SECRET_KEY", "default-secret-change-in-production")
    
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple:
        """
        Cria hash seguro da password com salt.
        
        Args:
            password: Password em texto simples
            salt: Salt opcional (gera um novo se None)
            
        Returns:
            Tuple (hash, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Usar PBKDF2 para hash seguro
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt, 
                                          100000)  # 100k iterações
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: bytes, salt: bytes) -> bool:
        """
        Verifica se a password está correcta.
        
        Args:
            password: Password inserida pelo utilizador
            stored_hash: Hash guardado na base de dados
            salt: Salt usado no hash original
            
        Returns:
            True se a password estiver correcta
        """
        test_hash, _ = UserManager.hash_password(password, salt)
        return hmac.compare_digest(test_hash, stored_hash)
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> Dict:
        """
        Cria um novo utilizador.
        
        Args:
            username: Nome de utilizador
            email: Email do utilizador
            password: Password em texto simples
            
        Returns:
            Resultado da operação
        """
        # Validações básicas
        if len(username) < 3:
            return {"success": False, "error": "Nome de utilizador deve ter pelo menos 3 caracteres"}
        
        if len(password) < 8:
            return {"success": False, "error": "Password deve ter pelo menos 8 caracteres"}
        
        if "@" not in email or "." not in email:
            return {"success": False, "error": "Email inválido"}
        
        # Verificar se utilizador já existe
        conn = db.get_connection()
        if not conn:
            return {"success": False, "error": "Erro de ligação à base de dados"}
        
        try:
            cursor = conn.cursor()
            
            # Criar tabela de utilizadores se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash BYTEA NOT NULL,
                    salt BYTEA NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium BOOLEAN DEFAULT FALSE,
                    daily_profit_target DECIMAL(10,2) DEFAULT 100.00,
                    total_profit DECIMAL(10,2) DEFAULT 0.00,
                    subscription_expires TIMESTAMP NULL
                );
            """)
            
            # Verificar se username ou email já existem
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                         (username, email))
            if cursor.fetchone():
                return {"success": False, "error": "Utilizador ou email já existem"}
            
            # Criar hash da password
            password_hash, salt = UserManager.hash_password(password)
            
            # Inserir novo utilizador
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (username, email, password_hash, salt))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            if conn:
                conn.close()
            return {"success": False, "error": f"Erro ao criar utilizador: {str(e)}"}
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict]:
        """
        Autentica um utilizador.
        
        Args:
            username: Nome de utilizador ou email
            password: Password
            
        Returns:
            Dados do utilizador se autenticado, None caso contrário
        """
        conn = db.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # Procurar utilizador por username ou email
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, is_premium, 
                       daily_profit_target, total_profit, subscription_expires
                FROM users 
                WHERE username = %s OR email = %s
            """, (username, username))
            
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_data:
                return None
            
            # Verificar password
            stored_hash = bytes(user_data[3])
            salt = bytes(user_data[4])
            
            if UserManager.verify_password(password, stored_hash, salt):
                return {
                    "id": user_data[0],
                    "username": user_data[1],
                    "email": user_data[2],
                    "is_premium": user_data[5],
                    "daily_profit_target": float(user_data[6]),
                    "total_profit": float(user_data[7]),
                    "subscription_expires": user_data[8]
                }
            
            return None
            
        except Exception as e:
            if conn:
                conn.close()
            return None
    
    @staticmethod
    def update_user_profit(user_id: int, profit_amount: float) -> bool:
        """
        Actualiza o lucro total do utilizador.
        
        Args:
            user_id: ID do utilizador
            profit_amount: Valor do lucro a adicionar
            
        Returns:
            True se actualizado com sucesso
        """
        conn = db.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET total_profit = total_profit + %s
                WHERE id = %s
            """, (profit_amount, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            if conn:
                conn.close()
            return False

class SubscriptionManager:
    """Gestor de subscrições premium."""
    
    PLANS = {
        "free": {
            "name": "Gratuito",
            "price": 0,
            "max_calculations_per_day": 10,
            "api_access": False,
            "priority_support": False,
            "advanced_analytics": False
        },
        "pro": {
            "name": "Profissional",
            "price": 9.99,
            "max_calculations_per_day": 100,
            "api_access": True,
            "priority_support": True,
            "advanced_analytics": True
        },
        "premium": {
            "name": "Premium",
            "price": 19.99,
            "max_calculations_per_day": -1,  # Ilimitado
            "api_access": True,
            "priority_support": True,
            "advanced_analytics": True,
            "custom_alerts": True,
            "white_label": True
        }
    }
    
    @staticmethod
    def check_usage_limits(user_data: Dict) -> Dict:
        """
        Verifica se o utilizador pode fazer mais cálculos.
        
        Args:
            user_data: Dados do utilizador
            
        Returns:
            Status dos limites
        """
        # Obter plano do utilizador
        plan = "premium" if user_data.get("is_premium") else "free"
        plan_limits = SubscriptionManager.PLANS[plan]
        
        # Calcular utilizações hoje (isto seria melhorado com tabela de logs)
        daily_usage = st.session_state.get("daily_calculations", 0)
        max_daily = plan_limits["max_calculations_per_day"]
        
        can_use = max_daily == -1 or daily_usage < max_daily
        remaining = max_daily - daily_usage if max_daily != -1 else -1
        
        return {
            "can_use": can_use,
            "remaining": remaining,
            "plan": plan,
            "plan_name": plan_limits["name"]
        }

def init_authentication():
    """Inicializa o sistema de autenticação."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'daily_calculations' not in st.session_state:
        st.session_state.daily_calculations = 0

def show_auth_form():
    """Mostra formulário de login/registo."""
    st.markdown("## 🔐 Acesso à Aplicação")
    
    tab1, tab2 = st.tabs(["Entrar", "Registar"])
    
    with tab1:
        st.markdown("### Entrar na sua conta")
        with st.form("login_form"):
            username = st.text_input("Nome de utilizador ou email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if username and password:
                    user_data = UserManager.authenticate_user(username, password)
                    if user_data:
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_data
                        st.success(f"Bem-vindo, {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas")
                else:
                    st.error("Preencha todos os campos")
    
    with tab2:
        st.markdown("### Criar nova conta")
        with st.form("register_form"):
            new_username = st.text_input("Nome de utilizador")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirmar password", type="password")
            submit_reg = st.form_submit_button("Registar")
            
            if submit_reg:
                if new_password != confirm_password:
                    st.error("Passwords não coincidem")
                elif len(new_password) < 8:
                    st.error("Password deve ter pelo menos 8 caracteres")
                else:
                    result = UserManager.create_user(new_username, new_email, new_password)
                    if result["success"]:
                        st.success("Conta criada com sucesso! Pode agora fazer login.")
                    else:
                        st.error(result["error"])

def require_authentication():
    """Verifica se o utilizador está autenticado."""
    if not st.session_state.get('authenticated', False):
        show_auth_form()
        st.stop()
    
    # Verificar limites de utilização
    usage_status = SubscriptionManager.check_usage_limits(st.session_state.user_data)
    if not usage_status["can_use"]:
        st.error(f"Limite diário atingido ({usage_status['plan_name']}). Faça upgrade para continuar.")
        if st.button("Ver Planos Premium"):
            show_pricing_page()
        st.stop()

def show_pricing_page():
    """Mostra página de preços."""
    st.markdown("## 💎 Planos Premium")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Gratuito
        - 10 cálculos/dia
        - Funcionalidades básicas
        - Suporte comunitário
        
        **€0/mês**
        """)
    
    with col2:
        st.markdown("""
        ### Profissional
        - 100 cálculos/dia
        - Acesso à API
        - Suporte prioritário
        - Análises avançadas
        
        **€9.99/mês**
        """)
        if st.button("Escolher Pro", key="pro"):
            st.info("Redirecionar para pagamento...")
    
    with col3:
        st.markdown("""
        ### Premium
        - Cálculos ilimitados
        - Todas as funcionalidades
        - Alertas personalizados
        - White label
        
        **€19.99/mês**
        """)
        if st.button("Escolher Premium", key="premium"):
            st.info("Redirecionar para pagamento...")