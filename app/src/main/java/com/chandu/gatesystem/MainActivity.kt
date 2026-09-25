package com.chandu.gatesystem

import android.Manifest
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CutCornerShape
import androidx.compose.foundation.clickable
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.animation.core.*
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.blur
import java.time.LocalDate
import java.time.temporal.ChronoUnit
import kotlinx.coroutines.delay
import kotlin.math.max
import com.chandu.gatesystem.data.GatePlan
import com.chandu.gatesystem.data.DailyQuest
import com.chandu.gatesystem.data.GaSet
import com.chandu.gatesystem.data.Mastery
import com.chandu.gatesystem.data.Achievements
import com.chandu.gatesystem.data.FormulaVault
import com.chandu.gatesystem.notifications.SoundManager
import com.chandu.gatesystem.notifications.SystemNotificationScheduler
import com.chandu.gatesystem.notifications.NotificationHelper
import com.chandu.gatesystem.widget.TodayWidgetProvider

class MainActivity : ComponentActivity() {
    companion object { const val EXTRA_OPEN_QUEST = "open_quest" }
    private lateinit var sounds: SoundManager
    private val notificationPermission = registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        sounds = SoundManager(this)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
        val prefs = getSharedPreferences("gate_progress", Context.MODE_PRIVATE)
        SystemNotificationScheduler.scheduleAll(this)
        setContent { GateSystemV63(sounds, prefs, wantsQuestScreen(intent)) }
        sounds.play(SoundManager.Event.SYSTEM_BOOT)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        if (wantsQuestScreen(intent)) {
            val prefs = getSharedPreferences("gate_progress", Context.MODE_PRIVATE)
            setContent { GateSystemV63(sounds, prefs, true) }
        }
    }

    // True if launched from a notification tap, the home-screen widget, or the
    // "Today's Quest" long-press app shortcut (which arrives as ACTION_VIEW).
    private fun wantsQuestScreen(intent: Intent): Boolean =
        intent.getBooleanExtra(EXTRA_OPEN_QUEST, false) || intent.action == Intent.ACTION_VIEW

    override fun onDestroy() { sounds.release(); super.onDestroy() }
}

private val Bg = Color(0xFF03070D)
private val Panel = Color(0xFF07101A)
private val Cyan = Color(0xFF63D8FF)
private val Gold = Color(0xFFFFD166)
private val Purple = Color(0xFFB98CFF)
private val Green = Color(0xFF68F5B0)
private val Red = Color(0xFFFF6B7A)
private val Muted = Color(0xFF91A1AF)

private const val XP_PER_OBJECTIVE = 50
private const val QUEST_BONUS_XP = 100
private const val GOLD_PER_OBJECTIVE = 25
private const val QUEST_BONUS_GOLD = 50
private const val OBJECTIVE_COUNT = 6

