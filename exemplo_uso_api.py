#!/usr/bin/env python3
"""
🚀 Face Manager - Exemplo de Uso da API
Demonstra como integrar com o Face Manager via API REST

Execute: python exemplo_uso_api.py
"""

import requests
import base64
import json
import os

# Configurações
API_BASE_URL = "http://localhost:5000/api"
CLIENTE = "carrefour"

def converter_imagem_para_base64(caminho_imagem):
    """Converte uma imagem para base64"""
    with open(caminho_imagem, "rb") as arquivo:
        return base64.b64encode(arquivo.read()).decode('utf-8')

def obter_imagem_teste():
    """Obtém uma imagem de teste com rosto real"""
    # Usar uma das imagens existentes como teste
    imagem_teste = "clients/carrefour/faces/lasaro.jpg"
    
    if os.path.exists(imagem_teste):
        try:
            return converter_imagem_para_base64(imagem_teste)
        except Exception as e:
            print(f"❌ Erro ao ler imagem de teste: {e}")
    
    return None

def exemplo_listar_clientes():
    """Exemplo: Listar todos os clientes disponíveis"""
    print("🔍 Listando clientes disponíveis...")
    
    response = requests.get(f"{API_BASE_URL}/clients")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['total']} clientes encontrados:")
        for cliente_id, nome in data['clients'].items():
            print(f"   📋 {cliente_id}: {nome}")
    else:
        print(f"❌ Erro: {response.status_code}")

def exemplo_cadastrar_pessoa():
    """Exemplo: Cadastrar uma nova pessoa"""
    print(f"\n📝 Cadastrando pessoa no cliente '{CLIENTE}'...")
    
    # Obter imagem de teste real
    image_base64 = obter_imagem_teste()
    if not image_base64:
        print("⚠️ Pulando exemplo de cadastro - sem imagem válida")
        return None
    
    # Dados da pessoa
    dados = {
        "name": "Exemplo API",
        "email": "exemplo@api.com",
        "phone": "+55 11 99999-0000",
        "image_base64": image_base64
    }
    
    response = requests.post(
        f"{API_BASE_URL}/{CLIENTE}/persons",
        json=dados,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Pessoa cadastrada com sucesso!")
        print(f"   ID: {result['subject_id']}")
        print(f"   Nome: {result['person']['name']}")
        return result['subject_id']
    else:
        error = response.json()
        print(f"❌ Erro ao cadastrar: {error.get('error', 'Erro desconhecido')}")
        return None

def exemplo_listar_pessoas():
    """Exemplo: Listar pessoas de um cliente"""
    print(f"\n👥 Listando pessoas do cliente '{CLIENTE}'...")
    
    response = requests.get(f"{API_BASE_URL}/{CLIENTE}/persons")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['total']} pessoas encontradas:")
        for person_id, person_data in data['persons'].items():
            print(f"   👤 {person_data['name']} ({person_data['email']})")
        return data['persons']
    else:
        print(f"❌ Erro: {response.status_code}")
        return {}

def exemplo_editar_pessoa(person_id):
    """Exemplo: Editar dados de uma pessoa"""
    print(f"\n✏️ Editando pessoa ID: {person_id}...")
    
    dados_edicao = {
        "name": "Exemplo API Editado",
        "email": "exemplo.editado@api.com"
    }
    
    response = requests.put(
        f"{API_BASE_URL}/{CLIENTE}/persons/{person_id}",
        json=dados_edicao,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Pessoa editada com sucesso!")
        print(f"   Novo nome: {result['person']['name']}")
    else:
        print(f"❌ Erro ao editar: {response.status_code}")

def exemplo_obter_pessoa(person_id):
    """Exemplo: Obter dados específicos de uma pessoa"""
    print(f"\n🔍 Obtendo dados da pessoa ID: {person_id}...")
    
    response = requests.get(f"{API_BASE_URL}/{CLIENTE}/persons/{person_id}")
    
    if response.status_code == 200:
        data = response.json()
        person = data['person']
        print(f"✅ Pessoa encontrada:")
        print(f"   Nome: {person['name']}")
        print(f"   Email: {person['email']}")
        print(f"   Telefone: {person['phone']}")
    else:
        print(f"❌ Erro: {response.status_code}")

def exemplo_deletar_pessoa(person_id):
    """Exemplo: Deletar uma pessoa"""
    print(f"\n🗑️ Deletando pessoa ID: {person_id}...")
    
    response = requests.delete(f"{API_BASE_URL}/{CLIENTE}/persons/{person_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Erro ao deletar: {response.status_code}")

def exemplo_cadastro_com_imagem_real():
    """Exemplo: Cadastrar pessoa com imagem real do arquivo"""
    print(f"\n📸 Exemplo de cadastro com imagem real...")
    
    # Verificar se existe uma imagem de exemplo
    imagem_exemplo = "upload_images/exemplo.jpg"
    
    if not os.path.exists(imagem_exemplo):
        print(f"⚠️  Para este exemplo, coloque uma imagem em: {imagem_exemplo}")
        return None
    
    # Converter imagem para base64
    try:
        image_base64 = converter_imagem_para_base64(imagem_exemplo)
    except Exception as e:
        print(f"❌ Erro ao ler imagem: {e}")
        return None
    
    # Dados da pessoa
    dados = {
        "name": "Pessoa com Foto Real",
        "email": "foto.real@example.com",
        "phone": "+55 11 88888-8888",
        "image_base64": image_base64
    }
    
    response = requests.post(
        f"{API_BASE_URL}/{CLIENTE}/persons",
        json=dados,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Pessoa com foto real cadastrada!")
        print(f"   ID: {result['subject_id']}")
        return result['subject_id']
    else:
        error = response.json()
        print(f"❌ Erro: {error.get('error', 'Erro desconhecido')}")
        return None

def main():
    """Executa todos os exemplos"""
    print("🚀 FACE MANAGER - EXEMPLOS DE USO DA API")
    print("=" * 60)
    
    try:
        # 1. Listar clientes
        exemplo_listar_clientes()
        
        # 2. Listar pessoas existentes
        exemplo_listar_pessoas()
        
        # 3. Cadastrar nova pessoa
        person_id = exemplo_cadastrar_pessoa()
        
        if person_id:
            # 4. Obter dados da pessoa
            exemplo_obter_pessoa(person_id)
            
            # 5. Editar pessoa
            exemplo_editar_pessoa(person_id)
            
            # 6. Obter dados atualizados
            exemplo_obter_pessoa(person_id)
            
            # 7. Deletar pessoa (opcional)
            confirmacao = input("\n🤔 Deletar pessoa de teste? (s/N): ").strip().lower()
            if confirmacao in ['s', 'sim', 'y', 'yes']:
                exemplo_deletar_pessoa(person_id)
        else:
            print("⏭️ Pulando testes que dependem de cadastro de pessoa")
        
        # 8. Exemplo com imagem real (opcional)
        print("\n" + "="*60)
        exemplo_cadastro_com_imagem_real()
        
        print("\n🎉 Exemplos concluídos!")
        print("\n💡 DICAS:")
        print("   - Modifique este script para suas necessidades")
        print("   - Use as funções como base para sua integração")
        print("   - Sempre valide as respostas da API")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão!")
        print("💡 Certifique-se que o Face Manager está rodando:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main() 