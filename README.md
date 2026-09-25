# GATE Solo Leveling System V7.1 — Modified Day 21+ Plan (C + Algorithms as real learning subjects, GA de-duplicated)

## V7.1 — Plan.kt rewritten for Day 21 onward; Days 1–20 untouched
This is a **data-only change** (`Plan.kt`, plus 3 syllabus-text lines in `MainActivity.kt`). No screens, tabs, checkboxes, notifications, widget, or SharedPreferences keys were touched, so your existing progress (Rank, Level, XP, Gold, Streak, Day, Mastery %, Formula Vault favorites, Error Monsters) carries over untouched as long as you **install this as an update over the existing app** (don't uninstall first) — updating an app leaves its on-device data alone; only an uninstall wipes it.

**What changed, and why:**
- **GA duplication fixed.** The old plan set `secondarySubject = "General Aptitude"` for every Day 21+ while *also* showing the dedicated GA block — so GA appeared twice on the same screen. From Day 21 onward, `secondary` is now a genuine **Core Recall** rotation through **DSA → Digital Logic → DBMS → COA → Operating Systems** (5-day cycle, 10–15 questions, real subtopics pulled from your own Days 1–20 syllabus), and GA stays its own single objective, exactly as before.
- **C Programming and Algorithms are now real, standalone learning subjects** (Days 21–40 and 41–60), each broken into its own topic ladder (C-1 Basics → C-9 GATE Problem Solving; A-1 Algorithm Analysis → A-9 GATE Algorithm Practice) instead of being folded into "DSA practice." DSA itself moves to Core Recall (it was already covered in Days 1–20).
- **New phase structure, Day 21–150:** `C + MATH` (21–40) → `ALGORITHMS + TOC` (41–60) → `TOC + COMPILER` (61–78) → `CN + ALGORITHMS` (79–100) → `MATH MASTER` (101–115) → `CORE RECALL DUNGEON` (116–125) → `PYQ DUNGEON` (126–135) → `FINAL BOSS` (136–150). Subjects interleave two-at-a-time instead of running 15–24 days back-to-back, so nothing sits unrevised for weeks.
- **147 Recall clarified**: the checkpoint window now explicitly names which two prior days to recall (Day d−3 and Day d−6) and notes that the 1-4-7 cycle applies only to the "new learning" subjects (C, Algorithms, TOC, Compiler, CN, Engineering Mathematics) — not to the Core Recall subjects, which have their own 5-day rotation instead.
- **Full official GATE 2027 CS syllabus coverage verified** against the syllabus PDF published by IIT Madras (the GATE 2027 organizing institute): Engineering Mathematics gained 3 previously-missing topics (LU Decomposition, Graph Theory, Combinatorics) and a fuller distributions list; Computer Networks, Digital Logic and Computer Organization syllabus text on the Plan screen was reworded to match the 2027 syllabus exactly (Computer Networks in particular dropped ARP, DHCP, ICMP, UDP, SMTP/FTP/email and gained "Principles of Layering", performance metrics and socket API, per the official 2027 revision).
- Every topic list was checked in a standalone script across all 150 days to confirm no index ever goes out of range — this was the most likely source of a crash, so it was verified before touching the real code, not after.
- `versionCode` bumped 14 → 15, `versionName` → `7.1.0-modified-day21-plan`, so Android recognizes this as an update rather than a conflicting install.

# GATE Solo Leveling System V6.7 — Hunter Tab: Mastery, Weak Topics, Bosses, Achievements, Formula Vault

## V6.7 — real, working subset of the "40-feature" master list
Implementing literally all 40 features from the master feature list isn't realistic in one pass — several (a real PYQ question bank, a timed 65-question mock-test engine, AI study assistant, marks/rank prediction) need either thousands of hand-authored questions or infrastructure this app doesn't have, and faking that content would make the app worse, not better. What's added here is a real, working slice of the Phase 1–3 features that run entirely on local data (no question bank needed):

- **New "👑 HUNTER" tab** added to the bottom nav (SYSTEM / QUEST / PLAN / HUNTER / SET).
- **Topic Mastery System**: self-rated 0–100% per subject (10 GATE CS subjects), adjustable with +/− in 5% steps, persisted locally.
- **Weak Topic Detector**: automatically lists every subject under 60% mastery, weakest first, with a VERY HIGH / HIGH / MEDIUM priority label — mirrors the "⚠ WEAK AREAS" behavior from the feature spec.
- **Boss Battle System**: every subject is a boss with 1000 HP; your mastery % is your damage dealt, so raising mastery visibly drops the boss's remaining HP until it's defeated at 100%.
- **Achievement System**: 12 achievements (first quest cleared, streak milestones, level milestones, error-monsters-defeated milestones, total XP milestones), evaluated live from your existing stats — no separate tracking system to keep in sync.
- **Formula / Concept Vault**: 15 seeded GATE CS formulas across Digital Logic, COA, OS, DBMS, TOC, CN, Engineering Maths, DSA and Compiler Design, each toggleable as ★ Favorite or ⚠ Difficult/frequently-forgotten.
- **Mistake Book upgrade**: Error Monsters now carry a mistake **category** (Concept / Calculation / Silly / Time pressure / Misread question / Guessing), matching the Mistake Book spec, and defeating one (3/3) now counts toward the "Error Monsters Defeated" achievements.
- New `total_quests_cleared` and `total_monsters_defeated` counters are tracked so achievements have real, permanent data to evaluate against (not just today's numbers).

### Deliberately not attempted in this pass (would need real content or infra, not just code)
Question Bank, Exam/Test Engine (topic/subject/full mock tests with negative marking), PYQ Intelligence, Marks Prediction Engine, Difficulty Adaptation, Anti-Cheating/Integrity Mode for mocks, AI Study Assistant, and the "GATE 85 Engine" auto-planner that reallocates your schedule from live test performance. These all depend on a real bank of graded questions/PYQs with correct answers, which nobody has authored yet — building the *engine* without real content behind it would just produce a hollow UI. Happy to start on the Question Bank data model next if you want to go there.

# GATE Solo Leveling System V6.6 — 147-Rule GA Cycle + Basic Daily Quest Notifications

## V6.6 changes
- **General Aptitude now shows all 4 chapters every day**: Verbal Aptitude, Quantitative Aptitude, Analytical & Logical Reasoning, and Spatial Aptitude are combined into every day's GA block instead of a flat "20/40 questions" label — you always see exactly which sub-topics from each of the 4 chapters to practice.
- **"147 rule" applied to GA as a 3-day repeating cycle**: the full GA syllabus is split into 3 balanced slots. Day 1, 4, 7, 10… always get slot 1; Day 2, 5, 8, 11… get slot 2; Day 3, 6, 9, 12… get slot 3 — so the same slot resurfaces every 3rd day across all 150 days for spaced repetition, instead of being covered once and forgotten. Visible in the Dashboard, Quest screen, and the full 150-day Plan list.
- **Engineering Mathematics + GA syllabus fully expanded** on the Plan → Syllabus screen: Linear Algebra, Calculus, Probability & Statistics, and Discrete Mathematics are each broken into their real sub-topics (vector spaces, Cayley-Hamilton, Bayes' theorem, Boolean algebra, graph theory, etc.), and GA is broken into its 4 named chapters with their real chapter lists instead of one merged line.
- **Instagram "mana-leak" monitoring removed completely**: `InstagramMonitor.kt` and `InstagramCheckReceiver.kt` are deleted, `PACKAGE_USAGE_STATS` permission is removed from the manifest, and all related Settings-screen UI is gone.
- **Replaced with a plain basic "Daily Quest" notification**, sent 3 times a day: 5:30 AM, 2:30 PM, and 6:00 PM, each summarizing today's quest (title, primary subject, current GA cycle slot, objectives done). Unlike the danger/inactivity/level-up alerts, this channel is `IMPORTANCE_DEFAULT` with the plain system notification sound — no full-screen intent, no alarm-style vibration — since it's a routine reminder, not an emergency alert. Settings screen has an enable/disable toggle and a "SEND TEST NOTIFICATION NOW" button.
- **Error Monsters** (add a mistake, defeat the same concept 3 times to clear it) — already present since V6.3.2 and unchanged; still available on the Quest screen.
- **New sound mapping** applied across `SoundManager`: system open / level-up / selecting → `arise_system.wav`; notifications and gaining XP/gold/objectives → `arise.wav`; everything else → `level_up_notification.wav`.

# GATE Solo Leveling System V6.5.3 — Test Alert Now Reports Real Failures

## V6.5.3 fix
The "SEND TEST ALERT NOW" button previously called `NotificationHelper.showInstagramWarning()` with no feedback at all — if it failed silently (blocked channel, exception, disabled notifications), you'd have no way to know why. It now:
- Wraps the call in try/catch and shows the exact exception via Toast if one occurs, instead of failing silently.
- Checks whether the "System — Mana Leak" channel specifically has been muted (Android lets a user block one channel while others still work) and tells you if so.
- Detects and warns if **Do Not Disturb** is active — DND silently swallows notifications below "priority" and is a very common reason a correctly-coded alert never appears even with every permission granted.
- On success, shows a Toast confirming the call actually ran, so "nothing appeared" now always comes with an explanation.

If your permissions all show green (as they did) and the test still shows nothing after this update, the Toast message it gives you is the real next clue — send me that exact text.



## V6.5.2 additions (Settings → Instagram Mana-Leak Alert)
- **Live minutes-today readout** so you can see the app is actually detecting Instagram usage in real time, instead of guessing.
- **Notification permission status** (Android 13+) with a direct link to the app's notification settings if it's off.
- **Exact-alarm permission status** (Android 12+) with a direct link to grant it — without this, the 5-minute background check can be delayed by Doze.
- **"SEND TEST ALERT NOW" button** — fires the exact same notification path as a real alert, immediately, bypassing usage tracking and the alarm scheduler entirely. This isolates the problem in one tap:
  - Test alert doesn't show → it's a phone-level notification/channel/permission block, not the app.
  - Test alert shows, but real 10-minute alerts never do → your background check is being killed between app opens. That's almost always **OEM battery/autostart restriction** (very common on Xiaomi/MIUI, Vivo, Oppo, Realme, Samsung with aggressive battery saver) — the app needs to be whitelisted from battery optimization and (on MIUI-style phones) have "Autostart" enabled, or the 5-minute self-re-arming alarm chain gets silently stopped.

# GATE Solo Leveling System V6.5.1 — Cinematic System UI

## V6.5.1 additions (in-app visual pass, no notification changes)
- **Glowing corner-bracket panels**: every `Window()` panel (Player Status, Daily Quest, Plan, etc.) now pulses its border and draws the same corner brackets used on the notification frames, instead of a flat static line.
- **HUD background**: a faint grid + scanline + top vignette now sits behind every screen (`SystemBackground`), drawn once with Canvas — cheap and matches the notification aesthetic.
- **Typewriter text**: the quest title on the Awakening splash and the Quest window now reveals character-by-character instead of appearing instantly.
- **Cinematic light-pillar burst**: a full-screen vertical beam + falling sparks + vertical "NOTIFICATION" text, shown for ~1.9s only on an actual level-up or rank-up (hooked into the existing `progressionLevel`/`progressionRank` checks in `completeObjective()`/`clearQuest()`). Deliberately not used for every notification so it stays a rare payoff moment. Tap anywhere to skip it early.
- Custom game-style fonts (e.g. Rajdhani) were **not** added in this pass — that needs a `.ttf` file bundled into `res/font`, which requires network access this environment doesn't have. Drop a font file into `app/src/main/res/font/` and I can wire it into the theme in one line whenever you have one, or point me to a specific Google Fonts family name next time you're online and I'll do it then.

# GATE Solo Leveling System V6.5.0 — Custom Notification UI Edition

## V6.5.0 additions
- **Custom glowing-frame notification UI**: alerts (inactivity, danger, mana leak, level-up) now render with the angular cut-corner frame + corner brackets from the widget redesign, both collapsed and expanded, instead of the stock notification look.
- **Per-alert notification sound**: each alert type now has its own notification channel with a dedicated sound — level_up_notification.wav (level up), arise_system.wav (danger), arise.wav (inactivity), system_tick.wav (mana leak). See the comment at the top of `NotificationHelper.kt` for the exact priority mapping — flag it if you want it reordered.
- **Instagram tracking fix**: switched from the legacy MOVE_TO_FOREGROUND/BACKGROUND usage events to ACTIVITY_RESUMED/ACTIVITY_PAUSED (API 29+), and now ignores foreground bursts under 8 seconds. This should stop mana-leak alerts firing from brief, non-deliberate opens (a shared link, a widget refresh, a notification tap-through) rather than actually using the app. Worth a day of real-world testing since I can't reproduce the original bug on-device myself — let me know if it still over-fires.

# GATE Solo Leveling System V6.4.0 — Notifications + Widget Edition

GATE CS 2027 150-day Solo Leveling-style Android study system.

## V6.4.0 additions
- **Instagram "mana-leak" alert**: warns you every 10 minutes of Instagram use in a day, System-style. Requires manually granting "Usage Access" once (Settings screen has a one-tap shortcut to the right page — Android does not allow this to be auto-granted).
- **Awakening window**: a full-screen "System" boot screen shown each time you open the app — player rank, level, streak, and today's quest, before you tap through to the dashboard.
- **Home-screen widget**: add the "GATE System" widget to your home screen to see today's quest topic + today's workout + objective progress without opening the app at all. Tapping it opens straight to the Quest screen. Updates automatically, and instantly whenever you tick an objective.
- **"Today's Quest" app shortcut**: long-press the app icon for a shortcut straight into today's quest (same as tapping a notification).
- **Streak tracker**: counts consecutive days you fully cleared the quest.
- **GATE exam countdown**: editable exam date on the dashboard, shows days remaining.
- Existing V6.3.2 features preserved: 4-hour inactivity alert, 8:30 PM danger alert, Error Monsters, 85+ Plan Readiness Index, 150-day syllabus/plan.

## Notification & background behavior
- All alerts use native Android AlarmManager + notification channels (no extra battery-hungry services).
- Exact alarms are used when Android allows them; otherwise the app falls back to an allowed inexact idle alarm.
- Notification permission is requested on Android 13+.
- Inactivity reminders are limited to daytime and use a four-hour cooldown.
- 8:30 PM danger notification is skipped when all 6 objectives are complete.
- Instagram checks run roughly every 5 minutes in the background; on some devices Doze/battery-optimization may space these out further. For most reliable delivery, exclude the app from battery optimization (Settings → Apps → GATE Solo Leveling System → Battery → Unrestricted).

## Setup after install
1. Open the app once, allow notifications when prompted.
2. Go to Settings tab → grant Usage Access for the Instagram alert to work.
3. Long-press your home screen → Widgets → find "GATE Solo Leveling System" → add the "SYSTEM" widget.

## Build
GitHub Actions builds the debug APK with Java 17, Android SDK 35, and Gradle 8.10.2.
