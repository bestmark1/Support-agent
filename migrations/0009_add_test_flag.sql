alter table support_threads
  add column if not exists is_test boolean not null default false;

create index if not exists idx_support_threads_is_test_last_message_at
  on support_threads (is_test, last_message_at desc);
