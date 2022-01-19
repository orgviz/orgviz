import pytest
from orgviz.person import Person

def test_name():
    p = Person("Alice")

    assert p.fullName == "Alice"

def test_dmu_descriptions():
    p = Person("Alice")
    assert p.getDmuDescription() == "User"

    p.setDmu("D")
    assert p.getDmuDescription() == "Decision Maker"

    p.setDmu("Waffles")
    assert p.getDmuDescription() == "User"

    p.setDmu("d")
    assert p.getDmuDescription() == "Decision Maker"

def test_sentiment_set():
    p = Person("Geoffrey")

    p.setSentiment("P")

def test_sentiment_descriptions():
    p = Person("Bob")
    assert p.getSentimentDescription() == "Neutral"

    p.setSentiment("PROPONENT")
    assert p.getSentimentDescription() == "Proponent"

    p.setSentiment("Neutral")
    assert p.getSentimentDescription() == "Neutral"

def test_names():
    p = Person("Alice O'Donnel")
    assert p.isNameValid();

    p = Person("Bob Smithy-Smitherson")
    assert p.isNameValid();

    p = Person("Charles O‘Dowd")
    assert p.isNameValid();

    p = Person("Dávéy Jöñês")
    assert p.isNameValid();

    p = Person("þor")
    assert p.isNameValid();

    with pytest.raises(Exception):
        p = Person("Mr Waffles (yay!)")
        assert not p.isNameValid();

    with pytest.raises(Exception):
        p = Person("Neo 123#@!'")
        assert not p.isNameValid();
