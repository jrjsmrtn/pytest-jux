# Tutorial: Custom Signing Workflows

**Build custom signing workflows with the pytest-jux API**

---

## What You'll Learn

By the end of this tutorial, you will:

✅ Use pytest-jux programmatically (Python API)
✅ Implement custom signing workflows
✅ Create custom metadata collectors
✅ Build batch signing processors
✅ Implement custom verification logic
✅ Integrate with external systems

**Time Required**: 30-40 minutes

**Difficulty**: Advanced

**Prerequisites**:
- Completed [First Signed Report](first-signed-report.md) and [Integration Testing](integration-testing.md) tutorials
- Strong Python programming skills
- Understanding of cryptographic concepts
- Familiarity with pytest internals

---

## Tutorial Overview

This tutorial demonstrates advanced pytest-jux usage beyond CLI tools:
- Programmatic signing and verification
- Custom metadata collection
- Batch report processing
- Integration with monitoring systems
- Custom storage backends

**Scenario**: Your organization needs custom workflows that:
1. Sign reports from multiple sources (not just pytest)
2. Add custom metadata (build info, deployment targets)
3. Integrate with internal monitoring systems
4. Implement custom report retention policies

---

## Part 1: Programmatic Signing

### Basic Programmatic Signing

```python
"""
custom_signer.py - Programmatic XML signing example
"""
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml
from lxml import etree

def sign_report_programmatically(
    input_path: Path,
    output_path: Path,
    key_path: Path,
    cert_path: Path | None = None
) -> None:
    """Sign a test report programmatically.

    Args:
        input_path: Path to unsigned XML report
        output_path: Path to write signed report
        key_path: Path to private key (PEM)
        cert_path: Optional path to certificate (PEM)
    """
    # Load XML
    tree = load_xml(input_path)

    # Load private key
    private_key = load_private_key(key_path)

    # Load certificate (optional)
    cert_bytes = cert_path.read_bytes() if cert_path else None

    # Sign XML
    signed_tree = sign_xml(tree, private_key, cert_bytes)

    # Write signed XML
    signed_xml = etree.tostring(
        signed_tree,
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=True
    )
    output_path.write_bytes(signed_xml)

    print(f"✓ Signed: {input_path} → {output_path}")


# Usage example
if __name__ == "__main__":
    sign_report_programmatically(
        input_path=Path("junit.xml"),
        output_path=Path("junit-signed.xml"),
        key_path=Path("~/.ssh/jux/key.pem").expanduser(),
        cert_path=Path("~/.ssh/jux/cert.pem").expanduser()
    )
```

**Run**:
```bash
# Generate test report
pytest --junitxml=junit.xml --jux-no-sign

# Sign programmatically
python custom_signer.py
```

**✓ Checkpoint**: Programmatic signing works

---

## Part 2: Custom Metadata Collection

### Extend EnvironmentMetadata

```python
"""
custom_metadata.py - Custom metadata collection
"""
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
import subprocess
from pathlib import Path
from pytest_jux.metadata import EnvironmentMetadata

@dataclass
class CustomMetadata:
    """Custom metadata for internal deployment system."""

    # Standard metadata
    standard: dict

    # Custom fields
    build_number: str | None = None
    deployment_target: str | None = None
    jira_ticket: str | None = None
    docker_image: str | None = None
    git_pr_number: int | None = None

    @classmethod
    def collect(cls, **custom_fields) -> "CustomMetadata":
        """Collect standard + custom metadata.

        Args:
            **custom_fields: Additional custom metadata fields

        Returns:
            CustomMetadata instance
        """
        # Collect standard metadata
        standard = EnvironmentMetadata.collect()

        # Collect custom metadata from environment
        import os

        return cls(
            standard=standard.to_dict(),
            build_number=os.getenv("BUILD_NUMBER"),
            deployment_target=os.getenv("DEPLOYMENT_TARGET"),
            jira_ticket=os.getenv("JIRA_TICKET"),
            docker_image=cls._get_docker_image(),
            git_pr_number=cls._get_pr_number(),
            **custom_fields
        )

    @staticmethod
    def _get_docker_image() -> str | None:
        """Get current Docker image name."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format={{.Config.Image}}", "$(hostname)"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or None
        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    @staticmethod
    def _get_pr_number() -> int | None:
        """Extract PR number from git branch or environment."""
        import os
        import re

        # Try environment variable first (GitHub Actions)
        pr_num = os.getenv("GITHUB_PR_NUMBER")
        if pr_num:
            return int(pr_num)

        # Try git branch name (e.g., "pr-123")
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = result.stdout.strip()
            match = re.match(r"pr-(\d+)", branch)
            if match:
                return int(match.group(1))
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)


# Usage example
if __name__ == "__main__":
    import os

    # Set custom environment variables
    os.environ["BUILD_NUMBER"] = "456"
    os.environ["DEPLOYMENT_TARGET"] = "production-us-east-1"
    os.environ["JIRA_TICKET"] = "PROJ-123"

    # Collect metadata
    metadata = CustomMetadata.collect(
        custom_field="custom_value"
    )

    # Display
    print(metadata.to_json())
```