@Composable
private fun GateSystemV63(sounds: SoundManager, prefs: android.content.SharedPreferences, openQuest: Boolean) {
    var tab by remember { mutableIntStateOf(if (openQuest) 1 else 0) }
    var showSplash by remember { mutableStateOf(!openQuest) }
    val context = LocalContext.current
    val today = LocalDate.now()
    val day = GatePlan.currentDay(today)
    val quest = remember(day) { GatePlan.forDay(day) }
    var doneCount by remember(day) { mutableIntStateOf(prefs.getInt("day_${day}_done", 0).coerceIn(0, OBJECTIVE_COUNT)) }
    var questCleared by remember(day) { mutableStateOf(prefs.getBoolean("day_${day}_cleared", false)) }
    var totalXp by remember { mutableIntStateOf(prefs.getInt("xp", 0).coerceAtLeast(0)) }
    var gold by remember { mutableIntStateOf(prefs.getInt("gold", 0).coerceAtLeast(0)) }
    var streak by remember { mutableIntStateOf(prefs.getInt("streak", 0).coerceAtLeast(0)) }
    var soundOn by remember { mutableStateOf(true) }
    var vibrationOn by remember { mutableStateOf(true) }
    var dailyQuestNotifsOn by remember { mutableStateOf(prefs.getBoolean("daily_quest_notifs_enabled", true)) }
    var burst by remember { mutableStateOf<SystemBurst?>(null) }

    LaunchedEffect(Unit) {
        if (!prefs.contains("last_progress_at")) {
            prefs.edit().putLong("last_progress_at", System.currentTimeMillis()).apply()
        }
        SystemNotificationScheduler.scheduleAll(context)
        TodayWidgetProvider.updateAll(context)
    }

    LaunchedEffect(dailyQuestNotifsOn) { prefs.edit().putBoolean("daily_quest_notifs_enabled", dailyQuestNotifsOn).apply() }

    val level = progressionLevel(totalXp)
    val rank = progressionRank(level)
    val levelBaseXp = levelBase(level)
    val nextLevelXp = levelBase(level + 1)
    val levelProgress = ((totalXp - levelBaseXp).toFloat() / max(1, nextLevelXp - levelBaseXp)).coerceIn(0f, 1f)
    val gatePower = totalXp / 10 + doneCount * 25

    LaunchedEffect(soundOn, vibrationOn) { sounds.enabled = soundOn; sounds.vibrationEnabled = vibrationOn }

    fun save() {
        prefs.edit().putInt("day_${day}_done", doneCount).putBoolean("day_${day}_cleared", questCleared).putInt("xp", totalXp).putInt("gold", gold).apply()
    }

    fun completeObjective() {
        if (doneCount >= OBJECTIVE_COUNT) return
        val oldLevel = progressionLevel(totalXp)
        doneCount += 1
        totalXp += XP_PER_OBJECTIVE
        gold += GOLD_PER_OBJECTIVE
        val leveledUp = progressionLevel(totalXp) > oldLevel

        // Persist XP/level/progress FIRST, before any sound/vibration/animation effect
        // runs. Those effects are already crash-proofed internally, but saving first
        // means even an unforeseen effect failure can never cost real progress.
        prefs.edit().putLong("last_progress_at", System.currentTimeMillis()).apply()
        save()

        sounds.play(SoundManager.Event.CHECKBOX_TICK)
        sounds.play(SoundManager.Event.EXP_GAIN)
        if (leveledUp) {
            sounds.play(SoundManager.Event.LEVEL_UP)
            burst = SystemBurst("\u25B2 LEVEL UP", "YOU HAVE REACHED LEVEL ${progressionLevel(totalXp)}")
        }
        SystemNotificationScheduler.scheduleInactivityFromProgress(context, System.currentTimeMillis())
        TodayWidgetProvider.updateAll(context)
    }

    fun clearQuest() {
        if (questCleared || doneCount < OBJECTIVE_COUNT) return
        val oldRank = progressionRank(progressionLevel(totalXp))
        totalXp += QUEST_BONUS_XP
        gold += QUEST_BONUS_GOLD
        questCleared = true
        val lastClearedDay = prefs.getString("last_cleared_date", null)
        val yesterday = today.minusDays(1).toString()
        streak = if (lastClearedDay == yesterday) streak + 1 else 1
        val rankedUp = progressionRank(progressionLevel(totalXp)) != oldRank

        // Same principle: persist first, cosmetic effects after.
        prefs.edit().putInt("streak", streak).putInt("total_quests_cleared", prefs.getInt("total_quests_cleared", 0) + 1).putString("last_cleared_date", today.toString()).apply()
        save()

        sounds.play(SoundManager.Event.QUEST_APPEAR)
        if (rankedUp) {
            sounds.play(SoundManager.Event.RANK_UP)
            burst = SystemBurst("\u2605 RANK UP", "RANK ${progressionRank(progressionLevel(totalXp))} ATTAINED")
        }
        TodayWidgetProvider.updateAll(context)
    }

    MaterialTheme(colorScheme = darkColorScheme(background = Bg, surface = Panel, primary = Cyan)) {
        Surface(Modifier.fillMaxSize(), color = Bg) {
          Box(Modifier.fillMaxSize()) {
            SystemBackground(Modifier.fillMaxSize())
            if (showSplash) {
                AwakeningWindow(day, rank, level, quest, streak) { showSplash = false; sounds.play(SoundManager.Event.ARISE_SYSTEM) }
            } else {
                Column(Modifier.fillMaxSize().padding(14.dp)) {
                    SystemHeader(level, rank, totalXp, gatePower, day)
                    Spacer(Modifier.height(10.dp))
                    Box(Modifier.fillMaxWidth().weight(1f)) {
                        when (tab) {
                            0 -> Dashboard(level, rank, totalXp, gold, gatePower, levelProgress, day, quest, doneCount, questCleared, streak, prefs, sounds, ::completeObjective)
                            1 -> QuestScreen(day, quest, doneCount, questCleared, totalXp, gold, sounds, prefs, ::completeObjective, ::clearQuest)
                            2 -> PlanScreen(day)
                            3 -> HunterScreen(context, prefs, totalXp, level, streak, sounds)
                            else -> SettingsScreen(soundOn, vibrationOn, dailyQuestNotifsOn, { soundOn = it }, { vibrationOn = it }, { dailyQuestNotifsOn = it }, sounds, context, { doneCount = 0; questCleared = false; totalXp = 0; gold = 0; streak = 0; prefs.edit().clear().apply(); SystemNotificationScheduler.scheduleAll(context); sounds.play(SoundManager.Event.WARNING) })
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        NavButton("◈ SYSTEM", tab == 0) { tab = 0 }
                        NavButton("⚔ QUEST", tab == 1) { tab = 1; sounds.play(SoundManager.Event.QUEST_APPEAR) }
                        NavButton("▣ PLAN", tab == 2) { tab = 2; sounds.play(SoundManager.Event.QUEST_APPEAR) }
                        NavButton("👑 HUNTER", tab == 3) { tab = 3; sounds.play(SoundManager.Event.QUEST_APPEAR) }
                        NavButton("⚙ SET", tab == 4) { tab = 4 }
                    }
                }
            }
            burst?.let { b -> CinematicBurstOverlay(b) { burst = null } }
          }
        }
    }
}

/** Full-screen "System" awakening window shown once per app open, Solo-Leveling style. */
@Composable
private fun AwakeningWindow(day: Int, rank: String, level: Int, quest: DailyQuest, streak: Int, onDismiss: () -> Unit) {
    var visible by remember { mutableStateOf(false) }
    val alpha by animateFloatAsState(if (visible) 1f else 0f, animationSpec = tween(700), label = "splashAlpha")
    val glow by rememberInfiniteTransition(label = "glow").animateFloat(
        initialValue = 0.35f, targetValue = 0.85f,
        animationSpec = infiniteRepeatable(tween(1200, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "glowAnim"
    )
    LaunchedEffect(Unit) { visible = true; delay(2600); onDismiss() }

    Box(
        Modifier
            .fillMaxSize()
            .clickable { onDismiss() }
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            Modifier
                .alpha(alpha)
                .fillMaxWidth()
                .border(1.dp, Cyan.copy(alpha = glow), CutCornerShape(14.dp))
                .background(Panel)
                .padding(22.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("◈ ◈ ◈", color = Cyan.copy(alpha = glow), fontSize = 14.sp)
            Spacer(Modifier.height(10.dp))
            Text("THE SYSTEM HAS AWAKENED", color = Cyan, fontSize = 15.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text("GATE CS 2027", color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Black)
            Spacer(Modifier.height(14.dp))
            Text("PLAYER RANK  $rank", color = Gold, fontSize = 13.sp, fontWeight = FontWeight.Bold)
            Text("LEVEL $level  •  DAY $day / 150", color = Muted, fontSize = 12.sp)
            if (streak > 0) Text("STREAK  🔥 $streak DAY${if (streak == 1) "" else "S"}", color = Green, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(16.dp))
            Text("TODAY'S QUEST", color = Purple, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            TypewriterText(quest.title, color = Color.White, fontSize = 18.sp)
            Text("${quest.primarySubject} • ${quest.primaryTopic}", color = Cyan, fontSize = 11.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            Spacer(Modifier.height(18.dp))
            Text("[ TAP TO ENTER ]", color = Muted, fontSize = 11.sp)
        }
    }
}

private fun levelBase(level: Int): Int = if (level <= 1) 0 else (level - 1) * 500
private fun progressionLevel(xp: Int): Int = (xp / 500) + 1
private fun progressionRank(level: Int): String = when { level >= 21 -> "S"; level >= 16 -> "A"; level >= 11 -> "B"; level >= 7 -> "C"; level >= 4 -> "D"; else -> "E" }

@Composable
private fun SystemHeader(level: Int, rank: String, xp: Int, gatePower: Int, day: Int) {
    Column(Modifier.fillMaxWidth().border(1.dp, Cyan.copy(alpha = .7f), CutCornerShape(8.dp)).padding(14.dp)) {
        Text("▣ SYSTEM ONLINE • V6.7", color = Cyan, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp)
        Text("GATE CS 2027", color = Color.White, fontSize = 25.sp, fontWeight = FontWeight.Black, letterSpacing = 0.5.sp)
        Text("PLAYER • RANK $rank • LEVEL $level • GATE POWER $gatePower", color = Muted, fontSize = 11.sp)
        Text("DAY $day / 150  •  XP $xp / NEXT ${levelBase(level + 1)}", color = Gold, fontSize = 10.sp)
    }
}

@Composable
private fun Dashboard(level: Int, rank: String, xp: Int, gold: Int, gatePower: Int, progress: Float, day: Int, quest: DailyQuest, done: Int, cleared: Boolean, streak: Int, prefs: android.content.SharedPreferences, sounds: SoundManager, onObjective: () -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
        item { Window("◈ PLAYER STATUS") {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Stat("RANK", rank); Stat("LEVEL", level.toString()); Stat("EXP", xp.toString()); Stat("GOLD", gold.toString()) }
            Spacer(Modifier.height(10.dp)); Text("LEVEL PROGRESS", color = Cyan, fontSize = 10.sp, fontWeight = FontWeight.Bold)
            LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth().height(8.dp))
            Spacer(Modifier.height(5.dp)); Text("GATE POWER  $gatePower", color = Gold, fontWeight = FontWeight.Bold)
        }}
        item { StreakAndCountdownWindow(streak, prefs) }
        item { DailyQuestWindow(day, quest, done, cleared, sounds, onObjective) }
        item { WorkoutWindow(LocalDate.now()) }
        item { ReadinessWindow(day, done, cleared) }
        item { Window("▣ 147 / RNR CHECKPOINT") {
            Text(quest.rnr, color = Color.White, fontSize = 12.sp)
            Spacer(Modifier.height(4.dp)); Text(quest.pyq, color = Muted, fontSize = 11.sp)
        }}
    }
}

@Composable
private fun StreakAndCountdownWindow(streak: Int, prefs: android.content.SharedPreferences) {
    var examDateText by remember { mutableStateOf(prefs.getString("exam_date", GatePlan.START_DATE.plusDays(150).toString()) ?: "") }
    var editing by remember { mutableStateOf(false) }
    val daysLeft = remember(examDateText) {
        try { ChronoUnit.DAYS.between(LocalDate.now(), LocalDate.parse(examDateText)).toInt() } catch (_: Exception) { null }
    }
    Window("🔥 STREAK  •  ⏳ EXAM COUNTDOWN") {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Column { Text("$streak", color = if (streak > 0) Green else Muted, fontSize = 26.sp, fontWeight = FontWeight.Black); Text("DAY STREAK", color = Muted, fontSize = 10.sp) }
            Column(horizontalAlignment = Alignment.End) {
                Text(daysLeft?.let { "$it" } ?: "—", color = Gold, fontSize = 26.sp, fontWeight = FontWeight.Black)
                Text("DAYS TO GATE", color = Muted, fontSize = 10.sp)
            }
        }
        Spacer(Modifier.height(6.dp))
        if (editing) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(value = examDateText, onValueChange = { examDateText = it }, label = { Text("Exam date (YYYY-MM-DD)") }, singleLine = true, modifier = Modifier.weight(1f))
                TextButton(onClick = { prefs.edit().putString("exam_date", examDateText).apply(); editing = false }) { Text("SAVE") }
            }
        } else {
            TextButton(onClick = { editing = true }) { Text("SET EXAM DATE: $examDateText", color = Cyan, fontSize = 11.sp) }
        }
    }
}

