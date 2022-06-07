// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#pragma once

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for an asset management system.

 If you are a tool or application developer, see @ref hostAPI.
*/
namespace managerAPI {

/**
 * This Interface binds a @ref asset_management_system into
 * OpenAssetIO. It is not called directly by a @ref host, but by the
 * middleware that presents a more object-oriented model of this to
 * the @ref host - namely, the @ref openassetio.hostAPI.Manager.
 *
 * It is structured around the following principles:
 *
 *   @li The currency of the API is either data, or an @ref
 *   entity_reference. objects should not be used to represent an @ref
 *   entity or its properties.
 *
 *   @li The manager plugin is expected to be batch-first. That is,
 *   where relevant, methods expect lists as their primary input
 *   parameters, and return a list as the result. This means a host
 *   can batch together multiple items and execute the same command
 *   on every item in the list in a single call, saving on
 *   potentially expensive round-trips and allowing the manager to
 *   use other back-end optimisations.
 *
 *   @li The interface is stateless as far as the host-facing API is
 *   concerned. The result of any method should solely depend on its
 *   inputs. This class could be static. In practice though, in a
 *   real-world session with a host, there are benefits to having an
 *   'instance' with a managed lifetime. This can be used to facilitate
 *   caching etc.
 *
 *   @li The implementation of this class should have no UI
 *   dependencies, so that it can be used in command-line only
 *   hosts/batch process etc...
 *
 *   @li You generally don't need to call the superclass implementation
 *   of any methods in this interface, unless you are deriving from your
 *   own subclass which requires it.
 *
 * Logging and Error Handling
 * --------------------------
 *
 * The supplied @ref openassetio.managerAPI.HostSession.HostSession
 * "HostSession" object provides logging methods that allow messages
 * and progress to be reported back to the user. All logging should go
 * through these methods otherwise it may not be correctly presented to
 * the user. The loose term "user" also covers developers, who may need
 * to see log output for debugging and other purposes.
 *
 * @warning Your plugin may be hosted out of process, or even on
 * another machine, the HostSession bridge takes care of relaying
 * messages accordingly. Using custom logging mechanisms may well
 * result in output being lost.
 *
 * @see @ref openassetio.managerAPI.HostSession.HostSession.log
 * "HostSession.log"
 * @see @ref openassetio.managerAPI.HostSession.HostSession.progress
 * "HostSession.progress"
 *
 * Exceptions should be thrown to handle any in-flight errors that
 * occur. The error should be mapped to a derived class of
 * exceptions.OpenAssetIOException, and thrown.  All exceptions of this
 * kind will be correctly passed across the plug-in C boundary,
 * and re-thrown. Other exceptions should not be used.
 *
 *  @see @ref openassetio.exceptions "exceptions"
 *
 * Threading
 * ---------
 * Any implementation of the ManagerInterface should be thread safe.
 * The one exception being Manager::initialize, this will never be
 * called concurrently.
 *
 * When a @ref openassetio.Context object is constructed by @ref
 * openassetio.hostAPI.Manager.Manager.createContext, the @needsref
 * createState method will be called, and the resulting state object
 * stored in the context. This context will then be re-used across
 * related API calls to your implementation of the ManagerInterface.
 * You can use this to determine which calls may be part of a specific
 * 'action' in the same host, or logically grouped processes such as a
 * batch render. This should allow you to implement stable resolution
 * of @ref meta_version "meta-versions" or other resolve-time concepts.
 *
 * There should be no persistent state in the implementation, concepts
 * such as getError(), etc.. for example should not be used.
 *
 * Hosts
 * -----
 *
 * Sometimes you may need to know more information about the API host.
 * A @ref openassetio.managerAPI.Host object is available through the
 * @ref openassetio.managerAPI.HostSession object passed to each method
 * of this class. This provides a standardised interface that all API
 * hosts guarantee to implement. This can be used to identify exactly
 * which host you are being called for, and query various entity
 * related specifics of the hosts data model.
 *
 * @see @ref openassetio.managerAPI.Host "Host"
 *
 * Initialization
 * --------------
 *
 * The constructor makes a new instance, but at this point it is not
 * ready for use. Instances of this class should be light weight to
 * create, but don't have to be lightweight to initialize. The
 * informational methods must be available pre-initialization, so that
 * UI and other display-type queries can be made relatively cheaply to
 * provide users with a list of managers and their settings. None of
 * the entity-related methods will be called until after @needsref
 * initialize has been called. The following methods must be callable
 * prior to initialization:
 *
 *    @li @ref identifier()
 *    @li @ref displayName()
 *    @li @needsref info()
 *    @li @needsref updateTerminology()
 *    @li @needsref getSettings()
 *    @li @needsref setSettings()
 *
 * @todo Finish/Document settings mechanism.
 * @see @needsref initialize
 */
class OPENASSETIO_CORE_EXPORT ManagerInterface {
 public:
  /**
   * Constructor.
   *
   * No work is done here - ManagerInterface instances should be cheap
   * to construct and stateless.
   */
  ManagerInterface();

  /**
   * Polymorphic destructor.
   */
  virtual ~ManagerInterface() = default;

  /**
   * @name Asset Management System Information
   *
   * These functions provide hosts with general information about the
   * @ref asset_management_system itself.
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify a specific asset
   * manager.
   *
   * This may be used by a host to persist the users preferred manager
   * via a preferences mechanism, or when spawning child processes,
   * etc...
   *
   * It should match the name used to register the plug-in with the
   * plug-in host.  The identifier should use only alpha-numeric
   * characters and '.', '_' or '-'.  Generally speaking, we recommend
   * using the 'reverse-DNS' convention, for example:
   *
   *     "org.openassetio.manager.test"
   *
   * @return Unique identifier of the manager.
   */
  [[nodiscard]] virtual Str identifier() const = 0;

  /**
   * Returns a human readable name to be used to reference this
   * specific asset manager in UIs or other user-facing messaging.
   *
   * One instance of its use may be in a host's preferences UI or
   * logging. For example:
   *
   *     "OpenAssetIO Test Asset Manager"
   *
   * @return Manager's display name.
   */
  [[nodiscard]] virtual Str displayName() const = 0;

  /**
   * Returns other information that may be useful about this @ref
   * asset_management_system. This can contain arbitrary key/value
   * pairs. For example:
   *
   *     { 'version' : '1.1v3', 'server' : 'assets.openassetio.org' }
   *
   * There are certain optional keys that may be used by a host or
   * the API:
   *
   *   @li openassetio.constants.kField_SmallIcon (upto 32x32)
   *   @li openassetio.constants.kField_Icon (any size)
   *
   * Because it can often be expensive to bridge between languages,
   * info can also contain an additional field - a prefix that
   * identifies a string as a valid entity reference. If supplied,
   * this will be used by the API to optimize calls to
   * isEntityReference when bridging between C/Python etc.
   * If this isn't supplied, then isEntityReference will always be
   * called to determine if a string is an @ref entity_reference or
   * not. Note, not all invocations require this optimization, so
   * @needsref isEntityReference should be implemented regardless.
   *
   *   @li openassetio.constants.kField_EntityReferencesMatchPrefix
   *
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] virtual InfoDictionary info() const;

  /**
   * @}
   */
};

using ManagerInterfacePtr = SharedPtr<ManagerInterface>;
}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
