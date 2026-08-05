# Next Task

## Metadata
- Task ID: ET0-SSH-001
- Stage: Stage 0 — Project Discovery, Baseline and Automation Foundation
- Status: Blocked pending authorized operator action
- Owner: Authorized infrastructure operator

## Objective
Add the already-created Enterprise AI project public key to the `root` account's `authorized_keys` file on each declared host, then verify non-interactive public-key login through the configured aliases.

## Rationale
All five hosts are reachable and their host keys are registered locally, but `BatchMode=yes` fails with `auth_failed` because the project public key is absent remotely. Completing this prerequisite enables the approved read-only baseline collector without password prompts.

## Preconditions
- The operator has authorized root access to each declared Ubuntu host.
- The local public key exists at `%USERPROFILE%\\.ssh\\enterprise_ai_ed25519.pub` on the control workstation.
- The operator has independently verified the intended host and root account before modifying `authorized_keys`.

## Scope
- Append the exact existing public-key line once to `/root/.ssh/authorized_keys` on each declared host.
- Ensure `/root/.ssh` is mode `700` and `authorized_keys` is mode `600` when needed for SSH to accept the key.
- Test `ssh -o BatchMode=yes -o ConnectTimeout=10 <alias> 'id -un'` for every declared alias.

## Out of Scope
- Changing passwords, `sshd_config`, password-authentication policy, users, sudoers, firewall, services, packages, containers, or network settings.
- Adding keys for hosts outside `inventory/hosts.yaml`.
- Copying passwords, private keys, or raw evidence into the repository.

## Files to Inspect
- `inventory/hosts.yaml`
- `CURRENT_STATE.md`
- `%USERPROFILE%\\.ssh\\enterprise_ai_ed25519.pub` (local, untracked)

## Files Allowed to Change
- Remote `/root/.ssh/authorized_keys` and its required standard SSH permissions only.
- This repository remains unchanged until a following evidence-review task is explicitly created.

## Execution Steps
1. On each declared host, append the local public-key line only if that exact line is not already present.
2. Apply only the standard SSH directory/file modes in Scope when required.
3. From the control workstation, run the five verification commands below with `BatchMode=yes`.
4. Record the remote identity and exit code per alias; do not record credentials.

## Acceptance Criteria
- Each host accepts the project public key for the declared root account.
- Every verification command exits `0` and prints `root`.
- No password prompt occurs and no SSH host-key warning/change occurs.
- No secret or private key is added to Git, logs, evidence, or documentation.

## Verification Commands
```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rddb 'id -un'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdapp 'id -un'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdvector 'id -un'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdautomation 'id -un'
ssh -o BatchMode=yes -o ConnectTimeout=10 enterprise-ai-rdmonitor 'id -un'
```

## Evidence Required
- Per-host exit code and remote identity from the five verification commands.
- Explicit blocker for any host that cannot accept the key.

## Rollback
Remove only the exact project public-key line from the affected remote `authorized_keys` file. Do not delete other keys or the `.ssh` directory.

## Completion Updates
- `CURRENT_STATE.md`
- `SESSION_LOG.md`
- `CHANGELOG.md`
- `NEXT_TASK.md`
- `DECISIONS.md`, only if a new architecture or security policy is required
