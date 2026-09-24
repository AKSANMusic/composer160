"""Unit tests for the COMPOSER-160 Core Data Model."""

import pytest
from composer160.core.types import Domain, ParamType, Tier
from composer160.core.parameters import (
    ParameterDef,
    PARAMETER_REGISTRY,
    T1_PARAMETER_IDS,
)
from composer160.core.vector import ParameterVector


def test_param_types():
    assert ParamType.S.value == "scalar"
    assert ParamType.N.value == "numeric"
    assert ParamType.C.value == "categorical"
    assert ParamType.O.value == "ordered"
    assert ParamType.B.value == "boolean"
    assert ParamType.T.value == "timeline"


def test_tiers():
    assert Tier.T1 == 1
    assert Tier.T2 == 2
    assert Tier.T3 == 3
    assert Tier.T1 < Tier.T2 < Tier.T3  # Priority order: T1 is highest priority


def test_domains():
    assert len(Domain) == 20
    assert Domain.A.value == "Tonal Foundation"
    assert Domain.B.value == "Tempo & Meter"
    assert Domain.K.value == "Emotion & Narrative"
    assert Domain.T.value == "Project & Release Context"


def test_parameter_registry_basic_t1():
    assert 1 in PARAMETER_REGISTRY
    p1 = PARAMETER_REGISTRY[1]
    assert p1.name == "Root Key"
    assert p1.param_type == ParamType.C
    assert p1.tier == Tier.T1
    assert p1.domain == Domain.A
    assert "A" in p1.values

    assert 2 in PARAMETER_REGISTRY
    p2 = PARAMETER_REGISTRY[2]
    assert p2.name == "Tonality"
    assert p2.param_type == ParamType.C
    assert p2.tier == Tier.T1
    assert "Minor" in p2.values

    assert 8 in PARAMETER_REGISTRY
    p8 = PARAMETER_REGISTRY[8]
    assert p8.name == "BPM"
    assert p8.param_type == ParamType.N
    assert p8.tier == Tier.T1
    assert p8.unit == "BPM"


def test_parameter_def_frozen():
    p = PARAMETER_REGISTRY[1]
    with pytest.raises(AttributeError):
        p.name = "New Name"  # type: ignore[misc]


def test_vector_set_and_get():
    v = ParameterVector()
    assert v.get(1) == "auto"
    assert not v.is_set(1)

    v.set(1, "A", assumed=False)
    assert v.get(1) == "A"
    assert v.is_set(1)
    assert v.assumed_t1_fields() == []

    v.set(2, "Minor", assumed=True)
    assert v.get(2) == "Minor"
    assert v.is_set(2)
    assert (2, "Tonality", "Minor") in v.assumed_t1_fields()


def test_vector_t1_completeness():
    v = ParameterVector()
    assert not v.t1_complete()

    # Fill all 12 T1 parameters
    for pid in T1_PARAMETER_IDS:
        v.set(pid, "val")

    assert v.t1_complete()


def test_vector_bounds():
    v = ParameterVector()
    with pytest.raises(ValueError):
        v.set(0, "invalid")
    with pytest.raises(ValueError):
        v.set(161, "invalid")
    with pytest.raises(ValueError):
        v.get(0)
    with pytest.raises(ValueError):
        v.get(161)


def test_vector_copy():
    v = ParameterVector()
    v.set(1, "D", assumed=True)
    v2 = v.copy()
    assert v2.get(1) == "D"
    assert (1, "Root Key", "D") in v2.assumed_t1_fields()

    # Modifying copy does not mutate original
    v2.set(1, "G", assumed=False)
    assert v2.get(1) == "G"
    assert v.get(1) == "D"
