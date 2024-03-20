"""
Tests for the traits data container
"""

# pylint: disable=invalid-name,missing-class-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
import pytest

# TODO(DF): @pylint - re-enable once Python dev vs. install mess sorted.
# pylint: disable=no-name-in-module
from openassetio.trait import TraitsData


class Test_TraitsData_Inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(TraitsData):
                pass


class Test_TraitsData_Copy_Constructor:
    def test_when_source_is_None_then_raises(self):
        with pytest.raises(TypeError, match="incompatible constructor arguments"):
            TraitsData(None)

    def test_when_copying_then_deep_copy_is_made(self):
        data_a = TraitsData()
        data_a.setTraitProperty("a", "p", 1)
        data_a.addTrait("b")
        data_b = TraitsData(data_a)
        assert data_b == data_a

    def test_when_copying_then_data_is_decoupled(self):
        data_a = TraitsData()
        data_a.setTraitProperty("a", "p", 1)
        data_b = TraitsData(data_a)
        data_b.addTrait("b")
        data_b.setTraitProperty("a", "p", 2)
        assert data_a.getTraitProperty("a", "p") == 1
        assert not data_a.hasTrait("b")


class Test_TraitsData_traitSet:
    ## TODO(TC): Asset that result is a set, and not a reference to
    ## any internal structures.
    def test_when_has_no_traits_returns_empty_list(self):
        empty_data = TraitsData()
        assert empty_data.traitSet() == set()

    def test_when_has_traits_returns_expected_trait_ids(self):
        expected_ids = {"a", "b", "🐠🐟🐠🐟"}
        populated_data = TraitsData(expected_ids)
        assert populated_data.traitSet() == expected_ids


class Test_TraitsData_addTrait:
    def test_when_trait_is_new_then_added(self):
        data = TraitsData()
        trait_name = "a 🐍"
        data.addTrait(trait_name)
        assert data.traitSet() == {trait_name}

    def test_when_trait_is_new_then_existing_traits_are_unaffected(self, a_traitsdata):
        trait_set = set(a_traitsdata.traitSet())
        new_trait = "another trait"
        a_traitsdata.addTrait(new_trait)
        trait_set.add(new_trait)
        assert a_traitsdata.traitSet() == trait_set

    def test_when_trait_already_exists_then_is_noop(self, a_traitsdata):
        old_traits = a_traitsdata.traitSet()
        a_traitsdata.addTrait(next(iter(a_traitsdata.traitSet())))
        assert a_traitsdata.traitSet() == old_traits


class Test_TraitsData_addTraits:
    def test_when_traits_are_new_the_added(self):
        data = TraitsData()
        trait_set = {"🐌", "🐞", "🐜"}
        data.addTraits(trait_set)
        assert data.traitSet() == trait_set

    def test_when_traits_are_new_then_existing_traits_are_unaffected(self, a_traitsdata):
        trait_set = set(a_traitsdata.traitSet())
        new_traits = {"🐌", "🐞", "🐜"}
        a_traitsdata.addTraits(new_traits)
        expected_traits = trait_set.union(new_traits)
        assert a_traitsdata.traitSet() == expected_traits

    def test_when_trait_ids_already_exist_then_is_noop(self, a_traitsdata):
        traits = a_traitsdata.traitSet()
        old_traits = traits
        a_traitsdata.addTraits(traits)
        assert a_traitsdata.traitSet() == old_traits


class Test_TraitsData_hasTrait:
    def test_when_has_trait_then_returns_true(self, a_traitsdata):
        assert a_traitsdata.hasTrait("second_trait")

    def test_when_not_has_trait_then_returns_false(self, a_traitsdata):
        assert not a_traitsdata.hasTrait("unknown_trait")


