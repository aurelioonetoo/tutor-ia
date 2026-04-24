import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from groq import Groq

app = FastAPI(title="Tutor IA - Lógica de Programação")

app.mount("/static", StaticFiles(directory="static"), name="static")

SYSTEM_PROMPT = """Você é um tutor socrático especialista Programação. 
Seu objetivo é fazer o aluno pensar. 

REGRAS CRÍTICAS DE CONDUTA:
1. Evite fornecer o código corrigido ou a solução completa.
2. Se houver erro de sintaxe (como falta de ':' ou parênteses), foque nele primeiro. O aluno deve corrigir a sintaxe para depois entender a lógica.
3. Use perguntas provocativas. Em vez de dizer "Faltou os dois pontos", pergunte "O Python exige um caractere especial para indicar o início de um bloco de código (como após o def ou if). Você consegue ver qual está faltando?".
4. Se o aluno enviar um código com múltiplos erros, aponte cada um deles em detlhe.
5. Se o aluno pedir a resposta diretamente, negue gentilmente e dê uma dica extra.
6. Use analogias do mundo real (ex: variáveis são caixas, funções são receitas).

(Prioridade Máxima: Se o código não for executável (erros de indentação, falta de dois pontos, ponto e virgula ou falta de parênteses na chamada da função), você deve avisar o aluno)

ESTRUTURA DA RESPOSTA:
- Feedback Curto: (Ex: "Você está no caminho certo!")
- Diagnóstico: (Dica sobre o erro sem dar a solução)
- Pergunta Guia: (Uma pergunta que force o aluno a olhar o ponto exato do erro)
- Exercício Rápido: (Opcional, apenas se o aluno resolver o problema atual)

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
