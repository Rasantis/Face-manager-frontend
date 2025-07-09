import requests

# Configurações da API do CompreFace
API_KEY = "52f25461-4ef8-4489-a10d-c2b076fc62a2"
RECOGNITION_URL = "https://facial-back.visionlabss.com/api/v1/recognition/faces"
HEADERS = {"x-api-key": API_KEY}

def cadastrar_face(img_path, subject_id):
    """Envia uma imagem para cadastrar no CompreFace"""
    with open(img_path, "rb") as f:
        files = {"file": f}
        response = requests.post(
            f"{RECOGNITION_URL}?subject={subject_id}",
            headers=HEADERS,
            files=files
        )
    
    print(f"📥 [CADASTRO] Status: {response.status_code}")
    print(f"📥 [CADASTRO] Resposta: {response.text}")
    response.raise_for_status()
    return response.json()

def deletar_face(subject_id):
    """Deleta todas as faces vinculadas ao subject"""
    response = requests.delete(
        f"{RECOGNITION_URL}?subject={subject_id}",
        headers=HEADERS
    )
    
    print(f"🗑️ [DELETE] Subject: {subject_id} - Status: {response.status_code}")
    response.raise_for_status()
    return response.json()

def reconhecer_face(img_path, cliente):
    """
    Envia uma imagem para reconhecer a pessoa.
    Aplica filtro de subject pelo nome do cliente (ex: 'carrefour_').
    """
    prefixo_subject = f"{cliente}_"  # Importante: prefixo que restringe ao cliente

    with open(img_path, "rb") as f:
        files = {
            "file": f,
            "subject": (None, prefixo_subject)  # <- ESSENCIAL para filtrar
        }
        response = requests.post(
            f"{RECOGNITION_URL}/recognize",  # endpoint de reconhecimento
            headers=HEADERS,
            files=files
        )

    print(f"🔍 [RECONHECIMENTO] Enviando imagem para CompreFace...")
    print(f"📦 [RECONHECIMENTO] Subject prefixo: {prefixo_subject}")
    print(f"📊 [RECONHECIMENTO] Status: {response.status_code}")
    print(f"📨 [RECONHECIMENTO] Resposta: {response.text}")

    response.raise_for_status()
    return response.json()