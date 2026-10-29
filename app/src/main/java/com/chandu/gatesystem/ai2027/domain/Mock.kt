package com.chandu.gatesystem.ai2027.domain

/** One slot in a mock paper. */
data class MockSlot(val subjectId: String, val marks: Int)

object MockBlueprint {
    /**
     * Official GATE CS pattern per the plan document: 65 questions, 100 marks, 180 min.
     * GA = 10 questions / 15 marks (5x1 + 5x2), Engineering Mathematics = 8 questions / 13 marks (3x1 + 5x2),
     * CS subjects = 47 questions / 72 marks (22x1 + 25x2).
     */
    private val ece = listOf(
        Pair("EDC", 8), Pair("ANA", 9), Pair("DIG", 9), Pair("COM", 8), Pair("MPMC", 6), Pair("EMI", 5),
        Pair("SS", 6), Pair("CTRL", 6), Pair("NT", 8), Pair("EMFW", 7), Pair("EM", 8)
    )
    /** VSSC TA (ECE) mock: 80 questions x 1 mark = 80 marks, 90 minutes, -0.33 per wrong answer. */
    val fullGateCs: List<MockSlot> by lazy {
        val l = ArrayList<MockSlot>()
        for ((s, n) in ece) repeat(n) { l += MockSlot(s, 1) }
        l
    }
    const val FULL_DURATION_SEC = 90 * 60
    val totalMarks get() = fullGateCs.sumOf { it.marks }
}

data class MockResult(
    val id: String, val day: Int?, val type: String, val percent: Double, val netMarks: Double, val maxMarks: Double,
    val accuracy: Double, val attempted: Int, val total: Int, val timeUsedSec: Int, val durationSec: Int, val createdEpochDay: Long
)

object MockAnalytics {
    /** Linear-regression slope of percent over attempt number (percentage points per mock). */
    fun trendSlope(results: List<MockResult>): Double {
        val r = results.sortedBy { it.createdEpochDay }
        if (r.size < 2) return 0.0
        val n = r.size
        val xs = (0 until n).map { it.toDouble() }; val ys = r.map { it.percent }
        val mx = xs.average(); val my = ys.average()
        val den = xs.sumOf { (it - mx) * (it - mx) }
        return if (den == 0.0) 0.0 else xs.indices.sumOf { (xs[it] - mx) * (ys[it] - my) } / den
    }
    fun recentAverage(results: List<MockResult>, n: Int = 3): Double =
        results.sortedBy { it.createdEpochDay }.takeLast(n).let { l -> if (l.isEmpty()) 0.0 else l.map { it.percent }.average() }

    data class TimeAnalysis(val minutesPerQuestion: Double, val minutesPerMark: Double, val usedFraction: Double, val advice: String)

    fun timeManagement(report: SetReport, durationSec: Int): TimeAnalysis {
        val used = report.timeSpentSec
        val mpq = if (report.attempted == 0) 0.0 else used / 60.0 / report.attempted
        val mpm = if (report.maxMarks == 0.0) 0.0 else used / 60.0 / report.maxMarks
        val frac = if (durationSec == 0) 0.0 else used.toDouble() / durationSec
        val advice = when {
            report.attempted < report.total * 0.8 && frac > 0.95 -> "You ran out of time with ${report.unanswered} unattempted. Skip long questions earlier and bank easy marks first."
            report.accuracy < 0.5 && report.attempted > report.total * 0.9 -> "You attempted almost everything but accuracy was low; slow down and avoid guessing on MCQs (negative marks)."
            frac < 0.7 -> "You finished with lots of time left; use the spare time to re-check calculations."
            else -> "Pacing looked reasonable. Keep targeting about ${"%.1f".format(durationSec / 60.0 / maxOf(1, report.total))} min per question."
        }
        return TimeAnalysis(mpq, mpm, frac, advice)
    }

    /** Topics with accuracy below [threshold] (and at least 2 attempts), weakest first. */
    fun weakTopics(report: SetReport, threshold: Double = 0.5): List<GroupStat> =
        report.byTopic.filter { it.attempted >= 2 && it.accuracy < threshold }.sortedBy { it.accuracy }
}
