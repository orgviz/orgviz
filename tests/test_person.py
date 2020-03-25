import pytest
import orgviz

def test_name():
    p = orgviz.Person("Alice")

    assert p.fullName == "Alice"

def test_dmu_values():
    p = orgviz.Person("Alice")
    assert p.getDmuDescription() == "User"

    p.setDmu("D")
    assert p.getDmuDescription() == "Decision Maker"

    p.setDmu("Waffles")
    assert p.getDmuDescription() == "User"

def test_sentiment_values():
    p = orgviz.Person("Bob")
    assert p.getSentimentDescription() == "Neutral"

    p.setSentiment("PROPONENT")
    assert p.getSentimentDescription() == "Proponent"

    p.setSentiment("Neutral")
    assert p.getSentimentDescription() == "Neutral"

