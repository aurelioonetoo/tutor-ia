import os
import uuid
import httpx
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq

app = FastAPI(title="Tutor IA - Lógica de Programação")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Configurações ────────────────────────────────────────
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY")
DB_API_URL    = "https://1nyfoa5i76.execute-api.us-east-2.amazonaws.com/default/API-PostgreeIEEE"

SYSTEM_PROMPT = """Você é um tutor especialista em Lógica de Programação para estudantes iniciantes.
Seu papel é GUIAR o aluno ao aprendizado, nunca entregar a resposta pronta.

Quando receber código ou uma dúvida do aluno, siga estas diretrizes:
1. Identifique tanto erros de sintaxe quanto falhas de raciocínio lógico.
2. Explique o problema em linguagem simples, sem jargão técnico. Use analogias do cotidiano.
3. Dê dicas que levem o aluno a descobrir a solução, nunca entregue pronta.
4. Explique brevemente o conceito de lógica de programação envolvido.
5. Ao final, sugira um pequeno exercício relacionado para reforçar o aprendizado.
6. Seja sempre positivo e motivador.

Responda sempre em Português do Brasil.
Use formatação Markdown quando útil (blocos de código com ```, listas, negrito)."""

# ── Modelos ──────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None   # ID da sessão do aluno

class ChatResponse(BaseModel):
    reply: str
    session_id: str

class HistoryResponse(BaseModel):
    session_id: str
    conversations: list

# ── Funções do banco de dados ────────────────────────────
async def salvar_conversa(session_id: str, pergunta: str, resposta: str):
    """Salva uma interação no PostgreSQL via API."""
    payload = {
        "action": "insert",
        "table": "conversas",
        "data": {
            "session_id": session_id,
            "pergunta": pergunta,
            "resposta": resposta,
            "criado_em": datetime.utcnow().isoformat()
        }
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.put(DB_API_URL, json=payload)
    except Exception as e:
        # Não interrompe o chat se o banco falhar
        print(f"[DB] Erro ao salvar conversa: {e}")

async def buscar_historico(session_id: str) -> list:
    """Busca o histórico de conversas de uma sessão."""
    params = {"action": "select", "table": "conversas", "session_id": session_id}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(DB_API_URL, params=params)
            data = resp.json()
            # Tenta pegar a lista de conversas — ajuste a chave se necessário
            return data.get("data", data.get("conversas", data.get("rows", [])))
    except Exception as e:
        print(f"[DB] Erro ao buscar histórico: {e}")
        return []

# ── Rotas ────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Nenhuma mensagem enviada.")

    # Gera ou reutiliza o ID da sessão
    session_id = req.session_id or str(uuid.uuid4())
    pergunta   = req.messages[-1].content

    try:
        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in req.messages:
            role = "user" if m.role == "user" else "assistant"
            messages.append({"role": role, "content": m.content})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao chamar a IA: {str(e)}")

    # Salva no banco em background (não trava o chat se falhar)
    await salvar_conversa(session_id, pergunta, reply)

    return ChatResponse(reply=reply, session_id=session_id)

@app.get("/historico/{session_id}", response_model=HistoryResponse)
async def historico(session_id: str):
    """Retorna o histórico de conversas de uma sessão."""
    conversas = await buscar_historico(session_id)
    return HistoryResponse(session_id=session_id, conversations=conversas)

@app.get("/health")
async def health():
    return {"status": "ok"}
