# 🧠 Tutor IA — Lógica de Programação
> Projeto 1 · Subgrupo de Inteligência Artificial · Prosel 2026.1 · IEEE Computer Society

Um tutor inteligente que usa IA para ensinar lógica de programação a estudantes iniciantes, fornecendo explicações didáticas, identificando erros lógicos (não só sintaxe) e sugerindo exercícios personalizados.

---

## 📁 Estrutura do Projeto

```
tutor-ia/
├── main.py              # Backend FastAPI
├── requirements.txt     # Dependências Python
├── README.md            # Este arquivo
└── static/
    └── index.html       # Frontend (interface de chat)
```

---

## ⚙️ Pré-requisitos

- Python 3.10 ou superior
- Uma **API Key da Anthropic** (gratuita para começar)
  → Crie em: https://console.anthropic.com/

---

## 🚀 Como rodar

### 1. Clone ou baixe o projeto

```bash
# Se estiver usando Git:
git clone <url-do-repositorio>
cd tutor-ia
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Linux / Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a API Key

**Linux / Mac:**
```bash
export ANTHROPIC_API_KEY="sk-ant-sua-chave-aqui"
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-sua-chave-aqui"
```

> 💡 Dica: para não precisar setar toda vez, crie um arquivo `.env` e use a biblioteca `python-dotenv`.

### 5. Inicie o servidor

```bash
uvicorn main:app --reload
```

### 6. Acesse no navegador

```
http://localhost:8000
```

---

## 🎯 Como usar

1. **Escreva sua dúvida** ou cole seu código na caixa de texto
2. O tutor irá **analisar e explicar** o problema em linguagem simples
3. Use a **barra lateral** para explorar tópicos como variáveis, condicionais e laços
4. Peça **exercícios** para praticar o que aprendeu
5. Use **Shift+Enter** para quebrar linha, **Enter** para enviar

---

## 🧩 Como funciona (por dentro)

```
Aluno digita mensagem
        ↓
    Frontend (index.html)
        ↓ POST /chat
    Backend (main.py / FastAPI)
        ↓ System Prompt + histórico
    API Anthropic (Claude)
        ↓ Resposta didática
    Frontend renderiza em Markdown
        ↓
    Aluno lê a explicação
```

O segredo está no **system prompt** em `main.py`, que instrui a IA a:
- Nunca dar a resposta direta
- Usar linguagem simples e analogias
- Sempre sugerir um exercício ao final
- Identificar erros de **lógica**, não só de sintaxe

---

## 🛠️ Tecnologias utilizadas

| Camada    | Tecnologia         | Por quê?                              |
|-----------|--------------------|---------------------------------------|
| IA        | Claude (Anthropic) | Respostas didáticas e contextualizadas|
| Backend   | FastAPI (Python)   | Simples, rápido e fácil de aprender   |
| Frontend  | HTML + CSS + JS    | Sem frameworks complexos; roda em qualquer lugar |
| Highlight | highlight.js       | Coloração de código no chat           |
| Markdown  | marked.js          | Renderiza as respostas formatadas     |

---

## 🔮 Melhorias futuras

- [ ] Suporte a múltiplas linguagens (Python, C, JS, Java)
- [ ] Histórico de conversas salvo no banco de dados
- [ ] Dashboard de progresso do aluno
- [ ] Autenticação com login
- [ ] Modo offline com modelo local (Ollama)
- [ ] Integração com exercícios do LeetCode / Beecrowd

---

## 📜 Alinhamento com IEEE CS

Este projeto se alinha à missão da **IEEE Computer Society** de promover a educação em computação e o desenvolvimento de comunidade técnica. Pode ser usado como ferramenta de onboarding para novos membros do capítulo.

---

*Prosel 2026.1 · IEEE Computer Society*
