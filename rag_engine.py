# rag_engine.py

import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from web_scraper import get_all_documents
from langchain.memory import ConversationBufferMemory          # NEW
from langchain.chains import ConversationalRetrievalChain      # NEW

INDEX_PATH = "faiss_index"

QA_TEMPLATE = """You are ASU Writing Support Bot.
Answer the question using the provided context. 
Always answer in the same language that the user used.

Context:
{context}

Question:
{question}
"""

def rebuild_vectorstore(embeddings):
    raw_docs = get_all_documents()
    splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    docs = splitter.create_documents(raw_docs)
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(INDEX_PATH)
    return vs

def setup_rag(refresh: bool = False):
    llm = Ollama(model="llama3", num_ctx=32768 )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    if refresh or not os.path.exists(INDEX_PATH):
        vectorstore = rebuild_vectorstore(embeddings)
    else:
        vectorstore = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    prompt = PromptTemplate(
        template=QA_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True            # returns a list[dict(role,content)]
    )

    qa_chain = ConversationalRetrievalChain.from_llm(     # CHANGED
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return qa_chain, llm
