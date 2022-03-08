
# Simple blob resolve

### Option 1: std::optional forgiveness
```c++
try {
  auto url = BlobTrait(data).getUrl().value();
} catch (std::bad_optional_access&) {
// Handle error that should never happen.
}
```

### Option 2: std::optional permission
```c++
auto maybeUrl = BlobTrait(data).getUrl();
if (!maybeUrl.has_value()) {
  throw SomeException();
}
auto url = maybeUrl.value()
```

### Option 3: Ask permission from API
```c++
auto trait = BlobTrait(data);
if (trait.hasUrl()) {
  throw SomeException();
}
auto url = trait.getUrl();
```

### Option 4: Ask forgiveness from wrapped iterator
```c++
auto trait = BlobTrait(data);
auto urlIter = trait.findUrl()
try {
  auto url = *urlIter;
} catch (openassetio::BadIterator&) {
// Handle exception that should never happen.
}
```

### Option 5: Ask permission from wrapped iterator

```c++
auto trait = BlobTrait(data);
auto urlIter = trait.findUrl()
if (urlIter.isValid())) {
  throw SomeException();
}
auto url = trait.getFromIter(urlIter);
```

### Option 6: Out parameter and boolean return

See e.g.: 
* [UsdAttribute::Get](https://graphics.pixar.com/usd/release/api/class_usd_attribute.html#a9d41bc223be86408ba7d7f74df7c35a9)
* [UsdClipsAPI::GetClips](https://graphics.pixar.com/usd/release/api/class_usd_clips_a_p_i.html#a94d6e4d856cc3a92aae45953b9e942a6)

USD Attributes support out parameters, `HasValue`/bool conversion, and 
default (fallback) values. In Python there is no support for out 
parameters.

```c++
string url;
if (!BlobTrait(data).getUrl(&url)) {
  throw SomeException();
}
```

# Blob resolve with optional colorspace with default

### Option 1: std::optional forgiveness
```c++
try {
  auto url = BlobTrait(data).getUrl().value();
  auto colorSpace = ImageTrait(data).getColorSpace().value_or(
      "default_color_space");
} catch (std::bad_optional_access&) {
// Handle error that should never happen.
}
```

### Option 2: std::optional permission

```c++
string url;
string colorSpace;

auto maybeUrl = BlobTrait(data).getUrl();
if (!maybeUrl) {
  throw SomeException();
}

auto maybeColorSpace = ImageTrait(data).getColorSpace();
if (maybeColorSpace) {
  colorSpace = *maybeColorSpace''
} else {
  colorSpace = "default_color_space";
}
```

### Option 3: Ask permission from API
```c++
auto blob = BlobTrait(data);
if (!blob.hasUrl()) {
  throw SomeException();
}
auto url = blob.getUrl();

colorSpace = "default_color_space";
auto image = ImageTrait(data);
if (image.hasColorSpace()) {
  colorSpace = image.getColorSpace();
}
```

### Option 5: Ask permission from wrapped iterator

```c++
auto blob = BlobTrait(data);
auto urlIter = blob.findUrl()
if (urlIter.isValid())) {
  throw SomeException();
}
auto url = blob.getFromIter(urlIter);

colorSpace = "default_color_space";
auto image = BlobTrait(data);
auto imageIter = blob.findUrl()
if (imageIter.isValid())) {
  throw SomeException();
}
auto url = image.getFromIter(imageIter);
```

### Option 6: Out parameter and boolean return

```c++
string url;
string colorSpace;
if (!BlobTrait(data).getUrl(&url)) {
  throw SomeException();
}
if (!ImageTrait(data).getColorSpace(&colorSpace)) {
  colorSpace = "default_color_space";
}
```

```python
url = BlobTrait(data).getUrl()
if url is None:
  raise SomeException()

color_space = ImageTrait(data).getColorSpace()
if color_space is None:
  color_space = "default_color_space"
```

# OTIO image sequence resolve

### Option 1: std::optional forgiveness
```c++

OTIOTrait otio(data);
BlobTrait blob(data);


try {
  string url = *blob.getUrl();
  
  int start_frame = *otio.getStartFrame();
  int frame_step = *otio.getFrameStep();
  int rate = *otio.getRate();
  string target_url_base = *otio.getTargetUrlBase();
  string name_prefix = *otio.getNamePrefix();
  string name_suffix = *otio.getNameSuffix();
  int frame_zero_padding = *otio.getFrameZeroPadding();
} catch (std::bad_optional_access&) {
  throw SomeException();
}
``` 

### Option 6: Out parameter and boolean return
```c++

OTIOTrait otio(data);
BlobTrait blob(data);
string url;
int start_frame;
int frame_step;
int rate;
string target_url_base;
string name_prefix;
string name_suffix;
int frame_zero_padding;

if (!blob.getUrl(&url)) {
  throw SomeException();
}

if (!otio.getStartFrame(&start_frame) || 
    !otio.getFrameStep(&frame_step) ||
    !otio.getRate(&rate) ||
    !otio.getTargetUrlBase(&target_url_base) ||
    !otio.getNamePrefix(&name_prefix) ||
    !otio.getNameSuffix(&name_suffix) ||
    !otio.getFrameZeroPadding(&frame_zero_padding)) {
      throw SomeException();
}
``` 


# Nuke Read node knobs trait

### Option 1: std::optional forgiveness
```c++
NukeReadNodeTrait nuke{data};
BlobTrait blob(data);

try {
  op->knob("file").set_value(*blob.getUrl());
} catch (std::bad_optional_access&) {
  throw SomeException();
}

if(auto maybeLocalizationPolicy = nuke.getLocalisationPolicy()) {
  op->knob("localizationPolicy").set_value(*maybeLocalizationPolicy);
}
if(auto maybeUpdateLocalization = nuke.getUpdateLocalisation()) {
  op->knob("updateLocalization").set_value(*maybeUpdateLocalization);
}
if(auto maybeProxy = nuke.getProxy()) {
  op->knob("proxy").set_value(*maybeProxy);
}
// ... many many more
``` 

### Option 6: Out parameter and boolean return

```c++
NukeReadNodeTrait nuke{data};
BlobTrait blob(data);

string file;
int localizationPolicy;
bool updateLocalization
string proxy;

if (!blob.getUrl(&file)) {
  throw SomeException();
}

if(nuke.getLocalisationPolicy(&localizationPolicy)) {
  op->knob("localizationPolicy").set_value(localizationPolicy);
}
if(nuke.getUpdateLocalisation(&updateLocalization)) {
  op->knob("updateLocalization").set_value(updateLocalization);
}
if(nuke.getProxy(&proxy)) {
  op->knob("proxy").set_value(proxy);
}

// ... many many more
``` 

```c++
NukeReadNodeTrait nuke{data};
BlobTrait blob(data);

if (!blob.getUrl(&file)) {
  throw SomeException();
}

nuke.getLocalisationPolicy(&m_localizationPolicy);
nuke.getUpdateLocalisation(&m_updateLocalization);
nuke.getProxy(&m_proxy);

// ... many many more
``` 
