import pandas as pd
import json

# Caminho do arquivo Excel exportado pelo cliente
excel_path = "login_foto.xlsx"

# Carrega os dados da planilha
df = pd.read_excel(excel_path)

# Lista de pessoas no formato esperado
persons = []

for _, row in df.iterrows():
    id_login = row['id_login']
    image_file = row['foto']  # Nome da imagem
    name = f"login_{id_login}"  # Nome baseado no ID
    email = f"login{id_login}@buybye.com.br"  # Email fictício
    phone = f"+55 11 99999-{str(id_login)[-4:]}"  # Telefone fictício

    persons.append({
        "image_file": image_file,
        "name": name,
        "email": email,
        "phone": phone
    })

# Estrutura final do JSON
data = {
    "client": "buybye",
    "upload_folder": "upload_images",
    "persons": persons
}

# Caminho de saída do JSON
json_output_path = "buybye_faces.json"

# Salva o JSON no disco
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ JSON salvo em: {json_output_path}")
