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
    'en',
    'What Is FitMentor',
    'FitMentor is an AI nutrition coach that works directly inside Telegram. It is designed as a chat-first product for nutrition and habit tracking, so users interact with it in Telegram rather than in a separate installed app.',
    array['product', 'overview', 'telegram'],
    'fitmentor-ai.ru landing page',
    true
  ),
  (
    'product',
    'how_fitmentor_works_in_telegram',
    'en',
    'How FitMentor Works In Telegram',
    'FitMentor works inside Telegram. Users can log food, water, weight, activity, and sleep in chat. The public FAQ says no separate app installation is required: users can start through the Telegram bot and interact with the service there.',
    array['product', 'how-it-works', 'telegram'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'faq',
    'do_i_need_to_install_an_app',
    'en',
    'Do I Need To Install An App',
    'No. The public FAQ says the bot works inside Telegram and users do not need to install anything. They can start in Telegram and send /start.',
    array['faq', 'installation', 'telegram'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_free_plan',
    'en',
    'What Is Included In The Free Plan',
    'The free plan is available forever. The public pricing section says it includes text food logging, water, weight, activity, and sleep tracking, 3 AI messages per day, and a daily summary with calories, macros, and alerts.',
    array['faq', 'pricing', 'free-plan'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_pro_plan',
    'en',
    'What Is Included In The Pro Plan',
    'The Pro plan includes everything in Free, plus meal photos and voice input, 30 AI messages per day, a weekly report with AI patterns, Sunday insights, and 3 personal recipes per week. The public site shows Pro pricing as 399 RUB per month or 2,999 RUB per year.',
    array['faq', 'pricing', 'pro-plan'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'what_is_included_in_the_premium_plan',
    'en',
    'What Is Included In The Premium Plan',
    'The Premium plan includes everything in Pro, plus unlimited AI messages, unlimited recipes, mood-nutrition analysis, slip-risk alerts, and priority support. The public site shows Premium pricing as 999 RUB per month or 7,999 RUB per year.',
    array['faq', 'pricing', 'premium-plan'],
    'fitmentor-ai.ru landing page pricing',
    true
  ),
  (
    'faq',
    'can_i_use_voice_input',
    'en',
    'Can I Use Voice Input',
    'Yes, in paid tiers. The public site says voice input is available in Pro and Premium. Users can send a voice message and the bot can transcribe and log food, water, or activity automatically.',
    array['faq', 'voice', 'paid-features'],
    'fitmentor-ai.ru landing page FAQ and pricing',
    true
  ),
  (
    'faq',
    'how_calorie_estimates_work',
    'en',
    'How Calorie Estimates Work',
    'The public FAQ says standard foods use a local database and trusted reference values. If a meal is recognized through AI or by photo, the bot clearly marks the result as an approximate estimate.',
    array['faq', 'calories', 'estimates'],
    'fitmentor-ai.ru landing page FAQ',
    true
  ),
  (
    'policy',
    'fitmentor_is_not_a_medical_service',
    'en',
    'FitMentor Is Not A Medical Service',
    'FitMentor is not a medical service. The Terms of Use state that AI-based recommendations are informational only and do not replace medical advice, diagnosis, or treatment.',
    array['policy', 'medical', 'safety'],
    'fitmentor-ai.ru terms-en.html',
    true
  ),
  (
    'policy',
    'who_can_use_fitmentor',
    'en',
    'Who Can Use FitMentor',
    'The Terms of Use say the service is intended for users aged 16 or older.',
    array['policy', 'eligibility', 'age'],
    'fitmentor-ai.ru terms-en.html',
    true
  ),
  (
    'policy',
    'what_data_fitmentor_collects',
    'en',
    'What Data FitMentor Collects',
    'The Privacy Policy says FitMentor is a Telegram-based nutrition and habit-tracking service with AI-powered coaching and collects account-related Telegram data, including Telegram ID, username, and first name, along with other data needed to operate the service.',
    array['policy', 'privacy', 'data-collection'],
    'fitmentor-ai.ru privacy-en.html',
    true
  ),
  (
    'policy',
    'how_fitmentor_handles_user_data',
    'en',
    'How FitMentor Handles User Data',
    'The public FAQ says user data is used only to run the bot and is not shared with third parties. The Privacy Policy and support answers should stay aligned with published statements and should not invent broader data uses.',
    array['policy', 'privacy', 'data-use'],
    'fitmentor-ai.ru landing page FAQ and privacy-en.html',
    true
  ),
  (
    'policy',
    'how_to_request_data_deletion',
    'en',
    'How To Request Data Deletion',
    'The public FAQ says users can request full deletion at any time. Support should direct deletion requests to the official FitMentor support channels.',
    array['policy', 'privacy', 'deletion'],
    'fitmentor-ai.ru landing page FAQ and contacts-en.html',
    true
  ),
  (
    'faq',
    'official_fitmentor_support_contacts',
    'en',
    'Official FitMentor Support Contacts',
    'Official support contacts published by FitMentor are Telegram support @fitmentor_support and email support@fitmentor-ai.ru.',
    array['faq', 'support', 'contacts'],
    'fitmentor-ai.ru contacts-en.html',
    true
  ),
  (
    'policy',
    'who_provides_the_service',
    'en',
    'Who Provides The Service',
    'The Contacts page identifies the provider as Nikolay V. Sadovnikov, self-employed individual, Tax ID 121521606260.',
    array['policy', 'provider', 'contacts'],
    'fitmentor-ai.ru contacts-en.html',
    true
  ),
  (
    'policy',
    'refund_policy_priority_rule',
    'en',
    'Refund Policy Priority Rule',
    'For refund-related support, FitMentor''s own Refund Policy is the primary source of truth. Payment processor or bank documentation may help explain mechanics, but it does not override FitMentor''s published refund rules.',
    array['policy', 'refunds', 'priority'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'when_a_refund_may_be_possible',
    'en',
    'When A Refund May Be Possible',
    'Refunds are not the default outcome. The Refund Policy says that once a digital subscription has been activated and used, it may no longer be refundable unless required by applicable law or because of a technical failure on FitMentor''s side. A refund may be reviewed manually if payment succeeded but the subscription was not activated, or if there was a duplicate charge.',
    array['faq', 'refunds', 'eligibility'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'when_refunds_are_usually_not_granted',
    'en',
    'When Refunds Are Usually Not Granted',
    'The Refund Policy says refunds are normally not available when the subscription was activated and paid features were used. The main policy position is that refunds are generally not provided after activation and use.',
    array['faq', 'refunds', 'denial'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'how_to_request_a_refund',
    'en',
    'How To Request A Refund',
    'Refund requests should be sent through Telegram support or support email. The Refund Policy says the user should include their Telegram account, payment date, amount, and the reason for the request.',
    array['faq', 'refunds', 'request-process'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'how_long_refund_processing_can_take',
    'en',
    'How Long Refund Processing Can Take',
    'If a refund request is approved, the Refund Policy says it is processed through the same payment channel that was used for the purchase, usually within up to 10 business days, unless the relevant payment method requires a different process.',
    array['faq', 'refunds', 'timing'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_happens_if_paid_access_is_not_renewed',
    'en',
    'What Happens If Paid Access Is Not Renewed',
    'If paid access is not renewed, the subscription simply expires at the end of the paid period. There is no automatic obligation to keep using the service.',
    array['faq', 'subscription', 'renewal'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'payment_succeeded_but_subscription_did_not_activate',
    'en',
    'Payment Succeeded But Subscription Did Not Activate',
    'If payment succeeded but the subscription did not activate, this is a support case that should be reviewed manually. Support should ask for the user''s Telegram account, payment date, amount, and any payment confirmation details. Support should not promise an automatic refund before review.',
    array['faq', 'billing', 'activation-issue'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_to_do_if_money_was_charged_twice',
    'en',
    'What To Do If Money Was Charged Twice',
    'A duplicate charge is a case that may be reviewed for refund under the public Refund Policy. Support should collect the user''s Telegram account, payment date, amount, and payment confirmation details, then route the case to manual review.',
    array['faq', 'billing', 'duplicate-charge'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_information_to_request_for_payment_or_refund_issues',
    'en',
    'What Information To Request For Payment Or Refund Issues',
    'For payment or refund issues, support should request the user''s Telegram account, payment date, amount, a short description of the issue, and any available payment confirmation or receipt details.',
    array['faq', 'support', 'billing-intake'],
    'fitmentor-ai.ru refund-en.html',
    true
  ),
  (
    'faq',
    'what_support_can_and_cannot_help_with',
    'en',
    'What Support Can And Cannot Help With',
    'FitMentor support can help with access, payment review, subscription-related questions, and general service clarification. It should not present medical guidance as professional healthcare advice and should stay within the published service scope.',
    array['faq', 'support', 'scope'],
    'fitmentor-ai.ru terms-en.html and contacts-en.html',
    true
  ),
  (
    'faq',
    'what_priority_support_means',
    'en',
    'What Priority Support Means',
    'Premium includes priority support on the public pricing page. Support should describe this as a higher-priority support path for paying users, but should not promise a specific response-time SLA unless one is explicitly published.',
    array['faq', 'support', 'priority-support'],
    'fitmentor-ai.ru landing page pricing',
    true
  )
on conflict do nothing;