**Run**:
```bash
python custom_metadata.py
```

**Output**:
```json
{
  "standard": {
    "hostname": "dev-machine.local",
    "python_version": "3.11.14",
    ...
  },
  "build_number": "456",
  "deployment_target": "production-us-east-1",
  "jira_ticket": "PROJ-123",
  "docker_image": "myapp:1.0.0",
  "git_pr_number": 123
}
```

**✓ Checkpoint**: Custom metadata collection works

---

## Part 3: Batch Report Processing

### Batch Signing Processor

```python
"""
batch_signer.py - Process multiple reports in batch
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List
import logging

from pytest_jux.canonicalizer import load_xml, compute_canonical_hash
from pytest_jux.signer import load_private_key, sign_xml
from lxml import etree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SigningResult:
    """Result of signing operation."""
    input_path: Path
    output_path: Path | None
    canonical_hash: str | None
    success: bool
    error: str | None = None


class BatchSigner:
    """Batch report signing processor."""

    def __init__(self, key_path: Path, cert_path: Path | None = None):
        """Initialize batch signer.

        Args:
            key_path: Path to private key
            cert_path: Optional path to certificate
        """
        self.private_key = load_private_key(key_path)
        self.cert_bytes = cert_path.read_bytes() if cert_path else None

    def sign_single(
        self,
        input_path: Path,
        output_dir: Path
    ) -> SigningResult:
        """Sign a single report.

        Args:
            input_path: Input XML file
            output_dir: Output directory

        Returns:
            SigningResult
        """
        try:
            # Load and hash XML
            tree = load_xml(input_path)
            canonical_hash = compute_canonical_hash(tree)

            # Sign XML
            signed_tree = sign_xml(tree, self.private_key, self.cert_bytes)

            # Write output
            output_path = output_dir / f"{canonical_hash}.xml"
            signed_xml = etree.tostring(
                signed_tree,
                xml_declaration=True,
                encoding="utf-8",
                pretty_print=True
            )
            output_path.write_bytes(signed_xml)

            logger.info(f"✓ Signed: {input_path.name} → {output_path.name}")

            return SigningResult(
                input_path=input_path,
                output_path=output_path,
                canonical_hash=canonical_hash,
                success=True
            )

        except Exception as e:
            logger.error(f"✗ Failed: {input_path.name} - {e}")
            return SigningResult(
                input_path=input_path,
                output_path=None,
                canonical_hash=None,
                success=False,
                error=str(e)
            )

    def sign_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        pattern: str = "*.xml",
        max_workers: int = 4
    ) -> List[SigningResult]:
        """Sign multiple reports in parallel.

        Args:
            input_dir: Input directory
            output_dir: Output directory
            pattern: File glob pattern
            max_workers: Number of parallel workers

        Returns:
            List of SigningResults
        """
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find input files
        input_files = list(input_dir.glob(pattern))
        logger.info(f"Found {len(input_files)} files to sign")

        # Process in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.sign_single, input_path, output_dir): input_path
                for input_path in input_files
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # Summary
        successes = sum(1 for r in results if r.success)
        failures = len(results) - successes
        logger.info(f"Completed: {successes} signed, {failures} failed")

        return results


# Usage example
if __name__ == "__main__":
    # Initialize batch signer
    signer = BatchSigner(
        key_path=Path("~/.ssh/jux/key.pem").expanduser(),
        cert_path=Path("~/.ssh/jux/cert.pem").expanduser()
    )

    # Sign all reports in directory
    results = signer.sign_batch(
        input_dir=Path("test-results/"),
        output_dir=Path("signed-reports/"),
        pattern="junit-*.xml",
        max_workers=8
    )

    # Report failures
    failures = [r for r in results if not r.success]
    if failures:
        print("\nFailed reports:")
        for result in failures:
            print(f"  - {result.input_path.name}: {result.error}")
```

**Run**:
```bash
# Generate multiple test reports
pytest --junitxml=test-results/junit-unit.xml tests/unit/ --jux-no-sign
pytest --junitxml=test-results/junit-integration.xml tests/integration/ --jux-no-sign
pytest --junitxml=test-results/junit-e2e.xml tests/e2e/ --jux-no-sign

# Sign all reports in batch
python batch_signer.py
```

