from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
import json
import os
import uuid
import base64
import shutil
from werkzeug.utils import secure_filename
from compreface_client import cadastrar_face, deletar_face
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_multi_cliente_face_manager_2024'

# 🌐 Tentar importar flask-cors, se falhar usar método manual
try:
    from flask_cors import CORS, cross_origin
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # 🚀 Produção: aceita qualquer origem
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True
        }
    })
    CORS_ENABLED = True
except ImportError:
    CORS_ENABLED = False
    print("⚠️ flask-cors não encontrado. Usando headers CORS manuais.")

# 🔧 Função para adicionar headers CORS manualmente
def add_cors_headers(response):
    """Adiciona headers CORS manualmente se flask-cors não estiver disponível"""
    if not CORS_ENABLED:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# 🚫 Função para adicionar headers anti-cache
def add_no_cache_headers(response):
    """Adiciona headers para evitar cache do navegador em rotas dinâmicas"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Aplicar headers CORS em todas as respostas
@app.after_request
def after_request(response):
    """Processa respostas adicionando headers necessários"""
    response = add_cors_headers(response)
    
    # Adicionar anti-cache para rotas específicas
    if request.endpoint in ['client_dashboard', 'editar', 'deletar', 'api_listar_pessoas']:
        response = add_no_cache_headers(response)
    
    return response

# Rota OPTIONS para preflight CORS
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    return add_cors_headers(response)

# 🔐 Configurações de Login (Hardcoded)
LOGIN_CREDENTIALS = {
    "email": "Rafa25santis@gmail.com",
    "password": "Rafa2503"
}

# 📋 Configurações Multi-Cliente
CLIENTS_FOLDER = "clients"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DEFAULT_CLIENT = "carrefour"

# 📁 Lista de clientes disponíveis
AVAILABLE_CLIENTS = {
    "carrefour": "Carrefour",
    "pao_de_acucar": "Pão de Açúcar", 
    "rede_sonda": "Rede Sonda",
    "buybye": "Buybye"
}

# =====================
# 🛠️ FUNÇÕES UTILITÁRIAS
# =====================

def get_client_path(cliente, subfolder=""):
    """Retorna o caminho para um cliente específico"""
    if subfolder:
        return os.path.join(CLIENTS_FOLDER, cliente, subfolder)
    return os.path.join(CLIENTS_FOLDER, cliente)

def get_metadata_file(cliente):
    """Retorna o caminho do arquivo metadata.json do cliente"""
    return os.path.join(get_client_path(cliente), "metadata.json")

def get_faces_folder(cliente):
    """Retorna o caminho da pasta faces do cliente"""
    return get_client_path(cliente, "faces")

def ensure_client_structure(cliente):
    """Garante que a estrutura de pastas do cliente existe"""
    client_folder = get_client_path(cliente)
    faces_folder = get_faces_folder(cliente)
    metadata_file = get_metadata_file(cliente)
    
    # Criar pastas se não existirem
    os.makedirs(faces_folder, exist_ok=True)
    
    # Criar metadata.json se não existir
    if not os.path.exists(metadata_file):
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)

def validate_client(cliente):
    """Valida se o cliente existe na lista de clientes disponíveis"""
    return cliente in AVAILABLE_CLIENTS

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def carregar_metadata(cliente):
    """Carrega os metadados do cliente específico"""
    ensure_client_structure(cliente)
    metadata_file = get_metadata_file(cliente)
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_metadata(cliente, metadata):
    """Salva os metadados do cliente específico"""
    ensure_client_structure(cliente)
    metadata_file = get_metadata_file(cliente)
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

# =====================
# 🔐 SISTEMA DE AUTENTICAÇÃO
# =====================

def login_required(f):
    """Decorator para proteger rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('🔒 Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================
# 🌐 ROTAS PRINCIPAIS (WEB)
# =====================

@app.route("/")
def home():
    """Página inicial - redireciona para cliente padrão ou login"""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Tela de login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if email == LOGIN_CREDENTIALS["email"] and password == LOGIN_CREDENTIALS["password"]:
            session['logged_in'] = True
            session['user_email'] = email
            flash('✅ Login realizado com sucesso! Bem-vindo ao Face Manager!', 'success')
            return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))
        else:
            flash('❌ Email ou senha incorretos. Tente novamente.', 'error')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout do usuário"""
    session.clear()
    flash('👋 Logout realizado com sucesso. Até logo!', 'info')
    return redirect(url_for('login'))

@app.route("/<cliente>/")
@login_required
def client_dashboard(cliente):
    """Dashboard principal do cliente"""
    if not validate_client(cliente):
        flash(f'❌ Cliente "{cliente}" não encontrado!', 'error')
        return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))
    
    try:
        metadata = carregar_metadata(cliente)
        client_display_name = AVAILABLE_CLIENTS[cliente]
        
        return render_template(
            "index.html", 
            pessoas=metadata,
            cliente_atual=cliente,
            cliente_nome=client_display_name,
            clientes_disponiveis=AVAILABLE_CLIENTS,
            session=session
        )
    except Exception as e:
        flash(f'❌ Erro ao carregar dados do cliente: {str(e)}', 'error')
        return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))

# Rota de cadastro via formulário web REMOVIDA (usar apenas API)
# @app.route("/<cliente>/cadastrar", methods=["POST"])
# @login_required
# def cadastrar(cliente):
#     """Cadastra nova pessoa para o cliente específico"""
#     # Esta funcionalidade foi removida da interface web
#     # Use a API REST: POST /api/<cliente>/persons
#     pass

@app.route("/<cliente>/editar/<subject_id>", methods=["POST"])
@login_required
def editar(cliente, subject_id):
    """Edita dados de uma pessoa do cliente específico"""
    if not validate_client(cliente):
        flash(f'❌ Cliente "{cliente}" não encontrado!', 'error')
        return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))
    
    try:
        metadata = carregar_metadata(cliente)
        
        if subject_id not in metadata:
            flash('❌ Pessoa não encontrada!', 'error')
            return redirect(url_for('client_dashboard', cliente=cliente))
        
        # Capturar nome antigo para comparação
        nome_antigo = metadata[subject_id]["name"]
        
        # Atualizar dados
        metadata[subject_id]["name"] = request.form["name"]
        metadata[subject_id]["email"] = request.form["email"]
        metadata[subject_id]["phone"] = request.form["phone"]
        
        salvar_metadata(cliente, metadata)
        client_name = AVAILABLE_CLIENTS[cliente]
        
        # Flash message mais detalhada
        flash(f'✅ SUCESSO: Dados de "{nome_antigo}" atualizados para "{metadata[subject_id]["name"]}" no {client_name}!', 'success')
        
        print(f"🔧 EDIÇÃO REALIZADA: {nome_antigo} -> {metadata[subject_id]['name']} no cliente {cliente}")
        
    except Exception as e:
        flash(f'❌ Erro ao editar: {str(e)}', 'error')
        print(f"🚨 ERRO NA EDIÇÃO: {str(e)}")
    
    # Redirect com parâmetro para forçar refresh
    return redirect(url_for('client_dashboard', cliente=cliente, _external=True, _scheme='http'))

@app.route("/<cliente>/deletar/<subject_id>", methods=["POST"])
@login_required
def deletar(cliente, subject_id):
    """Deleta uma pessoa do cliente específico"""
    if not validate_client(cliente):
        flash(f'❌ Cliente "{cliente}" não encontrado!', 'error')
        return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))
    
    try:
        metadata = carregar_metadata(cliente)
        
        if subject_id not in metadata:
            flash('❌ Pessoa não encontrada!', 'error')
            return redirect(url_for('client_dashboard', cliente=cliente))
        
        # Obter informações da pessoa
        pessoa = metadata[subject_id]
        nome = pessoa["name"]
        email = pessoa["email"]
        
        # Deletar da API do CompreFace (com prefixo do cliente)
        api_subject_id = f"{cliente}_{subject_id}"
        try:
            deletar_face(api_subject_id)
            print(f"✅ Face deletada da API CompreFace: {api_subject_id}")
        except Exception as api_error:
            print(f"⚠️ Aviso: Erro ao deletar da API CompreFace: {api_error}")
        
        # Deletar arquivo de imagem
        faces_folder = get_faces_folder(cliente)
        img_path = os.path.join(faces_folder, pessoa["image"])
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"🗑️ Imagem removida: {img_path}")
        
        # Remover dos metadados
        del metadata[subject_id]
        salvar_metadata(cliente, metadata)
        
        client_name = AVAILABLE_CLIENTS[cliente]
        flash(f'🗑️ DELETADO: "{nome}" ({email}) foi removido com sucesso do {client_name}!', 'success')
        
        print(f"🗑️ EXCLUSÃO REALIZADA: {nome} ({email}) removido do cliente {cliente}")
        
    except Exception as e:
        flash(f'❌ Erro ao deletar: {str(e)}', 'error')
        print(f"🚨 ERRO NA EXCLUSÃO: {str(e)}")
    
    # Redirect com parâmetro para forçar refresh
    return redirect(url_for('client_dashboard', cliente=cliente, _external=True, _scheme='http'))

@app.route("/<cliente>/faces/<filename>")
@login_required
def uploaded_file(cliente, filename):
    """Serve as imagens do cliente específico com headers anti-cache"""
    if not validate_client(cliente):
        return "Cliente não encontrado", 404
    
    faces_folder = get_faces_folder(cliente)
    response = send_from_directory(faces_folder, filename)
    
    # Adicionar headers para evitar cache de imagens
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = 'Wed, 01 Jan 1997 12:00:00 GMT'
    
    return response

@app.route("/trocar_cliente", methods=["POST"])
@login_required
def trocar_cliente():
    """Troca de cliente via dropdown"""
    novo_cliente = request.form.get("cliente", DEFAULT_CLIENT)
    if validate_client(novo_cliente):
        return redirect(url_for('client_dashboard', cliente=novo_cliente))
    else:
        flash(f'❌ Cliente "{novo_cliente}" inválido!', 'error')
        return redirect(url_for('client_dashboard', cliente=DEFAULT_CLIENT))

# =====================
# 🔗 ROTAS DE API (JSON)
# =====================

@app.route("/api/clients", methods=["GET"])
def api_listar_clientes():
    """API: Lista todos os clientes disponíveis"""
    return jsonify({
        "success": True,
        "total": len(AVAILABLE_CLIENTS),
        "clients": AVAILABLE_CLIENTS
    })

@app.route("/api/<cliente>/persons", methods=["GET"])
def api_listar_pessoas(cliente):
    """API: Lista todas as pessoas do cliente"""
    if not validate_client(cliente):
        return jsonify({"error": "Cliente não encontrado"}), 404
    
    try:
        metadata = carregar_metadata(cliente)
        return jsonify({
            "success": True,
            "client": cliente,
            "client_name": AVAILABLE_CLIENTS[cliente],
            "total": len(metadata),
            "persons": metadata
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/<cliente>/persons", methods=["POST"])
def api_cadastrar_pessoa(cliente):
    """API: Cadastra nova pessoa via JSON com imagem base64"""
    if not validate_client(cliente):
        return jsonify({"error": "Cliente não encontrado"}), 404
    
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ["name", "email", "phone", "image_base64"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        # Decodificar imagem base64
        try:
            image_data = base64.b64decode(data["image_base64"])
        except Exception:
            return jsonify({"error": "Imagem base64 inválida"}), 400
        
        # Gerar ID único e salvar imagem
        subject_id = str(uuid.uuid4())
        filename = secure_filename(f"{subject_id}.jpg")
        faces_folder = get_faces_folder(cliente)
        img_path = os.path.join(faces_folder, filename)
        
        with open(img_path, "wb") as f:
            f.write(image_data)
        
        # Cadastrar face na API do CompreFace
        api_subject_id = f"{cliente}_{subject_id}"
        compreface_response = cadastrar_face(img_path, api_subject_id)
        
        # Salvar metadados
        metadata = carregar_metadata(cliente)
        metadata[subject_id] = {
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
            "image": filename
        }
        salvar_metadata(cliente, metadata)
        
        return jsonify({
            "success": True,
            "message": f"Pessoa cadastrada com sucesso no {AVAILABLE_CLIENTS[cliente]}",
            "subject_id": subject_id,
            "api_subject_id": api_subject_id,
            "compreface_response": compreface_response,
            "person": metadata[subject_id]
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/<cliente>/persons/<subject_id>", methods=["GET"])
def api_obter_pessoa(cliente, subject_id):
    """API: Obtém dados de uma pessoa específica"""
    if not validate_client(cliente):
        return jsonify({"error": "Cliente não encontrado"}), 404
    
    try:
        metadata = carregar_metadata(cliente)
        
        if subject_id not in metadata:
            return jsonify({"error": "Pessoa não encontrada"}), 404
        
        return jsonify({
            "success": True,
            "client": cliente,
            "client_name": AVAILABLE_CLIENTS[cliente],
            "subject_id": subject_id,
            "person": metadata[subject_id]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/<cliente>/persons/<subject_id>", methods=["PUT"])
def api_editar_pessoa(cliente, subject_id):
    """API: Edita dados de uma pessoa"""
    if not validate_client(cliente):
        return jsonify({"error": "Cliente não encontrado"}), 404
    
    try:
        data = request.get_json()
        metadata = carregar_metadata(cliente)
        
        if subject_id not in metadata:
            return jsonify({"error": "Pessoa não encontrada"}), 404
        
        # Atualizar campos fornecidos
        if "name" in data:
            metadata[subject_id]["name"] = data["name"]
        if "email" in data:
            metadata[subject_id]["email"] = data["email"]
        if "phone" in data:
            metadata[subject_id]["phone"] = data["phone"]
        
        salvar_metadata(cliente, metadata)
        
        return jsonify({
            "success": True,
            "message": "Dados atualizados com sucesso",
            "person": metadata[subject_id]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/<cliente>/persons/<subject_id>", methods=["DELETE"])
def api_deletar_pessoa(cliente, subject_id):
    """API: Deleta uma pessoa"""
    if not validate_client(cliente):
        return jsonify({"error": "Cliente não encontrado"}), 404
    
    try:
        metadata = carregar_metadata(cliente)
        
        if subject_id not in metadata:
            return jsonify({"error": "Pessoa não encontrada"}), 404
        
        pessoa = metadata[subject_id]
        
        # Deletar da API do CompreFace
        api_subject_id = f"{cliente}_{subject_id}"
        try:
            deletar_face(api_subject_id)
        except Exception as api_error:
            print(f"⚠️ Aviso: Erro ao deletar da API CompreFace: {api_error}")
        
        # Deletar arquivo de imagem
        faces_folder = get_faces_folder(cliente)
        img_path = os.path.join(faces_folder, pessoa["image"])
        if os.path.exists(img_path):
            os.remove(img_path)
        
        # Remover dos metadados
        del metadata[subject_id]
        salvar_metadata(cliente, metadata)
        
        return jsonify({
            "success": True,
            "message": f"Pessoa {pessoa['name']} removida com sucesso"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================
# 🚀 INICIALIZAÇÃO
# =====================

if __name__ == "__main__":
    # Garantir que a estrutura de todos os clientes existe
    for cliente in AVAILABLE_CLIENTS.keys():
        ensure_client_structure(cliente)
    
    print("🎯 Face Manager Multi-Cliente")
    print("📁 Clientes disponíveis:")
    for cliente, nome in AVAILABLE_CLIENTS.items():
        print(f"   👉 /{cliente}/ - {nome}")
    print(f"\n🏠 Página inicial: https://facial-front.visionlabss.com/ (redireciona para {DEFAULT_CLIENT})")
    print("\n🔗 API Endpoints:")
    print("   👉 GET    /api/clients - Listar clientes")
    print("   👉 GET    /api/<cliente>/persons - Listar pessoas")
    print("   👉 POST   /api/<cliente>/persons - Cadastrar pessoa")
    print("   👉 GET    /api/<cliente>/persons/<id> - Obter pessoa")
    print("   👉 PUT    /api/<cliente>/persons/<id> - Editar pessoa")
    print("   👉 DELETE /api/<cliente>/persons/<id> - Deletar pessoa")
    print("🚀 Servidor iniciando...")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 