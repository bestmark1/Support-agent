alter table knowledge_base
  add column if not exists canonical_key text;

alter table knowledge_base
  add column if not exists language text;

update knowledge_base
set language = 'ru'
where language is null
  and tags @> array['ru'];

update knowledge_base
set language = 'en'
where language is null;

alter table knowledge_base
  alter column language set not null;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'knowledge_base_language_check'
  ) then
    alter table knowledge_base
      add constraint knowledge_base_language_check
      check (language in ('ru', 'en'));
  end if;
end $$;

update knowledge_base
set canonical_key = case title
  when 'What Is FitMentor' then 'what_is_fitmentor'
  when 'Что такое FitMentor' then 'what_is_fitmentor'
  when 'How FitMentor Works In Telegram' then 'how_fitmentor_works_in_telegram'
  when 'Как работает FitMentor в Telegram' then 'how_fitmentor_works_in_telegram'
  when 'Do I Need To Install An App' then 'do_i_need_to_install_an_app'
  when 'Нужно ли устанавливать отдельное приложение' then 'do_i_need_to_install_an_app'
  when 'What Is Included In The Free Plan' then 'what_is_included_in_the_free_plan'
  when 'Что входит в бесплатный тариф' then 'what_is_included_in_the_free_plan'
  when 'What Is Included In The Pro Plan' then 'what_is_included_in_the_pro_plan'
  when 'Что входит в тариф Pro' then 'what_is_included_in_the_pro_plan'
  when 'What Is Included In The Premium Plan' then 'what_is_included_in_the_premium_plan'
  when 'Что входит в тариф Premium' then 'what_is_included_in_the_premium_plan'
  when 'Can I Use Voice Input' then 'can_i_use_voice_input'
  when 'Можно ли использовать голосовой ввод' then 'can_i_use_voice_input'
  when 'How Calorie Estimates Work' then 'how_calorie_estimates_work'
  when 'Как считаются калории и оценки по еде' then 'how_calorie_estimates_work'
  when 'FitMentor Is Not A Medical Service' then 'fitmentor_is_not_a_medical_service'
  when 'FitMentor не является медицинским сервисом' then 'fitmentor_is_not_a_medical_service'
  when 'Who Can Use FitMentor' then 'who_can_use_fitmentor'
  when 'Кто может пользоваться FitMentor' then 'who_can_use_fitmentor'
  when 'What Data FitMentor Collects' then 'what_data_fitmentor_collects'
  when 'Какие данные собирает FitMentor' then 'what_data_fitmentor_collects'
  when 'How FitMentor Handles User Data' then 'how_fitmentor_handles_user_data'
  when 'Как FitMentor использует данные пользователей' then 'how_fitmentor_handles_user_data'
  when 'How To Request Data Deletion' then 'how_to_request_data_deletion'
  when 'Как запросить удаление данных' then 'how_to_request_data_deletion'
  when 'Official FitMentor Support Contacts' then 'official_fitmentor_support_contacts'
  when 'Официальные контакты поддержки FitMentor' then 'official_fitmentor_support_contacts'
  when 'Who Provides The Service' then 'who_provides_the_service'
  when 'Кто оказывает сервис FitMentor' then 'who_provides_the_service'
  when 'Refund Policy Priority Rule' then 'refund_policy_priority_rule'
  when 'Приоритет политики возврата FitMentor' then 'refund_policy_priority_rule'
  when 'When A Refund May Be Possible' then 'when_a_refund_may_be_possible'
  when 'Когда возврат может быть возможен' then 'when_a_refund_may_be_possible'
  when 'When Refunds Are Usually Not Granted' then 'when_refunds_are_usually_not_granted'
  when 'Когда возврат обычно не предоставляется' then 'when_refunds_are_usually_not_granted'
  when 'How To Request A Refund' then 'how_to_request_a_refund'
  when 'Как запросить возврат' then 'how_to_request_a_refund'
  when 'How Long Refund Processing Can Take' then 'how_long_refund_processing_can_take'
  when 'Сколько может занять обработка возврата' then 'how_long_refund_processing_can_take'
  when 'What Happens If Paid Access Is Not Renewed' then 'what_happens_if_paid_access_is_not_renewed'
  when 'Что происходит, если платный доступ не продлевается' then 'what_happens_if_paid_access_is_not_renewed'
  when 'Payment Succeeded But Subscription Did Not Activate' then 'payment_succeeded_but_subscription_did_not_activate'
  when 'Что делать, если оплата прошла, а подписка не активировалась' then 'payment_succeeded_but_subscription_did_not_activate'
  when 'What To Do If Money Was Charged Twice' then 'what_to_do_if_money_was_charged_twice'
  when 'Что делать, если деньги списались дважды' then 'what_to_do_if_money_was_charged_twice'
  when 'What Information To Request For Payment Or Refund Issues' then 'what_information_to_request_for_payment_or_refund_issues'
  when 'Какие данные запросить по вопросу оплаты или возврата' then 'what_information_to_request_for_payment_or_refund_issues'
  when 'What Support Can And Cannot Help With' then 'what_support_can_and_cannot_help_with'
  when 'С чем поддержка может и не может помочь' then 'what_support_can_and_cannot_help_with'
  when 'What Priority Support Means' then 'what_priority_support_means'
  when 'Что означает priority support' then 'what_priority_support_means'
  else canonical_key
end
where canonical_key is null;

create unique index if not exists idx_knowledge_base_canonical_key_language
  on knowledge_base (canonical_key, language)
  where canonical_key is not null;

create index if not exists idx_knowledge_base_approved_language_category
  on knowledge_base (is_approved, language, category);

alter table support_threads
  add column if not exists preferred_language text;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'support_threads_preferred_language_check'
  ) then
    alter table support_threads
      add constraint support_threads_preferred_language_check
      check (preferred_language is null or preferred_language in ('ru', 'en'));
  end if;
end $$;
