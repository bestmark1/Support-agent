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
    'product',
    'FitMentor Overview',
    'FitMentor is a Telegram bot for nutrition tracking. Users log meals, track eating habits, and receive structured support around food awareness and consistency.',
    array['product', 'overview', 'nutrition'],
    'seed',
    true
  ),
  (
    'faq',
    'What FitMentor Helps With',
    'FitMentor helps users track nutrition, stay consistent with food logging, and build better nutrition habits. It does not replace a doctor, dietitian, or formal medical care.',
    array['faq', 'capabilities', 'scope'],
    'seed',
    true
  ),
  (
    'policy',
    'Medical Safety Boundary',
    'Support must not present medical diagnosis, prescribe treatment, or claim that FitMentor replaces professional healthcare advice. If a user asks about medical conditions, the answer should stay cautious and recommend professional care when appropriate.',
    array['policy', 'medical', 'safety'],
    'seed',
    true
  ),
  (
    'tone',
    'Support Tone',
    'Responses should be calm, practical, respectful, and concise. Avoid hype, avoid pressure, and avoid pretending the product can do more than it actually does.',
    array['tone', 'support', 'brand'],
    'seed',
    true
  );
