# All installs (Only required if running in Colab/Jupyter)
# !pip install faiss-cpu
# !pip install -U langchain-community
# !pip install -U langchain-openai
# !pip install rouge-score
# !pip install ragas datasets
# !pip install --upgrade ragas

# Import necessary libraries
import numpy as np
import pandas as pd
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load datasets
df1 = pd.read_csv("data/Gp-data (PROTOTYPE).csv", encoding="latin1")
df2 = pd.read_csv("data/Places to visit(PROTOTYPE).csv", encoding="latin1")
df3 = pd.read_csv("data/GP_Museum_DataSet_the_final1.csv", encoding="latin1")

# I added this because I faced an error while generating the next code
print(df3.columns)

# Convert data to LangChain Document format
documents_events_places = [
    Document(page_content=f"{row['Place']} | {row['Description']} | {row['Location']} | {row['Ticket Price']} | {row['Opening Hours']}")
    for _, row in pd.concat([df1, df2]).iterrows()
]

documents_museums = [
    Document(page_content=f"{row['ï»¿Museum Name ']} | {row['Description']} | {row['City']} | {row['Type']} | {row['Location']}")
    for _, row in df3.iterrows()
]

documents = documents_events_places + documents_museums

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

print(f"Number of chunks: {len(chunks)}")
print(chunks[:2])

# Load Hugging Face Embeddings(CHANGED TO LIGHTWEIGHT)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v1")

# Generate embeddings and store in FAISS vector store
vector_store = FAISS.from_documents(chunks, embedding_model)

# Perform Vector Search
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.4, "k": 5}  # Return top 5 relevant docs
)

# Add models
llm1 = ChatOpenAI(model="gpt-4o-mini", openai_api_key="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")
llm2 = ChatOpenAI(model="gpt-4-turbo", openai_api_key="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")


# Function to query the RAG model
def query_rag(query: str) -> str:
    retrieved_docs = retriever.invoke(query)

    if not retrieved_docs:
        return "I apologize, I don't have information about that."

    results = []
    seen = set() 

    for doc in retrieved_docs:
        data = doc.page_content.split(" | ")
        event_data = {
            "name": data[0].strip(),
            "description": data[1].strip() if len(data) > 1 else "",
            "city": data[2].strip() if len(data) > 2 else "",
            "price": data[3].strip() if len(data) > 3 else "",
            "time": data[4].strip() if len(data) > 4 else "",
            "location": data[4] if len(data) > 4 and data[4].strip() else None,
        }
# Unique key to detect duplicates
        event_key = f"{event_data['name']}|{event_data['city']}"

        if event_key in seen:
            continue  # Skip 

        seen.add(event_key)

        structured_response = f"""
**Name:** {event_data['name']}
**City:** {event_data['city']}
**Price:** {event_data['price']}
**Description:** {event_data['description']}
**Time:** {event_data['time']}
        """

        results.append(structured_response.strip())

    return "\n\n".join(results)
