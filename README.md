# 🎯 Face Manager Multi-Cliente

Sistema de gerenciamento de faces com suporte multi-cliente, interface web e API REST completa.

## 🔥 **FUNCIONALIDADES IMPLEMENTADAS**

### ✅ **Sistema Principal**
- ✅ Interface web multi-cliente com Bootstrap
- ✅ Upload, edição e exclusão de pessoas
- ✅ Suporte a múltiplos clientes (Carrefour, Pão de Açúcar, Rede Sonda)
- ✅ Integração completa com CompreFace API
- ✅ Validação de arquivos e segurança

### ✅ **API REST Completa**
- ✅ `GET /api/clients` - Listar clientes
- ✅ `GET /api/<cliente>/persons` - Listar pessoas
- ✅ `POST /api/<cliente>/persons` - Cadastrar pessoa
- ✅ `GET /api/<cliente>/persons/<id>` - Obter pessoa
- ✅ `PUT /api/<cliente>/persons/<id>` - Editar pessoa
- ✅ `DELETE /api/<cliente>/persons/<id>` - Deletar pessoa

### ✅ **Upload em Lote**
- ✅ Script Python para upload automático
- ✅ Configuração via JSON
- ✅ Validação e logs detalhados
- ✅ Conversão automática base64

## 🚀 **COMO USAR**

### **1. Instalação**
```bash
pip install -r requirements.txt
```

### **2. Iniciar Face Manager**
```bash
python app.py
```

**Interface web:** http://localhost:5000

### **3. Upload em Lote**

#### **Configurar:**
```bash
python bulk_upload.py --setup
```

#### **Editar configuração:**
```json
{
  "client": "carrefour",
  "upload_folder": "upload_images",
  "persons": [
    {
      "image_file": "joao_silva.jpg",
      "name": "João Silva",
      "email": "joao.silva@carrefour.com.br",
      "phone": "+55 11 99999-1111"
    }
  ]
}
```

#### **Executar upload:**
```bash
python bulk_upload.py
```

### **4. Testar API**
```bash
python test_api.py
```

## 📡 **API REST - DOCUMENTAÇÃO**

### **Listar Clientes**
```bash
GET /api/clients
```

**Resposta:**
```json
{
  "success": true,
  "total": 3,
  "clients": {
    "carrefour": "Carrefour",
    "pao_de_acucar": "Pão de Açúcar",
    "rede_sonda": "Rede Sonda"
  }
}
```

### **Listar Pessoas de um Cliente**
```bash
GET /api/carrefour/persons
```

**Resposta:**
```json
{
  "success": true,
  "client": "carrefour",
  "total": 2,
  "persons": {
    "uuid-1": {
      "name": "João Silva",
      "email": "joao@carrefour.com.br",
      "phone": "+55 11 99999-1111",
      "image": "uuid-1.jpg"
    }
  }
}
```

### **Cadastrar Pessoa**
```bash
POST /api/carrefour/persons
Content-Type: application/json

{
  "name": "Maria Santos",
  "email": "maria@carrefour.com.br",
  "phone": "+55 11 99999-2222",
  "image_base64": "iVBORw0KGgoAAAANSUhEU..."
}
```

**Resposta:**
```json
{
  "success": true,
  "subject_id": "uuid-2",
  "message": "Pessoa cadastrada com sucesso"
}
```

### **Obter Pessoa**
```bash
GET /api/carrefour/persons/uuid-1
```

### **Editar Pessoa**
```bash
PUT /api/carrefour/persons/uuid-1
Content-Type: application/json

{
  "name": "João Silva Editado",
  "email": "joao.editado@carrefour.com.br"
}
```

### **Deletar Pessoa**
```bash
DELETE /api/carrefour/persons/uuid-1
```

## 🎨 **EXEMPLOS DE USO DA API**

### **Python - Cadastrar Pessoa**
```python
import requests
import base64

# Ler imagem e converter para base64
with open("foto.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

# Cadastrar pessoa
data = {
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "+55 11 99999-1111",
    "image_base64": image_base64
}

response = requests.post(
    "http://localhost:5000/api/carrefour/persons",
    json=data
)

print(response.json())
```

### **cURL - Listar Pessoas**
```bash
curl -X GET http://localhost:5000/api/carrefour/persons
```

### **cURL - Deletar Pessoa**
```bash
curl -X DELETE http://localhost:5000/api/carrefour/persons/uuid-1
```

## 📁 **ESTRUTURA DO PROJETO**

```
face_manager/
├── app.py                 # Aplicação Flask principal
├── compreface_client.py   # Cliente CompreFace API
├── requirements.txt       # Dependências Python
├── upload_config.json     # Configuração upload lote
├── bulk_upload.py         # Script upload em lote
├── test_api.py           # Testes da API
├── templates/
│   └── index.html        # Interface web
└── clients/              # Dados por cliente
    ├── carrefour/
    ├── pao_de_acucar/
    └── rede_sonda/
```

## 🔧 **CONFIGURAÇÃO CompreFace**

**Chave API:** `68896071-a604-44b7-beed-6d019f6f62fe`  
**URL Base:** `http://localhost:8000`

## 📊 **LOGS E MONITORAMENTO**

- Upload em lote: Logs detalhados com timestamp
- API: Validação automática de entrada
- Testes: Suite completa de validação
- Errors: Tratamento robusto de exceções

## 🎯 **PRÓXIMOS PASSOS OPCIONAIS**

- [ ] Dashboard com estatísticas
- [ ] Backup automático de dados
- [ ] Histórico de alterações
- [ ] Autenticação JWT
- [ ] Webhook notifications

## 👨‍💻 **AUTOR**

Sistema desenvolvido para gerenciamento multi-cliente de reconhecimento facial com CompreFace. 