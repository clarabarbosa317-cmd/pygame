#!/usr/bin/env python3
"""
Script para verificar se os arquivos de nível estão corretos
Execute: python verificar_levels.py
"""

import os
from pathlib import Path

def check_level_file(filepath, level_num):
    """Verifica um arquivo de nível"""
    print(f"\n{'='*60}")
    print(f"Verificando {filepath.name}")
    print('='*60)
    
    if not filepath.exists():
        print(f"❌ ERRO: Arquivo não encontrado!")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove quebras de linha mas mantém as linhas
    lines = [line.rstrip('\n\r') for line in lines]
    
    # Verifica número de linhas
    if len(lines) != 24:
        print(f"❌ ERRO: Deveria ter 24 linhas, mas tem {len(lines)}")
        return False
    else:
        print(f"✓ Número de linhas correto: 24")
    
    # Verifica cada linha
    errors = []
    for i, line in enumerate(lines, 1):
        if len(line) != 40:
            errors.append(f"  Linha {i}: {len(line)} caracteres (deveria ter 40)")
    
    if errors:
        print(f"❌ ERRO: Linhas com tamanho incorreto:")
        for err in errors:
            print(err)
        return False
    else:
        print(f"✓ Todas as linhas têm 40 caracteres")
    
    # Junta tudo para análise
    content = ''.join(lines)
    
    # Conta elementos obrigatórios
    count_1 = content.count('1')
    count_2 = content.count('2')
    count_G = content.count('G')
    count_H = content.count('H')
    count_blocks = content.count('#')
    count_spikes = content.count('X')
    
    print(f"\n📊 Estatísticas do nível:")
    print(f"  • Spawn dino vermelho (1): {count_1}")
    print(f"  • Spawn dino azul (2): {count_2}")
    print(f"  • Portal vermelho (G): {count_G}")
    print(f"  • Portal azul (H): {count_H}")
    print(f"  • Blocos (#): {count_blocks}")
    print(f"  • Spikes (X): {count_spikes}")
    
    # Verifica elementos obrigatórios
    all_ok = True
    if count_1 == 0:
        print(f"❌ FALTA: Spawn do dino vermelho (1)")
        all_ok = False
    if count_2 == 0:
        print(f"❌ FALTA: Spawn do dino azul (2)")
        all_ok = False
    if count_G == 0:
        print(f"❌ FALTA: Portal vermelho (G)")
        all_ok = False
    if count_H == 0:
        print(f"❌ FALTA: Portal azul (H)")
        all_ok = False
    
    if all_ok:
        print(f"\n✅ Nível {level_num} está CORRETO!")
        return True
    else:
        print(f"\n❌ Nível {level_num} tem ERROS!")
        return False

def main():
    print("🔍 VERIFICADOR DE NÍVEIS - DinoWars")
    print("="*60)
    
    # Encontra pasta levels
    script_dir = Path(__file__).parent
    levels_dir = script_dir.parent / "levels"
    
    if not levels_dir.exists():
        levels_dir = script_dir / "levels"
    
    if not levels_dir.exists():
        print(f"❌ ERRO: Pasta 'levels' não encontrada!")
        print(f"Procurei em: {levels_dir}")
        return
    
    print(f"📁 Pasta de níveis: {levels_dir}")
    
    # Verifica cada nível
    results = {}
    for i in range(1, 7):
        level_file = levels_dir / f"level{i}.txt"
        results[i] = check_level_file(level_file, i)
    
    # Resumo final
    print("\n" + "="*60)
    print("📋 RESUMO FINAL")
    print("="*60)
    
    for level, ok in results.items():
        status = "✅ OK" if ok else "❌ ERRO"
        print(f"Level {level}: {status}")
    
    total_ok = sum(results.values())
    print(f"\nTotal: {total_ok}/6 níveis corretos")
    
    if total_ok == 6:
        print("\n🎉 Todos os níveis estão prontos para jogar!")
    else:
        print("\n⚠️  Corrija os erros antes de jogar!")

if __name__ == "__main__":
    main()