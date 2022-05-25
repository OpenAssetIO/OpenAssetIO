# OpenAssetIO Tests

The OpenAssetIO test infrastructure is currently in flux whilst the core
API stabilizes. At present, coverage is limited to simple unit tests of
core API components.

Over time, we aim to provide:

 - A test harness for `HostInterface` and `ManagerInterface` derived
   classes to allow developers to verify their implementation against
   expected behaviour.
 - Reference implementations for both hosts and managers that
   demonstrate canonical workflow sequences and expected behavior.
 - Stub/mock implementations for both hosts and managers that can be
   used in tests.
 - A utility host UI for exploratory testing/visual inspection of a
   manager's UI integration.
 - BDD tests that describe end-to-end workflows using these components.

