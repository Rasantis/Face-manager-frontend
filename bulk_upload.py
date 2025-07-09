#!/usr/bin/env python3
"""
🚀 Face Manager - Upload em Lote de Imagens
Sistema para upload automático de uma pasta de imagens para o Face Manager

Como usar:
1. Configure o arquivo upload_config.json com os dados das pessoas
2. Coloque as imagens na pasta especificada (padrão: upload_images/)
3. Execute: python bulk_upload.py

Autor: Face Manager Multi-Cliente
"""

import json
import os
import base64
import requests
import sys
from datetime import datetime

# =====================
# 🔧 CONFIGURAÇÕES
# =====================

API_BASE_URL = "https://facial-front.visionlabss.com/api"
CONFIG_FILE = "upload_config.json"
DEFAULT_UPLOAD_FOLDER = "upload_images"

# Extensões de imagem suportadas
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

class BulkUploader:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = None
        self.upload_folder = None
        self.client = None
        self.stats = {
            "total": 0,
            "success": 0,
            "errors": 0,
            "skipped": 0
        }
        self.log(f"🔧 Iniciando BulkUploader para o cliente: {self.client}")
        
    def log(self, message, level="INFO"):
        """Função de log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "SKIP": "⏭️ "
        }
        print(f"[{timestamp}] {prefix.get(level, '')} {message}")
    
    def carregar_config(self):
        """Carrega configuração do arquivo JSON"""
        try:
            if not os.path.exists(self.config_file):
                self.log(f"Arquivo de configuração não encontrado: {self.config_file}", "ERROR")
                return False
            
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # Validar configuração
            required_keys = ["client", "persons"]
            for key in required_keys:
                if key not in self.config:
                    self.log(f"Chave obrigatória '{key}' não encontrada na configuração", "ERROR")
                    return False
            
            self.client = self.config["client"]
            self.upload_folder = self.config.get("upload_folder", DEFAULT_UPLOAD_FOLDER)
            
            self.log(f"Configuração carregada: Cliente '{self.client}', {len(self.config['persons'])} pessoas")
            return True
            
        except json.JSONDecodeError as e:
            self.log(f"Erro ao decodificar JSON: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erro ao carregar configuração: {e}", "ERROR")
            return False
    
    def validar_estrutura(self):
        """Valida se a pasta de upload existe e contém imagens"""
        if not os.path.exists(self.upload_folder):
            self.log(f"Pasta de upload não encontrada: {self.upload_folder}", "ERROR")
            self.log(f"Crie a pasta e coloque as imagens nela", "INFO")
            return False
        
        # Listar imagens na pasta
        images = []
        for file in os.listdir(self.upload_folder):
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                images.append(file)
        
        if not images:
            self.log(f"Nenhuma imagem encontrada na pasta {self.upload_folder}", "WARNING")
            self.log(f"Extensões suportadas: {', '.join(SUPPORTED_EXTENSIONS)}", "INFO")
            return False
        
        self.log(f"Encontradas {len(images)} imagens na pasta {self.upload_folder}")
        return True
    
    def testar_conexao(self):
        """Testa conexão com a API"""
        try:
            response = requests.get(f"{API_BASE_URL}/clients", timeout=10)
            if response.status_code == 200:
                self.log("Conexão com Face Manager API: OK")
                return True
            else:
                self.log(f"API retornou status {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Erro de conexão com API: {e}", "ERROR")
            self.log("Certifique-se que o Face Manager está rodando (python app.py)", "INFO")
            return False
    
    def image_to_base64(self, image_path):
        """Converte imagem para base64"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                return base64_string
        except Exception as e:
            self.log(f"Erro ao converter imagem {image_path}: {e}", "ERROR")
            return None
    
    def upload_pessoa(self, pessoa_config):
        """Faz upload de uma pessoa para a API"""
        image_file = pessoa_config.get("image_file")
        name = pessoa_config.get("name")
        email = pessoa_config.get("email")
        phone = pessoa_config.get("phone")
        
        # Validar dados obrigatórios
        if not all([image_file, name, email, phone]):
            self.log(f"Dados incompletos para {name or 'pessoa'}: campos obrigatórios faltando", "ERROR")
            return False
        
        # Verificar se arquivo de imagem existe
        image_path = os.path.join(self.upload_folder, image_file)
        if not os.path.exists(image_path):
            self.log(f"Imagem não encontrada: {image_file}", "ERROR")
            return False
        
        # Converter imagem para base64
        base64_image = self.image_to_base64(image_path)
        if not base64_image:
            return False
        
        # Preparar dados para API
        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "image_base64": base64_image
        }
        
        # Fazer requisição
        try:
            url = f"{API_BASE_URL}/{self.client}/persons"
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 201:
                self.log(f"✅ {name} cadastrado com sucesso", "SUCCESS")
                return True
            else:
                # Melhor tratamento de erro
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Erro desconhecido")
                    
                    # Mensagens específicas para erros comuns
                    if "More than one face" in str(error_msg):
                        self.log(f"❌ {name}: A imagem {image_file} contém MÚLTIPLAS FACES. Use uma imagem com apenas 1 face.", "ERROR")
                    elif "No face found" in str(error_msg):
                        self.log(f"❌ {name}: NENHUMA FACE detectada na imagem {image_file}. Verifique se é uma foto de rosto.", "ERROR")
                    elif "image_base64" in str(error_msg):
                        self.log(f"❌ {name}: Problema no formato da imagem {image_file}. Use JPG, PNG ou WEBP.", "ERROR")
                    else:
                        self.log(f"❌ {name}: {error_msg}", "ERROR")
                        
                except:
                    self.log(f"❌ {name}: Erro HTTP {response.status_code} - {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Erro de rede ao cadastrar {name}: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erro inesperado ao cadastrar {name}: {e}", "ERROR")
            return False
    
    def processar_upload(self):
        """Processa upload de todas as pessoas"""
        self.log("🚀 Iniciando upload em lote...")
        
        self.stats["total"] = len(self.config["persons"])
        
        for i, pessoa in enumerate(self.config["persons"], 1):
            self.log(f"[{i}/{self.stats['total']}] Processando {pessoa.get('name', 'pessoa')}")
            
            if self.upload_pessoa(pessoa):
                self.stats["success"] += 1
            else:
                self.stats["errors"] += 1
        
        # Relatório final
        self.log("📊 RELATÓRIO FINAL:")
        self.log(f"   Total de pessoas: {self.stats['total']}")
        self.log(f"   Sucessos: {self.stats['success']}")
        self.log(f"   Erros: {self.stats['errors']}")
        
        if self.stats["success"] > 0:
            self.log(f"🎉 Upload concluído! {self.stats['success']} pessoas cadastradas", "SUCCESS")
        
        if self.stats["errors"] > 0:
            self.log(f"⚠️  {self.stats['errors']} erros ocorreram durante o upload", "WARNING")
    
    def executar(self):
        """Execução principal do upload"""
        self.log("🎯 Face Manager - Upload em Lote")
        self.log("=" * 50)
        
        # 1. Carregar configuração
        if not self.carregar_config():
            return False
        
        # 2. Validar estrutura
        if not self.validar_estrutura():
            return False
        
        # 3. Testar conexão
        if not self.testar_conexao():
            return False
        
        # 4. Confirmar upload
        self.log(f"Pronto para upload:")
        self.log(f"   Cliente: {self.client}")
        self.log(f"   Pasta: {self.upload_folder}")
        self.log(f"   Pessoas: {len(self.config['persons'])}")
        
        resposta = input("\n🤔 Confirma o upload? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            self.log("Upload cancelado pelo usuário", "INFO")
            return False
        
        # 5. Processar upload
        self.processar_upload()
        return True

def criar_estrutura_exemplo():
    """Cria estrutura de exemplo para demonstração"""
    print("🔧 Criando estrutura de exemplo...")
    
    # Criar pasta de upload se não existir
    if not os.path.exists(DEFAULT_UPLOAD_FOLDER):
        os.makedirs(DEFAULT_UPLOAD_FOLDER)
        print(f"✅ Pasta criada: {DEFAULT_UPLOAD_FOLDER}")
    
    # Criar arquivo de configuração exemplo se não existir
    if not os.path.exists(CONFIG_FILE):
        config_exemplo = {
            "client": "carrefour",
            "upload_folder": DEFAULT_UPLOAD_FOLDER,
            "persons": [
                {
                    "image_file": "exemplo_pessoa1.jpg",
                    "name": "João Silva",
                    "email": "joao.silva@carrefour.com.br",
                    "phone": "+55 11 99999-1111"
                },
                {
                    "image_file": "exemplo_pessoa2.jpg",
                    "name": "Maria Santos",
                    "email": "maria.santos@carrefour.com.br",
                    "phone": "+55 11 99999-2222"
                }
            ]
        }
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_exemplo, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração exemplo criada: {CONFIG_FILE}")
    
    print("\n📝 PRÓXIMOS PASSOS:")
    print(f"1. Coloque suas imagens na pasta: {DEFAULT_UPLOAD_FOLDER}/")
    print(f"2. Edite o arquivo: {CONFIG_FILE}")
    print("3. Execute: python bulk_upload.py")

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        criar_estrutura_exemplo()
        return
    
    uploader = BulkUploader()
    
    try:
        uploader.executar()
    except KeyboardInterrupt:
        print("\n⏹️  Upload interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main() 