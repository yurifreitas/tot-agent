
# Agente Multi-Step com Tree of Thoughts + Azure OpenAI + MCP

Este projeto implementa um agente de atendimento multi-etapas que utiliza raciocínio simbólico com árvore de pensamentos (Tree of Thoughts), integrado com ferramentas externas via MCP (Modular Command Protocol), usando Azure OpenAI Vision para interpretar imagens.

---

## ✨ O que ele faz

- Classifica a intenção da mensagem do usuário (ex: mercado, dúvida, imagem)
- Expande a ideia com uma cadeia de raciocínio deliberado (ToT)
- Identifica comandos simbólicos como `#extract_info_from_image(...)`
- Executa os comandos via um servidor MCP externo
- Retorna a resposta final para o usuário

---

## 📦 Componentes

### 1. `multi_step_agent.py`
- Contém o agente principal (registrado via `@agent`)
- Usa `LangGraph` para raciocínio em árvore (intenção → subintenção → pensamento)
- Usa `ToolCallingAgent` + `ToolCollection.from_mcp(...)` para executar comandos MCP

### 2. `info_reader_server.py`
- Servidor MCP externo que define a ferramenta:
  - `extract_info_from_image(image_url: str)` → Usa Azure OpenAI Vision para extrair conteúdo da imagem
- Pode ser executado com:
  ```bash
  uv run info_reader_server.py
  ```

---

## 🚀 Como rodar

### 1. Inicie o servidor da ferramenta MCP

```bash
uv run info_reader_server.py
```

Ele deve exibir algo como:

```
✔ Registered tool: extract_info_from_image
```

---

### 2. Inicie o agente FastAPI

```bash
python main.py
```

---

### 3. Envie requisições

Use a rota `/runs` com este payload (via `curl`, Postman ou frontend):

```json
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "multi_step_agent",
    "input": [
      {
        "role": "user",
        "parts": [
          {
            "content": "Leia as infos dessa imagen: https://lh7-rt.googleusercontent.com/docsz/AD_4nXdpK2zHbFKJOysyQKHioIs0walFWRkF4ofSG4F3UoN9NaPHc4Rt-9suiJXy1RFMzo7VI31nSChlnn-KjWQHMbZfXB4jFiF5GmaslBa1BAY5ZPMOPpnn-qWGNR8vE-Ovk1LbeDVUeBVLUZGP1QPN1sQOafsK?key=EYqhVGgK_DvkU9gLMkh-5A"
          }
        ]
      }
    ]
  }'

```

---

## 🧠 Tecnologias

- ✅ [LangGraph](https://python.langchain.com/docs/langgraph/)
- ✅ [LangChain](https://www.langchain.com/)
- ✅ [Azure OpenAI Vision](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- ✅ [MCP](https://github.com/microsoft/acp)
- ✅ [smol-agents](https://github.com/microsoft/smol-agents)
- ✅ FastAPI + Uvicorn

---

## 🔐 Variáveis de ambiente `.env`

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_API_VERSION=
```

---

## 📂 Estrutura

```
.
├── multi_step_agent.py         # Agente principal
├── info_reader_server.py       # Tool MCP externa com Vision
├── main.py                     # Runner do agente FastAPI
├── .env                        # Variáveis sensíveis
```

---

## 🛠️ Exemplo de comando MCP

No fluxo, será gerado algo como:

```
#extract_info_from_image("https://api.exemplo.com/image.jpg")
```

Este comando será reconhecido e executado pela tool MCP, que retorna a resposta do Azure Vision.

---

## 🧩 Extensível para:

- Leitura de notas fiscais, documentos e imagens complexas
- Classificação de documentos
- Extração de múltiplos dados via visão
- Consulta de mercado, preço, saldo, etc.

---