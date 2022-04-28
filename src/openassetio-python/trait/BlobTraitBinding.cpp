// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <optional>
#include <type_traits>

#include <pybind11/stl.h>

// Public.
#include <openassetio/export.h>
#include <openassetio/trait/BlobTrait.hpp>
// Private.
#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace trait {
/**
 * Utility function to convert a trait accessor result with error status
 * to a std::optional or an exception.
 *
 * @tparam Ret Type of return value if everything is OK.
 * @param traitId ID of trait to put in any exception message.
 * @param propKey Name of property to put in any exception message.
 * @param throwOnError If `true`, throw exceptions rather than returning
 * an unset `optional`.
 * @param status Property status.
 * @param out Return value if status is OK.
 * @return `out` if property is set, unset otherwise.
 * @exception `pybind11::attribute_error` if `throwOnError=true` and the
 * property is not set.
 * @exception `pybind11::type_error` if `throwOnError=true` and the
 * property contains the wrong type.
 */
template <class Ret>
std::optional<std::decay_t<Ret>> maybeProperty(const bool throwOnError,
                                               const TraitPropertyStatus status, Ret&& out) {
  std::string err;
  switch (status) {
    case TraitPropertyStatus::kFound:
      return {std::forward<Ret>(out)};

    case TraitPropertyStatus::kMissing:
      if (!throwOnError) {
        return {};
      }
      throw py::attribute_error{"Property not set"};

    case TraitPropertyStatus::kInvalidValue:
      if (!throwOnError) {
        return {};
      }
      throw py::type_error{"Property set to an unexpected value type"};
  }
  // Will (should!) never happen.
  throw std::runtime_error{"Unknown trait property state"};
}
}  // namespace trait
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio

void registerBlobTrait(const py::module& mod) {
  using openassetio::trait::BlobTrait;
  using openassetio::trait::maybeProperty;
  namespace specification = openassetio::specification;
  namespace trait = openassetio::trait;

  py::class_<BlobTrait, Holder<BlobTrait>>(mod, "BlobTrait")
      .def(py::init<Holder<specification::Specification>>(), py::arg("specification"))
      .def_readonly_static("kId", &BlobTrait::kId)
      .def("isValid", &BlobTrait::isValid)
      .def(
          "getUrl",
          [](const BlobTrait& self, const bool raiseOnError) {
            openassetio::Str out;
            trait::TraitPropertyStatus status = self.getUrl(&out);
            return maybeProperty(raiseOnError, status, std::move(out));
          },
          py::arg("raiseOnError") = false)
      .def("setUrl", &BlobTrait::setUrl, py::arg("url"))
      .def(
          "getMimeType",
          [](const BlobTrait& self, const bool raiseOnError) {
            openassetio::Str out;
            trait::TraitPropertyStatus status = self.getMimeType(&out);
            return maybeProperty(raiseOnError, status, std::move(out));
          },
          py::arg("raiseOnError") = false)
      .def("setMimeType", &BlobTrait::setMimeType, py::arg("mimeType"));
}
