-- Habilita extensões necessárias
create extension if not exists vector;
create extension if not exists "uuid-ossp";

-- Tabela de usuários (gerenciada pelo Supabase Auth)
-- Apenas criamos uma view para acessar os dados públicos
create or replace view public_users as
    select id, email, raw_user_meta_data->>'name' as name
    from auth.users;

-- Tabela de parashiot
create table if not exists parashot (
    id uuid primary key default uuid_generate_v4(),
    name text not null unique,
    reference text not null,
    text text not null,
    hebrew text,
    book text not null,
    verses text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    embedding vector(1536)
);

-- Tabela de estudos
create table if not exists studies (
    id uuid primary key default uuid_generate_v4(),
    parasha text not null references parashot(name),
    type text not null default 'default',
    content jsonb not null,
    user_id uuid references auth.users(id),
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de documentos (para busca semântica)
create table if not exists documents (
    id uuid primary key default uuid_generate_v4(),
    content text not null,
    metadata jsonb not null,
    embedding vector(1536),
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de histórico de chat
create table if not exists chat_history (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users(id),
    messages jsonb not null,
    name text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Índices para busca por similaridade
create index if not exists idx_parashot_embedding on parashot
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

create index if not exists idx_documents_embedding on documents
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Função para buscar documentos similares
create or replace function match_documents (
    query_embedding vector(1536),
    match_count int default 5,
    match_threshold float default 0.78
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

-- Função para buscar parashiot similares
create or replace function match_parashot (
    query_embedding vector(1536),
    match_count int default 5,
    match_threshold float default 0.78
)
returns table (
    id uuid,
    name text,
    reference text,
    text text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        parashot.id,
        parashot.name,
        parashot.reference,
        parashot.text,
        1 - (parashot.embedding <=> query_embedding) as similarity
    from parashot
    where 1 - (parashot.embedding <=> query_embedding) > match_threshold
    order by parashot.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- Políticas de segurança RLS (Row Level Security)

-- Habilita RLS para todas as tabelas
alter table parashot enable row level security;
alter table studies enable row level security;
alter table documents enable row level security;
alter table chat_history enable row level security;

-- Políticas para parashot (leitura pública, escrita apenas por admin)
create policy "Parashot são públicas para leitura"
    on parashot for select
    to authenticated
    using (true);

create policy "Apenas admin pode modificar parashot"
    on parashot for all
    to authenticated
    using (auth.jwt() ->> 'email' = current_setting('app.admin_email'));

-- Políticas para studies (usuários veem apenas seus próprios estudos)
create policy "Usuários veem apenas seus próprios estudos"
    on studies for select
    to authenticated
    using (user_id = auth.uid());

create policy "Usuários podem criar seus próprios estudos"
    on studies for insert
    to authenticated
    with check (user_id = auth.uid());

-- Políticas para chat_history (usuários veem apenas seu próprio histórico)
create policy "Usuários veem apenas seu próprio histórico de chat"
    on chat_history for select
    to authenticated
    using (user_id = auth.uid());

create policy "Usuários podem criar seu próprio histórico de chat"
    on chat_history for insert
    to authenticated
    with check (user_id = auth.uid());
