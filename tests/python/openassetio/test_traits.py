"""
Tests for the traits type system.
"""
# pylint: disable=invalid-name,missing-class-docstring
# pylint: disable=redefined-outer-name,no-self-use
# pylint: disable=missing-function-docstring
import pytest
# TODO(DF): @pylint - re-enable once Python dev vs. install mess sorted.
# pylint: disable=no-name-in-module
from openassetio import specification, trait


class Test_Specification_traitIds:
    def test_when_has_no_traits_returns_empty_list(self):
        empty_specification = specification.Specification(set())
        assert empty_specification.traitIds() == set()

    def test_when_has_traits_returns_expected_trait_ids(self):
        expected_ids = {"a", "b", "🐠🐟🐠🐟"}
        populated_specification = specification.Specification(expected_ids)
        assert populated_specification.traitIds() == expected_ids


class Test_Specification_hasTrait:
    def test_when_has_trait_then_returns_true(self, a_specification):
        assert a_specification.hasTrait("second_trait")

    def test_when_not_has_trait_then_returns_false(self, a_specification):
        assert not a_specification.hasTrait("unknown_trait")


class Test_Specification_getsetTraitProperty:
    def test_valid_values(self, a_specification):
        a_specification.setTraitProperty("first_trait", "a string", "string")
        a_specification.setTraitProperty("second_trait", "an int", 1)
        a_specification.setTraitProperty("first_trait", "a float", 1.0)
        a_specification.setTraitProperty("second_trait", "a bool", True)

        assert a_specification.getTraitProperty("first_trait", "a string") == "string"
        assert isinstance(a_specification.getTraitProperty("first_trait", "a string"), str)
        assert a_specification.getTraitProperty("second_trait", "an int") == 1
        assert isinstance(a_specification.getTraitProperty("second_trait", "an int"), int)
        assert a_specification.getTraitProperty("first_trait", "a float") == 1.0
        assert isinstance(a_specification.getTraitProperty("first_trait", "a float"), float)
        assert a_specification.getTraitProperty("second_trait", "a bool") is True

    def test_when_key_is_not_found_then_get_returns_None(self, a_specification):
        assert a_specification.getTraitProperty("first_trait", "a string") is None

    def test_when_trait_is_not_found_then_IndexError_raised(self, a_specification):
        with pytest.raises(IndexError):
            a_specification.setTraitProperty("unknown_trait", "a string", "string")

        with pytest.raises(IndexError):
            _ = a_specification.getTraitProperty("unknown_trait", "a string")

    def test_when_value_is_not_supported_then_set_raises_TypeError(self, a_specification):
        with pytest.raises(TypeError):
            a_specification.setTraitProperty("first_trait", "unknown type", object())

        with pytest.raises(TypeError):
            a_specification.setTraitProperty("first_trait", "unknown type", None)


def test_BlobTrait_traitId():
    assert trait.BlobTrait.kId == "blob"


class Test_BlobTrait_isValid:
    def test_when_wrapping_BlobSpecification_then_returns_true(self, a_blob_specification):
        assert trait.BlobTrait(a_blob_specification).isValid()

    def test_when_wrapping_blob_supporting_spec_then_returns_true(self):
        assert trait.BlobTrait(
            specification.Specification({trait.BlobTrait.kId, "other"})).isValid()

    def test_when_wrapping_non_blob_spec_then_returns_false(self, a_specification):
        assert not trait.BlobTrait(a_specification).isValid()


