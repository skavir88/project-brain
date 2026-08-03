# Evidence Handling

Raw output from `scripts/collect-host-baseline.sh` is intentionally ignored by Git. Run it locally on the relevant Ubuntu host and write output to its default `/var/tmp/enterprise-ai-baseline` location.

Review each output for sensitive operational information before sharing it. A future explicitly approved task may extract a sanitized summary; do not copy raw evidence into this directory or commit it by default.
