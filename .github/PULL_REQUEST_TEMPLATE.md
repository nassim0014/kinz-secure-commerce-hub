<!--
Thanks for opening a PR! Please fill in the sections below.
See CONTRIBUTING.md for the full guidelines.
-->

## Summary

<!-- One paragraph: what & why. -->

## Type of change

- [ ] 🐛 Bug fix (non-breaking)
- [ ] ✨ New feature (non-breaking)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation only
- [ ] 🔧 Refactor / chore (no functional change)
- [ ] 🛡️ Security hardening

## Related issue

<!-- "Closes #123" or "Refs #123". Leave blank if no issue. -->

## Changes

<!-- Bullet list of concrete changes. -->
-
-
-

## Security considerations

<!-- If this PR touches auth, JWT, RBAC, secrets, Docker, CI, or any
     security-sensitive code, explain what was done to keep the system
     safe. If not applicable, write "N/A". -->

## How to test

<!-- Steps a reviewer can follow to verify this works. Include any
     env vars, curl commands, or test data needed. -->

```bash
# Example:
pytest tests/backend/test_jwt.py -v
curl -X POST http://localhost:8000/api/v1/auth/login -d '{"email":"...","password":"..."}'
```

## Checklist

- [ ] My code follows the project style (ruff / eslint pass)
- [ ] I added tests for any new behavior
- [ ] All new and existing tests pass locally
- [ ] I updated the documentation (README, SECURITY.md, threat-model) if behavior changed
- [ ] I did NOT commit any secrets, `.env` files, or private keys
- [ ] I added a CHANGELOG entry if user-facing
- [ ] PR title follows Conventional Commits (e.g. `feat(api):`, `fix(auth):`)

## Screenshots / logs (if UI or behavior change)

<!-- Drag-and-drop images or paste logs. Redact secrets. -->
