create index if not exists idx_knowledge_embeddings_embedding_hnsw
  on knowledge_embeddings
  using hnsw (embedding vector_cosine_ops);
