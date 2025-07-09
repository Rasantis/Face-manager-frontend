#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar o reconhecimento facial completo
"""

import requests
import json

# Configurações
COMPREFACE_URL = "https://facial-back.visionlabss.com/api/v1/recognition/recognize"
FACE_MANAGER_URL = "https://facial-front.visionlabss.com/api"
API_KEY = "52f25461-4ef8-4489-a10d-c2b076fc62a2"
TEST_IMAGE = "teste_faces_bulk/lasaro4.jpg"

def test_recognition():
    print("🧪 Teste de Reconhecimento Facial\n")
    
    # 1. Testar CompreFace
    print("1️⃣ Testando CompreFace...")
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': f}
            headers = {'x-api-key': API_KEY}
            
            response = requests.post(COMPREFACE_URL, files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ CompreFace respondeu com sucesso!")
                
                if data.get('result') and data['result'][0].get('subjects'):
                    subject = data['result'][0]['subjects'][0]['subject']
                    similarity = data['result'][0]['subjects'][0]['similarity']
                    print(f"   📷 Face reconhecida: {subject}")
                    print(f"   🎯 Confiança: {similarity * 100:.2f}%")
                    
                    # 2. Testar Face Manager
                    parts = subject.split('_')
                    if len(parts) >= 2:
                        cliente = parts[0]
                        person_id = '_'.join(parts[1:])
                        
                        print(f"\n2️⃣ Testando Face Manager...")
                        print(f"   🏢 Cliente: {cliente}")
                        print(f"   🆔 ID: {person_id}")
                        
                        api_url = f"{FACE_MANAGER_URL}/{cliente}/persons/{person_id}"
                        print(f"   🔗 URL: {api_url}")
                        
                        try:
                            person_response = requests.get(api_url)
                            
                            if person_response.status_code == 200:
                                person_data = person_response.json()
                                print("   ✅ Dados encontrados!")
                                
                                # Tentar diferentes formatos de resposta
                                if 'person' in person_data:
                                    p = person_data['person']
                                    print(f"   👤 Nome: {p.get('name')}")
                                    print(f"   📧 Email: {p.get('email')}")
                                    print(f"   📱 Telefone: {p.get('phone')}")
                                elif 'name' in person_data:
                                    print(f"   👤 Nome: {person_data.get('name')}")
                                    print(f"   📧 Email: {person_data.get('email')}")
                                    print(f"   📱 Telefone: {person_data.get('phone')}")
                                else:
                                    print(f"   ⚠️ Formato inesperado: {json.dumps(person_data, indent=2)}")
                            else:
                                print(f"   ❌ Erro {person_response.status_code}: {person_response.text}")
                                
                        except Exception as e:
                            print(f"   ❌ Erro ao buscar dados: {str(e)}")
                    else:
                        print(f"   ❌ Formato de subject inválido: {subject}")
                else:
                    print("   😞 Nenhuma face reconhecida")
            else:
                print(f"❌ Erro no CompreFace: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ Arquivo de teste não encontrado: {TEST_IMAGE}")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    test_recognition() 