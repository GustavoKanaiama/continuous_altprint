#!/bin/bash
# Script para voltar a rastrear arquivos .gcode, .yml e .stl ignorados localmente

# Garante que estamos na raiz do repo
cd "$(git rev-parse --show-toplevel)" || exit 1

echo "Voltando a rastrear mudanças em arquivos .gcode, .yml e .stl..."

# Remove skip-worktree em todos os arquivos rastreados com essas extensões
for ext in gcode yml stl; do
  files=$(git ls-files "*.${ext}")
  if [ -n "$files" ]; then
    echo "$files" | xargs git update-index --no-skip-worktree
  fi
done

echo "Pronto! O Git agora vai mostrar modificações locais nesses arquivos novamente."
