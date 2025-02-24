# -*- coding: utf-8 -*-
"""LangChain_chromadb.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LEyr3GME4N1GUZ1rMugNqb9e9wpK8W9U
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install langchain pypdf chromadb sentence-transformers transformers
!pip install langchain-community

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from transformers import pipeline
from langchain.llms import HuggingFacePipeline

# Load PDFs
pdf_path="/content/cleaned_text_output.pdf"
documents = []

loader = PyPDFLoader(pdf_path)
docs = loader.load()
documents.extend(docs)
print(f"Total number of documents: {len(documents)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
split_docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings()

vectordb=Chroma.from_documents(split_docs, embedding=embeddings, persist_directory="chroma_datab")

retriever=vectordb.as_retriever(search_type="similarity",search_kwargs={"k":3})

from transformers import pipeline

from huggingface_hub import login
login(token="YOUR_HF_TOKEN")

llama_pipeline = pipeline(
    "text-generation",
    model="meta-llama/Llama-2-7b-chat-hf",
    device=0,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
)

llm = HuggingFacePipeline(pipeline=llama_pipeline)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

query = "Which article is related to jammu and kashmir?"
retrieved_docs = retriever.get_relevant_documents(query)

# Combine retrieved context into a detailed prompt
context = "\n\n".join([doc.page_content for doc in retrieved_docs])  # Concatenate retrieved documents
detailed_prompt = (
    f"The following context is retrieved from legal documents:\n\n{context}\n\n"
    f"Based on the context, please provide a detailed and easy-to-understand answer to the following question:\n"
    f"{query}"
)

response = llm(detailed_prompt)

print("Answer:", response)

import shutil
from google.colab import files

folder_path = "/content/chroma_datab"
zip_path = "/content/chroma_datab"
shutil.make_archive(zip_path.replace('.zip', ''), 'zip', folder_path)

files.download(zip_path)

import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from transformers import pipeline
from huggingface_hub import login

login(token="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")

#Load the Chroma vector store (from your persisted directory)
persist_directory = "/content/chroma_datab"

# Load HuggingFace embeddings
embeddings = HuggingFaceEmbeddings()

# Load the Chroma vector store
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

#Set up the retriever
retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})

#Llama2 model for text generation
llama_pipeline = pipeline(
    "text-generation",
    model="meta-llama/Llama-2-7b-chat-hf",
    device=0,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
)

llm = HuggingFacePipeline(pipeline=llama_pipeline)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

"""**INFERENCE**"""

def perform_inference(query: str):
    retrieved_docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    detailed_prompt = (
        f"The following context is retrieved from legal documents:\n\n{context}\n\n"
        f"Based on the context, please provide a detailed and easy-to-understand answer to the following question:\n"
        f"{query}"
    )
    response = llm(detailed_prompt)

    return response

query = "Which article is related to Jammu and Kashmir?"
answer = perform_inference(query)
print("Answer:", answer)
