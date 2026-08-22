"""IP & Trademark Guard tests - BÁO CÁO 02 §3."""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BE_DIR))
sys.path.insert(0, BE_DIR)

from app.services.ip_guard import (check_ip_safety, levenshtein_distance,
                                   similarity)


def test_clean_keyword():
    r = check_ip_safety("personalized pickleball tumbler for club names")
    assert r["status"] == "CLEAN_IP"
    assert r["safety_score"] >= 95.0


def test_dictionary_match():
    r = check_ip_safety("martha stewart halloween mug")
    assert r["status"] == "TRADEMARK_ALERT"
    assert r["safety_score"] <= 45.0


def test_dictionary_match_snoopy():
    r = check_ip_safety("snoopy tumbler cup")
    assert r["status"] == "TRADEMARK_ALERT"


def test_levenshtein_typo_variants():
    for variant in ["snooppy tumbler", "disnney mug", "starbuckss cup"]:
        r = check_ip_safety(variant)
        assert r["status"] == "TRADEMARK_ALERT", f"missed {variant}"


def test_levenshtein_distance():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("a", "a") == 0


def test_similarity_threshold():
    assert similarity("snoopy", "snooppy") >= 0.85
    assert similarity("pickleball", "basketball") < 0.85
