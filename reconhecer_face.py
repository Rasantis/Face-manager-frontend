#!/usr/bin/env python3
"""
🔍 Face Manager - Reconhecimento Facial
Script para identificar uma pessoa usando reconhecimento facial

Configuração:
- Cliente: pao_de_acucar (hardcoded)
- Imagem: presidente.jpg (da pasta upload_images)

Execute: python reconhecer_face.py
"""

import requests
import json
import os
import base64
from datetime import datetime

# =====================
# 🔧 CONFIGURAÇÕES
# =====================

# Cliente fixo para busca (hardcoded como solicitado)
CLIENTE_BUSCA = "pao_de_acucar"

# Imagem para reconhecimento
IMAGEM_TESTE = "lasaro4.jpg"

# URLs das APIs
COMPREFACE_URL = "http://localhost:8000/api/v1/recognition/recognize"
FACE_MANAGER_URL = "http://localhost:5000/api"

# Chave da API CompreFace
API_KEY = "68896071-a604-44b7-beed-6d019f6f62fe"
HEADERS = {"x-api-key": API_KEY}

def log(message, level="INFO"):
    """Log com timestamp e cores"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",    # Azul
        "SUCCESS": "\033[92m", # Verde
        "ERROR": "\033[91m",   # Vermelho
        "WARNING": "\033[93m", # Amarelo
        "END": "\033[0m"       # Reset
    }
    prefix = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️ ",
    }
    print(f"[{timestamp}] {colors.get(level, '')}{prefix.get(level, '')}{message}{colors['END']}")

def verificar_imagem():
    """Verifica se a imagem existe"""
    if not os.path.exists(IMAGEM_TESTE):
        log(f"Imagem não encontrada: {IMAGEM_TESTE}", "ERROR")
        log("Coloque a imagem 'presidente.jpg' na pasta 'upload_images/'", "INFO")
        return False
    
    log(f"Imagem encontrada: {IMAGEM_TESTE}", "SUCCESS")
    return True

def obter_pessoas_cliente():
    """Obtém todas as pessoas do cliente para referência"""
    try:
        response = requests.get(f"{FACE_MANAGER_URL}/{CLIENTE_BUSCA}/persons")
        if response.status_code == 200:
            data = response.json()
            log(f"Base de dados {CLIENTE_BUSCA}: {data['total']} pessoas cadastradas", "INFO")
            return data['persons']
        else:
            log(f"Erro ao acessar base de dados: {response.status_code}", "ERROR")
            return {}
    except Exception as e:
        log(f"Erro de conexão com Face Manager: {e}", "ERROR")
        return {}

def reconhecer_face():
    """Executa reconhecimento facial usando CompreFace"""
    try:
        log("🔍 Iniciando reconhecimento facial...", "INFO")
        
        # Abrir e enviar imagem para CompreFace
        with open(IMAGEM_TESTE, "rb") as f:
            files = {"file": f}
            
            # Fazer reconhecimento sem filtro de subject (para buscar em toda a base)
            response = requests.post(
                COMPREFACE_URL,
                headers=HEADERS,
                files=files,
                timeout=30
            )
        
        log(f"Status CompreFace: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            log("Resposta do CompreFace recebida", "SUCCESS")
            return result
        else:
            log(f"Erro no CompreFace: {response.status_code} - {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log(f"Erro no reconhecimento: {e}", "ERROR")
        return None

def processar_resultado(compreface_result, pessoas_cliente):
    """Processa resultado do CompreFace e busca dados da pessoa"""
    if not compreface_result or 'result' not in compreface_result:
        log("Nenhum resultado de reconhecimento", "WARNING")
        return
    
    resultados = compreface_result['result']
    
    if not resultados:
        log("😞 Nenhuma face reconhecida na imagem", "WARNING")
        log(f"A pessoa não está cadastrada na base {CLIENTE_BUSCA.upper()}", "INFO")
        return
    
    log(f"🎯 {len(resultados)} face(s) detectada(s)", "SUCCESS")
    
    for i, resultado in enumerate(resultados, 1):
        log(f"\n--- RESULTADO {i} ---", "INFO")
        
        # Informações da detecção
        if 'box' in resultado:
            box = resultado['box']
            log(f"📍 Posição: ({box.get('x_min', 0)}, {box.get('y_min', 0)}) - ({box.get('x_max', 0)}, {box.get('y_max', 0)})", "INFO")
        
        # Verificar se há matches (pessoas reconhecidas)
        if 'subjects' in resultado and resultado['subjects']:
            melhor_match = resultado['subjects'][0]  # Primeiro é o melhor match
            
            subject_name = melhor_match.get('subject', '')
            similarity = melhor_match.get('similarity', 0)
            
            log(f"🎯 PESSOA RECONHECIDA!", "SUCCESS")
            log(f"   Confiança: {similarity:.2%}", "SUCCESS")
            log(f"   Subject ID: {subject_name}", "INFO")
            
            # Extrair ID real (remover prefixo do cliente)
            if subject_name.startswith(f"{CLIENTE_BUSCA}_"):
                person_id = subject_name.replace(f"{CLIENTE_BUSCA}_", "")
                log(f"   ID extraído: {person_id}", "INFO")
                
                # Buscar dados da pessoa - primeiro na cache local
                if person_id in pessoas_cliente:
                    pessoa = pessoas_cliente[person_id]
                    
                    log(f"\n👤 DADOS DA PESSOA:", "SUCCESS")
                    log(f"   Nome: {pessoa['name']}", "SUCCESS")
                    log(f"   Email: {pessoa['email']}", "SUCCESS")
                    log(f"   Telefone: {pessoa['phone']}", "SUCCESS")
                    log(f"   Cliente: {CLIENTE_BUSCA.upper()}", "SUCCESS")
                    log(f"   ID: {person_id}", "INFO")
                else:
                    # Busca direta na API como fallback
                    log(f"   Buscando na API...", "INFO")
                    try:
                        resp = requests.get(f"{FACE_MANAGER_URL}/{CLIENTE_BUSCA}/persons/{person_id}")
                        if resp.status_code == 200:
                            pessoa = resp.json()
                            log(f"\n👤 DADOS DA PESSOA (via API):", "SUCCESS")
                            log(f"   Nome: {pessoa['name']}", "SUCCESS")
                            log(f"   Email: {pessoa['email']}", "SUCCESS")
                            log(f"   Telefone: {pessoa['phone']}", "SUCCESS")
                            log(f"   Cliente: {CLIENTE_BUSCA.upper()}", "SUCCESS")
                            log(f"   ID: {person_id}", "INFO")
                        else:
                            log(f"⚠️ Pessoa não encontrada na API: {resp.status_code}", "WARNING")
                    except Exception as e:
                        log(f"⚠️ Erro ao consultar API: {e}", "ERROR")
            else:
                log(f"⚠️ Subject não pertence ao cliente {CLIENTE_BUSCA}", "WARNING")
        else:
            log(f"👤 Face detectada mas não reconhecida", "WARNING")
            log(f"   A pessoa não está cadastrada na base {CLIENTE_BUSCA.upper()}", "INFO")

def main():
    """Função principal"""
    log("🔍 FACE MANAGER - RECONHECIMENTO FACIAL", "INFO")
    log("=" * 60, "INFO")
    log(f"🎯 Cliente de busca: {CLIENTE_BUSCA.upper()}", "INFO")
    log(f"📷 Imagem: {IMAGEM_TESTE}", "INFO")
    print()
    
    # 1. Verificar se imagem existe
    if not verificar_imagem():
        return
    
    # 2. Obter pessoas do cliente
    pessoas_cliente = obter_pessoas_cliente()
    if not pessoas_cliente:
        log("Não há pessoas cadastradas no cliente ou erro de conexão", "ERROR")
        return
    
    print()
    
    # 3. Executar reconhecimento
    resultado = reconhecer_face()
    
    if resultado:
        print()
        # 4. Processar e exibir resultado
        processar_resultado(resultado, pessoas_cliente)
    
    print()
    log("🎉 Reconhecimento concluído!", "SUCCESS")
    
    # 5. Instruções para outros clientes
    print("\n💡 DICA:")
    print("   Para buscar em outro cliente, edite a variável CLIENTE_BUSCA")
    print("   Clientes disponíveis: carrefour, pao_de_acucar, rede_sonda")

if __name__ == "__main__":
    main() 