#!/bin/bash
# Script para ignorar mudanças locais em arquivos .gcode, .yml e .stl

# Garante que estamos na raiz do repo
cd "$(git rev-parse --show-toplevel)" || exit 1

echo "Ignorando mudanças locais em arquivos .gcode, .yml e .stl..."

# Aplica skip-worktree em todos os arquivos rastreados com essas extensões
for ext in gcode yml stl; do
  files=$(git ls-files "*.${ext}")
  if [ -n "$files" ]; then
    echo "$files" | xargs git update-index --skip-worktree
  fi
done

echo "Pronto! Agora o Git não vai mostrar modificações locais nesses arquivos."
