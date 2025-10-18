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


def validar_qualidade_texto(texto):
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

    def motivo_insuficiente(detalhe: str) -> str:
        detalhe = detalhe.strip().rstrip('.')
        return f"Dados fornecidos insuficientes: {detalhe}"
    
    # ========================================================================
    # VERIFICAÇÃO 1: Repetições excessivas de caracteres
    # ========================================================================
    repeticoes = re.findall(r'(.)\1{4,}', texto_limpo)
    if repeticoes:
        # Extrair apenas os caracteres únicos
        chars_unicos = []
        for r in repeticoes:
            if isinstance(r, str):
                chars_unicos.append(r)
        
        chars_unicos = list(set(chars_unicos))[:3]
        
        if chars_unicos:
            chars_str = ', '.join(chars_unicos)
            return {
                'valido': False,
                'motivo': motivo_insuficiente(f"caracteres repetidos excessivamente ({chars_str})"),
                'score_qualidade': 0.0,
                'problemas': ['Caracteres repetidos excessivamente']
            }
    
    # ========================================================================
    # VERIFICAÇÃO 2: Proporção de palavras únicas
    # ========================================================================
    palavras = re.findall(r'\b\w+\b', texto_limpo.lower())
    
    if len(palavras) < 5:
        return {
            'valido': False,
            'motivo': motivo_insuficiente('menos de 5 palavras'),
            'score_qualidade': 0.0,
            'problemas': ['Texto muito curto']
        }
    
    palavras_unicas = len(set(palavras))
    proporcao_unicas = palavras_unicas / len(palavras)
    
    # Se menos de 20% das palavras são únicas, REJEITA
    if proporcao_unicas < 0.20:
        try:
            palavra_mais_comum = max(set(palavras), key=palavras.count)
            freq_max = palavras.count(palavra_mais_comum)
            
            return {
                'valido': False,
                'motivo': motivo_insuficiente(
                    f"a palavra '{palavra_mais_comum}' aparece {freq_max} vezes"
                ),
                'score_qualidade': 0.1,
                'problemas': [
                    f"Poucas palavras únicas ({int(proporcao_unicas * 100)}%)",
                    f"Palavra repetida {freq_max} vezes",
                    'Muitas palavras soltas sem contexto'
                ]
            }
        except:
            return {
                'valido': False,
                'motivo': motivo_insuficiente('muitas palavras repetidas'),
                'score_qualidade': 0.1,
                'problemas': ['Muitas palavras repetidas']
            }

    # ========================================================================
    # VERIFICAÇÃO 2.1: Sequências repetidas de palavras/frases
    # ========================================================================
    palavras_lower = palavras
    max_window = min(8, len(palavras_lower) // 2)
    sequencia_repetida = None
    if max_window >= 3:
        for tamanho in range(max_window, 2, -1):
            for inicio in range(0, len(palavras_lower) - tamanho * 2 + 1):
                bloco = palavras_lower[inicio : inicio + tamanho]
                prox = palavras_lower[inicio + tamanho : inicio + tamanho * 2]
                if bloco == prox:
                    sequencia_repetida = " ".join(bloco)
                    break
            if sequencia_repetida:
                break

    if sequencia_repetida:
        return {
            'valido': False,
            'motivo': motivo_insuficiente('sequência repetida de termos'),
            'score_qualidade': 0.1,
            'problemas': [f"Sequência repetida: {sequencia_repetida}"]
        }
    
    # ========================================================================
    # VERIFICAÇÃO 3: Texto predominantemente não-alfabético
    # ========================================================================
    caracteres_alfabeticos = len(re.findall(r'[a-zA-ZÀ-ÿ]', texto_limpo))
    total_caracteres = len(re.sub(r'\s', '', texto_limpo))
    
    if total_caracteres > 0:
        proporcao_alfabetica = caracteres_alfabeticos / total_caracteres
        
        if proporcao_alfabetica < 0.5:
            problemas.append(f"Pouco texto alfabético ({int(proporcao_alfabetica * 100)}%)")
            score_qualidade -= 0.3
    
    # ========================================================================
    # VERIFICAÇÃO 4: Palavras significativas
    # ========================================================================
    palavras_longas = [p for p in palavras if len(p) >= 3]
    
    if len(palavras_longas) < 3:
        problemas.append("Poucas palavras significativas")
        score_qualidade -= 0.2
    
    # ========================================================================
    # DECISÃO FINAL
    # ========================================================================
    score_qualidade = max(0.0, score_qualidade)
    
    valido = score_qualidade >= 0.5 and len(problemas) <= 1
    
    if not valido:
        motivo = motivo_insuficiente("; ".join(problemas) if problemas else "qualidade insuficiente")
    else:
        motivo = "Texto válido para análise"
    
    return {
        'valido': valido,
        'motivo': motivo,
        'score_qualidade': round(score_qualidade, 2),
        'problemas': problemas
    }


def validar_url(url):
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

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTANDO VALIDADOR DE TEXTO")
    print("=" * 70)
    print()
    
    # Teste 1: Texto repetitivo
    print("Teste 1: Texto repetitivo")
    print("-" * 70)
    texto1 = "teste teste teste teste teste teste"
    resultado1 = validar_qualidade_texto(texto1)
    print(f"Texto: {texto1}")
    print(f"✅ Válido: {resultado1['valido']}")
    print(f"📊 Score: {resultado1['score_qualidade']}")
    print(f"💬 Motivo: {resultado1['motivo']}")
    print()
    
    # Teste 2: Texto válido
    print("Teste 2: Texto válido")
    print("-" * 70)
    texto2 = "Governo anuncia aumento do salário mínimo para 2026"
    resultado2 = validar_qualidade_texto(texto2)
    print(f"Texto: {texto2}")
    print(f"✅ Válido: {resultado2['valido']}")
    print(f"📊 Score: {resultado2['score_qualidade']}")
    print(f"💬 Motivo: {resultado2['motivo']}")
    print()
    
    print("=" * 70)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 70)