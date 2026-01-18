import os
from dotenv import load_dotenv
from chromadb import EmbeddingFunction
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import embeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class RagEngine:
    def __init__(self):
        
        db_directory = "./chroma_db"
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Vector database
        self.vector_store = Chroma (
            collection_name="example_collection",
            embedding_function = self.embeddings,
            persist_directory = db_directory
        )
        
        self.llm = ChatOpenAI(
            model=os.getenv("GPT_MODEL", "gpt-4o-mini"),
            temperature=0
        )
            
    def process_document(self, file_path: str):
        
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        
        finals_chunks = text_splitter.split_documents(documents)
        
        self.vector_store.add_documents(finals_chunks)
        
        return "Document processed successfully!"
    
    def answer(self, question: str):
        
        retrieved_docs = self.vector_store.similarity_search(
            question,
            k=3
        )
        
        context_text = "\n".join([doc.page_content for doc in retrieved_docs])
        
        prompt = f"""
        You are an helpful assistant answering questions based on the provided documents.
        Use ONLY the provided context below to answer the question.
        
        If the answer is not available in the context, reply exactly: "I couldn't find this information in the documents."
        Do not make up an answer.

        Context:
        {context_text}

        Question:
        {question}
        """
        response = self.llm.invoke(prompt)
        
        return response.content
        