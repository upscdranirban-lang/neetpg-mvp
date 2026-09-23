from engine.classifier import classify


def test_final_result_round_3():
    c = classify("Final Result for Round-III of NEET PG Counselling 2025")
    assert c.doc_type == "final_result"
    assert c.round_label == "Round 3"
    assert c.cycle_label == "PG Counselling 2025"


def test_stray_vacancy_typo_tolerant():
    # MCC has actually published titles with "VACANY" (missing the C).
    c = classify("PG VACANY SEATS FOR STRAY ROUND PG 2025")
    assert c.doc_type == "vacancy"
    assert c.round_label == "Stray"


def test_unknown_title_is_low_confidence_not_a_crash():
    c = classify("Some completely novel announcement nobody has seen before")
    assert c.doc_type == "unclassified"
    assert c.doc_type_confidence < 0.5


def test_choice_filling_notice():
    c = classify("Notice for extension of Choice Filling of Round 3")
    assert c.doc_type == "choice_filling_notice"
    assert c.round_label == "Round 3"


def test_revised_result_beats_generic_result():
    c = classify("Notice Provisional Revised Result for Round 3 of PG counselling 2025")
    assert c.doc_type == "revised_result"


def test_academic_year_mention_does_not_invent_a_new_cycle():
    # A document about the *next* academic year's NRI eligibility must not
    # be mistaken for a document belonging to a "PG Counselling 2026"
    # cycle that does not exist yet -- MCC's academic-year label and its
    # counselling-cycle label are different things.
    c = classify("Public Notice for eligibility of NRI candidature for Academic Year 2026-27")
    assert c.cycle_label is None
