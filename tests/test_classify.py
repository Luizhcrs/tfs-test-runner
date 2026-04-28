from tfs_test_runner.classify import assign_phases, apply_yaml_phases, _case_matches


def test_assign_phases_default_single_phase():
    cases = [{"id": "1", "title": "T1"}, {"id": "2", "title": "T2"}]
    out = assign_phases(cases)
    assert len(out) == 1
    assert out[0]["id"] == "all"
    assert len(out[0]["cases"]) == 2


def test_assign_phases_empty():
    assert assign_phases([]) == []


def test_case_matches_by_id():
    case = {"id": "42", "title": "Whatever"}
    assert _case_matches(case, {"case_ids": ["42"]})
    assert _case_matches(case, {"case_ids": [42]})  # tolerates int
    assert not _case_matches(case, {"case_ids": ["99"]})


def test_case_matches_by_keyword():
    case = {"id": "x", "title": "Login Failure: invalid password"}
    assert _case_matches(case, {"match": ["failure"]})
    assert _case_matches(case, {"match": ["LOGIN"]})
    assert not _case_matches(case, {"match": ["timeout"]})


def test_case_matches_uses_title_en_first():
    case = {"id": "x", "title_en": "Login Failure", "title": "Falha no login"}
    assert _case_matches(case, {"match": ["failure"]})


def test_apply_yaml_phases_with_leftover():
    cases = [{"id": "1", "title": "T1"}, {"id": "2", "title": "T2"}, {"id": "3", "title": "T3"}]
    cfg = [{"id": "pA", "title": "Group A", "level": "easy", "desc": "...", "case_ids": ["1", "2"]}]
    out = apply_yaml_phases(cases, cfg)
    assert len(out) == 2
    assert out[0]["id"] == "pA"
    assert len(out[0]["cases"]) == 2
    assert out[1]["id"] == "others"
    assert out[1]["cases"][0]["id"] == "3"


def test_apply_yaml_phases_match_keyword():
    cases = [
        {"id": "1", "title": "Login OK"},
        {"id": "2", "title": "Login Failure"},
        {"id": "3", "title": "Logout"},
    ]
    cfg = [
        {"id": "p1", "title": "Failures", "level": "hard", "desc": "", "match": ["failure"]},
    ]
    out = apply_yaml_phases(cases, cfg)
    assert out[0]["id"] == "p1"
    assert [c["id"] for c in out[0]["cases"]] == ["2"]
    assert out[1]["id"] == "others"
    assert [c["id"] for c in out[1]["cases"]] == ["1", "3"]


def test_apply_yaml_phases_no_double_assignment():
    cases = [{"id": "1", "title": "Login Failure"}]
    cfg = [
        {"id": "pA", "title": "A", "level": "easy", "desc": "", "case_ids": ["1"]},
        {"id": "pB", "title": "B", "level": "easy", "desc": "", "match": ["failure"]},
    ]
    out = apply_yaml_phases(cases, cfg)
    # case 1 should land in pA only
    assert len(out) == 1
    assert out[0]["id"] == "pA"
