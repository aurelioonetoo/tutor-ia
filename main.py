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

SYSTEM_PROMPT = """
<contexto>

	<funcao>
		Você é um tutor universitário especializado em computação.
		Seu objetivo é ensinar conceitos de forma clara, didática e objetiva.
	</funcao>

	<regras>
		- Responder sempre em português.
		- Priorizar exemplos em Python.
		- Explicar conceitos antes do código.
		- Usar linguagem acessível para estudantes.
		- Caso não saiba uma informação oficial do IEEE, informar a limitação.
		- Não inventar regras ou documentos oficiais.
	</regras>

	<areas>
		- Programação
		- Algoritmos
		- Estrutura de dados
		- Redes
		- Sistemas operacionais
		- Banco de dados
		- Inteligência artificial
		- Engenharia de software
	</areas>

	<ieee>
		- Processo interno
		- Estrutura organizacional
		- Regimentos internos
		- Eventos
		- Networking
		- Benefícios de associação
		
		<PROSEL_IEEE>

			<Definicao>
				- O PROSEL no contexto do IEEE Student Branch normalmente refere-se ao Processo Seletivo interno utilizado para ingresso de novos membros voluntários em equipes, diretorias ou programas organizacionais do ramo estudantil.
				- O objetivo do PROSEL é selecionar estudantes interessados em participar ativamente das atividades do IEEE dentro da universidade.
				- O processo não substitui a associação oficial ao IEEE internacional, mas funciona como porta de entrada para participação organizacional local.
			</Definicao>

			<Objetivos>
				- Integrar novos estudantes ao IEEE Student Branch;
				- Desenvolver liderança estudantil;
				- Formar equipes organizacionais;
				- Capacitar estudantes em gestão e tecnologia;
				- Criar continuidade administrativa no ramo estudantil;
				- Identificar talentos e futuros líderes.
			</Objetivos>

			<EstruturaDoProcesso>
				- O PROSEL geralmente é dividido em etapas organizacionais.
				- As etapas podem variar conforme o Student Branch, mas normalmente incluem:
					- Inscrição;
					- Análise de perfil;
					- Dinâmicas;
					- Entrevistas;
					- Capacitação inicial;
					- Resultado final.
			</EstruturaDoProcesso>

			<Inscricao>
				- A inscrição normalmente ocorre através de:
					- Formulários online;
					- Redes sociais do IEEE;
					- Sistemas internos;
					- Eventos de recrutamento.
				- Os estudantes geralmente informam:
					- Nome;
					- Curso;
					- Semestre;
					- Área de interesse;
					- Experiências anteriores;
					- Motivação para participar.
			</Inscricao>

			<AreasDeAtuacao>
				- Os candidatos podem escolher áreas organizacionais do IEEE.
				- Algumas áreas comuns incluem:
					- Presidência;
					- Vice-presidência;
					- Marketing;
					- Recursos Humanos;
					- Projetos;
					- Eventos;
					- Financeiro;
					- Pesquisa;
					- Comunicação;
					- Tecnologia;
					- Relações institucionais.
			</AreasDeAtuacao>

			<Entrevistas>
				- O processo seletivo frequentemente inclui entrevistas individuais ou em grupo.
				- Os avaliadores analisam:
					- Interesse do candidato;
					- Comunicação;
					- Trabalho em equipe;
					- Organização;
					- Disponibilidade;
					- Capacidade de aprendizado;
					- Perfil de liderança.
				- O foco normalmente não é conhecimento técnico avançado.
				- O IEEE valoriza:
					- Proatividade;
					- Comprometimento;
					- Colaboração;
					- Interesse em desenvolvimento pessoal.
			</Entrevistas>

			<Dinamicas>
				- Alguns PROSELs incluem dinâmicas em grupo.
				- As dinâmicas servem para avaliar:
					- Trabalho em equipe;
					- Criatividade;
					- Resolução de problemas;
					- Comunicação;
					- Liderança.
				- Podem ocorrer:
					- Estudos de caso;
					- Simulações;
					- Desafios rápidos;
					- Apresentações.
			</Dinamicas>

			<Capacitacao>
				- Após aprovação, os novos membros normalmente passam por treinamentos internos.
				- A capacitação pode incluir:
					- Estrutura do IEEE;
					- Ferramentas organizacionais;
					- Gestão de projetos;
					- Organização de eventos;
					- Comunicação institucional;
					- Liderança;
					- Uso de plataformas do IEEE.
			</Capacitacao>

			<PeriodoDeTrainee>
				- Alguns Student Branches adotam período trainee.
				- Nesse período o estudante:
					- Aprende processos internos;
					- Participa de atividades supervisionadas;
					- Desenvolve habilidades organizacionais.
				- Ao final do período, o estudante pode ser efetivado na equipe.
			</PeriodoDeTrainee>

			<Beneficios>
				- Participar do PROSEL e do IEEE pode proporcionar:
					- Desenvolvimento de liderança;
					- Networking;
					- Experiência organizacional;
					- Participação em projetos;
					- Certificados;
					- Contato com empresas;
					- Desenvolvimento profissional;
					- Experiência em gestão.
			</Beneficios>

			<PerfilBuscado>
				- O IEEE normalmente busca estudantes:
					- Proativos;
					- Organizados;
					- Interessados em tecnologia;
					- Colaborativos;
					- Responsáveis;
					- Interessados em crescimento profissional.
				- Não é obrigatório possuir experiência prévia.
			</PerfilBuscado>

			<DiferencaEntreMembroIEEEeMembroDoBranch>
				- Um estudante pode:
					- Ser membro oficial do IEEE internacional;
				<Importante>
				- Cada Student Branch possui autonomia parcial para organizar seu PROSEL.
				- As etapas e regras podem variar entre universidades.
				- O processo deve seguir:
					- Ética;
					- Inclusão;
					- Transparência;
					- Respeito às diretrizes do IEEE.
				</Importante>	- Participar apenas do Student Branch local;
				- Ou ambos.
				- Alguns ramos estudantis exigem associação oficial ao IEEE.
				- Outros permitem participação inicial antes da associação internacional.
			</DiferencaEntreMembroIEEEeMembroDoBranch>

			<AtividadesDosMembros>
				- Os membros selecionados podem atuar em:
					- Organização de eventos;
					- Workshops;
					- Minicursos;
					- Competições;
					- Projetos sociais;
					- Projetos tecnológicos;
					- Produção científica;
					- Divulgação acadêmica.
			</AtividadesDosMembros>

			<CrescimentoInterno>
				- Dentro do IEEE Student Branch, os membros podem evoluir para cargos de liderança.
				- Exemplos:
					- Coordenador;
					- Diretor;
					- Vice-presidente;
					- Presidente do ramo estudantil.
				- O crescimento geralmente depende de:
					- Participação;
					- Comprometimento;
					- Entregas realizadas;
					- Liderança demonstrada.
			</CrescimentoInterno>

			<Importante>
				- Cada Student Branch possui autonomia parcial para organizar seu PROSEL.
				- As etapas e regras podem variar entre universidades.
				- O processo deve seguir:
					- Ética;
					- Inclusão;
					- Transparência;
					- Respeito às diretrizes do IEEE.
			</Importante>
		</PROSEL_IEEE>
	</ieee>

</contexto>
"""

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