class Test_TraitsData_getsetTraitProperty:
    def test_valid_values(self, a_traitsdata):
        a_traitsdata.setTraitProperty("first_trait", "a string", "string")
        a_traitsdata.setTraitProperty("second_trait", "an int", 1)
        a_traitsdata.setTraitProperty("first_trait", "a float", 1.0)
        a_traitsdata.setTraitProperty("second_trait", "a bool", True)

        assert a_traitsdata.getTraitProperty("first_trait", "a string") == "string"
        assert isinstance(a_traitsdata.getTraitProperty("first_trait", "a string"), str)
        assert a_traitsdata.getTraitProperty("second_trait", "an int") == 1
        assert isinstance(a_traitsdata.getTraitProperty("second_trait", "an int"), int)
        assert a_traitsdata.getTraitProperty("first_trait", "a float") == 1.0
        assert isinstance(a_traitsdata.getTraitProperty("first_trait", "a float"), float)
        assert a_traitsdata.getTraitProperty("second_trait", "a bool") is True

    def test_when_key_is_not_found_then_get_returns_None(self, a_traitsdata):
        assert a_traitsdata.getTraitProperty("first_trait", "a string") is None

    def test_when_trait_is_not_found_then_set_adds_trait(self, a_traitsdata):
        new_trait_id, a_property, a_value = "a_new_trait", "a string", "string"
        a_traitsdata.setTraitProperty(new_trait_id, a_property, a_value)
        assert new_trait_id in a_traitsdata.traitSet()
        assert a_traitsdata.getTraitProperty(new_trait_id, a_property) == a_value

    def test_when_trait_is_not_found_then_get_returns_None(self, a_traitsdata):
        assert a_traitsdata.getTraitProperty("unknown_trait", "a string") is None

    def test_when_value_is_not_supported_then_set_raises_TypeError(self, a_traitsdata):
        with pytest.raises(TypeError):
            a_traitsdata.setTraitProperty("first_trait", "unknown type", object())

        with pytest.raises(TypeError):
            a_traitsdata.setTraitProperty("first_trait", "unknown type", None)


class Test_TraitsData_traitPropertyKeys:
    def test_when_trait_has_no_properties_then_returns_empty_set(self, a_traitsdata):
        a_traitsdata.addTrait("a_trait")
        assert a_traitsdata.traitPropertyKeys("a_trait") == set()

    def test_when_has_trait_with_properties_then_returns_keys(self, a_traitsdata):
        expected_keys = {"proprty_one", "🦆"}
        for prop in expected_keys:
            a_traitsdata.setTraitProperty("a_trait", prop, "a value")
        assert a_traitsdata.traitPropertyKeys("a_trait") == expected_keys

    def test_when_trait_not_set_then_returns_empty_set(self, a_traitsdata):
        assert a_traitsdata.traitPropertyKeys("a_trait") == set()


class Test_TraitsData_equality:
    def test_when_comparing_with_same_data_then_are_equal(self):
        data_a = TraitsData({"a_trait"})
        data_a.setTraitProperty("a_trait", "a_property", 1)
        data_b = TraitsData({"a_trait"})
        data_b.setTraitProperty("a_trait", "a_property", 1)
        assert data_a == data_b

    def test_when_comparing_with_different_property_value_then_are_not_equal(self):
        data_a = TraitsData({"a_trait"})
        data_a.setTraitProperty("a_trait", "a_property", 1)
        data_b = TraitsData({"a_trait"})
        data_b.setTraitProperty("a_trait", "a_property", 2)
        assert data_a != data_b

    def test_when_comparing_with_subset_of_properties_then_are_not_equal(self):
        data_a = TraitsData({"a_trait"})
        data_a.setTraitProperty("a_trait", "a_property", 1)
        data_b = TraitsData({"a_trait"})
        data_b.setTraitProperty("a_trait", "a_property", 1)
        data_b.setTraitProperty("a_trait", "another_property", 1)
        assert data_a != data_b

    def test_when_comparing_with_different_trait_then_are_not_equal(self):
        data_a = TraitsData({"a_trait"})
        data_b = TraitsData({"another_trait"})
        assert data_a != data_b
        assert data_a != data_b


class Test_TraitsData_repr:
    def test(self, a_traitsdata):
        assert repr(a_traitsdata) == str(a_traitsdata)
        assert (
            str(a_traitsdata) == 'TraitsData({"first_trait", "second_trait"})'
            or str(a_traitsdata) == 'TraitsData({"second_trait", "first_trait"})'
        )


@pytest.fixture
def a_traitsdata():
    return TraitsData({"first_trait", "second_trait"})
