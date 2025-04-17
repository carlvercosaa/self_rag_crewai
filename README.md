## 🧠 Self-RAG com CrewAI

Este repositório implementa uma arquitetura **Self-RAG (Self-Reflective Retrieval-Augmented Generation)** integrada com a ferramenta **CrewAI**, permitindo que agentes recuperem conhecimento externo, gere respostas e reflitam sobre tarefas de forma autônoma em fluxos baseados em LLMs.

## 📌 Visão Geral

A arquitetura combina os seguintes componentes:

- **Retriever Agent**: Busca informações relevantes em uma base de conhecimento externa.
- **Grader Agents**: Avalia a relevancia dos documentos recuperados e das respostas geradas com base em uma pergunta.
- **Generator Agent**: Gera uma resposta com base no conhecimento externo recuperado.
- **Rewriter Agent**: Reescreve a pergunta caso necessário.
- **CrewAI Flow**: Orquestra a comunicação e interação entre os agentes de forma coordenada.

Essa abordagem visa aumentar a precisão, a coerência e a capacidade de autoavaliação do sistema em tarefas complexas com múltiplas etapas.

## 🚀 Tecnologias Utilizadas

- Python
- CrewAI
- LangChain
- OpenAI
- Databricks Vector Search
- Pydantic

## 📸 Execution Flow

![Execution Flow](image/crewai_image_img.png)

```text

📑 Retriever:
Recupera documentos relevantes para responder a pergunta.

🧠 Document grader:
Avalia a relevancia dos documentos recuperados.

🧠 Generate answer:
Gera uma resposta para a pergunta baseada nos documentos filtrados.

🧠 Answer grader:
Avalia a relevancia da resposta gerada.

🧠 Resposta Final:
Gera uma resposta final.
