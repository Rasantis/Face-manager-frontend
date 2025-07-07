import requests

# Configurações da API do CompreFace
API_KEY = "52f25461-4ef8-4489-a10d-c2b076fc62a2"
RECOGNITION_URL = "https://facial-back.visionlabss.com/api/v1/recognition/faces"
HEADERS = {"x-api-key": API_KEY}

def cadastrar_face(img_path, subject_id):
    """
    Envia uma imagem para a API do CompreFace vinculando-a ao subject_id.
    """
    with open(img_path, "rb") as f:
        files = {"file": f}
        response = requests.post(
            f"{RECOGNITION_URL}?subject={subject_id}",
            headers=HEADERS,
            files=files
        )
    
    print(f"🔁 Status code: {response.status_code}")
    print(f"📨 Response: {response.text}")
    response.raise_for_status()
    return response.json()

def deletar_face(subject_id):
    """
    Remove todas as faces de um subject do CompreFace.
    """
    response = requests.delete(
        f"{RECOGNITION_URL}?subject={subject_id}",
        headers=HEADERS
    )
    
    print(f"🗑️ Deletando subject {subject_id} - Status: {response.status_code}")
    response.raise_for_status()
    return response.json() 