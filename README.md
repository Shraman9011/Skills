# Skills

A collection of reusable [Claude Code](https://claude.com/claude-code) skills by Unichronic. Each skill lives in its own folder with its own README.

## Available skills

| Skill | What it does |
| --- | --- |
| [android-qa-testing](android-qa-testing/) | Tests an Android app on an emulator or phone through `adb` using a blind first-time-user tester, seeded stress testing and an authorized security review, then writes an evidence-backed report. |

## Using a skill in your project

1. Clone this repo:
   ```
   git clone <this-repo-url>
   ```
2. Open the skill's folder and follow its README. For example, [android-qa-testing/README.md](android-qa-testing/README.md) has the full step-by-step setup.
3. Copy the skill's `.claude` folder into the root of your own project. Claude Code picks up skills from `.claude/skills/` and agents from `.claude/agents/`.
4. If your project already has a `.claude/settings.json`, merge the permission entries instead of overwriting it.

## Repository layout

```
Skills/
  README.md
  android-qa-testing/
    README.md
    .claude/            # copy this into your project
    .qa-scope.example.json
    .gitignore
```

## Adding a new skill

1. Create a folder named after the skill, such as `my-skill/`.
2. Put the skill under `my-skill/.claude/skills/<skill-name>/SKILL.md`, with any helper scripts beside it. Agents go in `my-skill/.claude/agents/`.
3. Add a `README.md` in the folder covering prerequisites and step-by-step usage.
4. Add a row to the table above.

## Safety

Skills here may drive real devices or touch real systems. Read each skill's README first, use test environments and test accounts only, and never run them against apps or services you are not authorized to test.
