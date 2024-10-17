from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import pandas as pd
import numpy as np

# Load the CSV file into a DataFrame
CSV_FILE_NAME = 'player_outlooks.csv'
player_df = pd.read_csv(CSV_FILE_NAME)

# Use Hugging Face embeddings directly via LangChain
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Use a text splitter if the text is long
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

def find_similar_players(player, player_df_by_pos):
    """Finds the most similar player descriptions based on user input"""

    # Extract metadata (player names)
    metadata = [{"player_name": name} for name in player_df_by_pos['name']]

    # Split outlooks into chunks and convert each chunk into a Document
    outlook_chunks = []
    for outlook, name in zip(player_df_by_pos['outlook'], player_df_by_pos['name']):
        chunks = splitter.split_text(outlook)
        outlook_chunks += [Document(page_content=chunk, metadata={"player_name": name}) for chunk in chunks]

    # Create vector store using the embeddings
    db = FAISS.from_documents(outlook_chunks, embeddings)   
    
    # Convert the user's input into an embedding
    query_embedding = embeddings.embed_query(player['outlook'])
    
    # Perform similarity search on the vector store
    similar_docs = db.similarity_search_with_score(player['outlook'], k=3)  # k is the number of top similar results

    similar_players = []
    for doc, score in similar_docs:
        print(score)
        similar_players.append({
            'name': doc.metadata['player_name'],
            'outlook': doc.page_content,
            'score': score
        })

    return similar_players