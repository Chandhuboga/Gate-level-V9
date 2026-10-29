package com.chandu.gatesystem.ai2027.data.repo

import com.chandu.gatesystem.ai2027.data.SettingsStore
import com.chandu.gatesystem.ai2027.domain.*
import com.chandu.gatesystem.ai2027.domain.gen.QuestionFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class Provided(val questions: List<Question>, val usedAi: Boolean, val note: String)

/**
 * Question supply, in this order:
 *  1. (optional) AI-generated questions, a share of the set, validated and labelled AI-generated;
 *  2. UNSEEN questions from the pre-installed 250-per-subject bank (topic first, then the whole subject);
 *  3. the offline generator (computed answers), which never runs dry.
 * Nothing the learner has already attempted is served again.
 */
class QuestionProvider(private val content: ContentRepository, private val settings: SettingsStore, private val transport: AiTransport) {

    suspend fun provide(subjectId: String, topicId: String, topicTitle: String, count: Int, wantAi: Boolean, seed: Long,
                        exclude: Set<String>, previousMistakes: List<String> = emptyList(), role: BankRole = BankRole.PRACTICE,
                        avoidIds: Collection<String> = emptyList()): Provided = withContext(Dispatchers.IO) {
        val notes = ArrayList<String>(); val got = ArrayList<Question>(); var usedAi = false
        fun add(qs: List<Question>) { for (q in qs) if (got.none { it.id == q.id } && q.id !in avoidIds) got += q }
        val cfg = settings.aiConfig()
        if (wantAi && subjectId != "MIXED") {
            if (!cfg.configured) notes += AiOutcome.NotConfigured.describe()
            else {
                val ai = AiService(transport, cfg)
                val existing = content.recentForTopic(topicId, 60)
                val aiCount = minOf(count, maxOf(3, (count * 4 + 9) / 10))
                val plan = if (aiCount >= 6) listOf(QType.MCQ to (aiCount * 7 / 10), QType.NAT to (aiCount - aiCount * 7 / 10)) else listOf(QType.MCQ to aiCount)
                var failed = false
                for ((type, n) in plan) {
                    var left = n
                    while (left > 0 && !failed) {
                        val take = minOf(left, 10); left -= take
                        val req = GenerationRequest(Subjects.get(subjectId).name, topicTitle, topicTitle, "VSSC Technical Assistant (ECE) practice on $topicTitle",
                            Difficulty.MEDIUM, type, take, null, previousMistakes, existing.map { it.concept }.distinct().take(20))
                        val out = ai.generate(req, existing + got)
                        notes += out.describe()
                        if (out is AiOutcome.Success) {
                            content.ensureAll(out.batch.flagged, flagged = true)
                            val stored = content.ensureAll(out.batch.accepted)
                            add(stored); usedAi = usedAi || stored.isNotEmpty()
                        } else failed = true
                    }
                }
            }
        }
        val salt = ((seed % 9973).toInt() + 7).coerceAtLeast(1)
        if (got.size < count) {
            val bank = content.unseen(subjectId, topicId, null, null, role, got.map { it.id } + avoidIds, salt, count - got.size)
            add(bank)
            if (got.size < count) add(content.unseen(subjectId, null, null, null, role, got.map { it.id } + avoidIds, salt, count - got.size))
            if (got.size < count && role != BankRole.PRACTICE) add(content.unseen(subjectId, null, null, null, null, got.map { it.id } + avoidIds, salt, count - got.size))
            if (got.isNotEmpty()) notes += "Pre-installed question bank supplied ${got.count { it.source != QSource.AI_GENERATED }}"
        }
        if (got.size < count) {
            val ids = HashSet<String>(exclude + avoidIds).also { s -> got.forEach { s += it.id; s += QuestionValidator.fingerprint(it) } }
            var local = QuestionFactory.generate(subjectId, topicId, topicTitle, count - got.size, seed, ids)
            if (local.size < count - got.size) local = local + QuestionFactory.staticFor(subjectId).filter { it.id !in ids && local.none { l -> l.id == it.id } }.take(count - got.size - local.size)
            val stored = content.ensureAll(local)
            add(stored)
            if (stored.isNotEmpty()) notes += "Offline generator supplied ${stored.size} fresh questions (bank exhausted for this topic)"
        }
        Provided(got.take(count), usedAi, notes.joinToString("; ").ifBlank { "Pre-installed question bank" })
    }
}
