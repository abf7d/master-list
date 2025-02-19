# ## embeddings.py
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import os

# embeddings = OpenAIEmbeddings()
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200,
#     separators=["\n\n", "\n", " ", ""]
# )

# def create_embeddings(text: str, metadata: dict):
#     """Create embeddings for text and store in ChromaDB"""
#     chunks = text_splitter.split_text(text)
#     embeddings_list = embeddings.embed_documents(chunks)
    
#     # Store in ChromaDB with metadata
#     vector_collection.add(
#         embeddings=embeddings_list,
#         documents=chunks,
#         metadatas=[metadata for _ in chunks]
#     )

# def search_similar(query: str, n_results: int = 5):
#     """Search for similar text chunks"""
#     query_embedding = embeddings.embed_query(query)
#     results = vector_collection.query(
#         query_embeddings=[query_embedding],
#         n_results=n_results
#     )
#     return results