**Expected Output**:
```
INFO:batch_signer:Found 3 files to sign
INFO:batch_signer:✓ Signed: junit-unit.xml → a1b2c3d4...xml
INFO:batch_signer:✓ Signed: junit-integration.xml → b2c3d4e5...xml
INFO:batch_signer:✓ Signed: junit-e2e.xml → c3d4e5f6...xml
INFO:batch_signer:Completed: 3 signed, 0 failed
```

**✓ Checkpoint**: Batch processing works

---

## Part 4: Custom Verification Logic

### Advanced Verification with Callbacks

```python
"""
custom_verifier.py - Custom verification logic
"""
from pathlib import Path
from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime, UTC

from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature
from lxml import etree


@dataclass
class VerificationResult:
    """Enhanced verification result."""
    file_path: Path
    is_valid: bool
    canonical_hash: str
    signature_algorithm: str | None
    signature_timestamp: datetime | None
    custom_checks: dict[str, bool]
    error: str | None = None


class CustomVerifier:
    """Custom verification with additional checks."""

    def __init__(self, cert_path: Path):
        """Initialize custom verifier.

        Args:
            cert_path: Path to certificate for verification
        """
        self.cert_bytes = cert_path.read_bytes()
        self.custom_checks: list[Callable[[etree._Element], tuple[str, bool]]] = []

    def add_check(
        self,
        check_func: Callable[[etree._Element], tuple[str, bool]]
    ) -> None:
        """Add a custom verification check.

        Args:
            check_func: Function that takes XML tree and returns (name, passed)
        """
        self.custom_checks.append(check_func)

    def verify_enhanced(self, report_path: Path) -> VerificationResult:
        """Verify report with enhanced checks.

        Args:
            report_path: Path to signed report

        Returns:
            VerificationResult
        """
        try:
            # Load XML
            tree = load_xml(report_path)

            # Verify signature
            is_valid = verify_signature(tree, self.cert_bytes)

            # Extract signature metadata
            from pytest_jux.canonicalizer import compute_canonical_hash
            canonical_hash = compute_canonical_hash(tree)

            # Extract signature info
            sig_elem = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
            sig_method = sig_elem.find(
                ".//{http://www.w3.org/2000/09/xmldsig#}SignatureMethod"
            ).get("Algorithm") if sig_elem is not None else None

            # Run custom checks
            custom_results = {}
            for check_func in self.custom_checks:
                check_name, check_passed = check_func(tree)
                custom_results[check_name] = check_passed

            return VerificationResult(
                file_path=report_path,
                is_valid=is_valid,
                canonical_hash=canonical_hash,
                signature_algorithm=sig_method,
                signature_timestamp=datetime.now(UTC),
                custom_checks=custom_results,
                error=None if is_valid else "Signature verification failed"
            )

        except Exception as e:
            return VerificationResult(
                file_path=report_path,
                is_valid=False,
                canonical_hash="",
                signature_algorithm=None,
                signature_timestamp=None,
                custom_checks={},
                error=str(e)
            )


# Custom check examples
def check_minimum_tests(tree: etree._Element) -> tuple[str, bool]:
    """Check that report has minimum number of tests."""
    testsuite = tree.find(".//testsuite")
    if testsuite is None:
        return ("minimum_tests", False)

    test_count = int(testsuite.get("tests", "0"))
    return ("minimum_tests", test_count >= 1)


def check_no_failures(tree: etree._Element) -> tuple[str, bool]:
    """Check that report has no failures."""
    testsuite = tree.find(".//testsuite")
    if testsuite is None:
        return ("no_failures", False)

    failures = int(testsuite.get("failures", "0"))
    return ("no_failures", failures == 0)


def check_has_metadata(tree: etree._Element) -> tuple[str, bool]:
    """Check that report has metadata."""
    # Custom check - look for metadata in properties
    properties = tree.find(".//properties")
    return ("has_metadata", properties is not None)


# Usage example
if __name__ == "__main__":
    # Initialize verifier
    verifier = CustomVerifier(
        cert_path=Path("~/.ssh/jux/cert.pem").expanduser()
    )

    # Add custom checks
    verifier.add_check(check_minimum_tests)
    verifier.add_check(check_no_failures)
    verifier.add_check(check_has_metadata)

    # Verify report
    result = verifier.verify_enhanced(Path("junit-signed.xml"))

    # Display results
    print(f"File: {result.file_path}")
    print(f"Valid: {result.is_valid}")
    print(f"Hash: {result.canonical_hash[:16]}...")
    print(f"Algorithm: {result.signature_algorithm}")
    print("\nCustom Checks:")
    for check_name, passed in result.custom_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
```

