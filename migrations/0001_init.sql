create extension if not exists vector;

create table if not exists knowledge_base (
  id uuid primary key default gen_random_uuid(),
  category text not null check (category in ('policy', 'faq', 'product', 'tone')),
  title text,
  content text not null,
  tags text[] not null default '{}',
  source text,
  is_approved boolean not null default false,
  version integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists knowledge_embeddings (
  knowledge_id uuid primary key references knowledge_base(id) on delete cascade,
  embedding vector(1536),
  created_at timestamptz not null default now()
);

create table if not exists proposed_updates (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  suggested_category text check (suggested_category in ('policy', 'faq', 'product', 'tone')),
  suggested_title text,
  suggested_content text not null,
  reason text,
  evidence jsonb not null default '{}'::jsonb,
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text
);

create table if not exists support_threads (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id text not null,
  telegram_chat_id text not null,
  last_message_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table if not exists support_messages (
  id uuid primary key default gen_random_uuid(),
  thread_id uuid not null references support_threads(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  message_text text not null,
  retrieval_context jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists partnership_leads (
  id uuid primary key default gen_random_uuid(),
  telegram_handle text,
  title text,
  description text,
  niche text,
  status text not null default 'new' check (status in ('new', 'reviewing', 'shortlisted', 'contacted', 'rejected')),
  score numeric,
  source text not null default 'manual',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists partnership_observations (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references partnership_leads(id) on delete cascade,
  observation_type text not null,
  note text not null,
  source_url text,
  created_at timestamptz not null default now()
);

create index if not exists idx_knowledge_base_approved_category
  on knowledge_base (is_approved, category);

create index if not exists idx_knowledge_base_tags
  on knowledge_base using gin (tags);

create index if not exists idx_proposed_updates_status_created_at
  on proposed_updates (status, created_at desc);

create index if not exists idx_support_threads_telegram_user_id
  on support_threads (telegram_user_id);

create index if not exists idx_partnership_leads_status
  on partnership_leads (status, updated_at desc);
