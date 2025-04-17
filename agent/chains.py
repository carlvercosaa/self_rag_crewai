from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import prompts

llm = ChatOpenAI(model="gpt-4o-mini")

def grade_documents(question, document):
    class GradeDocuments(BaseModel):
        """Binary score for relevance check on retrieved documents."""

        binary_score: str = Field(
            description="Documents are relevant to the question, 'yes' or 'no'"
        )

    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system = prompts.DOCUMENTS_GRADER_SYSTEM_PROMPT
        
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )

    retrieval_grader = grade_prompt | structured_llm_grader

    response = retrieval_grader.invoke({"question":question, "document":document})

    return response

def generate_answer(question, context):
    template = prompts.GENERATE_ANSWER_PROMPT

    prompt_template = ChatPromptTemplate.from_template(template)

    answer_chain = prompt_template | llm | StrOutputParser()

    response = answer_chain.invoke({"question":question, "context": context})
    
    return response

def rewrite_question(question, documents):
    system = prompts.REWRITE_QUESTION_SYSTEM_PROMPT
        
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human","""Here is the initial question: \n\n {question} \n,
                Here is the document: \n\n {documents} \n ,
                Formulate an improved question. if possible other return 'question not relevant'."""
            ),
        ]
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()

    response = question_rewriter.invoke({"question":question,"documents":documents})

    return response

def grade_answer(question, generation):

    class GradeAnswer(BaseModel):
        """Binary score to assess answer addresses question."""

        binary_score: str = Field(
            description="Answer addresses the question, 'yes' or 'no'"
        )

    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    system = prompts.ANSWER_GRADER_SYSTEM_PROMPT
    answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
    )

    answer_grader = answer_prompt | structured_llm_grader

    response = answer_grader.invoke({"question":question,"generation":generation})

    return response