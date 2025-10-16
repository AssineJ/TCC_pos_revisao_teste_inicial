"""
preload_models.py - Script para pré-carregar modelos de IA

Execute ANTES de iniciar a aplicação para evitar travamentos:
    python preload_models.py

Isso baixará e armazenará em cache:
1. Modelo spaCy (pt_core_news_lg) - ~560MB
2. Modelo Sentence Transformer (paraphrase-multilingual-mpnet-base-v2) - ~1.1GB
"""

import sys
import os
from pathlib import Path

def print_step(emoji, message):
    """Imprime mensagem formatada"""
    print(f"\n{emoji} {message}")
    print("=" * 70)

def check_spacy_model():
    """Verifica e carrega modelo spaCy"""
    print_step("📚", "Verificando modelo spaCy...")
    
    try:
        import spacy
        model_name = "pt_core_news_lg"
        
        try:
            nlp = spacy.load(model_name)
            print(f"✅ Modelo '{model_name}' já está instalado!")
            return True
        except OSError:
            print(f"⚠️  Modelo '{model_name}' não encontrado.")
            print(f"📥 Baixando modelo spaCy (~560MB)...")
            
            os.system(f'python -m spacy download {model_name}')
            
            # Verificar se instalou corretamente
            nlp = spacy.load(model_name)
            print(f"✅ Modelo '{model_name}' instalado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar modelo spaCy: {e}")
        return False

def check_sentence_transformer():
    """Verifica e carrega modelo Sentence Transformer"""
    print_step("🤖", "Verificando modelo Sentence Transformer...")
    
    try:
        from sentence_transformers import SentenceTransformer
        from config import Config
        
        model_name = Config.SENTENCE_TRANSFORMER_MODEL
        print(f"📥 Baixando/carregando '{model_name}' (~1.1GB)...")
        print("⏳ Isso pode levar alguns minutos na primeira execução...")
        
        # Isso irá baixar se não existir, ou carregar do cache
        model = SentenceTransformer(model_name)
        
        # Teste rápido
        test_embedding = model.encode("Teste de funcionamento", show_progress_bar=False)
        
        print(f"✅ Modelo carregado com sucesso!")
        print(f"   Dimensões do embedding: {len(test_embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar Sentence Transformer: {e}")
        return False

def check_cache_directory():
    """Verifica diretório de cache"""
    print_step("📁", "Verificando diretórios de cache...")
    
    try:
        from pathlib import Path
        
        # Diretório de cache do transformers
        cache_dir = Path.home() / '.cache' / 'huggingface'
        
        if cache_dir.exists():
            # Calcular tamanho do cache
            total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"✅ Cache encontrado: {cache_dir}")
            print(f"   Tamanho total: {size_mb:.2f} MB")
        else:
            print(f"📁 Cache será criado em: {cache_dir}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Aviso ao verificar cache: {e}")
        return True  # Não é crítico

def main():
    """Executa todas as verificações"""
    print("=" * 70)
    print("🚀 PRÉ-CARREGAMENTO DE MODELOS - NEWS VERIFIER")
    print("=" * 70)
    
    results = []
    
    # 1. Verificar cache
    results.append(("Cache", check_cache_directory()))
    
    # 2. Verificar spaCy
    results.append(("spaCy", check_spacy_model()))
    
    # 3. Verificar Sentence Transformer (esse é o problema!)
    results.append(("Sentence Transformer", check_sentence_transformer()))
    
    # Resumo final
    print_step("📊", "RESUMO FINAL")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n🎉 Todos os modelos estão prontos!")
        print("✅ Você pode iniciar a aplicação normalmente:")
        print("   python app.py")
        return 0
    else:
        print("\n⚠️  Alguns modelos falharam ao carregar.")
        print("❌ Verifique os erros acima antes de prosseguir.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrompido pelo usuário.")
        print("Execute novamente para continuar.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)