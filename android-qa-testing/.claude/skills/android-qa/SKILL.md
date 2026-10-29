---
name: android-qa
description: Run a first-time-user exploratory test, stress test and authorized security assessment of the Android app on a connected adb device or emulator, and produce an evidence-backed report. Use when asked to test, break, or security-check the Android app.
---

Phase 0, preflight
1. export QA_HOME=<absolute path>/.qa-run
2. python3 .claude/skills/android-qa/scripts/admin.py devices ; select a device with admin.py select <serial>. Prefer an emulator. For a physical phone use a dedicated test device and admin.py pair / connect.
3. Read .qa-scope.json. Run admin.py scope-check <package>. Stop if it fails.
4. admin.py install <apk> (or build and install the debug APK).

Phase 1, blind first-user exploration (repeat per persona in personas.md)
1. admin.py fresh <package> ; admin.py newrun --persona <name> --steps 60
2. admin.py start <package> (the tester is NOT told the package name)
3. Give the blind-tester ONLY: the persona and a plain goal, such as: find out what this app does and create an account. Do not include code, screen names, or feature lists.
4. After it finishes, admin.py crashes and save the output.

Phase 2, stress
1. admin.py stress <package> --events 5000 --seed 1 (repeat with other seeds)
2. Keep seeds and crash logs. Mark crashes that do not reproduce as flaky.

Phase 3, security (only inside the scope file)
1. Static: scan the APK with MobSF (run it in Docker, upload the APK, download the JSON report).
2. White-box: delegate to code-analyst for manifest, exported components, cleartext traffic, storage and logging review.
3. Never run destructive tests unless destructive_tests is true in the scope file.

Phase 4, analysis and report
1. Delegate to code-analyst with the event logs, crash logs and scan results.
2. Write the report using report-template.md. Unexecuted tests are skipped or inconclusive, never passed.
