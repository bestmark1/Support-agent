alter table support_threads
  add column if not exists priority_support boolean not null default false;

create index if not exists idx_support_threads_priority_support_last_message_at
  on support_threads (priority_support, last_message_at desc);
