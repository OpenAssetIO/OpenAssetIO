# simpleResolver.py

A simple python CLI that uses OpenAssetIO to resolve a supplied Entity
Reference for some specified traits to JSON data.

It illustrates a "bare minimum" host implementation, that makes use of
the default OpenAssetIO config mechanism to initialize a pre-configured
manager.

## Usage

```
./simpleResolver.py --help
usage: simpleResolver.py [-h] traitset entityref

positional arguments:
  traitset    A comma separated list of traits to resolve eg: trati1,trait2
  entityref   An entity reference to resolve

optional arguments:
  -h, --help  show this help message and exit
```

## Example

The included OpenAssetIO config file sets the API up to use the
[BasicAssetLibrary](../../manager/BasicAssetLibrary) example asset
manager, with a simple library containing information about some
random animals.

We can then use the CLI resolver to query this information.

First off, set your working directory to this folder:

```bash
cd resources/examples/host/simpeResolver
```

The CLI doesn't have any configuration options itself, it makes use of
the [default manager](https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1v1_1_1host_api_1_1_manager_factory.html#a8b6c44543faebcb1b441bbf63c064c76)
mechanism. We need to tell OpenAssetIO which config file to use:

```bash
export OPENASSETIO_DEFAULT_CONFIG=bal_animals_openassetio_config.toml
```

This will tell the API to use BAL, we need to configure the environment
to add it's plugin to the plugin system search paths:

```bash
export OPENASSETIO_PLUGIN_PATH=../../manager/BasicAssetLibrary/plugin
```

At this point, we can now use the CLI to resolve entity data.
The sample library has two entities `bal:///cat` and `bal:///dog`.

The first argument to the CLI is a list of [traits](https://openassetio.github.io/OpenAssetIO/entities_traits_and_specifications.html)
to resolve for, the second is the entity reference to resolve:

```bash
python ./simpleResolver.py animal,named bal:///cat
python ./simpleResolver.py locatableContent bal:///cat
```

### Tips and tricks

As output is in JSON format, if you have tools such as
[`jq`](https://github.com/stedolan/jq) available, you can do fun things
with it (assuming linux/macOS).

Pretty print the output:

```bash
python ./simpleResolver.py animal bal:///cat | jq
```

Extract the name:

```bash
python ./simpleResolver.py named bal:///cat | jq -r '.named.name'
```

ASCII art for the win!

```bash
python ./simpleResolver.py locatableContent bal:///cat | jq -r '.locatableContent.url' | xargs jp2a
```
