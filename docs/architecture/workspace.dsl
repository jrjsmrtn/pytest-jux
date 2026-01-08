workspace "pytest-jux" "Client-side pytest plugin for signing and publishing JUnit XML test reports" {

    model {
        # People
        developer = person "Developer" "Software developer running pytest test suites"
        sysadmin = person "System Administrator" "Infrastructure engineer managing test reporting"

        # External Systems
        juxApiServer = softwareSystem "Jux API Server" "Server-side backend for receiving, verifying, and storing signed test reports" "External System"

        cicdPipeline = softwareSystem "CI/CD Pipeline" "Continuous integration system (GitHub Actions, GitLab CI, Jenkins)" "External System"

        # pytest-jux System
        pytestJux = softwareSystem "pytest-jux" "Client-side pytest plugin for signing and publishing JUnit XML test reports" {

            # Containers (runtime components)
            pytestPlugin = container "pytest Plugin" "pytest hook integration for automated report processing" "Python 3.11+" "Plugin" {
                # Core Components
                pluginHooks = component "Plugin Hooks" "pytest hook implementations (pytest_sessionfinish)" "Python module (plugin.py)"

                # XML Processing
                signer = component "XML Signer" "Generates XMLDSig signatures using RSA/ECDSA keys" "Python module (signer.py)"
                verifier = component "Signature Verifier" "Verifies XMLDSig signatures on signed reports" "Python module (verifier.py)"
                canonicalizer = component "XML Canonicalizer" "C14N canonicalization and hash computation" "Python module (canonicalizer.py)"

                # Configuration & Metadata
                configManager = component "Configuration Manager" "Multi-source config (CLI, env, files) with precedence" "Python module (config.py)"
                metadataCollector = component "Metadata Collector" "Captures environment metadata and injects into pytest-metadata hook" "Python module (metadata.py)"

                # Storage & Publishing
                storageManager = component "Storage Manager" "XDG-compliant local storage and caching (4 modes)" "Python module (storage.py)"
                apiClient = component "API Client" "REST API client for Jux API v1.0.0 with retry logic" "Python module (api_client.py)"

                # Relationships within plugin
                pluginHooks -> signer "Signs report with"
                pluginHooks -> metadataCollector "Injects metadata via pytest_metadata hook"
                pluginHooks -> storageManager "Stores locally via"
                pluginHooks -> apiClient "Publishes via"

                signer -> canonicalizer "Canonicalizes XML with"
                verifier -> canonicalizer "Verifies hash with"

                pluginHooks -> configManager "Reads configuration from"
                storageManager -> configManager "Uses storage config from"
                apiClient -> configManager "Uses API config from"
            }

            cliTools = container "CLI Tools" "Standalone command-line utilities for manual operations" "Python 3.11+" "CLI" {
                # CLI Components
                keygenCmd = component "jux-keygen" "Generate RSA/ECDSA signing keys with certificates" "Python CLI (commands/keygen.py)"
                signCmd = component "jux-sign" "Offline signing of JUnit XML reports" "Python CLI (commands/sign.py)"
                verifyCmd = component "jux-verify" "Signature verification for signed reports" "Python CLI (commands/verify.py)"
                inspectCmd = component "jux-inspect" "Report inspection (metadata, hash, signature)" "Python CLI (commands/inspect.py)"
                cacheCmd = component "jux-cache" "Cache management (list, show, stats, clean)" "Python CLI (commands/cache.py)"
                configCmd = component "jux-config" "Configuration management (init, dump, validate)" "Python CLI (commands/config_cmd.py)"
                publishCmd = component "jux-publish" "Manual publishing to Jux API (single file or queue)" "Python CLI (commands/publish.py)"

                # CLI tool relationships
                keygenCmd -> signer "Generates keys for" "Uses cryptography library"
                signCmd -> signer "Signs reports with"
                signCmd -> canonicalizer "Canonicalizes with"
                verifyCmd -> verifier "Verifies signatures with"
                inspectCmd -> canonicalizer "Computes hash with"
                cacheCmd -> storageManager "Manages cache via"
                configCmd -> configManager "Manages config via"
                publishCmd -> apiClient "Publishes reports via"
                publishCmd -> storageManager "Reads queue from"
            }

            # Container relationships
            pytestPlugin -> cliTools "Uses shared components" "Python imports"
        }

        # System-level relationships
        developer -> pytestJux "Runs tests with" "pytest CLI"
        sysadmin -> pytestJux "Configures and manages" "CLI tools"

        pytestJux -> juxApiServer "Publishes signed reports to" "HTTPS/REST API (POST /api/v1/junit/submit)"

        cicdPipeline -> pytestJux "Executes tests with" "pytest --junit-xml --jux-publish"

        # Container-level relationships (for dynamic views)
        developer -> pytestPlugin "Executes tests" "pytest CLI"
        developer -> cliTools "Uses offline tools" "CLI commands"
        sysadmin -> pytestPlugin "Configures plugin" "Configuration files"
        sysadmin -> cliTools "Manages keys and reports" "CLI commands"

        # External dependencies (shown as relationships)
        signer -> juxApiServer "References API endpoint" "Configuration only"
    }

    views {
        # System Context View
        systemContext pytestJux "SystemContext" {
            include *
            autolayout lr
            description "System context diagram showing pytest-jux in the Jux ecosystem"
        }

        # Container View
        container pytestJux "Containers" {
            include *
            autolayout lr
            description "Container diagram showing pytest plugin and CLI tools"
        }

        # Component View - pytest Plugin
        component pytestPlugin "PluginComponents" {
            include *
            autolayout lr
            description "Component diagram showing pytest plugin internal structure"
        }

        # Component View - CLI Tools
        component cliTools "CLIComponents" {
            include *
            autolayout tb
            description "Component diagram showing standalone CLI utilities"
        }

        # Dynamic View - Test Execution Flow (Container Level)
        dynamic pytestJux "TestExecutionFlow" "Test execution and report signing workflow" {
            developer -> pytestPlugin "1. Runs pytest --junit-xml --jux-publish"
            pytestPlugin -> juxApiServer "2. Publishes signed report"
            autolayout lr
        }

        # Dynamic View - Offline Signing Flow (Container Level)
        dynamic pytestJux "OfflineSigningFlow" "Manual offline signing workflow" {
            sysadmin -> cliTools "1. Generate keys (jux-keygen)"
            sysadmin -> cliTools "2. Sign report (jux-sign)"
            sysadmin -> cliTools "3. Verify signature (jux-verify)"
            autolayout lr
        }

        # Styling
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
            element "Future" {
                background #cccccc
                color #666666
                opacity 50
            }
        }

        theme default
    }

    configuration {
        scope softwaresystem
    }
}
