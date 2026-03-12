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
    '{"input_schema": "EventNormalized", "output_schema": "ProposalDraft"}',
    '{"cases": 0, "pass_rate": 0}',
    'Initial placeholder skill registration.'
)
ON CONFLICT (id) DO NOTHING;
