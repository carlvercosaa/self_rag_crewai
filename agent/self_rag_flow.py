import os
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_openai import ChatOpenAI
from crewai.flow.flow import Flow, listen, router, start
from typing_extensions import TypedDict
from typing import List
import chains
from dotenv import load_dotenv

load_dotenv()

databricks_host = os.environ.get("DATABRICKS_HOST")
databricks_token = os.environ.get("DATABRICKS_TOKEN")
endpoint_name = os.environ.get("ENDPOINT_NAME")
index_name = os.environ.get("INDEX_NAME")
embeddings_endpoint = os.environ.get("EMBEDDINGS_ENDPOINT")

vs_client = VectorSearchClient(disable_notice=True)

index = vs_client.get_index(endpoint_name=endpoint_name, index_name=index_name)

text_column = 'Conteudo'
        
columns = ["Conteudo", "Indice"]
        
search_kwargs = {"k": 4}
        
vector_search = DatabricksVectorSearch(
    index,
    text_column= text_column,
    columns = columns,
)
        
retriever = vector_search.as_retriever(search_kwargs=search_kwargs)

llm = ChatOpenAI(model="gpt-4o-mini")

class AgentState(TypedDict):
    question: str
    generation: str
    documents: List[str]
    success_flag: bool
    rewrite_flag: bool
    rewrite_after_generation_flag: bool
    filter_documents: List[str]
    unfilter_documents: List[str]

class RouterFlow(Flow[AgentState]):

    @start()
    @listen("rewrite")
    def retrieve(self):

        print("----CALLING RETRIEVER----")

        question = "Qual a diferença entre crime doloso e crime culposo?"

        self.question = question
        
        documents = retriever.invoke(self.question)

        self.documents = documents
    
    @listen(retrieve)
    def grade_documents(self):

        print("----CHECKING DOCUMENTS RELEVANCE TO THE QUESTION----")

        documents = self.documents
        question = self.state
        
        filtered_docs = []
        unfiltered_docs = []
        page_contents = []

        for doc in documents:
            page_contents.append(doc.page_content)

        for doc in page_contents:
        
            score = chains.grade_documents(question, doc)
            grade = score.binary_score
            
            if grade=='yes':
                print("----DOCUMENT----")
                print(doc)
                print("----GRADE: DOCUMENT RELEVANT----\n")
                filtered_docs.append(doc)
            else:
                print("----DOCUMENT----")
                print(doc)
                print("----GRADE: DOCUMENT NOT RELEVANT----\n")
                unfiltered_docs.append(doc)

        if len(unfiltered_docs)>4:
            self.success_flag = False
            print("----ALL THE DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY----")
            self.unfilter_docs = unfiltered_docs
        else:
            self.success_flag = True
            print("----DECISION: GENERATE----")
            self.filter_docs = filtered_docs

    @router(grade_documents)
    def grade_doc_router(self):
        if self.success_flag:
            print("----SUCCESS----")
            return "success"
        else:
            print("----FAILED----")
            return "failed"

    @listen("success")
    def generate(self):
        print("----GENERATING RESPONSE----")
        
        question= self.question
        documents= self.filter_docs
        
        generation = chains.generate_answer(documents, question)
        self.generation = generation
        print(generation)

    @listen("failed")
    def transform_query(self):

        print("----TRANSFORMING QUERY----")

        question = self.question
        documents = self.documents

        response = chains.rewrite_question(question, documents)

        print(f"----RESPONSE----")
        print(response)
        
        if response == 'question not relevant':
            self.rewrite_flag = False
        else:   
            self.question = response
            self.rewrite_flag = True
    
    @router(transform_query)
    def rewrite_decision(self):
        if self.rewrite_flag:
            print("----REWRITTEN----")
            return "rewrite"
        else:
            print("----NOT REWRITTEN----")
            return "no rewrite"
        
    @listen(generate)
    def grade_generation_vs_question(self):

        print("---CHECKING HALLUCINATIONS---")
        
        question = self.question
        generation = self.generation
            
        score = chains.grade_answer(question, generation)
            
        grade = score.binary_score
            
        if grade=='yes':
            print("---DECISION: GENERATION ADDRESS THE QUESTION ---")
            self.rewrite_after_generation_flag = False
        else:
            print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---TRANSFORM QUERY")
            self.rewrite_after_generation_flag = True
    
    @router(grade_generation_vs_question)
    def rewrite_after_generation_router(self):
        if self.rewrite_after_generation_flag:
            print("----REWRITTEN QUESTION----")
            return "failed"
        else:
            print("----PROCESS COMPLETED----")

flow = RouterFlow()
flow.kickoff()