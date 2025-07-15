"""
Sistema de pagamentos para monetização da aplicação
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import database as db

class PaymentSystem:
    """Sistema de pagamentos e subscrições."""
    
    STRIPE_PUBLIC_KEY = "pk_test_..."  # Será definido pelo utilizador
    PAYPAL_CLIENT_ID = "..."  # PayPal para Portugal
    
    PLANS = {
        "pro": {
            "name": "Profissional",
            "price": 9.99,
            "currency": "EUR",
            "duration_days": 30,
            "features": [
                "100 cálculos por dia",
                "Acesso à API ao vivo",
                "Suporte prioritário",
                "Analytics básico",
                "Exportação CSV"
            ],
            "stripe_price_id": "price_pro_monthly",
            "paypal_plan_id": "P-pro-monthly"
        },
        "premium": {
            "name": "Premium",
            "price": 19.99,
            "currency": "EUR", 
            "duration_days": 30,
            "features": [
                "Cálculos ilimitados",
                "API prioritária",
                "Suporte VIP 24/7",
                "Analytics avançado",
                "Alertas personalizados",
                "White label",
                "Exportação completa"
            ],
            "stripe_price_id": "price_premium_monthly",
            "paypal_plan_id": "P-premium-monthly"
        }
    }
    
    @staticmethod
    def create_stripe_checkout_session(plan_id: str, user_id: int) -> Dict:
        """
        Cria sessão de checkout Stripe.
        
        Args:
            plan_id: ID do plano (pro/premium)
            user_id: ID do utilizador
            
        Returns:
            Dados da sessão de checkout
        """
        plan = PaymentSystem.PLANS.get(plan_id)
        if not plan:
            return {"error": "Plano inválido"}
        
        # Em produção, usar Stripe API real
        checkout_data = {
            "session_id": f"cs_test_{plan_id}_{user_id}_{datetime.now().timestamp()}",
            "url": f"https://checkout.stripe.com/pay/cs_test_{plan_id}",
            "plan": plan,
            "user_id": user_id,
            "amount": plan["price"],
            "currency": plan["currency"]
        }
        
        return checkout_data
    
    @staticmethod
    def create_paypal_order(plan_id: str, user_id: int) -> Dict:
        """
        Cria order PayPal.
        
        Args:
            plan_id: ID do plano
            user_id: ID do utilizador
            
        Returns:
            Dados da order PayPal
        """
        plan = PaymentSystem.PLANS.get(plan_id)
        if not plan:
            return {"error": "Plano inválido"}
        
        # Em produção, usar PayPal API
        order_data = {
            "order_id": f"PAYPAL_{plan_id}_{user_id}_{datetime.now().timestamp()}",
            "approval_url": f"https://paypal.com/checkout?token=EC-{plan_id}",
            "plan": plan,
            "user_id": user_id,
            "amount": plan["price"],
            "currency": plan["currency"]
        }
        
        return order_data
    
    @staticmethod
    def verify_payment(payment_data: Dict) -> bool:
        """
        Verifica se o pagamento foi processado com sucesso.
        
        Args:
            payment_data: Dados do pagamento
            
        Returns:
            True se o pagamento foi verificado
        """
        # Em produção, verificar com API real
        # Por agora, simulamos verificação bem-sucedida
        return payment_data.get("status") == "completed"
    
    @staticmethod
    def activate_subscription(user_id: int, plan_id: str) -> bool:
        """
        Activa subscrição do utilizador.
        
        Args:
            user_id: ID do utilizador
            plan_id: ID do plano
            
        Returns:
            True se activado com sucesso
        """
        plan = PaymentSystem.PLANS.get(plan_id)
        if not plan:
            return False
        
        conn = db.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Calcular data de expiração
            expiry_date = datetime.now() + timedelta(days=plan["duration_days"])
            
            # Actualizar utilizador
            cursor.execute("""
                UPDATE users 
                SET is_premium = %s,
                    subscription_plan = %s,
                    subscription_expires = %s,
                    subscription_activated = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (True, plan_id, expiry_date, user_id))
            
            # Registar transacção
            cursor.execute("""
                INSERT INTO transactions (user_id, plan_id, amount, currency, status, created_at)
                VALUES (%s, %s, %s, %s, 'completed', CURRENT_TIMESTAMP)
            """, (user_id, plan_id, plan["price"], plan["currency"]))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            if conn:
                conn.close()
            return False
    
    @staticmethod
    def check_subscription_status(user_id: int) -> Dict:
        """
        Verifica status da subscrição do utilizador.
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            Status da subscrição
        """
        conn = db.get_connection()
        if not conn:
            return {"active": False}
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT subscription_plan, subscription_expires, is_premium
                FROM users 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result:
                return {"active": False}
            
            plan_id, expires, is_premium = result
            
            # Verificar se ainda está activa
            if expires and datetime.now() > expires:
                return {"active": False, "expired": True, "plan": plan_id}
            
            return {
                "active": is_premium,
                "plan": plan_id,
                "expires": expires,
                "days_remaining": (expires - datetime.now()).days if expires else None
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {"active": False}

def show_pricing_page():
    """Mostra página de preços com opções de pagamento."""
    
    st.markdown("## 💎 Planos Premium")
    st.markdown("Escolha o plano ideal para maximizar os seus lucros de arbitragem!")
    
    # Mostrar planos lado a lado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <h3 style="color: #4CAF50; margin-bottom: 1rem;">Gratuito</h3>
            <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">€0</div>
            <div style="opacity: 0.7; margin-bottom: 1.5rem;">por mês</div>
            <ul style="text-align: left; list-style: none; padding: 0;">
                <li style="margin: 0.5rem 0;">✅ 10 cálculos por dia</li>
                <li style="margin: 0.5rem 0;">✅ Funcionalidades básicas</li>
                <li style="margin: 0.5rem 0;">✅ Suporte comunitário</li>
                <li style="margin: 0.5rem 0;">❌ Analytics avançado</li>
                <li style="margin: 0.5rem 0;">❌ API access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3366ff 0%, #667eea 100%); padding: 2rem; border-radius: 15px; text-align: center; position: relative;">
            <div style="position: absolute; top: -10px; right: 10px; background: #FF5722; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold;">POPULAR</div>
            <h3 style="color: white; margin-bottom: 1rem;">Profissional</h3>
            <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0; color: white;">€9.99</div>
            <div style="opacity: 0.8; margin-bottom: 1.5rem; color: white;">por mês</div>
            <ul style="text-align: left; list-style: none; padding: 0; color: white;">
                <li style="margin: 0.5rem 0;">✅ 100 cálculos por dia</li>
                <li style="margin: 0.5rem 0;">✅ Acesso à API ao vivo</li>
                <li style="margin: 0.5rem 0;">✅ Suporte prioritário</li>
                <li style="margin: 0.5rem 0;">✅ Analytics básico</li>
                <li style="margin: 0.5rem 0;">✅ Exportação CSV</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Subscrever Pro", type="primary", key="subscribe_pro"):
            show_payment_options("pro")
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FF5722 0%, #FF9800 100%); padding: 2rem; border-radius: 15px; text-align: center;">
            <h3 style="color: white; margin-bottom: 1rem;">Premium</h3>
            <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0; color: white;">€19.99</div>
            <div style="opacity: 0.8; margin-bottom: 1.5rem; color: white;">por mês</div>
            <ul style="text-align: left; list-style: none; padding: 0; color: white;">
                <li style="margin: 0.5rem 0;">✅ Cálculos ilimitados</li>
                <li style="margin: 0.5rem 0;">✅ API prioritária</li>
                <li style="margin: 0.5rem 0;">✅ Suporte VIP 24/7</li>
                <li style="margin: 0.5rem 0;">✅ Analytics completo</li>
                <li style="margin: 0.5rem 0;">✅ Alertas personalizados</li>
                <li style="margin: 0.5rem 0;">✅ White label</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Subscrever Premium", type="primary", key="subscribe_premium"):
            show_payment_options("premium")
    
    # FAQ de pagamentos
    st.markdown("---")
    st.markdown("### ❓ Perguntas Frequentes")
    
    with st.expander("Como funcionam os pagamentos?"):
        st.markdown("""
        - **Seguro**: Usamos Stripe e PayPal, os processadores mais seguros do mundo
        - **Fácil**: Cartão de débito/crédito ou conta PayPal
        - **Flexível**: Pode cancelar a qualquer momento
        - **Suporte**: Ajuda em português 24/7 para clientes premium
        """)
    
    with st.expander("Que métodos de pagamento aceitam?"):
        st.markdown("""
        **Cartões Aceites:**
        - Visa, Mastercard, American Express
        - Cartões de débito nacionais
        - Apple Pay, Google Pay
        
        **Outros Métodos:**
        - PayPal (conta ou cartão)
        - SEPA Direct Debit (EU)
        - MB Way (brevemente)
        """)
    
    with st.expander("Posso cancelar a qualquer altura?"):
        st.markdown("""
        **Sim, sem complicações!**
        - Cancele quando quiser na área de conta
        - Sem taxas de cancelamento
        - Mantém acesso até ao fim do período pago
        - Dados preservados por 30 dias após cancelamento
        """)

def show_payment_options(plan_id: str):
    """Mostra opções de pagamento para um plano."""
    
    if not st.session_state.get('authenticated', False):
        st.error("Faça login primeiro para subscrever")
        return
    
    plan = PaymentSystem.PLANS.get(plan_id)
    user_data = st.session_state.user_data
    
    st.markdown(f"## 💳 Pagamento - {plan['name']}")
    st.markdown(f"**Preço:** €{plan['price']}/mês")
    
    # Escolher método de pagamento
    payment_method = st.radio(
        "Escolha o método de pagamento:",
        ["💳 Cartão (Stripe)", "🅿️ PayPal"],
        key=f"payment_method_{plan_id}"
    )
    
    col1, col2 = st.columns(2)
    
    if payment_method == "💳 Cartão (Stripe)":
        with col1:
            if st.button("Pagar com Stripe", type="primary", key=f"stripe_{plan_id}"):
                checkout_session = PaymentSystem.create_stripe_checkout_session(plan_id, user_data['id'])
                
                # Em produção, redirecionar para Stripe
                st.success("Redireccionando para checkout seguro...")
                st.markdown(f"[Continuar para Stripe]({checkout_session.get('url', '#')})")
                
                # Simular activação (remover em produção)
                if st.button("Simular Pagamento Concluído", key=f"sim_stripe_{plan_id}"):
                    if PaymentSystem.activate_subscription(user_data['id'], plan_id):
                        st.success("Subscrição activada com sucesso!")
                        st.rerun()
    
    else:  # PayPal
        with col2:
            if st.button("Pagar com PayPal", type="primary", key=f"paypal_{plan_id}"):
                paypal_order = PaymentSystem.create_paypal_order(plan_id, user_data['id'])
                
                # Em produção, redirecionar para PayPal
                st.success("Redireccionando para PayPal...")
                st.markdown(f"[Continuar para PayPal]({paypal_order.get('approval_url', '#')})")
                
                # Simular activação (remover em produção)
                if st.button("Simular Pagamento PayPal", key=f"sim_paypal_{plan_id}"):
                    if PaymentSystem.activate_subscription(user_data['id'], plan_id):
                        st.success("Subscrição activada com sucesso!")
                        st.rerun()
    
    # Mostrar detalhes do plano
    st.markdown("### 📋 O que está incluído:")
    for feature in plan['features']:
        st.markdown(f"✅ {feature}")
    
    # Política de segurança
    st.markdown("---")
    st.markdown("""
    🔒 **Pagamento 100% Seguro**
    - Encriptação SSL 256-bits
    - Dados de cartão nunca armazenados
    - Conformidade PCI DSS
    - Política de reembolso de 30 dias
    """)

def init_payment_system():
    """Inicializa o sistema de pagamentos."""
    
    # Criar tabela de transacções se não existir
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    plan_id VARCHAR(50) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'EUR',
                    status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    transaction_id VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Adicionar colunas de subscrição à tabela users se não existirem
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50),
                ADD COLUMN IF NOT EXISTS subscription_activated TIMESTAMP;
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            if conn:
                conn.close()
            pass  # Tabelas já existem