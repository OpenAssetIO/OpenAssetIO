// Copyright 2013-2021 [The Foundry Visionmongers Ltd]
// SPDX-License-Identifier: Apache-2.0
/**
 * GitHub Action to execute pylint and annotate discovered issues.
 *
 * Can be configured with severity levels to disable, the location of
 * a pylint config file, as well as the paths to scan.
 *
 * The number of issues of each severity level is reported in the action
 * log/summary, followed by annotations for individual issues associated
 * to the appropriate source line in the codebase.
 */

const core = require('@actions/core');
const exec = require('@actions/exec');

/**
 * Execute pylint and report issues, if any found.
 */
async function run() {
    let pylintOutput = "";  // Pylint process output.
    const pylintDisable = core.getInput('pylint-disable') || "";
    const pylintRCFile = core.getInput('pylint-rcfile') || "";
    const pylintPaths = core.getInput('pylint-paths');

    try {
        // Run pylint
        await exec.exec("pylint", [
            `--disable=${pylintDisable}`,
            `--rcfile=${pylintRCFile}`,
            `--output-format=json`,
            ...pylintPaths.split(" ")
        ], {
            listeners: {
                stdout: (data) => pylintOutput += data.toString()
            }
        });
    } catch (pylintError) {
        try {
            reportResults(JSON.parse(pylintOutput), pylintDisable);
        } catch (reportingError) {
            // The exception thrown by `exec` doesn't include the exit
            // code as a field (we'd have to parse the error message).
            // So report the pylint process error here as well, in case
            // that was the root cause for `reportResults` failing.
            console.error(pylintError);
            console.error(reportingError);
        }
    }
}

/**
 * Create GitHub annotations and set the action to failed.
 *
 * Report a summary followed by per-line annotations.
 *
 * @param pylintMessages List of Pylint messages decoded from JSON.
 * @param pylintDisable Disabled checks to add to summary, potentially
 *  useful for debugging.
 *
 */
function reportResults(pylintMessages, pylintDisable) {
    const pylintErrors = pylintMessages.filter(message => message.type === 'error');
    const pylintWarnings = pylintMessages.filter(message => message.type === 'warning');
    const pylintConvention = pylintMessages.filter(message => message.type === 'convention');
    const pylintRefactor = pylintMessages.filter(message => message.type === 'refactor');
    const pylintInfo = pylintMessages.filter(message => message.type === 'info');

    // Construct summary report.

    let summaryTitle = "Pylint linter issues detected";
    if (pylintDisable) {
        summaryTitle += ` (disabled checks '${pylintDisable}')`;
    }
    const summaryLines = [summaryTitle];

    const appendToSummaryIfNonEmpty = (messages, severity) => messages.length &&
        summaryLines.push(`${messages.length} ${severity}`);

    appendToSummaryIfNonEmpty(pylintErrors, "error");
    appendToSummaryIfNonEmpty(pylintWarnings, "warning");
    appendToSummaryIfNonEmpty(pylintConvention, "convention");
    appendToSummaryIfNonEmpty(pylintRefactor, "refactor");
    appendToSummaryIfNonEmpty(pylintInfo, "info");

    core.setFailed(summaryLines.join("\n\n"));

    // Annotate individual issues.

    pylintErrors.forEach(
        message => core.error(
            annotationMessage(message),
            annotationProperties(message)));

    [...pylintWarnings, ...pylintRefactor, ...pylintConvention].forEach(
        message => core.warning(
            annotationMessage(message),
            annotationProperties(message)));

    pylintInfo.forEach(
        message => core.notice(
            annotationMessage(message),
            annotationProperties(message)));
}

/**
 * Parse a Pylint message into GitHub annotation properties.
 *
 * @param message Pylint message decoded from JSON.
 * @returns core.AnnotationProperties Github annotation properties.
 */
function annotationProperties(message) {
    return {
        title: `Linter ${message.type} ${message['message-id']} (${message.symbol})`,
        file: message.path,
        startLine: message.line,
        endLine: message.line,
        startColumn: message.column,
        endColumn: message.column
    };
}

/**
 * Parse a Pylint message into a GitHub annotation message.
 *
 * @param message Pylint message encoded as JSON.e
 * @returns string Message to display on annotation.
 */
function annotationMessage(message) {
    if (message.obj) {
        return `${message.message}\n\n` +
            `${message.obj} (${message.path}:${message.line}:${message.column})`;
    } else {
        return `${message.message}\n\n` +
            `${message.module} (${message.path}:${message.line}:${message.column})`;
    }
}

run();