class Test_BlobTrait_getURL:
    def test_when_spec_doesnt_have_blob_trait_then_raises_IndexError(self, a_specification):
        with pytest.raises(IndexError):
            trait.BlobTrait(a_specification).getUrl()

    def test_when_spec_has_no_url_then_returns_None(self, a_blob_specification):
        assert trait.BlobTrait(a_blob_specification).getUrl() is None

    def test_when_url_in_spec_has_wrong_value_type_then_returns_None(self, a_blob_specification):
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "url", 123)

        assert trait.BlobTrait(a_blob_specification).getUrl() is None

    def test_when_raiseOnError_and_spec_has_no_url_then_raises_AttributeError(
            self, a_blob_specification):
        with pytest.raises(AttributeError) as err:
            trait.BlobTrait(a_blob_specification).getUrl(raiseOnError=True)

        assert str(err.value) == "Property not set"

    def test_when_raiseOnError_and_url_in_spec_has_wrong_value_type_then_raises_TypeError(
            self, a_blob_specification):
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "url", 123)

        with pytest.raises(TypeError) as err:
            trait.BlobTrait(a_blob_specification).getUrl(raiseOnError=True)

        assert str(err.value) == "Property set to an unexpected value type"

    def test_when_spec_has_url_then_returns_url(self, a_blob_specification):
        expected = "some://url"
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "url", expected)

        actual = trait.BlobTrait(a_blob_specification).getUrl()

        assert actual == expected


class Test_BlobTrait_setURL:
    def test_when_spec_doesnt_have_blob_trait_then_raises_IndexError(self, a_specification):
        with pytest.raises(IndexError):
            trait.BlobTrait(a_specification).setUrl("some://url")

    def test_when_url_is_wrong_type_then_TypeError_is_raised(self, a_blob_specification):
        with pytest.raises(TypeError):
            trait.BlobTrait(a_blob_specification).setUrl(123)

    def test_when_url_is_a_str_then_url_is_added_to_spec(self, a_blob_specification):
        expected = "some://url"

        trait.BlobTrait(a_blob_specification).setUrl(expected)

        assert a_blob_specification.getTraitProperty(trait.BlobTrait.kId, "url") == expected


class Test_BlobTrait_getMimeType:
    def test_when_spec_doesnt_have_blob_trait_then_raises_IndexError(self, a_specification):
        with pytest.raises(IndexError):
            trait.BlobTrait(a_specification).getMimeType()

    def test_when_spec_has_no_mimeType_then_returns_None(self, a_blob_specification):
        assert trait.BlobTrait(a_blob_specification).getMimeType() is None

    def test_when_mimeType_in_spec_has_wrong_value_type_then_returns_None(
            self, a_blob_specification):
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "mimeType", 123)

        assert trait.BlobTrait(a_blob_specification).getMimeType() is None

    def test_when_raiseOnError_and_spec_has_no_mimeType_then_raises_AttributeError(
            self, a_blob_specification):
        with pytest.raises(AttributeError) as err:
            trait.BlobTrait(a_blob_specification).getMimeType(raiseOnError=True)

        assert str(err.value) == "Property not set"

    def test_when_raiseOnError_and_mimeType_in_spec_has_wrong_value_type_then_raises_TypeError(
            self, a_blob_specification):
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "mimeType", 123)

        with pytest.raises(TypeError) as err:
            trait.BlobTrait(a_blob_specification).getMimeType(raiseOnError=True)

        assert str(err.value) == "Property set to an unexpected value type"

    def test_when_data_has_mimeType_then_returns_mimeType(self, a_blob_specification):
        expected = "some://url"
        a_blob_specification.setTraitProperty(trait.BlobTrait.kId, "mimeType", expected)

        actual = trait.BlobTrait(a_blob_specification).getMimeType()

        assert actual == expected


class Test_BlobTrait_setMimeType:
    def test_when_spec_doesnt_have_blob_trait_then_raises_IndexError(self, a_specification):
        with pytest.raises(IndexError):
            trait.BlobTrait(a_specification).setMimeType("application/x-something")

    def test_when_mimeType_is_a_str_then_mimeType_is_added_to_spec(
            self, a_blob_specification):
        expected = "application/x-something"

        trait.BlobTrait(a_blob_specification).setMimeType(expected)

        assert a_blob_specification.getTraitProperty(
            trait.BlobTrait.kId, "mimeType") == expected

    def test_when_mimeType_is_wrong_type_then_TypeError_is_raised(self, a_blob_specification):
        with pytest.raises(TypeError):
            trait.BlobTrait(a_blob_specification).setMimeType(123)


@pytest.fixture
def a_specification():
    return specification.Specification({"first_trait", "second_trait"})


@pytest.fixture
def a_blob_specification():
    return specification.Specification({trait.BlobTrait.kId})
