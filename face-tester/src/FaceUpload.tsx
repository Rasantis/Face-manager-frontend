import React, { useState } from 'react';

const FaceUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [selectedClient, setSelectedClient] = useState<string>('carrefour'); // Cliente selecionado pelo usuário

  // 🚀 CONFIGURAÇÕES DE PRODUÇÃO
  const COMPREFACE_URL = 'https://facial-back.visionlabss.com/api/v1/recognition/recognize';
  const FACE_MANAGER_URL = 'https://facial-front.visionlabss.com/api';
  const API_KEY = '52f25461-4ef8-4489-a10d-c2b076fc62a2';

  // 🏢 CLIENTES DISPONÍVEIS
  const AVAILABLE_CLIENTS = {
    'carrefour': 'Carrefour',
    'buybye': 'Buybye',
    'pao_de_acucar': 'Pão de Açúcar',
    'rede_sonda': 'Rede Sonda'
  };

  const logMessage = (msg: string) => {
    console.log(msg);
    setLog(prev => [...prev, msg]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      logMessage(`📁 Imagem selecionada: ${e.target.files[0].name}`);
    }
  };

  const handleClientChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedClient(e.target.value);
    logMessage(`🏢 Cliente selecionado: ${AVAILABLE_CLIENTS[e.target.value as keyof typeof AVAILABLE_CLIENTS]}`);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      logMessage('⚠️ Nenhuma imagem selecionada.');
      return;
    }

    logMessage('🚀 Enviando imagem para CompreFace...');
    logMessage(`🎯 Buscando na base de dados: ${AVAILABLE_CLIENTS[selectedClient as keyof typeof AVAILABLE_CLIENTS]}`);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const comprefaceResp = await fetch(COMPREFACE_URL, {
        method: 'POST',
        headers: {
          'x-api-key': API_KEY
        },
        body: formData
      });

      if (!comprefaceResp.ok) {
        logMessage(`❌ Erro no CompreFace: ${comprefaceResp.status}`);
        return;
      }

      const comprefaceData = await comprefaceResp.json();
      console.log('🧠 Resposta CompreFace:', comprefaceData);

      const result = comprefaceData.result?.[0];
      if (!result || !result.subjects || result.subjects.length === 0) {
        logMessage('😞 Nenhuma face reconhecida.');
        return;
      }

      const bestMatch = result.subjects[0];
      const subject = bestMatch.subject;
      const confidence = bestMatch.similarity;

      logMessage(`🎯 Face reconhecida: ${subject} (Confiança: ${(confidence * 100).toFixed(2)}%)`);

      // 🔧 USAR CLIENTE SELECIONADO PELO USUÁRIO
      const parts = subject.split('_');
      if (parts.length < 2) {
        logMessage(`❌ Formato de subject inválido: ${subject}`);
        return;
      }
      
      const clienteDetectado = parts[0]; // Cliente detectado pelo CompreFace
      const personId = parts.slice(1).join('_');
      
      logMessage(`🔍 CompreFace detectou: ${clienteDetectado} | ID: ${personId}`);
      logMessage(`🏢 Mas vamos buscar na base selecionada: ${selectedClient}`);

      // Validar se temos um ID válido
      if (!personId || personId.trim() === '') {
        logMessage(`❌ ID da pessoa inválido ou vazio`);
        return;
      }

      // 🎯 BUSCA INTELIGENTE: Primeiro na empresa selecionada, depois na detectada
      const trySearchInClient = async (clientToSearch: string, isOriginalClient: boolean = false) => {
        const apiUrl = `${FACE_MANAGER_URL}/${clientToSearch}/persons/${personId}`;
        logMessage(`📡 ${isOriginalClient ? 'Tentando' : 'Buscando'} em: ${apiUrl}`);
        
        try {
          const pessoaResp = await fetch(apiUrl, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            mode: 'cors'
          });

          if (pessoaResp.ok) {
            const pessoa = await pessoaResp.json();
            console.log('👤 Dados da pessoa:', pessoa);

            // Verificar se a resposta tem os dados esperados
            if (pessoa.success && pessoa.person) {
              const p = pessoa.person;
              logMessage(`✅ Pessoa encontrada no ${AVAILABLE_CLIENTS[clientToSearch as keyof typeof AVAILABLE_CLIENTS]}!`);
              logMessage(`👤 Nome: ${p.name}`);
              logMessage(`📧 Email: ${p.email}`);
              logMessage(`📱 Telefone: ${p.phone}`);
              return true;
            } else if (pessoa.person) {
              const p = pessoa.person;
              logMessage(`✅ Pessoa: ${p.name} | Email: ${p.email} | Telefone: ${p.phone}`);
              return true;
            } else if (pessoa.name) {
              logMessage(`✅ Pessoa: ${pessoa.name} | Email: ${pessoa.email} | Telefone: ${pessoa.phone}`);
              return true;
            } else {
              logMessage(`⚠️ Resposta em formato inesperado: ${JSON.stringify(pessoa)}`);
              return true;
            }
          } else {
            if (!isOriginalClient) {
              const errorText = await pessoaResp.text();
              logMessage(`❌ Erro ${pessoaResp.status}: ${errorText}`);
            }
            return false;
          }
        } catch (fetchError: any) {
          if (!isOriginalClient) {
            logMessage(`❌ Erro ao buscar dados: ${fetchError.message}`);
          }
          return false;
        }
      };

      // 🔍 BUSCA INTELIGENTE: Primeira tentativa na empresa selecionada
      let found = await trySearchInClient(selectedClient, true);

      if (!found && clienteDetectado !== selectedClient) {
        // Se não encontrou na empresa selecionada, tenta na empresa detectada
        logMessage(`🤔 Pessoa não encontrada no ${AVAILABLE_CLIENTS[selectedClient as keyof typeof AVAILABLE_CLIENTS]}`);
        logMessage(`🔄 Tentando buscar no ${AVAILABLE_CLIENTS[clienteDetectado as keyof typeof AVAILABLE_CLIENTS]} (detectado pelo CompreFace)...`);
        
        found = await trySearchInClient(clienteDetectado, false);
        
        if (!found) {
          logMessage(`😞 Pessoa não encontrada em nenhuma base de dados`);
          logMessage(`💡 Dica: Talvez essa pessoa precise ser cadastrada primeiro`);
        }
      } else if (!found) {
        logMessage(`😞 Pessoa não encontrada no ${AVAILABLE_CLIENTS[selectedClient as keyof typeof AVAILABLE_CLIENTS]}`);
        logMessage(`💡 Dica: Talvez essa pessoa precise ser cadastrada primeiro`);
      }

    } catch (err) {
      console.error('Erro:', err);
      logMessage(`❌ Erro inesperado: ${err}`);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h2>🔍 Reconhecimento Facial</h2>
      
      {/* SELETOR DE CLIENTE */}
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f0f8ff', border: '1px solid #ddd', borderRadius: '5px' }}>
        <label htmlFor="client-select" style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
          🏢 Selecione a empresa para buscar:
        </label>
        <select 
          id="client-select"
          value={selectedClient} 
          onChange={handleClientChange}
          style={{ 
            padding: '8px 12px', 
            fontSize: '16px', 
            borderRadius: '4px', 
            border: '1px solid #ccc',
            minWidth: '200px'
          }}
        >
          {Object.entries(AVAILABLE_CLIENTS).map(([key, name]) => (
            <option key={key} value={key}>{name}</option>
          ))}
        </select>
      </div>

      {/* UPLOAD DE ARQUIVO */}
      <div style={{ marginBottom: '20px' }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button
          style={{ 
            marginLeft: '10px', 
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
          onClick={handleUpload}
        >
          🚀 Reconhecer Face
        </button>
      </div>

      {/* LOGS */}
      <div style={{ marginTop: '20px' }}>
        <h3>📋 Logs:</h3>
        <pre style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '15px', 
          borderRadius: '5px',
          border: '1px solid #dee2e6',
          maxHeight: '400px',
          overflowY: 'auto',
          fontSize: '14px'
        }}>
          {log.map((msg, idx) => (
            <div key={idx} style={{ marginBottom: '5px' }}>{msg}</div>
          ))}
        </pre>
      </div>
    </div>
  );
};

export default FaceUpload;
