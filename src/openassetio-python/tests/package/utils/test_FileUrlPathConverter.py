#
#   Copyright 2023 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Tests that cover the FileUrlPathConverter utility.
"""
import collections
import json
import os
import re
from pathlib import Path

# pylint: disable=invalid-name,redefined-outer-name, too-few-public-methods
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio import utils
from openassetio.errors import InputValidationException
from openassetio.utils import PathType


URLMap = collections.namedtuple("URLMap", ("path_type", "path", "url"))

relative_path_error_message = "Relative paths cannot be converted to a URL ('{}')"
non_file_scheme_error_message = "Must be a 'file' scheme URL ('{}')"
server_invalid_on_posix_error_message = (
    "Server name components are invalid on POSIX for file scheme URLs ('{}')"
)

error_messages = {
    "relative-path": "Path is relative ('{}')",
    "empty-input": "Path is empty",
    "invalid-namespaced-path": "Path is ill-formed ('{}')",
    "invalid-hostname": "Path references an invalid hostname ('{}')",
    "unsupported-namespaced-path": "Unsupported Win32 device path ('{}')",
    "upwards-traversal": "Path contains upwards traversal ('{}')",
    "null-byte": "Path contains NULL bytes",
    "unsupported-non-local-file": "Unsupported non-local file ('{}')",
    "not-a-file-url": "Not a file URL ('{}')",
    "encoded-separator": "Percent-encoded path separator ('{}')",
    "unsupported-hostname": "Unsupported hostname ('{}')",
}


class Test_pathToUrl:
    def test_posix(self, subtests, file_path_to_url_json, url_path_converter):
        for case in file_path_to_url_json:
            with subtests.test(msg=case["comment"], path=case["file_path"], url=case["URL_posix"]):
                self.assert_expected_url(
                    URLMap(
                        PathType.kPOSIX,
                        case["file_path"],
                        str_or_error(case["URL_posix"], case["file_path"]),
                    ),
                    url_path_converter,
                )

    def test_windows(self, subtests, file_path_to_url_json, url_path_converter):
        for case in file_path_to_url_json:
            with subtests.test(
                msg=case["comment"], path=case["file_path"], url=case["URL_windows"]
            ):
                self.assert_expected_url(
                    URLMap(
                        PathType.kWindows,
                        case["file_path"],
                        str_or_error(case["URL_windows"], case["file_path"]),
                    ),
                    url_path_converter,
                )

    def assert_expected_url(self, url_map, url_path_converter):
        os_path_type = PathType.kWindows if os.name == "nt" else PathType.kPOSIX

        # Happy.
        if isinstance(url_map.path, str) and isinstance(url_map.url, str):
            assert url_path_converter.pathToUrl(url_map.path, url_map.path_type) == url_map.url

            if os_path_type == url_map.path_type:
                assert url_path_converter.pathToUrl(url_map.path, PathType.kSystem) == url_map.url
                assert url_path_converter.pathToUrl(url_map.path) == url_map.url

        # Bad path.
        elif isinstance(url_map.path, str) and isinstance(url_map.url, Exception):

            with pytest.raises(type(url_map.url), match=exc_to_regex(url_map.url)):
                _unexpected = url_path_converter.pathToUrl(url_map.path, url_map.path_type)

            if os_path_type == url_map.path_type:
                with pytest.raises(type(url_map.url), match=exc_to_regex(url_map.url)):
                    url_path_converter.pathToUrl(url_map.path, PathType.kSystem)
                with pytest.raises(type(url_map.url), match=exc_to_regex(url_map.url)):
                    url_path_converter.pathToUrl(url_map.path)
        else:
            raise RuntimeError("Unhandled URL mapping")


class Test_pathFromUrl:
    def test_common(self, url_path_converter):
        with pytest.raises(InputValidationException, match="Invalid URL"):
            url_path_converter.pathFromUrl("file://^")

    def test_posix(self, subtests, url_to_file_path_json, url_path_converter):
        for case in url_to_file_path_json:
            with subtests.test(msg=case["comment"], path=case["file_path_posix"], url=case["URL"]):
                self.assert_expected_path(
                    URLMap(
                        PathType.kPOSIX,
                        str_or_error(case["file_path_posix"], case["URL"]),
                        case["URL"],
                    ),
                    url_path_converter,
                )

    def test_windows(self, subtests, url_to_file_path_json, url_path_converter):
        for case in url_to_file_path_json:
            with subtests.test(
                msg=case["comment"], path=case["file_path_windows"], url=case["URL"]
            ):
                self.assert_expected_path(
                    URLMap(
                        PathType.kWindows,
                        str_or_error(case["file_path_windows"], case["URL"]),
                        case["URL"],
                    ),
                    url_path_converter,
                )

    def assert_expected_path(self, url_map, url_path_converter):
        os_path_type = PathType.kWindows if os.name == "nt" else PathType.kPOSIX

        # Happy.
        if isinstance(url_map.path, str) and isinstance(url_map.url, str):
            assert url_path_converter.pathFromUrl(url_map.url, url_map.path_type) == url_map.path

            if os_path_type == url_map.path_type:
                assert (
                    url_path_converter.pathFromUrl(url_map.url, PathType.kSystem) == url_map.path
                )
                assert url_path_converter.pathFromUrl(url_map.url) == url_map.path

        # Bad URL.
        elif isinstance(url_map.path, Exception) and isinstance(url_map.url, str):
            with pytest.raises(type(url_map.path), match=exc_to_regex(url_map.path)):
                _ = url_path_converter.pathFromUrl(url_map.url, url_map.path_type)

            if os_path_type == url_map.path_type:
                with pytest.raises(type(url_map.path), match=exc_to_regex(url_map.path)):
                    url_path_converter.pathFromUrl(url_map.url, PathType.kSystem)
                with pytest.raises(type(url_map.path), match=exc_to_regex(url_map.path)):
                    url_path_converter.pathFromUrl(url_map.url)

        else:
            raise RuntimeError("Unhandled URL mapping")


def exc_to_regex(exc):
    return re.escape(str(exc))


def str_or_error(maybe_error, path_or_url):
    if isinstance(maybe_error, dict):
        return InputValidationException(
            error_messages[maybe_error["failure-reason"]].format(path_or_url)
        )
    return maybe_error


# "module" scope to ensure we test re-using long-lived instance.
@pytest.fixture(scope="module")
def url_path_converter():
    return utils.FileUrlPathConverter()


@pytest.fixture
def file_path_to_url_json(file_url_path_tests_json):
    return (
        case for case in file_url_path_tests_json["file_path_to_url"] if "__section__" not in case
    )


@pytest.fixture
def url_to_file_path_json(file_url_path_tests_json):
    return (
        case for case in file_url_path_tests_json["url_to_file_path"] if "__section__" not in case
    )


@pytest.fixture(scope="session")
def file_url_path_tests_json():
    with open(
        Path(__file__).parent / "resources" / "file_url_path_tests.json", "r", encoding="utf-8"
    ) as json_file:
        return json.load(json_file)
