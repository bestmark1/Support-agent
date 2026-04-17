insert into knowledge_base (
  category,
  title,
  content,
  tags,
  source,
  is_approved
)
values
  (
    'faq',
    'How To Start Logging Meals',
    'A new user should start by recording meals consistently. The support answer should explain that regular logging matters more than perfect detail at the beginning.',
    array['faq', 'onboarding', 'logging'],
    'seed',
    true
  ),
  (
    'faq',
    'Missed A Meal Log',
    'If a user forgot to log one meal, support should advise them to continue from the next meal and avoid treating one missed entry as a failure.',
    array['faq', 'logging', 'consistency'],
    'seed',
    true
  ),
  (
    'product',
    'FitMentor Scope For Nutrition Tracking',
    'FitMentor supports meal logging, routine building, and nutrition awareness. It should not be described as a treatment tool or a medical monitoring platform.',
    array['product', 'scope', 'nutrition'],
    'seed',
    true
  )
on conflict do nothing;
