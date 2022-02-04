#include <pybind11/pybind11.h>

#include <openassetio/managerAPI/ManagerInterface.hpp>

PYBIND11_MODULE(_openassetio, m) {
  using openassetio::managerAPI::ManagerInterface;
  namespace py = pybind11;

  py::module managerAPI = m.def_submodule("managerAPI");

  py::class_<ManagerInterface>(managerAPI, "ManagerInterface").def(py::init());
}
