// SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>
// SPDX-License-Identifier: Apache-2.0

/*
 * pytest-jux Architecture (C4 Model)
 *
 * Client-side pytest plugin for signing and publishing JUnit XML test reports.
 * Since Sprint 9, most modules are thin wrappers re-exporting from py-juxlib.
 *
 * Version: 0.6.0
 */

workspace "pytest-jux" "Client-side pytest plugin for signing and publishing JUnit XML test reports" {

    model {
        # People
        developer = person "Developer" "Software developer running pytest test suites"
        sysadmin = person "System Administrator" "Infrastructure engineer managing test reporting"

        # External Systems
        pytest = softwareSystem "pytest" "Python testing framework that executes tests and generates JUnit XML reports" "External System"
        pyJuxlib = softwareSystem "py-juxlib" "Shared client library: metadata, signing, config, storage, API" "External System"
        juxApiServer = softwareSystem "Jux API Server" "Server-side backend for receiving, verifying, and storing signed test reports" "External System"
        cicdPipeline = softwareSystem "CI/CD Pipeline" "Continuous integration system (GitHub Actions, GitLab CI, Jenkins)" "External System"

        # pytest-jux System
        pytestJux = softwareSystem "pytest-jux" "Client-side pytest plugin for signing and publishing JUnit XML test reports" {

            pytestPlugin = container "pytest Plugin" "pytest hook integration for automated report processing" "Python 3.11+" "Plugin" {
                pluginHooks = component "Plugin Hooks" "pytest hook implementations (addoption, configure, metadata, sessionfinish)" "Python module (plugin.py)"
                signer = component "XML Signer" "Re-exports sign_xml(), load_private_key() from py-juxlib" "Python module (signer.py)"
                verifier = component "Signature Verifier" "Re-exports verify_signature(), verify_with_certificate() from py-juxlib" "Python module (verifier.py)"
                canonicalizer = component "XML Canonicalizer" "Re-exports canonicalize_xml(), compute_canonical_hash() from py-juxlib" "Python module (canonicalizer.py)"
                configManager = component "Configuration Manager" "Re-exports ConfigurationManager, StorageMode from py-juxlib" "Python module (config.py)"
                metadataCollector = component "Metadata Collector" "EnvironmentMetadata subclass with pytest-specific properties" "Python module (metadata.py)"
                storageManager = component "Storage Manager" "Re-exports ReportStorage from py-juxlib (XDG-compliant, 4 modes)" "Python module (storage.py)"
                apiClient = component "API Client" "Re-exports JuxAPIClient, PublishResponse from py-juxlib" "Python module (api_client.py)"
                errorHandler = component "Error Handler" "JuxError hierarchy with error codes and user-friendly messages" "Python module (errors.py)"

                pluginHooks -> signer "Signs report with"
                pluginHooks -> metadataCollector "Injects metadata via pytest_metadata hook"
                pluginHooks -> storageManager "Stores locally via"
                pluginHooks -> apiClient "Publishes via"
                pluginHooks -> configManager "Reads configuration from"

                signer -> canonicalizer "Canonicalizes XML with"
                verifier -> canonicalizer "Verifies hash with"

                storageManager -> configManager "Uses storage config from"
                apiClient -> configManager "Uses API config from"
            }

            cliTools = container "CLI Tools" "Standalone command-line utilities for manual operations" "Python 3.11+" "CLI" {
                keygenCmd = component "jux-keygen" "Generate RSA/ECDSA signing keys with certificates" "Python CLI (commands/keygen.py)"
                signCmd = component "jux-sign" "Offline signing of JUnit XML reports" "Python CLI (commands/sign.py)"
                verifyCmd = component "jux-verify" "Signature verification for signed reports" "Python CLI (commands/verify.py)"
                inspectCmd = component "jux-inspect" "Report inspection (metadata, hash, signature)" "Python CLI (commands/inspect.py)"
                cacheCmd = component "jux-cache" "Cache management (list, show, stats, clean)" "Python CLI (commands/cache.py)"
                configCmd = component "jux-config" "Configuration management (init, dump, validate)" "Python CLI (commands/config_cmd.py)"
                publishCmd = component "jux-publish" "Manual publishing to Jux API (single file or queue)" "Python CLI (commands/publish.py)"

                keygenCmd -> signer "Generates keys for"
                signCmd -> signer "Signs reports with"
                signCmd -> canonicalizer "Canonicalizes with"
                verifyCmd -> verifier "Verifies signatures with"
                inspectCmd -> canonicalizer "Computes hash with"
                cacheCmd -> storageManager "Manages cache via"
                configCmd -> configManager "Manages config via"
                publishCmd -> apiClient "Publishes reports via"
                publishCmd -> storageManager "Reads queue from"
            }

            pytestPlugin -> cliTools "Uses shared components" "Python imports"
        }

        # System-level relationships
        developer -> pytest "Runs tests with" "pytest CLI"
        pytest -> pytestJux "Invokes plugin hooks" "pytest_sessionfinish"
        sysadmin -> pytestJux "Configures and manages" "CLI tools"
        pytestJux -> pyJuxlib "Delegates core operations to" "Python import"
        pytestJux -> juxApiServer "Publishes signed reports to" "HTTPS/REST (POST /api/v1/junit/submit)"
        cicdPipeline -> pytest "Executes tests with" "pytest --junit-xml --jux-publish"

        # Container-level relationships
        pytestPlugin -> juxApiServer "Publishes signed reports to" "HTTPS/REST"
        developer -> pytestPlugin "Executes tests via pytest" "pytest hooks"
        developer -> cliTools "Uses offline tools" "CLI commands"
        sysadmin -> pytestPlugin "Configures plugin" "Configuration files"
        sysadmin -> cliTools "Manages keys and reports" "CLI commands"
        pytest -> pytestPlugin "Invokes hooks" "pytest_sessionfinish"
    }

    views {
        systemContext pytestJux "SystemContext" {
            include *
            autolayout lr
            description "pytest-jux in the Jux ecosystem: delegates to py-juxlib, publishes to API server"
        }

        container pytestJux "Containers" {
            include *
            autolayout lr
            description "Plugin container (pytest hooks) and CLI tools container"
        }

        component pytestPlugin "PluginComponents" {
            include *
            autolayout lr
            description "Plugin internals: most modules re-export from py-juxlib"
        }

        component cliTools "CLIComponents" {
            include *
            autolayout tb
            description "Standalone CLI utilities for offline operations"
        }

        dynamic pytestJux "TestExecutionFlow" "Test execution and report signing workflow" {
            developer -> pytestPlugin "1. Runs pytest --junit-xml --jux-publish"
            pytestPlugin -> juxApiServer "2. Signs and publishes report"
            autolayout lr
        }

        dynamic pytestJux "OfflineSigningFlow" "Manual offline signing workflow" {
            sysadmin -> cliTools "1. Generate keys (jux-keygen)"
            sysadmin -> cliTools "2. Sign report (jux-sign)"
            sysadmin -> cliTools "3. Verify signature (jux-verify)"
            autolayout lr
        }

        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
                shape RoundedBox
            }
            element "External System" {
                background #999999
                color #ffffff
            }
            element "Person" {
                background #08427b
                color #ffffff
                shape Person
            }
            element "Container" {
                background #438dd5
                color #ffffff
                shape RoundedBox
            }
            element "Plugin" {
                background #2e7d32
                color #ffffff
            }
            element "CLI" {
                background #f57c00
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
                shape Component
            }
        }

        theme default
    }

    configuration {
        scope softwaresystem
    }
}
