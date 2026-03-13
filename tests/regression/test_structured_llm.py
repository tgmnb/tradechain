from apps.agent_core.app.llm.structured import extract_json_object


def test_extract_json_object_skips_think_block_text() -> None:
    content = (
        "<think>\n"
        'The model is considering the example {"ok": true} before answering.\n'
        "</think>\n\n"
        '{"title": "final", "confidence": 0.9}'
    )

    parsed = extract_json_object(content)

    assert parsed == {"title": "final", "confidence": 0.9}


def test_extract_json_object_reads_first_valid_json_object() -> None:
    content = 'noise {"broken": } more noise {"ok": true, "items": [1, 2]} trailing'

    parsed = extract_json_object(content)

    assert parsed == {"ok": True, "items": [1, 2]}
