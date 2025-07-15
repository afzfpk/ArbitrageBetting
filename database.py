import os
import psycopg2
import psycopg2.extras
from datetime import datetime

def get_connection():
    """Estabelece uma conexão com o banco de dados PostgreSQL."""
    try:
        # Usar variável de ambiente para a URL do banco de dados
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        # Conectar ao banco de dados com SSL obrigatório
        conn = psycopg2.connect(db_url, sslmode='require')
        return conn
    except Exception as e:
        print(f"Erro de conexão com o banco de dados: {e}")
        return None

def save_arbitrage_opportunity(odd1, odd2, total_stake, stake1, stake2, profit, profit_percent, 
                             event_name=None, bookmaker1=None, bookmaker2=None):
    """
    Salva uma oportunidade de arbitragem no banco de dados.
    
    Parâmetros:
    - odd1, odd2: As odds dos dois resultados
    - total_stake: Montante total apostado
    - stake1, stake2: Montantes para cada aposta individual
    - profit: Lucro absoluto
    - profit_percent: Percentagem de lucro
    - event_name: Nome do evento (opcional)
    - bookmaker1, bookmaker2: Nomes das casas de apostas (opcional)
    """
    conn = get_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar se a tabela tem as colunas adicionais
        try:
            # Verificar se as colunas existem
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'arbitrage_opportunities' 
                AND column_name IN ('event_name', 'bookmaker1', 'bookmaker2');
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Se as colunas não existirem, adicioná-las
            if 'event_name' not in existing_columns:
                cursor.execute("ALTER TABLE arbitrage_opportunities ADD COLUMN event_name TEXT;")
            if 'bookmaker1' not in existing_columns:
                cursor.execute("ALTER TABLE arbitrage_opportunities ADD COLUMN bookmaker1 TEXT;")
            if 'bookmaker2' not in existing_columns:
                cursor.execute("ALTER TABLE arbitrage_opportunities ADD COLUMN bookmaker2 TEXT;")
            
            conn.commit()
        except Exception as e:
            print(f"Erro ao verificar/adicionar colunas: {e}")
            # Continuar mesmo se houver erro (usar colunas existentes)
            conn.rollback()
        
        # Inserir os dados com as colunas adicionais, se disponíveis
        query = """
            INSERT INTO arbitrage_opportunities 
            (odd1, odd2, total_stake, stake1, stake2, profit, profit_percent, event_name, bookmaker1, bookmaker2) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(query, (
            odd1, odd2, total_stake, stake1, stake2, profit, profit_percent,
            event_name, bookmaker1, bookmaker2
        ))
        result = cursor.fetchone()
        opportunity_id = result[0] if result else None
        conn.commit()
        cursor.close()
        conn.close()
        return opportunity_id
    except Exception as e:
        print(f"Erro ao salvar oportunidade de arbitragem: {e}")
        if conn:
            conn.close()
        return False

def get_arbitrage_history(limit=10):
    """Recupera o histórico de oportunidades de arbitragem."""
    conn = get_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            # Tentar selecionar todos os campos, incluindo os novos
            query = """
                SELECT * FROM arbitrage_opportunities 
                ORDER BY date_created DESC 
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
        except Exception as e:
            print(f"Erro na primeira consulta: {e}")
            # Fallback para colunas básicas se houver erro
            query = """
                SELECT id, odd1, odd2, total_stake, stake1, stake2, profit, profit_percent, date_created 
                FROM arbitrage_opportunities 
                ORDER BY date_created DESC 
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Converter para lista de dicionários
        history = []
        for row in results:
            item = dict(row)
            # Garantir que os campos novos existam, mesmo que nulos
            for field in ['event_name', 'bookmaker1', 'bookmaker2']:
                if field not in item:
                    item[field] = None
            history.append(item)
        
        return history
    except Exception as e:
        print(f"Erro ao recuperar histórico de arbitragem: {e}")
        if conn:
            conn.close()
        return []

def delete_arbitrage_opportunity(opportunity_id):
    """Exclui uma oportunidade de arbitragem do banco de dados."""
    conn = get_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        query = "DELETE FROM arbitrage_opportunities WHERE id = %s;"
        cursor.execute(query, (opportunity_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao excluir oportunidade de arbitragem: {e}")
        if conn:
            conn.close()
        return False