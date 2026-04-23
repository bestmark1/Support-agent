alter table support_threads
  add column if not exists case_status text not null default 'open';

alter table support_threads
  add column if not exists resolution_note text;

alter table support_threads
  add column if not exists resolved_at timestamptz;

alter table support_threads
  add column if not exists reviewed_by text;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'support_threads_case_status_check'
  ) then
    alter table support_threads
      add constraint support_threads_case_status_check
      check (case_status in ('open', 'manual_review', 'resolved'));
  end if;
end $$;

create index if not exists idx_support_threads_case_status_last_message_at
  on support_threads (case_status, last_message_at desc);
