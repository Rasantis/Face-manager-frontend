#!/bin/bash
# Script para build de produção do Face Tester

echo "🚀 Iniciando build de produção..."

# Build do React para produção
npm run build

echo "✅ Build concluído!"
echo "📁 Arquivos prontos em: ./build"
echo ""
echo "🌐 Para servir em produção:"
echo "   - Copie o conteúdo da pasta 'build' para seu servidor web"
echo "   - Ou use: npx serve -s build -p 3000" 