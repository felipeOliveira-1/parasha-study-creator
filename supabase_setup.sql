-- Habilita a extensão vector
create extension if not exists vector;

-- Habilita a extensão para UUID
create extension if not exists "uuid-ossp";

-- Remove a função existente
drop function if exists match_documents(vector(1536), integer, float);

-- Remove a tabela existente se ela existir
drop table if exists documents;

-- Cria a tabela documents para armazenar os documentos e seus embeddings
create table if not exists documents (
    id uuid primary key default uuid_generate_v4(),
    content text,  -- Conteúdo do documento
    metadata jsonb,  -- Metadados (fonte, página, etc.)
    embedding vector(1536)  -- Vetor de embedding (1536 é o tamanho para o modelo text-embedding-ada-002 da OpenAI)
);

-- Cria um índice para busca por similaridade
create index on documents 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Função para buscar documentos similares
create or replace function match_documents (
  query_embedding vector(1536),
  match_count int DEFAULT 5,
  match_threshold float DEFAULT 0.78
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;
