insert into knowledge_base (
  category,
  canonical_key,
  language,
  title,
  content,
  tags,
  source,
  is_approved
)
values
  (
    'product',
    'what_is_fitmentor',
    'ru',
    'Что такое FitMentor',
    'FitMentor — это AI-коуч по питанию, который работает прямо в Telegram. Сервис построен в chat-first формате для трекинга питания и привычек, поэтому пользователю не нужно переходить в отдельное установленное приложение.',
    array['product', 'overview', 'telegram', 'ru'],
    'fitmentor-ai.ru landing page',
    true
  ),
  (
    'product',
    'how_fitmentor_works_in_telegram',
    'ru',
    'Как работает FitMentor в Telegram',
    'FitMentor работает внутри Telegram. Пользователь может в чате логировать еду, воду, вес, активность и сон. В публичном FAQ указано, что отдельная установка приложения не требуется: достаточно запустить бота в Telegram.',
    array['product', 'how-it-works', 'telegram', 'ru'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'faq',
    'do_i_need_to_install_an_app',
    'ru',
    'Нужно ли устанавливать отдельное приложение',
    'Нет. В публичном FAQ указано, что бот работает внутри Telegram и ничего отдельно устанавливать не нужно. Пользователь может начать работу через Telegram и команду /start.',
    array['faq', 'installation', 'telegram', 'ru'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_free_plan',
    'ru',
    'Что входит в бесплатный тариф',
    'Бесплатный тариф доступен без ограничения по времени. В публичном блоке с тарифами указано, что он включает текстовый логинг еды, воды, веса, активности и сна, 3 AI-сообщения в день, а также ежедневную сводку по калориям, макросам и алертам.',
    array['faq', 'pricing', 'free-plan', 'ru'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_pro_plan',
    'ru',
    'Что входит в тариф Pro',
    'Тариф Pro включает всё из бесплатного тарифа, а также фото еды, голосовой ввод, 30 AI-сообщений в день, еженедельный отчёт с AI-паттернами, Sunday insights и 3 персональных рецепта в неделю. На публичной странице указана цена 399 ₽ в месяц или 2 999 ₽ в год.',
    array['faq', 'pricing', 'pro-plan', 'ru'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_premium_plan',
    'ru',
    'Что входит в тариф Premium',
    'Тариф Premium включает всё из Pro, а также безлимитные AI-сообщения, безлимитные рецепты, анализ связи настроения и питания, slip-risk alerts и priority support. На публичной странице указана цена 999 ₽ в месяц или 7 999 ₽ в год.',
    array['faq', 'pricing', 'premium-plan', 'ru'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'can_i_use_voice_input',
    'ru',
    'Можно ли использовать голосовой ввод',
    'Да, в платных тарифах. На сайте указано, что голосовой ввод доступен в Pro и Premium. Пользователь может отправить голосовое сообщение, а бот расшифрует его и залогирует еду, воду или активность.',
    array['faq', 'voice', 'paid-features', 'ru'],
    'fitmentor-ai.ru landing page FAQ and pricing',
    true
  ),
  (
    'faq',
    'how_calorie_estimates_work',
    'ru',
    'Как считаются калории и оценки по еде',
    'В публичном FAQ указано, что для стандартных продуктов используются локальная база и trusted reference values. Если еда распознана через AI или по фото, бот явно помечает такой результат как приблизительную оценку.',
    array['faq', 'calories', 'estimates', 'ru'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'policy',
    'fitmentor_is_not_a_medical_service',
    'ru',
    'FitMentor не является медицинским сервисом',
    'FitMentor не является медицинским сервисом. В Terms of Use указано, что AI-рекомендации носят исключительно информационный характер и не заменяют медицинскую консультацию, диагноз или лечение.',
    array['policy', 'medical', 'safety', 'ru'],
    'fitmentor-ai.ru terms-en.html',
    true
  ),
  (
    'policy',
    'who_can_use_fitmentor',
    'ru',
    'Кто может пользоваться FitMentor',
    'В Terms of Use указано, что сервис предназначен для пользователей от 16 лет и старше.',
    array['policy', 'eligibility', 'age', 'ru'],
    'fitmentor-ai.ru terms-en.html',
    true
  ),
  (
    'policy',
    'what_data_fitmentor_collects',
    'ru',
    'Какие данные собирает FitMentor',
    'В Privacy Policy указано, что FitMentor — это Telegram-сервис для питания и трекинга привычек с AI-поддержкой, и он собирает данные Telegram-аккаунта, включая Telegram ID, username и first name, а также другие данные, необходимые для работы сервиса.',
    array['policy', 'privacy', 'data-collection', 'ru'],
    'fitmentor-ai.ru privacy-en.html',
    true
  ),
  (
    'policy',
    'how_fitmentor_handles_user_data',
    'ru',
    'Как FitMentor использует данные пользователей',
    'В публичном FAQ сказано, что данные используются только для работы бота и не передаются третьим лицам. Ответы поддержки должны опираться на опубликованные формулировки и не придумывать дополнительные способы использования данных.',
    array['policy', 'privacy', 'data-use', 'ru'],
    'fitmentor-ai.ru landing page FAQ and privacy-en.html',
    true
  ),
  (
    'policy',
    'how_to_request_data_deletion',
    'ru',
    'Как запросить удаление данных',
    'В публичном FAQ указано, что пользователь может в любой момент запросить полное удаление данных. Такие запросы нужно направлять в официальные каналы поддержки FitMentor.',
    array['policy', 'privacy', 'deletion', 'ru'],
    'fitmentor-ai.ru landing page FAQ and contacts-en.html',
    true
  ),
  (
    'faq',
    'official_fitmentor_support_contacts',
    'ru',
    'Официальные контакты поддержки FitMentor',
    'Официальные контакты поддержки, опубликованные FitMentor: Telegram поддержки @fitmentor_support и email support@fitmentor-ai.ru.',
    array['faq', 'support', 'contacts', 'ru'],
    'fitmentor-ai.ru contacts-en.html',
    true
  ),
  (
    'policy',
    'who_provides_the_service',
    'ru',
    'Кто оказывает сервис FitMentor',
    'На странице Contacts указано, что провайдер сервиса — Nikolay V. Sadovnikov, self-employed individual, Tax ID 121521606260.',
    array['policy', 'provider', 'contacts', 'ru'],
    'fitmentor-ai.ru contacts-en.html',
    true
  ),
  (
    'policy',
    'refund_policy_priority_rule',
    'ru',
    'Приоритет политики возврата FitMentor',
    'По вопросам возвратов основным источником истины является собственная Refund Policy FitMentor. Документация платёжного провайдера или банка может помогать понимать механику платежей и возвратов, но не отменяет опубликованные правила FitMentor.',
    array['policy', 'refunds', 'priority', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'when_a_refund_may_be_possible',
    'ru',
    'Когда возврат может быть возможен',
    'Возврат не является стандартным исходом по умолчанию. В Refund Policy указано, что после активации и использования цифровой подписки возврат, как правило, уже недоступен, кроме случаев, когда этого требует закон или когда произошёл технический сбой на стороне FitMentor. Также возврат может быть рассмотрен вручную, если оплата прошла, а подписка не активировалась, либо если произошло двойное списание.',
    array['faq', 'refunds', 'eligibility', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'when_refunds_are_usually_not_granted',
    'ru',
    'Когда возврат обычно не предоставляется',
    'В Refund Policy указано, что если подписка была активирована и платные функции уже использовались, возврат обычно не предоставляется. Базовая позиция политики — после активации и использования возвраты, как правило, не делаются.',
    array['faq', 'refunds', 'denial', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'how_to_request_a_refund',
    'ru',
    'Как запросить возврат',
    'Запрос на возврат нужно отправить через Telegram поддержки или на email поддержки. В Refund Policy указано, что пользователь должен сообщить свой Telegram-аккаунт, дату платежа, сумму и причину запроса.',
    array['faq', 'refunds', 'request-process', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'how_long_refund_processing_can_take',
    'ru',
    'Сколько может занять обработка возврата',
    'Если запрос на возврат одобрен, Refund Policy указывает, что возврат обрабатывается через тот же платёжный канал, который использовался при покупке, обычно в срок до 10 рабочих дней, если правила конкретного способа оплаты не требуют другого процесса.',
    array['faq', 'refunds', 'timing', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_happens_if_paid_access_is_not_renewed',
    'ru',
    'Что происходит, если платный доступ не продлевается',
    'Если платный доступ не продлевается, подписка просто истекает в конце оплаченного периода. Автоматической обязанности продолжать пользоваться сервисом нет.',
    array['faq', 'subscription', 'renewal', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'payment_succeeded_but_subscription_did_not_activate',
    'ru',
    'Что делать, если оплата прошла, а подписка не активировалась',
    'Если оплата прошла, но подписка не активировалась, это кейс для ручной проверки поддержкой. Нужно запросить у пользователя его Telegram-аккаунт, дату платежа, сумму и любые данные подтверждения оплаты. Поддержка не должна обещать автоматический возврат до завершения проверки.',
    array['faq', 'billing', 'activation-issue', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_to_do_if_money_was_charged_twice',
    'ru',
    'Что делать, если деньги списались дважды',
    'Двойное списание — это кейс, который по публичной Refund Policy может быть рассмотрен на возврат. Поддержка должна запросить Telegram-аккаунт пользователя, дату платежа, сумму и подтверждение оплаты, после чего передать случай на ручную проверку.',
    array['faq', 'billing', 'duplicate-charge', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_information_to_request_for_payment_or_refund_issues',
    'ru',
    'Какие данные запросить по вопросу оплаты или возврата',
    'Для кейсов по оплате или возврату поддержка должна запросить Telegram-аккаунт пользователя, дату платежа, сумму, краткое описание проблемы и, если есть, подтверждение оплаты или детали чека.',
    array['faq', 'support', 'billing-intake', 'ru'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_support_can_and_cannot_help_with',
    'ru',
    'С чем поддержка может и не может помочь',
    'Поддержка FitMentor помогает с доступом, проверкой оплаты, вопросами по подписке и общими разъяснениями по сервису. Поддержка не должна выдавать медицинские рекомендации за профессиональную медицинскую помощь и должна оставаться в рамках опубликованного описания сервиса.',
    array['faq', 'support', 'scope', 'ru'],
    'fitmentor-ai.ru terms-en.html and contacts-en.html',
    true
  ),
  (
    'faq',
    'what_priority_support_means',
    'ru',
    'Что означает priority support',
    'На публичной странице тарифов указано, что в Premium включён priority support. Поддержка может описывать это как более приоритетный канал обслуживания для платных пользователей, но не должна обещать конкретный SLA, если он отдельно не опубликован.',
    array['faq', 'support', 'priority-support', 'ru'],
    'fitmentor-ai.ru landing page pricing',
    true
  )
on conflict do nothing;