@Composable
private fun DailyQuestWindow(day: Int, quest: DailyQuest, done: Int, cleared: Boolean, sounds: SoundManager, onObjective: () -> Unit) {
    Window("⚔ DAILY QUEST • DAY $day / 150") {
        Text(quest.phase, color = Purple, fontSize = 11.sp, fontWeight = FontWeight.Bold)
        TypewriterText(quest.title, color = Color.White, fontSize = 20.sp)
        Text("Difficulty ${quest.difficulty} • ${quest.sets} set${if (quest.sets == 1) "" else "s"}", color = Gold, fontSize = 11.sp)
        Spacer(Modifier.height(6.dp))
        Text("📚 PRIMARY: ${quest.primarySubject}", color = Cyan, fontWeight = FontWeight.Bold)
        Text(quest.primaryTopic, color = Color.White, fontSize = 12.sp)
        Text("Practice target: ${quest.primaryQuestions} questions", color = Green, fontSize = 11.sp)
        Spacer(Modifier.height(6.dp))
        Text("◆ GENERAL APTITUDE (147-cycle slot ${quest.ga.cycleSlot}/3): ${quest.gaQuestions} questions", color = Cyan, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        GaBreakdown(quest.ga)
        Spacer(Modifier.height(4.dp))
        Text("◆ SECONDARY: ${quest.secondarySubject}", color = Cyan, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Text(quest.secondaryTopic, color = Color.White, fontSize = 12.sp)
        Text("Practice target: ${quest.secondaryQuestions} questions", color = Green, fontSize = 11.sp)
        Spacer(Modifier.height(7.dp))
        Text("Objectives: $done / $OBJECTIVE_COUNT", color = Color.White, fontWeight = FontWeight.Bold)
        QuestCheck("Primary study target completed", done >= 1, sounds, onObjective)
        QuestCheck("General Aptitude target completed", done >= 2, sounds, onObjective)
        QuestCheck("Secondary study target completed", done >= 3, sounds, onObjective)
        QuestCheck("147 / RNR completed", done >= 4, sounds, onObjective)
        QuestCheck("PYQ / marked-question review completed", done >= 5, sounds, onObjective)
        QuestCheck("Workout quest completed", done >= 6, sounds, onObjective)
        if (cleared) Text("QUEST CLEARED • REWARDS CLAIMED ✓", color = Green, fontWeight = FontWeight.Bold)
    }
}

/** Shows the 4-chapter GA combination (Verbal / Quantitative / Analytical / Spatial) for the current 147-cycle slot. */
@Composable
private fun GaBreakdown(ga: GaSet) {
    Column(Modifier.padding(top = 3.dp, start = 4.dp)) {
        Text("• Verbal: ${ga.verbal}", color = Color.White, fontSize = 10.sp)
        Text("• Quantitative: ${ga.quantitative}", color = Color.White, fontSize = 10.sp)
        Text("• Analytical & Logical Reasoning: ${ga.analytical}", color = Color.White, fontSize = 10.sp)
        Text("• Spatial Aptitude: ${ga.spatial}", color = Color.White, fontSize = 10.sp)
    }
}

@Composable
private fun QuestScreen(day: Int, quest: DailyQuest, done: Int, cleared: Boolean, xp: Int, gold: Int, sounds: SoundManager, prefs: android.content.SharedPreferences, onObjective: () -> Unit, onClear: () -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
        item { Window("⚔ QUEST WINDOW") {
            Text("DAY $day / 150 • ${quest.phase}", color = Purple, fontWeight = FontWeight.Bold)
            Text(quest.title, color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Black)
            Text("Primary: ${quest.primarySubject}", color = Cyan, fontWeight = FontWeight.Bold)
            Text(quest.primaryTopic, color = Color.White, fontSize = 12.sp)
            Text("Target: ${quest.primaryQuestions} questions", color = Green, fontSize = 12.sp)
            Spacer(Modifier.height(5.dp)); Text("Secondary: ${quest.secondarySubject} • ${quest.secondaryQuestions} questions", color = Cyan, fontSize = 12.sp)
            Text("GA (147-cycle slot ${quest.ga.cycleSlot}/3): ${quest.gaQuestions} questions", color = Cyan, fontSize = 12.sp)
            GaBreakdown(quest.ga)
            Spacer(Modifier.height(3.dp))
            Text("Total planned questions: ${quest.primaryQuestions + quest.secondaryQuestions + quest.gaQuestions}", color = Gold, fontWeight = FontWeight.Bold)
        }}
        item { Window("♻ 147 / RNR") { Text(quest.rnr, color = Color.White, fontSize = 12.sp); Spacer(Modifier.height(5.dp)); Text(quest.pyq, color = Muted, fontSize = 11.sp) } }
        item { WorkoutWindow(LocalDate.now()) }
        item { Window("☑ OBJECTIVES") {
            QuestCheck("Primary study target completed", done >= 1, sounds, onObjective)
            QuestCheck("General Aptitude target completed", done >= 2, sounds, onObjective)
            QuestCheck("Secondary study target completed", done >= 3, sounds, onObjective)
            QuestCheck("147 / RNR completed", done >= 4, sounds, onObjective)
            QuestCheck("PYQ / marked-question review completed", done >= 5, sounds, onObjective)
            QuestCheck("Workout quest completed", done >= 6, sounds, onObjective)
        }}
        item { ErrorMonsterWindow(day, prefs, sounds) }
        item { Window("☑ REWARD WINDOW") {
            Text("Current XP: $xp", color = Cyan); Text("Current Gold: $gold", color = Gold)
            Spacer(Modifier.height(6.dp)); Button(onClick = onClear, enabled = done >= OBJECTIVE_COUNT && !cleared) { Text(if (cleared) "QUEST REWARD CLAIMED" else "CLEAR QUEST + CLAIM REWARD") }
            if (cleared) Text("SYSTEM: QUEST CLEARED ✓", color = Green, fontWeight = FontWeight.Bold)
        }}
    }
}



@Composable
private fun ReadinessWindow(day: Int, done: Int, cleared: Boolean) {
    val planProgress = (day.coerceIn(1, 150) / 150f)
    val todayProgress = done / OBJECTIVE_COUNT.toFloat()
    val index = ((planProgress * 70f) + (todayProgress * 30f)).coerceIn(0f, 100f)
    Window("★ 85+ READINESS") {
        Text("PLAN READINESS INDEX  ${index.toInt()}%", color = if (index >= 85f) Green else Gold, fontSize = 18.sp, fontWeight = FontWeight.Black)
        LinearProgressIndicator(progress = { index / 100f }, modifier = Modifier.fillMaxWidth().height(8.dp))
        Spacer(Modifier.height(5.dp))
        Text("85+ goal • based on plan progress + today's execution", color = Muted, fontSize = 10.sp)
        Text(if (cleared) "TODAY'S QUEST: CLEARED ✓" else "TODAY'S QUEST: ${done}/${OBJECTIVE_COUNT} OBJECTIVES", color = if (cleared) Green else Cyan, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}

data class ErrorMonster(val topic: String, val reason: String, val defeats: Int, val category: String = "Concept mistake")

private val mistakeCategories = listOf("Concept mistake", "Calculation mistake", "Silly mistake", "Time pressure", "Misread question", "Guessing")

private fun loadErrorMonsters(prefs: android.content.SharedPreferences, day: Int): List<ErrorMonster> {
    val raw = prefs.getString("error_monsters_$day", "[]") ?: "[]"
    return try {
        val array = org.json.JSONArray(raw)
        buildList {
            for (i in 0 until array.length()) {
                val o = array.getJSONObject(i)
                add(ErrorMonster(o.optString("topic"), o.optString("reason"), o.optInt("defeats").coerceIn(0, 3), o.optString("category").ifBlank { "Concept mistake" }))
            }
        }
    } catch (_: Exception) { emptyList() }
}

private fun saveErrorMonsters(prefs: android.content.SharedPreferences, day: Int, list: List<ErrorMonster>) {
    val array = org.json.JSONArray()
    list.forEach {
        array.put(org.json.JSONObject().apply {
            put("topic", it.topic)
            put("reason", it.reason)
            put("defeats", it.defeats)
            put("category", it.category)
        })
    }
    prefs.edit().putString("error_monsters_$day", array.toString()).apply()
}

@Composable
private fun ErrorMonsterWindow(day: Int, prefs: android.content.SharedPreferences, sounds: SoundManager) {
    var monsters by remember(day) { mutableStateOf(loadErrorMonsters(prefs, day)) }
    var topic by remember(day) { mutableStateOf("") }
    var reason by remember(day) { mutableStateOf("") }
    var category by remember(day) { mutableStateOf(mistakeCategories.first()) }
    var categoryExpanded by remember { mutableStateOf(false) }
    Window("☠ MISTAKE BOOK — ERROR MONSTERS") {
        Text("Record mistakes, tag the category, and defeat the same concept 3 times.", color = Muted, fontSize = 10.sp)
        Spacer(Modifier.height(5.dp))
        OutlinedTextField(value = topic, onValueChange = { topic = it }, label = { Text("Topic") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(5.dp))
        OutlinedTextField(value = reason, onValueChange = { reason = it }, label = { Text("Mistake / reason") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(5.dp))
        Box {
            OutlinedButton(onClick = { categoryExpanded = true }) { Text("Category: $category") }
            DropdownMenu(expanded = categoryExpanded, onDismissRequest = { categoryExpanded = false }) {
                mistakeCategories.forEach { c ->
                    DropdownMenuItem(text = { Text(c) }, onClick = { category = c; categoryExpanded = false })
                }
            }
        }
        Spacer(Modifier.height(5.dp))
        Button(onClick = {
            if (topic.isNotBlank() && reason.isNotBlank()) {
                monsters = monsters + ErrorMonster(topic.trim(), reason.trim(), 0, category)
                saveErrorMonsters(prefs, day, monsters)
                topic = ""; reason = ""
                sounds.play(SoundManager.Event.EXP_GAIN)
            }
        }) { Text("ADD ERROR MONSTER") }
        Spacer(Modifier.height(5.dp))
        if (monsters.isEmpty()) Text("No error monsters yet.", color = Muted, fontSize = 11.sp)
        monsters.forEachIndexed { index, monster ->
            Column(Modifier.fillMaxWidth().padding(vertical = 5.dp)) {
                Text(monster.topic, color = if (monster.defeats >= 3) Green else Red, fontWeight = FontWeight.Bold)
                Text(monster.reason, color = Color.White, fontSize = 10.sp)
                Text(monster.category, color = Purple, fontSize = 10.sp)
                Text(if (monster.defeats >= 3) "DEFEATED ✓" else "DEFEATS ${monster.defeats}/3", color = if (monster.defeats >= 3) Green else Gold, fontSize = 10.sp)
                if (monster.defeats < 3) {
                    TextButton(onClick = {
                        val newDefeats = (monster.defeats + 1).coerceAtMost(3)
                        val updated = monsters.toMutableList()
                        updated[index] = monster.copy(defeats = newDefeats)
                        monsters = updated
                        saveErrorMonsters(prefs, day, monsters)
                        if (newDefeats >= 3) {
                            prefs.edit().putInt("total_monsters_defeated", prefs.getInt("total_monsters_defeated", 0) + 1).apply()
                        }
                        sounds.play(SoundManager.Event.EXP_GAIN)
                    }) { Text("DEFEAT +1", color = Red) }
                }
            }
        }
    }
}

@Composable
private fun SyllabusSection(title: String, text: String) {
    Text(title, color = Cyan, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 5.dp))
    Text(text, color = Color.White, fontSize = 10.sp, modifier = Modifier.padding(bottom = 3.dp))
}

@Composable
private fun PlanScreen(currentDay: Int) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        item {
            Window("▣ GATE CS 2027 • SYLLABUS") {
                Text("GENERAL APTITUDE — 15 marks (4 chapters, combined daily on a 147-rule / 3-day repeating cycle)", color = Cyan, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 5.dp))
                SyllabusSection("1. Verbal Aptitude", "English Grammar (Articles, Nouns, Pronouns, Parts of Speech, Prepositions, Conjunctions, Subject-Verb Agreement, Tenses, Gerund & Infinitive, Auxiliary Verbs, Adjectives, Adverbs) • Sentence Completion • Synonyms • Antonyms • Vocabulary, Word Analogy, Idioms & Phrases, Odd Word Out")
                SyllabusSection("2. Quantitative Aptitude", "Numbers, Algebra & Data Interpretation • Percentage, SI/CI, Profit & Loss, Partnership, Stocks & Shares • Speed-Time-Work, Boats & Streams, Pipes & Cisterns • Ratio, Proportion, Variation & Mixtures • Permutations-Combinations, Statistics & Probability • Linear/Quadratic Equations, Geometry & Mensuration, Powers, Exponents & Logarithms")
                SyllabusSection("3. Analytical & Logical Reasoning", "Verbal & Logical Reasoning, Analogy, Classification, Coding-Decoding, Blood Relations, Puzzle Test, Direction Sense, Logical Venn Diagrams, Number/Ranking/Time Sequence, Mathematical Operations, Decision Making, Cubes, Arrangements, Clocks, Calendars, Deductions, Data Sufficiency")
                SyllabusSection("4. Spatial Aptitude", "Transformations & Geometrical Transformations • Paper Folding and Cutting • Patterns in 2D & 3D Dimensions • Shape Matching in 2D & 3D")
                Text("ENGINEERING MATHEMATICS — 13 marks", color = Cyan, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 8.dp))
                SyllabusSection("1. Linear Algebra", "Vector Spaces, Subspaces & Spanning Sets • Determinants (Minors, Cofactors) • Algebra of Matrices, Equality, Transpose, Orthogonal Matrix • Rank of a Matrix, Cramer's Rule • Eigenvalues & Eigenvectors • Cayley-Hamilton Theorem")
                SyllabusSection("2. Calculus", "Limits, Continuity & Differentiability, Mean Value Theorems • Derivatives, Partial Derivatives, Taylor Series • Standard Integrations, Definite/Multiple/Triple Integrals, Change of Order • Line, Surface & Volume Integrals • Fourier Series")
                SyllabusSection("3. Probability & Statistics", "Probability, Sampling, Conditional Probability • Discrete Random Variables, Dependent Events, Total Probability & Bayes' Theorem • Central Tendency & Dispersion • Bernoulli Trials, Probability Distribution • Correlation & Regression")
                SyllabusSection("4. Discrete Mathematics", "Mathematical Logic — Statements, Connectives, WFF, Propositional & Predicate Calculus • Set Theory — Laws, Venn Diagrams, Cartesian Products, Relations, Functions • Algebra — Semigroups, Groups, Residue Classes, Partial Ordering, Lattices, Boolean Algebra • Graph Theory — Subgraphs, Binary Trees, Hamiltonian Graphs, Coverings • Combinatorics — Combinations, Counting")
                SyllabusSection("DIGITAL LOGIC (GATE 2027 wording)", "Boolean algebra and minimization — algebraic technique, Karnaugh map, tabular (Quine–McCluskey) method • Design of combinational circuits • Design of sequential circuits • Number representation and arithmetic (fixed and floating point)")
                SyllabusSection("COMPUTER ORGANIZATION & ARCHITECTURE (GATE 2027 wording)", "Instruction set and addressing modes • Design of arithmetic and logic unit (ALU) • Design of control unit — hardwired and microprogrammed • Memory interfacing and hierarchy: performance, cache memory mapping • I/O interface (interrupt and DMA) • Instruction pipelining, pipeline hazards")
                SyllabusSection("DATA STRUCTURES & ALGORITHMS", "C programming • Arrays • Linked lists • Stacks • Queues • Trees • BST • Heaps • Graphs • BFS/DFS • Spanning trees • Shortest paths • B-trees • Complexity • Divide & conquer • Searching • Sorting • Hashing")
                SyllabusSection("THEORY OF COMPUTATION", "Regular languages • Regular expressions • DFA • NFA • ε-NFA • CFL • CFG • PDA • Turing machines • Multitape TM • Nondeterministic TM • Universal TM • FSM with output • Undecidability")
                SyllabusSection("COMPILER DESIGN", "Compiler phases • Lexical analysis • Syntax analysis • Ambiguity • Semantic analysis • Parsing • LR/SLR • Conflicts • Parse tables • SDD • Syntax trees • L-attributed definitions • Intermediate code • Instruction selection • Optimization • Data flow • Liveness")
                SyllabusSection("OPERATING SYSTEMS", "Processes • Threads • IPC • System calls • Context switching • CPU scheduling • Concurrency • Critical section • Semaphores • Deadlock • Memory management • Paging • TLB • Page faults • Page replacement • Thrashing • File systems • Disk scheduling • Security")
                SyllabusSection("DATABASE MANAGEMENT SYSTEMS", "DBMS concepts • ER model • Relational model • Data models • Relational algebra • Set operations • Cartesian product • Normalization • Functional dependencies • SQL • File organization • Indexing • B-trees • Transactions • Concurrency control")
                SyllabusSection("COMPUTER NETWORKS (GATE 2027 wording — reduced from 2026)", "Principles of Layering • Switching: circuit, packet & virtual-circuit + performance metrics • Data link layer: error detection, Medium Access Control, Ethernet • Distance vector and link state routing • IPv4: Fragmentation, CIDR Notation, Network Address Translation • TCP: flow control and congestion control, socket API • DNS and HTTP  (ARP, DHCP, ICMP, UDP, SMTP/FTP/email and plain OSI-layer questions are de-emphasized for 2027 — treat as background only)")
            }
        }

        item {
            Window("▣ GATE CS 2027 • 150-DAY PLAN") {
                Text("START: ${GatePlan.START_DATE_TEXT}", color = Gold, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text("TARGET: 85+ / 100", color = Cyan, fontSize = 18.sp, fontWeight = FontWeight.Black)
                Text("Every day contains the primary topic, secondary revision, GA practice, 147/RNR and PYQ work.", color = Muted, fontSize = 11.sp)
            }
        }

        items(150) { index ->
            val d = index + 1
            val q = GatePlan.forDay(d)
            val date = GatePlan.START_DATE.plusDays(index.toLong())
            val active = d == currentDay

            Window(if (active) "▶ DAY $d • TODAY" else "DAY $d") {
                Text(date.toString(), color = Gold, fontSize = 10.sp)
                Text(q.phase, color = Purple, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                Text(q.title, color = Color.White, fontSize = 15.sp, fontWeight = FontWeight.Black)
                Spacer(Modifier.height(3.dp))
                Text("PRIMARY • ${q.primarySubject}", color = Cyan, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text(q.primaryTopic, color = Color.White, fontSize = 11.sp)
                Text("SECONDARY • ${q.secondarySubject}", color = Cyan, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                Text(q.secondaryTopic, color = Muted, fontSize = 10.sp)
                Text("QUESTIONS • Primary ${q.primaryQuestions} • Secondary ${q.secondaryQuestions} • GA ${q.gaQuestions} (slot ${q.ga.cycleSlot}/3)", color = Green, fontSize = 10.sp)
                GaBreakdown(q.ga)
                Text("147/RNR • ${q.rnr}", color = Gold, fontSize = 10.sp)
                Text("PYQ • ${q.pyq}", color = Muted, fontSize = 10.sp)
            }
        }
    }
}

@Composable
private fun WorkoutWindow(date: LocalDate) {
    Window("♨ WORKOUT QUEST • ${date.dayOfWeek.name}") {
        Text(GatePlan.workoutFor(date), color = Gold, fontSize = 15.sp, fontWeight = FontWeight.Black)
        Spacer(Modifier.height(4.dp))
        GatePlan.workoutExercises(date).forEach { Text("• $it", color = Color.White, fontSize = 12.sp, modifier = Modifier.padding(vertical = 2.dp)) }
    }
}

// ── HUNTER TAB ── Topic Mastery, Weak Topic Detector, Boss Battles, Achievements, Formula Vault ──

@Composable
private fun HunterScreen(context: android.content.Context, prefs: android.content.SharedPreferences, totalXp: Int, level: Int, streak: Int, sounds: SoundManager) {
    var masteryVersion by remember { mutableIntStateOf(0) } // bump to force re-read from prefs after +/- taps
    val mastery = remember(masteryVersion) { Mastery.all(context) }
    val weak = remember(masteryVersion) { Mastery.weakest(context) }
    val readiness = remember(masteryVersion) { Mastery.overallReadiness(context) }
    val questsCleared = prefs.getInt("total_quests_cleared", 0)
    val monstersDefeated = prefs.getInt("total_monsters_defeated", 0)
    val stats = AchievementStats(totalXp, level, streak, questsCleared, monstersDefeated)
    val earned = remember(totalXp, level, streak, questsCleared, monstersDefeated) { Achievements.earned(stats).map { it.id }.toSet() }

    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
        item {
            Window("🧠 SUBJECT MASTERY") {
                Text("Self-rated 0-100% per subject. Drives the Weak Topic Detector and Boss Battles below.", color = Muted, fontSize = 10.sp)
                Spacer(Modifier.height(6.dp))
                Text("OVERALL READINESS  $readiness%", color = if (readiness >= 70) Green else Gold, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                mastery.forEach { (subject, pct) ->
                    Row(Modifier.fillMaxWidth().padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(Modifier.weight(1f)) {
                            Text(subject, color = Color.White, fontSize = 11.sp)
                            LinearProgressIndicator(progress = { pct / 100f }, modifier = Modifier.fillMaxWidth().height(5.dp))
                        }
                        Spacer(Modifier.width(6.dp))
                        Text("$pct%", color = if (pct >= 60) Green else Red, fontWeight = FontWeight.Bold, fontSize = 11.sp, modifier = Modifier.width(38.dp))
                        TextButton(onClick = { Mastery.set(context, subject, pct - 5); masteryVersion++ }) { Text("−", color = Red) }
                        TextButton(onClick = { Mastery.set(context, subject, pct + 5); masteryVersion++ }) { Text("+", color = Green) }
                    }
                }
            }
        }
        item {
            Window("☠ WEAK TOPIC DETECTOR") {
                if (weak.isEmpty()) {
                    Text("No subject below 60% mastery — nothing flagged as weak right now.", color = Muted, fontSize = 11.sp)
                } else {
                    Text("Below 60% mastery, weakest first:", color = Muted, fontSize = 10.sp)
                    Spacer(Modifier.height(4.dp))
                    weak.forEach { (subject, pct) ->
                        val priority = when { pct < 30 -> "VERY HIGH" to Red; pct < 45 -> "HIGH" to Gold; else -> "MEDIUM" to Cyan }
                        Text("• $subject — $pct% • Priority: ${priority.first}", color = priority.second, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
        item {
            Window("👹 BOSS BATTLES") {
                Text("Each subject is a boss with 1000 HP. Raising mastery damages the boss.", color = Muted, fontSize = 10.sp)
                Spacer(Modifier.height(6.dp))
                mastery.forEach { (subject, pct) ->
                    val remainingHp = (1000 * (1 - pct / 100f)).toInt()
                    Column(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                        Text("BOSS: ${subject.uppercase()}", color = if (pct >= 100) Green else Purple, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                        LinearProgressIndicator(progress = { pct / 100f }, modifier = Modifier.fillMaxWidth().height(6.dp))
                        Text(if (pct >= 100) "DEFEATED ✓" else "Remaining HP: $remainingHp / 1000 • Your damage: $pct%", color = Muted, fontSize = 10.sp)
                    }
                }
            }
        }
        item {
            Window("🏅 ACHIEVEMENTS  (${earned.size}/${Achievements.all.size})") {
                Achievements.all.forEach { a ->
                    val done = earned.contains(a.id)
                    Text("${a.icon} ${a.title}", color = if (done) Green else Muted, fontWeight = if (done) FontWeight.Bold else FontWeight.Normal, fontSize = 11.sp, modifier = Modifier.padding(vertical = 1.dp))
                }
            }
        }
        item {
            Window("📖 FORMULA / CONCEPT VAULT") {
                var vaultVersion by remember { mutableIntStateOf(0) }
                Text("Tap ★ to favorite, ⚠ to mark as frequently forgotten.", color = Muted, fontSize = 10.sp)
                Spacer(Modifier.height(6.dp))
                FormulaVault.formulas.forEach { f ->
                    val fav = remember(vaultVersion) { FormulaVault.isFavorite(context, f.id) }
                    val hard = remember(vaultVersion) { FormulaVault.isDifficult(context, f.id) }
                    Column(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                        Text(f.subject, color = Cyan, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        Text(f.text, color = Color.White, fontSize = 11.sp)
                        Row {
                            TextButton(onClick = { FormulaVault.toggleFavorite(context, f.id); vaultVersion++ }) { Text(if (fav) "★ Favorited" else "☆ Favorite", color = if (fav) Gold else Muted, fontSize = 10.sp) }
                            TextButton(onClick = { FormulaVault.toggleDifficult(context, f.id); vaultVersion++ }) { Text(if (hard) "⚠ Forgotten often" else "⚠ Mark difficult", color = if (hard) Red else Muted, fontSize = 10.sp) }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SettingsScreen(soundOn: Boolean, vibrationOn: Boolean, dailyQuestNotifsOn: Boolean, setSound: (Boolean) -> Unit, setVibration: (Boolean) -> Unit, setDailyQuestNotifs: (Boolean) -> Unit, sounds: SoundManager, context: android.content.Context, onReset: () -> Unit) {
    var canExactAlarm by remember {
        mutableStateOf(
            if (Build.VERSION.SDK_INT >= 31) context.getSystemService(android.app.AlarmManager::class.java)?.canScheduleExactAlarms() ?: true
            else true
        )
    }
    val hasPostNotif = if (Build.VERSION.SDK_INT >= 33) {
        androidx.core.content.ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
    } else true
    val lifecycleOwner = androidx.compose.ui.platform.LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
            if (event == androidx.lifecycle.Lifecycle.Event.ON_RESUME) {
                if (Build.VERSION.SDK_INT >= 31) {
                    canExactAlarm = context.getSystemService(android.app.AlarmManager::class.java)?.canScheduleExactAlarms() ?: true
                }
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
        item { Window("🔔 DAILY QUEST NOTIFICATIONS") {
            Text("Plain basic notifications about today's quest, three times a day.", color = Muted, fontSize = 11.sp)
            Spacer(Modifier.height(6.dp))
            Text("• 5:30 AM — Morning quest briefing", color = Color.White, fontSize = 11.sp)
            Text("• 2:30 PM — Afternoon progress check", color = Color.White, fontSize = 11.sp)
            Text("• 6:00 PM — Evening quest reminder", color = Color.White, fontSize = 11.sp)
            Spacer(Modifier.height(8.dp))
            SettingRow("Enable Daily Quest Notifications", dailyQuestNotifsOn) { setDailyQuestNotifs(it); if (it) SystemNotificationScheduler.scheduleAll(context) }
            Spacer(Modifier.height(10.dp))
            if (!hasPostNotif) {
                Text("✗ Notification permission NOT granted — nothing will show", color = Red, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                Spacer(Modifier.height(4.dp))
                Button(onClick = {
                    context.startActivity(
                        Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                            .putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                    )
                }) { Text("OPEN NOTIFICATION SETTINGS") }
            } else {
                Text("✓ Notification permission granted", color = Green, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
            Spacer(Modifier.height(10.dp))
            if (!canExactAlarm) {
                Text("⚠ Exact alarms not permitted — reminders may run late", color = Gold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                Spacer(Modifier.height(4.dp))
                Button(onClick = {
                    context.startActivity(
                        Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, android.net.Uri.parse("package:${context.packageName}"))
                    )
                }) { Text("ALLOW EXACT ALARMS") }
            } else {
                Text("✓ Exact alarms permitted", color = Green, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
            Spacer(Modifier.height(10.dp))
            val powerManager = context.getSystemService(android.os.PowerManager::class.java)
            val ignoringBatteryOpt = powerManager?.isIgnoringBatteryOptimizations(context.packageName) ?: true
            if (!ignoringBatteryOpt) {
                Text("✗ Battery optimization is ON for this app — background alarms may be delayed", color = Red, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                Spacer(Modifier.height(4.dp))
                Button(onClick = {
                    try {
                        context.startActivity(
                            Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, android.net.Uri.parse("package:${context.packageName}"))
                        )
                    } catch (e: Exception) {
                        context.startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
                    }
                }) { Text("DISABLE BATTERY OPTIMIZATION") }
            } else {
                Text("✓ Battery optimization disabled for this app", color = Green, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
            Spacer(Modifier.height(10.dp))
            val nm = context.getSystemService(NotificationManager::class.java)
            val interruptionFilter = nm?.currentInterruptionFilter ?: NotificationManager.INTERRUPTION_FILTER_ALL
            if (interruptionFilter != NotificationManager.INTERRUPTION_FILTER_ALL) {
                Text("⚠ Do Not Disturb is ON — this may silently block alerts", color = Gold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                Text("Pull down your quick settings and turn DND off, or add this app to DND exceptions.", color = Muted, fontSize = 10.sp)
                Spacer(Modifier.height(10.dp))
            }
            Button(onClick = {
                try {
                    val enabled = NotificationManagerCompat.from(context).areNotificationsEnabled()
                    when {
                        !enabled -> Toast.makeText(context, "BLOCKED: notifications are disabled for this app in system settings", Toast.LENGTH_LONG).show()
                        else -> {
                            val day = GatePlan.currentDay(LocalDate.now())
                            NotificationHelper.showDailyQuest(context, day, "Test", GatePlan.forDay(day).title)
                            Toast.makeText(context, "Sent. Pull down the notification shade now.", Toast.LENGTH_LONG).show()
                        }
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "ERROR: ${e.javaClass.simpleName}: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }) { Text("SEND TEST NOTIFICATION NOW") }
        }}
        item { Window("⚙ SYSTEM AUDIO") {
            SettingRow("System Sounds", soundOn) { setSound(it) }; SettingRow("Haptic Feedback", vibrationOn) { setVibration(it) }
            Spacer(Modifier.height(8.dp)); Button(onClick = { sounds.play(SoundManager.Event.ARISE_SYSTEM) }) { Text("TEST SYSTEM") }
            Button(onClick = { sounds.play(SoundManager.Event.LEVEL_UP) }) { Text("TEST LEVEL-UP") }; Button(onClick = { sounds.play(SoundManager.Event.ARISE) }) { Text("TEST ARISE") }
        }}
        item { Window("▣ V6.7 DAILY QUEST SYSTEM") {
            Text("150-day plan • subjects • topics • question targets • 147/RNR • daily workout", color = Cyan, fontSize = 12.sp)
            Text("Today is calculated from ${GatePlan.START_DATE_TEXT} as Day 1.", color = Muted, fontSize = 11.sp)
            Text("Tip: add the SYSTEM widget to your home screen for a one-glance view of today's quest + workout.", color = Muted, fontSize = 11.sp)
            Spacer(Modifier.height(6.dp)); OutlinedButton(onClick = onReset) { Text("RESET ALL PROGRESS", color = Red) }
        }}
    }
}

@Composable private fun Window(title: String, content: @Composable ColumnScope.() -> Unit) {
    val glow by rememberInfiniteTransition(label = "panelGlow").animateFloat(
        initialValue = 0.28f, targetValue = 0.62f,
        animationSpec = infiniteRepeatable(tween(1800, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "panelGlowAnim"
    )
    Box(Modifier.fillMaxWidth()) {
        Column(
            Modifier
                .fillMaxWidth()
                .border(1.dp, Cyan.copy(alpha = glow), CutCornerShape(8.dp))
                .background(Panel)
                .padding(12.dp)
        ) {
            Text(title, color = Cyan, fontWeight = FontWeight.ExtraBold, fontSize = 13.sp, letterSpacing = 1.2.sp)
            Spacer(Modifier.height(7.dp))
            content()
        }
        SystemCornerBrackets(glow)
    }
}

/** Draws the same angular corner-bracket motif used in the notification frames on every in-app panel. */
@Composable
private fun BoxScope.SystemCornerBrackets(alpha: Float) {
    Canvas(Modifier.matchParentSize()) {
        val len = 9.dp.toPx()
        val stroke = 1.6.dp.toPx()
        val color = Cyan.copy(alpha = (alpha + 0.35f).coerceAtMost(1f))
        drawLine(color, Offset(0f, 0f), Offset(len, 0f), stroke)
        drawLine(color, Offset(0f, 0f), Offset(0f, len), stroke)
        drawLine(color, Offset(size.width, 0f), Offset(size.width - len, 0f), stroke)
        drawLine(color, Offset(size.width, 0f), Offset(size.width, len), stroke)
        drawLine(color, Offset(0f, size.height), Offset(len, size.height), stroke)
        drawLine(color, Offset(0f, size.height), Offset(0f, size.height - len), stroke)
        drawLine(color, Offset(size.width, size.height), Offset(size.width - len, size.height), stroke)
        drawLine(color, Offset(size.width, size.height), Offset(size.width, size.height - len), stroke)
    }
}

/** Faint HUD grid + scanlines + top vignette drawn once behind all screen content. */
@Composable
private fun SystemBackground(modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val gridColor = Cyan.copy(alpha = 0.05f)
        val step = 26.dp.toPx()
        var x = 0f
        while (x < size.width) { drawLine(gridColor, Offset(x, 0f), Offset(x, size.height), 1f); x += step }
        var y = 0f
        while (y < size.height) { drawLine(gridColor, Offset(0f, y), Offset(size.width, y), 1f); y += step }
        val scanColor = Color.White.copy(alpha = 0.02f)
        val scanStep = 3.dp.toPx()
        var sy = 0f
        while (sy < size.height) { drawLine(scanColor, Offset(0f, sy), Offset(size.width, sy), 1f); sy += scanStep }
        drawRect(
            brush = Brush.radialGradient(
                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.5f)),
                center = Offset(size.width / 2f, 0f),
                radius = size.height * 0.95f
            )
        )
    }
}

/** Reveals text one character at a time, System-message style. */
@Composable
private fun TypewriterText(
    text: String,
    color: Color,
    fontSize: TextUnit,
    fontWeight: FontWeight = FontWeight.Black,
    textAlign: TextAlign? = null,
    modifier: Modifier = Modifier
) {
    var shown by remember(text) { mutableStateOf("") }
    LaunchedEffect(text) {
        shown = ""
        for (i in text.indices) { shown = text.substring(0, i + 1); delay(22L) }
    }
    Text(shown, color = color, fontSize = fontSize, fontWeight = fontWeight, textAlign = textAlign, modifier = modifier)
}

private data class SystemBurst(val label: String, val title: String)

/**
 * Full-screen "light pillar" moment, reserved for level-up / rank-up only so it stays
 * a rare flourish rather than something the player sees on every action.
 */
@Composable
private fun CinematicBurstOverlay(burst: SystemBurst, onDone: () -> Unit) {
    val beamAlpha by rememberInfiniteTransition(label = "beam").animateFloat(
        initialValue = 0.7f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(700, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "beamAlpha"
    )
    LaunchedEffect(burst) { delay(1900); onDone() }

    Box(
        Modifier
            .fillMaxSize()
            .background(Color(0xFF010207))
            .clickable { onDone() },
        contentAlignment = Alignment.Center
    ) {
        Box(
            Modifier
                .width(70.dp)
                .fillMaxHeight()
                .blur(20.dp)
                .background(
                    Brush.horizontalGradient(
                        listOf(
                            Color.Transparent,
                            Cyan.copy(alpha = beamAlpha * 0.45f),
                            Color.White.copy(alpha = beamAlpha),
                            Cyan.copy(alpha = beamAlpha * 0.45f),
                            Color.Transparent
                        )
                    )
                )
        )
        listOf(-26, -12, 2, 16, -34, 10, 28).forEachIndexed { i, x -> FallingSpark(i, x) }
        Text(
            "NOTIFICATION",
            color = Color.White.copy(alpha = 0.85f),
            fontWeight = FontWeight.Bold,
            fontSize = 20.sp,
            letterSpacing = 6.sp,
            modifier = Modifier.graphicsLayer(rotationZ = 90f)
        )
        Column(
            Modifier.align(Alignment.BottomCenter).padding(bottom = 56.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(burst.label, color = Cyan, fontWeight = FontWeight.Bold, fontSize = 13.sp, letterSpacing = 3.sp)
            Spacer(Modifier.height(4.dp))
            Text(burst.title, color = Color.White, fontWeight = FontWeight.Black, fontSize = 22.sp, textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun FallingSpark(index: Int, xDp: Int) {
    val y by rememberInfiniteTransition(label = "spark$index").animateFloat(
        initialValue = -40f, targetValue = 900f,
        animationSpec = infiniteRepeatable(tween(1400 + index * 260, easing = LinearEasing), RepeatMode.Restart),
        label = "sparkY$index"
    )
    val sparkAlpha = (1f - (y / 900f)).coerceIn(0f, 1f) * 0.9f
    Box(
        Modifier
            .offset(x = xDp.dp, y = y.dp)
            .size(width = 2.dp, height = 16.dp)
            .background(Color.White.copy(alpha = sparkAlpha))
    )
}
@Composable private fun Stat(label: String, value: String) { Column(horizontalAlignment = Alignment.CenterHorizontally) { Text(value, color = Color.White, fontWeight = FontWeight.Black, fontSize = 20.sp); Text(label, color = Muted, fontSize = 9.sp) } }
@Composable private fun QuestCheck(label: String, checked: Boolean, sounds: SoundManager, onChange: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 2.dp), verticalAlignment = Alignment.CenterVertically) {
        Checkbox(checked = checked, onCheckedChange = { if (it && !checked) { sounds.play(SoundManager.Event.CHECKBOX_TICK); onChange() } })
        Text(label, color = if (checked) Muted else Color.White, fontSize = 12.sp)
    }
}
@Composable private fun SettingRow(label: String, checked: Boolean, onChecked: (Boolean) -> Unit) { Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) { Text(label, color = Color.White); Switch(checked = checked, onCheckedChange = onChecked) } }
@Composable private fun RowScope.NavButton(text: String, selected: Boolean, onClick: () -> Unit) { Button(onClick = onClick, modifier = Modifier.weight(1f), contentPadding = PaddingValues(horizontal = 4.dp, vertical = 8.dp), colors = ButtonDefaults.buttonColors(containerColor = if (selected) Cyan.copy(alpha = .20f) else Panel)) { Text(text, fontSize = 10.sp, color = if (selected) Cyan else Muted) } }
