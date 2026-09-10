# BMC Secret Configuration

## Security Notice

The `bmc-secret.env` file contains placeholder values (`CHANGEME`) for BMC credentials.

**IMPORTANT:** BMC credentials must be injected from an external secret store and must never be committed to version control with actual values.

## Usage

Before deploying, you must replace the placeholder values in `bmc-secret.env` with actual credentials from your secure secret store.
