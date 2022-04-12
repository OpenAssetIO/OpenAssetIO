# OpenAssetIO User Personas

> Note: This page is a WIP, please add/suggest omissions through PR

As a project, the majority of OpenAssetIO users are software developers.
We count a "user" as someone who interacts with the code base and/or
distribution, rather than with any higher-order functionality exposed by
an application integrating the API.

-   [Commercial DCC tool author](#commercial-dcc-tool-author)
-   [Proprietary DCC tool author](#proprietary-dcc-tool-author)
-   [Proprietary DAM/AMS/PT system author](#proprietary-damamspt-system-author)
-   [Commercial DAM/AMS/PT system author](#commercial-damamspt-system-author)
-   [Pipeline Technical Director (TD)](#pipeline-technical-director-td)

## Commercial DCC tool author

> DCC: Digital Content Creation, usually used to refer to tools such as
> Houdini, Nuke, Katana, Mari, Maya, Photoshop, ZBrush, et. al. that are
> used within the Media Creation sector to produce digital equivalents
> of the traditional mediums for making 2D/3D artwork/models. Known as a
> "host" in OpenAssetIO speak.

These developers predominantly work as part of a larger team,
maintaining desktop applications that typically run on desktop operating
systems. These applications themselves often act as a closed platform
for end user and plugin developers. Most of these developers work for an
ISV (Independent Software Vendor) who license their products through a
perpetual licence

-   annual maintenance or subscription model. Releases of their tools are
    usually a mix of iterative refinement and headline feature development
    to drive the sales cycle. As such, release windows are subject to
    influence by many commercial and technical factors.

These products are extensively customized in the field when deployed and
are required to provide robust, stable API surface areas to facilitate
extension and automation. They usually exist as "islands", and their
customers connect them together to form a pipeline, through proprietary
code using these APIs. There are also some commercial or open source
pipeline projects.

-   **OpenAssetIO API alignment:** Host
-   **Languages:** C, C++, Python, Lua
-   **Platforms:** Linux, Windows, macOS
-   **Frameworks:** STL, Qt, ImGui, proprietary, boost, pybind, pyside
-   **Codebase age:** Can be 20y+
-   **Ability to adopt new language standards:** Mixed, target platform
    limitations (eg: https://vfxplatform.com), codebase/toolchain age.
    Control over public API surface may make internal adoption easier.

Interested in:

-   Stable, robust, documented APIs.
-   Ways to abstract specific customer requirements.
-   Multi-platform compatibility.
-   Wide-spread adoption.
-   Delegating risk.

Uses OpenAssetIO to:

-   Build high-value asset-centric workflows by interacting with an
    asset management system directly, in a broadly compatible,
    manager-agnostic way.
-   Reduce cost/friction of pipeline integration and adoption of their
    product.
-   Help facilitate document portability.

## Proprietary DCC tool author

Similar to the commercial DCC tool author with some notable exceptions,
generally afforded by their target audience being an "in house crowd" vs
a broader range of public users.

-   Releases and functionality is often driven by specific internal
    deadlines/workflow requirements vs the need to create "perceived
    value" in the context of a broader commercial value proposition.
-   Target platforms and technologies can be more focused to a
    well-known set of users and scenarios vs having to generalize to a
    public user base
-   The approach to software development _may_ be more pragmatic than in
    a commercial engineering setting as allowed by a highly managed
    deployment environment.

Interested in:

-   Stable, robust, documented APIs.
-   Flexibility and ability to customize to specific needs.
-   Speeding up workflows or reducing cost of delivery.

Uses OpenAssetIO to:

-   Abstract their tool from the specifics of the current pipeline, to
    facilitate evolution or evaluation of alternatives.

## Proprietary DAM/AMS/PT system author

> DAM: Digital Asset Manager, AMS: Asset Management System, PT:
> Production tracking. Systems that form an authoritative source of
> truth for the state and location of data within a media creation
> production pipeline. Known as a "manager" in OpenAssetIO speak.

These developers work as part of an in-house team delivering the
production critical systems used within Media Creation environments such
as visual effects houses and animation studios. Similarly to the
proprietary tool developer, the main drive is to deliver specific
internal deadlines and workflow requirements.

Historically, the pipeline supported by these systems has been the
"secret sauce" forming the competitive advantage for any particular
business, by allowing forecasting and delivery to be as efficient as
possible. As such, the systems developed are often tightly coupled to a
particular companies business processes, and require deep integration
into artist tooling.

These systems are often a mix of centralized and decentralized
databases, distributed processing management, web services,
in-application plugins and extensions and miscellaneous glue code in a
variety of languages.

-   **OpenAssetIO API alignment:** Manager
-   **Languages:** JavaScript, C++, Python, Lua, CSS, HTML, \*SQL,
    GraphQL. Rust is anticipated as a target in coming years.
-   **Platforms:** Linux, Windows, macOS
-   **Frameworks:** STL, Qt, Node.js, React, Svelt, pyside, modern web
    and db stuff.
-   **Codebase age:** Can be 20y+
-   **Ability to adopt new language standards:** Mixed, there is often a
    service architecture de-coupling the in-application code from the
    storage back-end. In-application code however is often tied to the
    target tool versions. The sheer volume of code written, often by a
    small team, can also make updating to new technologies somewhat
    challenging (see the retirement of Python 2.6 in the sector). They
    also generally operate with a [TPN](https://www.ttpn.org) hardened
    environment, which places stringent restrictions on off-network
    activities.

Interested in:

-   Stable, robust, documented APIs.
-   Flexibility and ability to customize to specific needs.
-   Speeding up workflows or reducing cost of delivery.
-   Facilitating interoperability between tools.
-   Distributed and scalable systems.

Uses OpenAssetIO to:

-   Minimize the cost of integrating their custom solution into other
    software and DCC tools.

## Commercial DAM/AMS/PT system author

Similar to the in-house management system authors but with a commercial
focus. Their products are often designed to form off-the-shelf solutions
for customers who don't want (or don't have the inclination for) the
risk/resourcing overhead of developing their own. Notable differences:

-   As they have to satisfy a larger audience, the matrix of target
    applications and deployment platforms/scenarios may well be somewhat
    larger.
-   In recent years, many commercial managers have switched to a
    Software-as-a-Service (SaaS) model. Amongst other factors, the task
    of updating customer deployments within [TPN](https://www.ttpn.org)
    hardened networks is a huge support challenge.
-   Vendors supporting the SaaS model may well be taking advantage of
    modern Platform-as-a-Service (PasS) and SaaS solutions for
    database/storage etc such as those provided by Amazon, Google, Azure
    et. al.
-   For reasons of consensus, these tools may be somewhat less
    encompassing and still require a significant amount of proprietary
    development by their customers to fully integrate into their
    workflows. For this they are required to provide stable, and robust
    APIs as well as end-user functionality.
-   Codebases _may_ be much newer, than the proprietary ones.

Interested in:

-   Stable, robust, documented APIs.
-   Ways to abstract specific customer requirements.
-   Reducing the integration cost for customers.
-   Reducing the number of permutations in the integration matrix.
-   Facilitating interoperability between tools.
-   Distributed and scalable systems.

Uses OpenAssetIO to:

-   Minimize the cost of integrating their product into other software
    and DCC tools.

## Pipeline Technical Director (TD)

> Pipeline: The overarching term used to describe the systems that
> manage data and work as it moved between artists within media creation
> facilities.

These developers work as part of an in-house team to solve technical
challenges that arise during the delivery of a project. They may well
also be part of a team with the Proprietary DAM/AMS/PT system authors
described above. Though often more focused towards project-specific
deliverables, they also contribute to the general maintenance and
development of the pipeline itself.

When working under the broader remit, and on more immediate solutions,
their work may tend towards higher-level APIs and scripts over low-level
frameworks and shared library development. This means that from the
perspective of OpenAssetIO they may quickly jump from the host API to
the manager API. E.g, using the host API to quickly build scripts to
deal with data or asset management tasks. Maybe to support an ad-hoc
workflow required by a particular task that doesn't fit into the general
pipeline.

> There is debate as to whether they would use an abstraction such as
> OpenAssetIO over the first-class native SDK of the pipeline, but as it
> is a possibility, we should consider it.

-   **OpenAssetIO API alignment:** Manager, Host
-   **Languages:** Python, Lua, CSS, HTML, \*SQL, GraphQL. Rust has
    started to pick up momentum in some studios.
-   **Platforms:** Linux, Windows, macOS
-   **Frameworks:** Qt, pyside, database technologies
-   **Codebase age:** From short-lived to long term depending on
    specific tasks.
-   **Ability to adopt new language standards:** Mixed, often
    constrained by technology choices that exist within the pipeline
    itself, however new solutions may be free to innovate as required to
    solve a specific need.

Interested in:

-   Simple, easy to us, stable, robust, documented APIs.
-   Ways to solve a problem quickly.
-   Interoperability between tools.
-   Automation.
-   Availability of tools via common scripting languages.

Uses OpenAssetIO to:

-   Quickly build tools and scripts that interact with asset management
    systems to solve production problems.
-   Bridge between multiple independent asset management systems where
    OpenAssetIO is a common API.
