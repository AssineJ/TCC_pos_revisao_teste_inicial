"""
scorer.py - Módulo de Cálculo de Veracidade

Responsabilidade:
    Calcular o score final de veracidade (10-95%) baseado na análise semântica
    e gerar justificativa detalhada e profissional.
    
    ✅ NOVO: Agora penaliza FORTEMENTE notícias contraditadas por fontes

Lógica:
    - Peso por tipo de confirmação (forte, parcial, menciona)
    - Penalidades (contradições, poucas fontes, sem fontes)
    - Bônus (alta similaridade, múltiplas fontes)
    - Ajustes contextuais (notícia recente, tema regional)

Autor: Projeto Acadêmico
Data: 2025
"""

from config import Config
from datetime import datetime


class VeracityScorer:
    """
    Calculador de veracidade que transforma análise semântica em score final.
    """
    
    def __init__(self):
        """Inicializa scorer com configurações"""
        self.min_score = Config.MIN_VERACITY_SCORE
        self.max_score = Config.MAX_VERACITY_SCORE
    
    
    def calcular_veracidade(self, resultado_analise_semantica, metadata_contexto=None):
        """
        Calcula score final de veracidade.
        
        Args:
            resultado_analise_semantica (dict): Resultado do semantic_analyzer
            metadata_contexto (dict): Informações contextuais (opcional)
            
        Returns:
            dict: {
                'veracidade': int (10-95),
                'justificativa': str,
                'detalhes': dict,
                'nivel_confianca': str
            }
        """
        
        meta = resultado_analise_semantica.get('metadata', {})
        
        # Extrair dados da análise
        total_analisados = meta.get('total_analisados', 0)
        contradizem = meta.get('contradizem', 0)  # ✅ NOVO
        confirmam_forte = meta.get('confirmam_forte', 0)
        confirmam_parcial = meta.get('confirmam_parcial', 0)
        apenas_mencionam = meta.get('apenas_mencionam', 0)
        nao_relacionados = meta.get('nao_relacionados', 0)
        
        # ✅ NOVO: Se há contradições, inicia com score MUITO BAIXO
        if contradizem > 0:
            print(f"\n⚠️  ALERTA: {contradizem} fonte(s) CONTRADIZEM a informação!")
            score_base = 10.0  # Começa no mínimo para fake news
            detalhes_calculo = {
                'motivo': 'Fontes contradizem a informação',
                'contradizem': contradizem
            }
        else:
            # ETAPA 1: Calcular score base (lógica normal)
            score_base, detalhes_calculo = self._calcular_score_base(
                total_analisados,
                confirmam_forte,
                confirmam_parcial,
                apenas_mencionam
            )
        
        # ETAPA 2: Aplicar penalidades
        penalidades, score_com_penalidades = self._aplicar_penalidades(
            score_base,
            total_analisados,
            confirmam_forte,
            nao_relacionados,
            contradizem,  # ✅ NOVO
            resultado_analise_semantica
        )
        
        # ETAPA 3: Aplicar bônus (SÓ se não houver contradições)
        if contradizem == 0:
            bonus, score_com_bonus = self._aplicar_bonus(
                score_com_penalidades,
                confirmam_forte,
                total_analisados,
                resultado_analise_semantica
            )
        else:
            bonus = {}
            score_com_bonus = score_com_penalidades
            print(f"   🚫 Bônus desativados devido a contradições")
        
        # ETAPA 4: Aplicar limites (10-95%)
        score_final = max(self.min_score, min(self.max_score, int(score_com_bonus)))
        
        # ETAPA 5: Determinar nível de confiança
        nivel_confianca = self._determinar_nivel_confianca(
            score_final,
            total_analisados,
            confirmam_forte,
            contradizem  # ✅ NOVO
        )
        
        # ETAPA 6: Gerar justificativa
        justificativa = self._gerar_justificativa(
            score_final,
            total_analisados,
            confirmam_forte,
            confirmam_parcial,
            apenas_mencionam,
            contradizem,  # ✅ NOVO
            nivel_confianca,
            penalidades,
            bonus
        )
        
        return {
            'veracidade': score_final,
            'justificativa': justificativa,
            'detalhes': {
                'score_base': round(score_base, 2),
                'penalidades': penalidades,
                'bonus': bonus,
                'score_com_penalidades': round(score_com_penalidades, 2),
                'score_com_bonus': round(score_com_bonus, 2),
                'score_final': score_final,
                'contradizem': contradizem  # ✅ NOVO
            },
            'nivel_confianca': nivel_confianca
        }
    
    
    def _calcular_score_base(self, total, forte, parcial, menciona):
        """
        Calcula score base usando pesos configurados.
        
        Args:
            total (int): Total de fontes analisadas
            forte (int): Fontes que confirmam fortemente
            parcial (int): Fontes que confirmam parcialmente
            menciona (int): Fontes que apenas mencionam
            
        Returns:
            tuple: (score, detalhes)
        """
        if total == 0:
            return (10.0, {'motivo': 'Nenhuma fonte analisada'})
        
        # Calcular pesos
        peso_forte = forte * Config.WEIGHT_STRONG_CONFIRMATION
        peso_parcial = parcial * Config.WEIGHT_PARTIAL_CONFIRMATION
        peso_menciona = menciona * Config.WEIGHT_MENTION
        
        peso_total = peso_forte + peso_parcial + peso_menciona
        
        # Calcular percentual base
        score_base = (peso_total / total) * 100
        
        detalhes = {
            'peso_forte': peso_forte,
            'peso_parcial': peso_parcial,
            'peso_menciona': peso_menciona,
            'peso_total': peso_total,
            'divisor': total
        }
        
        return (score_base, detalhes)
    
    
    def _aplicar_penalidades(self, score, total, forte, nao_rel, contradizem, analise):
        """
        Aplica penalidades ao score.
        
        ✅ NOVO: Penalidade SEVERA para contradições
        
        Penalidades:
        - CONTRADIÇÕES: -70% (NOVA E PRIORIDADE)
        - Nenhuma fonte encontrada: -80%
        - Poucas fontes (< 3): -20%
        - Nenhuma confirmação forte: -15%
        - Muitos não relacionados: -10%
        
        Args:
            score (float): Score base
            total (int): Total analisado
            forte (int): Confirmações fortes
            nao_rel (int): Não relacionados
            contradizem (int): ✅ NOVO - Fontes que contradizem
            analise (dict): Análise completa
            
        Returns:
            tuple: (dict penalidades, score_final)
        """
        penalidades = {}
        score_atual = score
        
        # ✅ NOVA PENALIDADE 1: CONTRADIÇÕES (MÁXIMA PRIORIDADE!)
        if contradizem > 0:
            # Penalidade severa: 50% base + 10% por contradição adicional
            reducao = min(50 + (contradizem - 1) * 10, 70)
            penalidades['contradicoes_detectadas'] = {
                'percentual': reducao,
                'quantidade': contradizem,
                'motivo': f'⚠️ {contradizem} fonte(s) CONTRADIZEM a informação (provável FAKE NEWS)'
            }
            score_atual *= (1 - reducao/100)
            print(f"   🔻 Penalidade por contradição: -{reducao}% | Score: {score_atual:.1f}%")
        
        # Penalidade 2: Nenhuma fonte
        if total == 0:
            penalidades['sem_fontes'] = {
                'percentual': 80,
                'motivo': 'Nenhuma fonte confiável encontrada'
            }
            return (penalidades, score * Config.PENALTY_NO_SOURCES)
        
        # Penalidade 3: Poucas fontes
        if total < 3:
            reducao = 20
            penalidades['poucas_fontes'] = {
                'percentual': reducao,
                'motivo': f'Apenas {total} fonte(s) analisada(s)'
            }
            score_atual *= (1 - reducao/100)
        
        # Penalidade 4: Nenhuma confirmação forte (SÓ se NÃO houver contradições)
        if forte == 0 and total > 0 and contradizem == 0:
            reducao = 15
            penalidades['sem_confirmacao_forte'] = {
                'percentual': reducao,
                'motivo': 'Nenhuma fonte confirma fortemente'
            }
            score_atual *= (1 - reducao/100)
        
        # Penalidade 5: Muitos não relacionados (> 50%)
        if total > 0 and (nao_rel / total) > 0.5:
            reducao = 10
            penalidades['muitos_nao_relacionados'] = {
                'percentual': reducao,
                'motivo': f'{nao_rel} de {total} fontes não relacionadas'
            }
            score_atual *= (1 - reducao/100)
        
        return (penalidades, score_atual)
    
    
    def _aplicar_bonus(self, score, forte, total, analise):
        """
        Aplica bônus ao score.
        
        Bônus:
        - Alta taxa de confirmação forte (>70%): +10%
        - Múltiplas fontes (>=5): +5%
        - Alta similaridade média (>0.75): +10%
        
        Args:
            score (float): Score atual
            forte (int): Confirmações fortes
            total (int): Total analisado
            analise (dict): Análise completa
            
        Returns:
            tuple: (dict bonus, score_final)
        """
        bonus = {}
        score_atual = score
        
        if total == 0:
            return (bonus, score_atual)
        
        # Bônus 1: Alta taxa de confirmação forte
        taxa_forte = forte / total
        if taxa_forte > 0.7:
            aumento = 10
            bonus['alta_confirmacao'] = {
                'percentual': aumento,
                'motivo': f'{forte} de {total} fontes confirmam fortemente ({taxa_forte*100:.0f}%)'
            }
            score_atual *= (1 + aumento/100)
        
        # Bônus 2: Múltiplas fontes
        if total >= 5:
            aumento = 5
            bonus['multiplas_fontes'] = {
                'percentual': aumento,
                'motivo': f'{total} fontes analisadas (>=5)'
            }
            score_atual *= (1 + aumento/100)
        
        # Bônus 3: Alta similaridade média
        similaridade_media = self._calcular_similaridade_media(analise)
        if similaridade_media > 0.75:
            aumento = 10
            bonus['alta_similaridade'] = {
                'percentual': aumento,
                'motivo': f'Similaridade média muito alta ({similaridade_media:.2f})'
            }
            score_atual *= (1 + aumento/100)
        
        return (bonus, score_atual)
    
    
    def _calcular_similaridade_media(self, analise):
        """
        Calcula similaridade média das fontes que confirmam.
        
        Args:
            analise (dict): Análise semântica completa
            
        Returns:
            float: Similaridade média (0-1)
        """
        similaridades = []
        
        for fonte_nome, fonte_analises in analise.items():
            if fonte_nome == 'metadata':
                continue
            
            for item in fonte_analises:
                if item.get('sucesso') and item.get('status') in ['confirma_forte', 'confirma_parcial']:
                    sim = item.get('similaridade', 0)
                    if sim > 0:
                        similaridades.append(sim)
        
        if not similaridades:
            return 0.0
        
        return sum(similaridades) / len(similaridades)
    
    
    def _determinar_nivel_confianca(self, score, total, forte, contradizem):
        """
        Determina nível de confiança da análise.
        
        ✅ NOVO: Considera contradições
        
        Args:
            score (int): Score final
            total (int): Total analisado
            forte (int): Confirmações fortes
            contradizem (int): ✅ NOVO - Fontes que contradizem
            
        Returns:
            str: 'alto', 'medio', 'baixo'
        """
        # ✅ NOVO: Se há contradições, sempre é BAIXO
        if contradizem > 0:
            return 'baixo'
        
        # Alto: score >= 70 E (total >= 5 OU forte >= 3)
        if score >= 70 and (total >= 5 or forte >= 3):
            return 'alto'
        
        # Baixo: score < 30 OU total < 2
        if score < 30 or total < 2:
            return 'baixo'
        
        # Médio: resto
        return 'medio'
    
    
    def _gerar_justificativa(self, score, total, forte, parcial, menciona, 
                            contradizem, nivel, penalidades, bonus):
        """
        Gera justificativa detalhada e profissional.
        
        ✅ NOVO: Inclui alerta sobre contradições
        
        Args:
            score (int): Score final
            total (int): Total analisado
            forte (int): Confirmações fortes
            parcial (int): Confirmações parciais
            menciona (int): Apenas mencionam
            contradizem (int): ✅ NOVO - Fontes que contradizem
            nivel (str): Nível de confiança
            penalidades (dict): Penalidades aplicadas
            bonus (dict): Bônus aplicados
            
        Returns:
            str: Justificativa formatada
        """
        # ✅ NOVA ABERTURA: Se há contradições, alerta imediato
        if contradizem > 0:
            abertura = f"⚠️ ALERTA DE FAKE NEWS: {contradizem} fonte(s) confiável(is) CONTRADIZEM esta informação."
        elif score >= 80:
            abertura = "Informação amplamente confirmada por fontes confiáveis."
        elif score >= 60:
            abertura = "Informação parcialmente confirmada por fontes confiáveis."
        elif score >= 40:
            abertura = "Informação com confirmação limitada em fontes confiáveis."
        elif score >= 20:
            abertura = "Informação com pouca ou nenhuma confirmação em fontes confiáveis."
        else:
            abertura = "Informação não encontrada ou contradita por fontes confiáveis."
        
        # Detalhes da análise
        if total > 0:
            detalhes_partes = []
            
            if contradizem > 0:
                detalhes_partes.append(f"⚠️ {contradizem} CONTRADIZEM")
            
            if forte > 0:
                detalhes_partes.append(f"{forte} confirmam fortemente")
            
            if parcial > 0:
                detalhes_partes.append(f"{parcial} confirmam parcialmente")
            
            if menciona > 0:
                detalhes_partes.append(f"{menciona} apenas mencionam")
            
            detalhes = f"Análise baseada em {total} fonte(s): {', '.join(detalhes_partes)}."
        else:
            detalhes = "Nenhuma fonte confiável encontrou informações relacionadas ao tema."
        
        # Alertas sobre penalidades
        alertas = []
        
        if 'contradicoes_detectadas' in penalidades:
            alertas.append("🚨 ATENÇÃO: Fontes confiáveis apresentam informações OPOSTAS ao afirmado. Provável desinformação.")
        
        if 'sem_fontes' in penalidades:
            alertas.append("⚠️ Atenção: Tema não encontrado em portais confiáveis.")
        
        if 'poucas_fontes' in penalidades:
            alertas.append("⚠️ Atenção: Análise baseada em poucas fontes.")
        
        # Notas sobre bônus
        notas_bonus = []
        if 'alta_confirmacao' in bonus:
            notas_bonus.append("✓ Alta taxa de confirmação entre as fontes.")
        
        if 'multiplas_fontes' in bonus:
            notas_bonus.append("✓ Análise baseada em múltiplas fontes independentes.")
        
        # Nível de confiança
        if nivel == 'alto':
            confianca_msg = "Nível de confiança: ALTO"
        elif nivel == 'medio':
            confianca_msg = "Nível de confiança: MÉDIO"
        else:
            confianca_msg = "Nível de confiança: BAIXO"
        
        # Montar justificativa final
        partes = [abertura, detalhes]
        
        if alertas:
            partes.extend(alertas)
        
        if notas_bonus:
            partes.extend(notas_bonus)
        
        partes.append(confianca_msg)
        
        justificativa = " ".join(partes)
        
        return justificativa


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def calcular_veracidade(resultado_analise_semantica, metadata_contexto=None):
    """
    Função simplificada para calcular veracidade.
    
    Args:
        resultado_analise_semantica (dict): Resultado do semantic_analyzer
        metadata_contexto (dict): Contexto opcional
        
    Returns:
        dict: Score e justificativa
    """
    scorer = VeracityScorer()
    return scorer.calcular_veracidade(resultado_analise_semantica, metadata_contexto)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO SCORER COM DETECÇÃO DE CONTRADIÇÃO")
    print("=" * 70)
    print()
    
    # Cenário 1: FAKE NEWS com contradição
    print("Cenário 1: FAKE NEWS (com contradição)")
    print("-" * 70)
    
    analise_fake = {
        'metadata': {
            'total_analisados': 5,
            'contradizem': 3,  # ✅ NOVO
            'confirmam_forte': 0,
            'confirmam_parcial': 0,
            'apenas_mencionam': 2,
            'nao_relacionados': 0
        },
        'G1': [
            {'sucesso': True, 'similaridade': 0.65, 'status': 'CONTRADIZ'},
        ]
    }
    
    resultado = calcular_veracidade(analise_fake)
    print(f"Veracidade: {resultado['veracidade']}%")
    print(f"Nível: {resultado['nivel_confianca']}")
    print(f"Justificativa: {resultado['justificativa']}")
    print()
    
    # Cenário 2: Alta veracidade
    print("Cenário 2: Alta Veracidade (notícia real)")
    print("-" * 70)
    
    analise_alta = {
        'metadata': {
            'total_analisados': 8,
            'contradizem': 0,
            'confirmam_forte': 6,
            'confirmam_parcial': 2,
            'apenas_mencionam': 0,
            'nao_relacionados': 0
        },
        'G1': [
            {'sucesso': True, 'similaridade': 0.85, 'status': 'confirma_forte'},
            {'sucesso': True, 'similaridade': 0.78, 'status': 'confirma_forte'}
        ]
    }
    
    resultado = calcular_veracidade(analise_alta)
    print(f"Veracidade: {resultado['veracidade']}%")
    print(f"Nível: {resultado['nivel_confianca']}")
    print(f"Justificativa: {resultado['justificativa']}")
    print()
    
    # Cenário 3: Sem fontes
    print("Cenário 3: Sem Fontes")
    print("-" * 70)
    
    analise_sem = {
        'metadata': {
            'total_analisados': 0,
            'contradizem': 0,
            'confirmam_forte': 0,
            'confirmam_parcial': 0,
            'apenas_mencionam': 0,
            'nao_relacionados': 0
        }
    }
    
    resultado = calcular_veracidade(analise_sem)
    print(f"Veracidade: {resultado['veracidade']}%")
    print(f"Nível: {resultado['nivel_confianca']}")
    print(f"Justificativa: {resultado['justificativa']}")
    print()
    
    print("=" * 70)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 70)