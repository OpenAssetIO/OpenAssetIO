add_executable(openassetio-perftest
  perftest.cpp)

set_default_target_properties(openassetio-perftest)
install(TARGETS openassetio-perftest EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

target_link_libraries(openassetio-perftest
  PRIVATE
  openassetio-core)
