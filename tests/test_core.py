from paramhunter.core import extract_params, load_targets


def test_extract_params_basic():
    url = "https://example.com/?a=1&b=2&b=3&empty="
    keys = extract_params(url)
    assert set(keys) == {"a", "b", "empty"}


def test_load_targets(tmp_path):
    content = """
    # comment
    https://a.example/

    https://b.example/?x=1
    """.strip()
    file_path = tmp_path / "targets.txt"
    file_path.write_text(content, encoding="utf-8")
    targets = load_targets(str(file_path))
    assert targets == [
        "https://a.example/",
        "https://b.example/?x=1",
    ]


