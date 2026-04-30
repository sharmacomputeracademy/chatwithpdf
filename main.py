from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

class PDFChatBot:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY not found")
        os.environ["OPENAI_API_KEY"] = self.api_key
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant. Answer ONLY from the given context. If the answer is not present in the context, say "I don't know".

            Context:
            {context}

            Question:
            {question}
            """
        )
        self.vector_store = None
        self.retriever = None
        self.rag_chain = None

    def ingest_pdf(self, file_path):
        """Loads PDF, chunks it, and creates vector store."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 10}
        )
        
        self._build_chain()
        return len(docs), len(chunks)

    def _build_chain(self):
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.rag_chain = (
            {
                "context": self.retriever | format_docs,
                "question": lambda x: x if isinstance(x, str) else x.get("question", "")
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query):
        if not self.rag_chain:
            return "⚠️ Vector store not initialized. Please load a PDF first."
        
        try:
            return self.rag_chain.invoke(query)
        except Exception as e:
            return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    bot = PDFChatBot()
    try:
        pages, chunks = bot.ingest_pdf("DSA.pdf")
        print(f"✅ Loaded {pages} pages, created {chunks} chunks")
        print("\n💬 RAG Chatbot Ready! Type 'exit' to quit.\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            print("🤖:", bot.ask(user_input))
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
