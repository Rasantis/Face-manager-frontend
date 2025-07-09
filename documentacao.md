
# 📘 Documentação Técnica - Face Manager Frontend

## 📌 Visão Geral
O **Face Manager Frontend** é uma interface em Flask para facilitar a **gestão de reconhecimento facial** usando a API do **CompreFace**. Ele permite:
- Cadastrar pessoas (com nome, e-mail e telefone)
- Enviar imagens e associar rostos via CompreFace
- Reconhecer faces e buscar os dados relacionados
- Interface moderna e simplificada para uso em mercado autônomo

## 🧱 Estrutura do Projeto

```
Face-manager-frontend/
├── app.py
├── compreface_client.py
├── reconhecer_face.py
├── templates/
├── upload_images/
├── clients/
├── requirements.txt
├── venv/
└── facial-frontend.service
```

## ⚙️ Tecnologias Utilizadas
- **Python 3.10+**
- **Flask**
- **Gunicorn**
- **Nginx**
- **Certbot + Let's Encrypt**
- **Ubuntu Linux em VM GCP**

## 🚀 Setup e Deploy

### 🔧 Clonagem do Projeto
```bash
git clone https://github.com/Rasantis/Face-manager-frontend.git
cd Face-manager-frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🔧 Execução Local
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 🌐 Configuração de Domínio e HTTPS
- Configurar DNS `facial-front.visionlabss.com` apontando para IP da VM
- Gerar certificado SSL:
```bash
sudo certbot --nginx -d facial-front.visionlabss.com
```

## 🧩 Configuração de Produção

### 🛠️ Serviço Systemd
Arquivo `/etc/systemd/system/facial-frontend.service`:

```ini
[Unit]
Description=Face Manager Frontend (Gunicorn)
After=network.target

[Service]
User=rafaelsantis
Group=rafaelsantis
WorkingDirectory=/home/rafaelsantis/Face-manager-frontend
Environment="PATH=/home/rafaelsantis/Face-manager-frontend/venv/bin"
ExecStart=/home/rafaelsantis/Face-manager-frontend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Comandos úteis:
```bash
sudo systemctl start facial-frontend
sudo systemctl restart facial-frontend
sudo systemctl status facial-frontend
sudo systemctl enable facial-frontend
```

### 🌐 Nginx como Proxy
Arquivo `/etc/nginx/sites-available/facial_front`:
```nginx
server {
    listen 80;
    server_name facial-front.visionlabss.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Symlink e reload:
```bash
sudo ln -s /etc/nginx/sites-available/facial_front /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🧪 Testes
Rodar:
```bash
python reconhecer_face.py
```

## 🧠 Comunicação
```
Usuário → Flask → CompreFace → Busca metadados
```

## 🔁 Atualização em Produção
```bash
gcloud compute ssh cf-frontend --zone us-central1-a
cd ~/Face-manager-frontend
git pull origin main
sudo systemctl restart facial-frontend
```

## 🛠️ Problemas Comuns

| Problema             | Solução                          |
|----------------------|----------------------------------|
| Frontend fora do ar  | Restart com `systemctl`          |
| 502 Bad Gateway      | Reinicie gunicorn + nginx        |
| Porta 5000 bloqueada | Verifique o proxy no Nginx       |
| DNS não resolve      | Corrija A Record no GoDaddy      |
| API CompreFace off   | Cheque `compreface_client.py`    |

## ✅ Conclusão
Solução pronta para produção com deploy limpo, HTTPS, e manutenção simples.
