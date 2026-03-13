INSERT INTO skill_versions (id, skill_name, version, owner_department, status, manifest, test_result, changelog)
VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'news_parse_skill',
    'v0.1.0',
    '国家统计局',
    'draft',
    '{"input_schema": "EventIn", "output_schema": "EventNormalized"}',
    '{"cases": 0, "pass_rate": 0}',
    'Initial placeholder skill registration.'
),
(
    '22222222-2222-2222-2222-222222222222',
    'proposal_draft_skill',
    'v0.1.0',
    '国务院',
    'draft',
    '{"input_schema": "EventNormalized", "output_schema": "ProposalFinal"}',
    '{"cases": 0, "pass_rate": 0}',
    'Initial placeholder skill registration.'
),
(
    '33333333-3333-3333-3333-333333333333',
    'strategy_synthesis_skill',
    'v0.1.0',
    '中央军委',
    'draft',
    '{"input_schema": "ResearchReport", "output_schema": "Strategy"}',
    '{"cases": 0, "pass_rate": 0}',
    'Initial placeholder skill registration.'
),
(
    '44444444-4444-4444-4444-444444444444',
    'plan_generation_skill',
    'v0.1.0',
    '中央军委',
    'draft',
    '{"input_schema": "Strategy", "output_schema": "TradingPlan"}',
    '{"cases": 0, "pass_rate": 0}',
    'Initial placeholder skill registration.'
)
ON CONFLICT (id) DO NOTHING;