**Run**:
```bash
python custom_verifier.py
```

**Output**:
```
File: junit-signed.xml
Valid: True
Hash: a1b2c3d4e5f6g7h8...
Algorithm: http://www.w3.org/2001/04/xmldsig-more#rsa-sha256

Custom Checks:
  ✓ minimum_tests
  ✓ no_failures
  ✗ has_metadata
```

**✓ Checkpoint**: Custom verification logic works

---

## Part 5: Integration with External Systems

### Webhook Integration

```python
"""
webhook_notifier.py - Send signed reports to webhook
"""
import requests
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from pytest_jux.canonicalizer import load_xml, compute_canonical_hash


@dataclass
class ReportNotification:
    """Notification payload for webhook."""
    report_hash: str
    test_count: int
    passed: int
    failed: int
    errors: int
    skipped: int
    environment: str
    timestamp: str
    report_url: Optional[str] = None


class WebhookNotifier:
    """Send signed report notifications to webhook."""

    def __init__(self, webhook_url: str, api_key: Optional[str] = None):
        """Initialize webhook notifier.

        Args:
            webhook_url: Webhook endpoint URL
            api_key: Optional API key for authentication
        """
        self.webhook_url = webhook_url
        self.api_key = api_key

    def extract_stats(self, report_path: Path) -> ReportNotification:
        """Extract statistics from signed report.

        Args:
            report_path: Path to signed XML report

        Returns:
            ReportNotification
        """
        tree = load_xml(report_path)
        testsuite = tree.find(".//testsuite")

        # Extract statistics
        tests = int(testsuite.get("tests", "0"))
        failures = int(testsuite.get("failures", "0"))
        errors = int(testsuite.get("errors", "0"))
        skipped = int(testsuite.get("skipped", "0"))
        passed = tests - failures - errors - skipped

        # Extract metadata
        timestamp = testsuite.get("timestamp", "")

        # Compute hash
        report_hash = compute_canonical_hash(tree)

        return ReportNotification(
            report_hash=report_hash,
            test_count=tests,
            passed=passed,
            failed=failures,
            errors=errors,
            skipped=skipped,
            environment="production",  # Could read from metadata
            timestamp=timestamp
        )

    def send(self, notification: ReportNotification) -> bool:
        """Send notification to webhook.

        Args:
            notification: Report notification

        Returns:
            True if successful, False otherwise
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                self.webhook_url,
                headers=headers,
                json=asdict(notification),
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Webhook failed: {e}")
            return False


# Usage example
if __name__ == "__main__":
    # Initialize notifier
    notifier = WebhookNotifier(
        webhook_url="https://example.com/webhooks/test-reports",
        api_key="your-api-key"
    )

    # Extract stats and send
    notification = notifier.extract_stats(Path("junit-signed.xml"))
    success = notifier.send(notification)

    if success:
        print("✓ Webhook sent successfully")
    else:
        print("✗ Webhook failed")
```

**✓ Checkpoint**: Webhook integration implemented

---

## Summary: What You Accomplished

**✅ Completed**:
1. Used pytest-jux programmatically via Python API
2. Implemented custom signing workflows
3. Created custom metadata collectors
4. Built batch signing processors with parallel execution
5. Implemented custom verification logic with callbacks
6. Integrated with external systems (webhooks)

**🎓 Advanced Skills Learned**:
- Python API usage (signer, verifier, canonicalizer modules)
- Custom metadata extension
- Concurrent processing with ThreadPoolExecutor
- Custom verification callbacks
- Webhook integration
- Production-ready error handling

---

## Next Steps

### Advanced → Production

- **[Security Best Practices](../explanation/security.md)**: Production security
- **[Monitoring Guide](../howto/monitoring.md)**: Monitor signing operations
- **[Performance Optimization](../howto/performance.md)**: Optimize batch processing

### API Reference

- **[signer API](../reference/api/signer.md)**: Complete signing API
- **[verifier API](../reference/api/verifier.md)**: Complete verification API
- **[metadata API](../reference/api/metadata.md)**: Metadata collection API

---

## Troubleshooting

### ThreadPoolExecutor hangs

**Problem**: Batch signing hangs indefinitely

**Cause**: Exception in worker thread not properly handled

**Solution**: Add timeout and better exception handling:
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {...}
    for future in as_completed(futures, timeout=60):
        try:
            result = future.result(timeout=30)
        except Exception as e:
            logger.error(f"Task failed: {e}")
```

---

**Tutorial Version**: 1.0
**pytest-jux Version**: 0.1.9
**Last Updated**: 2025-10-20
