"""
text_validator.py - Validação de Qualidade de Texto

Detecta textos inválidos:
- Repetições excessivas (aaaaaaa, 111111)
- Falta de palavras únicas
- Texto sem contexto (só símbolos, números)
- Baixa entropia (pouca variação)

Autor: Projeto Acadêmico
Data: 2025
"""

import re
from collections import Counter


def validar_qualidade_texto(texto: str) -> dict:
    """
    Valida se o texto tem qualidade suficiente para análise.
    
    Args:
        texto (str): Texto a ser validado
        
    Returns:
        dict: {
            'valido': bool,
            'motivo': str,
            'score_qualidade': float (0-1),
            'problemas': list
        }
    """
    
    texto_limpo = texto.strip()
    problemas = []
    score_qualidade = 1.0
    
    # ========================================================================
    # REGRA 1: Detectar repetições excessivas de caracteres
    # ========================================================================
    # Exemplo: "aaaaaaa", "1111111"
    repeticoes = re.findall(r'(.)\1{4,}', texto_limpo)
    if repeticoes:
        problemas.append(f"Caracteres repetidos excessivamente: {set(repeticoes)}")
        score_qualidade -= 0.4
    
    # ========================================================================
    # REGRA 2: Verificar proporção de palavras únicas
    # ========================================================================
    palavras = re.findall(r'\b\w+\b', texto_limpo.lower())
    
    if len(palavras) < 5:
        problemas.append("Texto muito curto (menos de 5 palavras)")
        score_qualidade -= 0.3
    else:
        palavras_unicas = len(set(palavras))
        proporcao_unicas = palavras_unicas / len(palavras)
        
        # Se menos de 30% das palavras são únicas, é suspeito
        if proporcao_unicas < 0.3:
            problemas.append(f"Poucas palavras únicas ({proporcao_unicas:.0%})")
            score_qualidade -= 0.3
    
    # ========================================================================
    # REGRA 3: Detectar texto predominantemente não-alfabético
    # ========================================================================
    caracteres_alfabeticos = len(re.findall(r'[a-zA-ZÀ-ÿ]', texto_limpo))
    total_caracteres = len(re.sub(r'\s', '', texto_limpo))
    
    if total_caracteres > 0:
        proporcao_alfabetica = caracteres_alfabeticos / total_caracteres
        
        if proporcao_alfabetica < 0.5:
            problemas.append(f"Pouco texto alfabético ({proporcao_alfabetica:.0%})")
            score_qualidade -= 0.3
    
    # ========================================================================
    # REGRA 4: Verificar repetição de palavras completas
    # ========================================================================
    if palavras:
        contador = Counter(palavras)
        palavra_mais_comum, freq_max = contador.most_common(1)[0]
        
        # Se uma palavra aparece em mais de 50% do texto
        if freq_max / len(palavras) > 0.5:
            problemas.append(f"Palavra '{palavra_mais_comum}' repetida {freq_max} vezes")
            score_qualidade -= 0.3
    
    # ========================================================================
    # REGRA 5: Verificar se tem verbos/substantivos (heurística simples)
    # ========================================================================
    # Palavras muito curtas (< 3 letras) geralmente não são informativas
    palavras_longas = [p for p in palavras if len(p) >= 3]
    
    if len(palavras_longas) < 3:
        problemas.append("Poucas palavras significativas (≥ 3 letras)")
        score_qualidade -= 0.2
    
    # ========================================================================
    # DECISÃO FINAL
    # ========================================================================
    score_qualidade = max(0.0, score_qualidade)
    
    valido = score_qualidade >= 0.4 and len(problemas) <= 2
    
    if not valido:
        motivo = "Texto inválido: " + "; ".join(problemas)
    else:
        motivo = "Texto válido para análise"
    
    return {
        'valido': valido,
        'motivo': motivo,
        'score_qualidade': round(score_qualidade, 2),
        'problemas': problemas
    }


def validar_url(url: str) -> dict:
    """
    Valida se URL parece válida.
    
    Args:
        url (str): URL a validar
        
    Returns:
        dict: {'valido': bool, 'motivo': str}
    """
    
    url = url.strip()
    
    # Deve começar com http:// ou https://
    if not re.match(r'^https?://', url):
        return {
            'valido': False,
            'motivo': 'URL deve começar com http:// ou https://'
        }
    
    # Deve ter um domínio
    if not re.search(r'https?://[\w\-]+(\.[\w\-]+)+', url):
        return {
            'valido': False,
            'motivo': 'URL não parece válida (falta domínio)'
        }
    
    # Não pode ter espaços
    if ' ' in url:
        return {
            'valido': False,
            'motivo': 'URL não pode conter espaços'
        }
    
    return {
        'valido': True,
        'motivo': 'URL válida'
    }


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTANDO VALIDADOR DE TEXTO")
    print("=" * 70)
    print()
    
    # Teste 1: Texto repetitivo (INVÁLIDO)
    print("Teste 1: Texto repetitivo")
    print("-" * 70)
    texto1 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    resultado1 = validar_qualidade_texto(texto1)
    print(f"Texto: {texto1[:50]}...")
    print(f"✅ Válido: {resultado1['valido']}")
    print(f"📊 Score: {resultado1['score_qualidade']}")
    print(f"💬 Motivo: {resultado1['motivo']}")
    print()
    
    # Teste 2: Texto válido
    print("Teste 2: Texto válido (notícia real)")
    print("-" * 70)
    texto2 = "Governo Lula quer salário mínimo acima de R$ 1.631 em 2026 segundo fontes oficiais"
    resultado2 = validar_qualidade_texto(texto2)
    print(f"Texto: {texto2}")
    print(f"✅ Válido: {resultado2['valido']}")
    print(f"📊 Score: {resultado2['score_qualidade']}")
    print(f"💬 Motivo: {resultado2['motivo']}")
    print()
    
    # Teste 3: Texto com palavras repetidas
    print("Teste 3: Palavras repetidas")
    print("-" * 70)
    texto3 = "teste teste teste teste teste teste teste teste teste teste"
    resultado3 = validar_qualidade_texto(texto3)
    print(f"Texto: {texto3}")
    print(f"✅ Válido: {resultado3['valido']}")
    print(f"📊 Score: {resultado3['score_qualidade']}")
    print(f"💬 Motivo: {resultado3['motivo']}")
    print()
    
    # Teste 4: Só números
    print("Teste 4: Só números")
    print("-" * 70)
    texto4 = "123456789 987654321 111111111 222222222 333333333"
    resultado4 = validar_qualidade_texto(texto4)
    print(f"Texto: {texto4}")
    print(f"✅ Válido: {resultado4['valido']}")
    print(f"📊 Score: {resultado4['score_qualidade']}")
    print(f"💬 Motivo: {resultado4['motivo']}")
    print()
    
    print("=" * 70)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 70)