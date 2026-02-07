from pdf_organizer.classify import classify_text


def test_classify_prefers_best_category():
    cats = {
        "Genética": ["genética", "dna", "cromossomo"],
        "Bioquímica": ["enzima", "metabolismo"],
        "Outros": [],
    }
    text = "Introdução à genética: DNA, cromossomo e hereditariedade."
    res = classify_text(text, cats, title="Introdução à genética")
    assert res.category == "Genética"
    assert res.confidence > 0.0
    assert "dna" in res.matched_keywords


def test_classify_no_hits_goes_outros():
    cats = {"Genética": ["dna"], "Outros": []}
    res = classify_text("Nada a ver com isso.", cats)
    assert res.confidence == 0.0


def test_classify_uses_toc_when_available():
    cats = {"História": ["história", "revolução"], "Física": ["energia"], "Outros": []}
    res = classify_text("Texto neutro.", cats, toc="Capítulo 1: História da Revolução")
    assert res.category == "História"
    assert res.confidence > 0.0


def test_classify_weights_title_over_body():
    cats = {"Química": ["química"], "Física": ["física"], "Outros": []}
    res = classify_text(
        "Introdução à física.",
        cats,
        title="Fundamentos de Química",
    )
    assert res.category == "Química"
