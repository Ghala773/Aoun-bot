import pandas as pd
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import CSVLoader
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.schema.runnable import RunnablePassthrough
import os
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm.autonotebook import tqdm, trange

df1 = pd.read_csv("backend/data/Gp_event_data(PROTOTYPE).csv", encoding="latin1")
df2 = pd.read_csv("backend/data/Places to visit(PROTOTYPE).csv", encoding="latin1")
df3 = pd.read_csv("backend/data/GP_Museum_DataSet_the_final1.csv", encoding="latin1")
        
documents_events_places = [
    Document(page_content=f"{row['Place']} | {row['Description']} | {row['Location']} | {row['Ticket Price']} | {row['Opening Hours']}")
    for _, row in pd.concat([df1, df2]).iterrows()
]

documents_museums = [
    Document(page_content=f"{row['ï»¿Museum Name ']} | {row['Description']} | {row['City']} | {row['Type']} | {row['Location']}")
    for _, row in df3.iterrows()
]

documents = documents_events_places + documents_museums
#chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)
print(f"Number of chunks: {len(chunks)}")
print(chunks[:2])

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

vector_store = FAISS.from_documents(chunks, embedding_model)

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.4, "k": 5}  # Return docs with score > 0.6
)

# Example query
query = "What concerts are happening in Riyadh in 2025?"

# Use `.invoke()` instead of `.get_relevant_documents()`
retrieved_docs = retriever.invoke(query)

# Print results
for doc in retrieved_docs:
    print(doc.page_content, "\n" + "="*80 + "\n")


from langchain_openai import ChatOpenAI

llm1 = ChatOpenAI(model="gpt-4o-mini", openai_api_key="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")

llm2 = ChatOpenAI(model="gpt-4-turbo", openai_api_key="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")

from langchain_core.prompts import ChatPromptTemplate

# Enhanced prompt for tourism events and museums in Saudi Arabia
prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are a Saudi tourism assistant specializing in accurate retrieval of events and museums.
     Only respond with relevant facts. Do not add extra details or events.
     Your task is to answer user queries accurately based on the available dataset. Follow these strict rules:

### **General Rules**:
1. **Always provide complete and structured answers** with details about the event or museum, including name, city, type, and description.
2. **If a specific location link is available, always include it** in the response.
3. **Do not make up any information**; only use data that exists in the dataset.
4. **If the user asks about events or museums in a specific city**, filter results to match that city.
5. **If the user asks about a specific type (museum type or event type)**, respond only with those matching the specified type.
6. **If no relevant data is found**, respond with:
   *"I apologize, I don't have information about that."*
7. **Use formal and structured responses** in clear English.
     
### Response Style Example:
Sure! I found something that might interest you in [City]. It's called [Name], and it's a [Type]. This place is known for [Description]. If you're interested, you can check it out here: [Google Maps Link].

If you can't find anything relevant, respond with:
"I apologize, I don't have information about that."

Be warm, helpful, and concise.


### **Additional Context Handling**:
- If the user asks for **all events or museums in a city**, list all matching entries.
- If the user asks specifically for **private or licensed museums**, ensure they are clearly identified.
- If the user requests **educational, historical, or cultural events or museums**, provide only those relevant.
"""),

    ("human",
     "Here is the relevant information about Saudi events and museums:\n\n{context}\n\n"
     "Based on this, answer the following question concisely:\n"
     "{question}\n\n"
     "Your response should be **factual, to the point, and concise. Do not add extra details.**")
])

formatted_messages = prompt.format_messages(
    context=(
        "House Of Hype on January 22-23, 2025 in Riyadh. Free entry. "
        "Riyadh Zoo open from June 2-3, 2025. Free entry. "
        "Al-Munikh Visitor Center event on January 23-24, 2025 in Riyadh. Tickets from 99 SAR. "
        "Dunes of Arabia experience on January 23-24, 2025 in Riyadh. Tickets from 27 SAR per person. "
        "Sky Bridge at Kingdom Center open from June 2-3, 2025 in Riyadh. Tickets: 69 SAR for adults, 23 SAR for kids. "
        "BALAD BEAST Music Festival on October 30-31, 2024 in Jeddah. Tickets from 499 SAR. "
        "Bayada Island Snorkeling Trip with Lunch on January 23-24, 2025 in Jeddah. Tickets from 2550 SAR per person. "
        "Winter at Tantora Festival from December 20, 2024 to January 20, 2025 in AlUla."
    ),

    question="What tourism events are happening in Saudi Arabia next month?"
)

# Print output to verify clarity
for msg in formatted_messages:
    print(msg.content)

    from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Function to format retrieved documents from the database
# Extracts text from each document and joins them with a double newline separator
# This ensures that the input is well-structured for the language model
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm1
    | StrOutputParser()
)

for chunk in rag_chain.stream("Are there any free family-friendly events in Riyadh this month?"):
    print(chunk, end="", flush=True)


for chunk in rag_chain.stream("What is the most famous museum in AlUla?"):
    print(chunk, end="", flush=True)

def query_rag(question: str) -> str:
    """Handles a user query using the RAG pipeline."""
    return rag_chain.invoke(question)









