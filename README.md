# VSSC TA (ECE) Solo Leveling System

The GATE Solo Leveling AI app with the plan swapped to the VSSC Technical Assistant (ECE) 150-day plan,
27 Oct 2026 to 25 Mar 2027. Same engine: daily quests, 1-4-7 revision, Error Monster, timed exam sets,
full mocks, XP/ranks/streaks, alarms and the optional AI backend.

## What changed
- `assets/plan_150.json`: 150 days (103 learning days, 13 Sunday weekly tests, 20 revision days, 14 mocks).
- Subjects: 11 ECE subjects. Mock = 80 Q, 80 marks, 90 min, -1/3 per wrong MCQ.
- `assets/question_bank_v1.json`: 120 offline questions per subject (1320 total), answers computed by code.
  The AI backend generates more when it is configured in Settings.
- No daily General Aptitude quest (the plan has none). Workout, life skill and sleep quests are unchanged.
- Package/application id is `com.chandu.vssc.taece`, so it installs next to the old GATE app.
- `tools/ece/`: scripts that regenerate the plan and bank.

## Build the APK
Push to GitHub, open Actions, run **Build VSSC TA ECE APK**, download artifact **VSSC-TA-ECE-debug-apk**.
Local: JDK 17, Android SDK 35, `./gradlew assembleDebug`.
