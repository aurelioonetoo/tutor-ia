import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from groq import Groq

app = FastAPI(title="Tutor IA - Lógica de Programação")

app.mount("/static", StaticFiles(directory="static"), name="static")

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

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Nenhuma mensagem enviada.")
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
        err = str(e)
        if "api_key" in err.lower() or "auth" in err.lower():
            raise HTTPException(status_code=401, detail="API Key inválida. Verifique a variável GROQ_API_KEY.")
        raise HTTPException(status_code=500, detail=f"Erro ao chamar a IA: {err}")

    return ChatResponse(reply=reply)

@app.get("/health")
async def health():
    return {"status": "ok"}
