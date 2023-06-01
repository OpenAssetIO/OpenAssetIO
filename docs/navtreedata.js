var NAVTREE =
[
  [ "OpenAssetIO [beta]", "index.html", [
    [ "An Introduction", "index.html", [
      [ "Scope", "index.html#intro_scope", null ],
      [ "The Approach", "index.html#intro_approach", [
        [ "What is an Asset Management System", "index.html#intro_ams", null ],
        [ "What is a Host?", "index.html#intro_host", null ]
      ] ],
      [ "Architecture", "index.html#architecture_overview", null ],
      [ "The Basic Design for a Host", "index.html#host_implementation_concept", null ],
      [ "The Asset Manager's Commitment", "index.html#manager_implementation_concept", null ]
    ] ],
    [ "Configuring OpenAssetIO", "runtime_configuration.html", [
      [ "Overview", "runtime_configuration.html#runtime_configuration_overview", null ],
      [ "Installing Manager plugins", "runtime_configuration.html#installing_manager_plugins", [
        [ "Using pip", "runtime_configuration.html#installing_manager_plugins_pip", null ],
        [ "Manual installation", "runtime_configuration.html#installing_manager_plugins_manual", null ]
      ] ],
      [ "Host configuration", "runtime_configuration.html#host_settings", [
        [ "The Default Config Mechanism", "runtime_configuration.html#host_default_config", null ]
      ] ],
      [ "Troubleshooting", "runtime_configuration.html#configuration_troubleshooting", [
        [ "Pip installed Python plugins not being found", "runtime_configuration.html#pip_plugins_missing", null ],
        [ "Manually installed plugins not being found", "runtime_configuration.html#manual_plugins_missing", null ],
        [ "Default config mechanism not working", "runtime_configuration.html#default_config_not_working", null ]
      ] ]
    ] ],
    [ "Entities, Traits and Specifications", "entities_traits_and_specifications.html", [
      [ "Entities", "entities_traits_and_specifications.html#Entities", null ],
      [ "Traits", "entities_traits_and_specifications.html#Traits", null ],
      [ "Entity Data", "entities_traits_and_specifications.html#entity_data", [
        [ "Not Just for Files", "entities_traits_and_specifications.html#entities_not_just_for_files", [
          [ "Mapping to Existing Data", "entities_traits_and_specifications.html#trait_mapping", null ]
        ] ],
        [ "Modifying Trait Properties", "entities_traits_and_specifications.html#trait_property_modification", null ],
        [ "Traits as Views", "entities_traits_and_specifications.html#traits_as_views", null ]
      ] ],
      [ "Specifications", "entities_traits_and_specifications.html#Specifications", [
        [ "Locale Specifications", "entities_traits_and_specifications.html#locale_specifications", null ],
        [ "Entity Specifications", "entities_traits_and_specifications.html#entity_specifications", null ],
        [ "Relationship Specifications", "entities_traits_and_specifications.html#relationship_specifications", null ]
      ] ],
      [ "A Note on Trait Specificity and Entities", "entities_traits_and_specifications.html#specification_specificity", [
        [ "Trait Sets as a Filter Predicate", "entities_traits_and_specifications.html#Using", null ],
        [ "Publishing", "entities_traits_and_specifications.html#Publishing", null ],
        [ "Descriptions", "entities_traits_and_specifications.html#Descriptions", null ]
      ] ],
      [ "Mapping to Native Types", "entities_traits_and_specifications.html#specification_mapping", [
        [ "Picking Which Traits to Use", "entities_traits_and_specifications.html#specification_selection", null ]
      ] ]
    ] ],
    [ "Examples", "examples.html", [
      [ "Initializing the API in a Host", "examples.html#examples_api_initialization", null ],
      [ "Setting up a Manager", "examples.html#examples_picking_a_manager", null ],
      [ "Resolving a Reference", "examples.html#examples_resolving_a_reference", null ],
      [ "Publishing a File", "examples.html#example_publishing_a_file", null ],
      [ "Generating a Thumbnail During Publish", "examples.html#example_generating_a_thumbnail", null ]
    ] ],
    [ "Notes for API Host Developers", "notes_for_hosts.html", [
      [ "Architecture Summary", "notes_for_hosts.html#host_architecture", null ],
      [ "Recommended Reading", "notes_for_hosts.html#host_reading", null ],
      [ "Implementation Check List", "notes_for_hosts.html#host_todo", [
        [ "Required for Simple Resolution", "notes_for_hosts.html#host_todo_required_resolution", null ],
        [ "Required for Publishing", "notes_for_hosts.html#host_todo_required_publishing", null ],
        [ "Recommended", "notes_for_hosts.html#host_todo_recommended", null ]
      ] ]
    ] ],
    [ "Notes for Asset System Integrators", "notes_for_managers.html", [
      [ "Architecture Summary", "notes_for_managers.html#manager_architecture_summary", null ],
      [ "Implementation Check List", "notes_for_managers.html#manager_todo", [
        [ "Required for Resolution Only", "notes_for_managers.html#manager_todo_basic_resolution", null ],
        [ "Required for Publishing", "notes_for_managers.html#manager_todo_publishing", null ],
        [ "Supporting Relationships", "notes_for_managers.html#manager_todo_related_entities", null ],
        [ "Embedding Custom UI Within the Host", "notes_for_managers.html#manager_todo_ui", null ]
      ] ],
      [ "Recommended Reading", "notes_for_managers.html#manager_reading", null ]
    ] ],
    [ "Glossary", "glossary.html", [
      [ "Asset Management System", "glossary.html#asset_management_system", null ],
      [ "Context", "glossary.html#Context", null ],
      [ "Digital Contentent Creation tool (DCC)", "glossary.html#DCC", null ],
      [ "entity", "glossary.html#entity", null ],
      [ "Entity Reference", "glossary.html#entity_reference", null ],
      [ "host", "glossary.html#host", null ],
      [ "HostInterface", "glossary.html#HostInterface", null ],
      [ "locale", "glossary.html#locale", null ],
      [ "ManagerInterface", "glossary.html#ManagerInterface", null ],
      [ "Manager Plugin", "glossary.html#PythonPluginSystemManagerPlugin", null ],
      [ "$OPENASSETIO_DEFAULT_CONFIG", "glossary.html#default_config_var", null ],
      [ "$OPENASSETIO_PLUGIN_PATH", "glossary.html#plugin_path_var", null ],
      [ "$OPENASSETIO_LOGGING_SEVERITY", "glossary.html#logging_severity_var", null ],
      [ "Manager State", "glossary.html#manager_state", null ],
      [ "Meta-version", "glossary.html#meta_version", null ],
      [ "manager", "glossary.html#manager", null ],
      [ "preflight", "glossary.html#preflight", null ],
      [ "publish", "glossary.html#publish", null ],
      [ "register", "glossary.html#register", null ],
      [ "resolve", "glossary.html#resolve", null ],
      [ "Specification", "glossary.html#Specification", null ],
      [ "Trait", "glossary.html#trait", null ],
      [ "Trait Set", "glossary.html#trait_set", null ]
    ] ],
    [ "Stable Entity Resolution", "stable_resolution.html", [
      [ "Overview", "stable_resolution.html#stable_resolution_overview", null ],
      [ "Manager State", "stable_resolution.html#stable_resolution_manager_state", null ],
      [ "Distributed Processing", "stable_resolution.html#stable_resolution_manager_state_distribution", null ],
      [ "Implementation Guidelines", "stable_resolution.html#stable_resolution_manager_state_guidelines", null ]
    ] ],
    [ "Testing Your Implementation", "testing.html", [
      [ "Testing Manager Plugins", "testing.html#testing_manager_plugins", [
        [ "The Fixtures File", "testing.html#testing_manager_plugins_fixtures", null ],
        [ "Using the Command Line", "testing.html#testing_manager_plugins_cli", null ],
        [ "Scripting The Test Harness", "testing.html#testing_manager_plugins_api", null ]
      ] ]
    ] ],
    [ "Thumbnails", "thumbnails.html", [
      [ "Overview", "thumbnails.html#thumbnails_overview", null ],
      [ "Requesting Thumbnail Creation", "thumbnails.html#thumbnails_creation_during_publish", null ],
      [ "Looking Up Existing Thumbnails", "thumbnails.html#thumbnails_lookup", null ]
    ] ],
    [ "Todo List", "todo.html", null ],
    [ "Environment Variable List", "envvar.html", null ],
    [ "Modules", "modules.html", "modules" ],
    [ "Namespace Members", "namespacemembers.html", [
      [ "All", "namespacemembers.html", null ],
      [ "Functions", "namespacemembers_func.html", null ],
      [ "Variables", "namespacemembers_vars.html", null ],
      [ "Typedefs", "namespacemembers_type.html", null ],
      [ "Enumerations", "namespacemembers_enum.html", null ]
    ] ],
    [ "Classes", "annotated.html", [
      [ "Class List", "annotated.html", "annotated_dup" ],
      [ "Class Index", "classes.html", null ],
      [ "Class Hierarchy", "hierarchy.html", "hierarchy" ],
      [ "Class Members", "functions.html", [
        [ "All", "functions.html", "functions_dup" ],
        [ "Functions", "functions_func.html", "functions_func" ],
        [ "Variables", "functions_vars.html", null ],
        [ "Typedefs", "functions_type.html", null ],
        [ "Enumerations", "functions_enum.html", null ]
      ] ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"annotated.html",
"classopenassetio_1_1v1_1_1host_api_1_1_manager.html#a951a0ebcb54c4abd6f7a13325e514021",
"group__oa__host_api___manager.html#gad0220c0c96b94354c24d10e112586c6b"
];

var SYNCONMSG = 'click to disable panel synchronisation';
var SYNCOFFMSG = 'click to enable panel synchronisation';