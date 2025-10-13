from config import Config

print("=" * 70)
print("🧪 TESTE: VERIFICAR FONTES CONFIÁVEIS")
print("=" * 70)
print()

print("📰 Fontes configuradas:")
for i, fonte in enumerate(Config.TRUSTED_SOURCES, 1):
    status = "✅" if fonte['ativo'] else "❌"
    print(f"{i}. {status} {fonte['nome']}")
    print(f"   Domínio: {fonte['dominio']}")
    print(f"   Confiabilidade: {fonte['confiabilidade']*100:.0f}%")
    print()

print("=" * 70)
print(f"✅ Total: {len(Config.TRUSTED_SOURCES)} fontes")
print("=" * 70)