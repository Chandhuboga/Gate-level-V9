"""Builds app/src/main/assets/plan_150.json (same schema as the old plan_114.json) from the VSSC TA ECE 150-day plan."""
import re, json, datetime as dt, sys, os
HTML = sys.argv[1]; OLD = sys.argv[2]; OUT = sys.argv[3]
s = open(HTML, encoding='utf-8').read()
S = json.loads(re.search(r'var S=(\[\n.*?\n\]);\nvar MOCK', s, re.S).group(1))
learn = [(x[0], c) for x in S for c in x[1]]
subs = [x[0] for x in S]
short = {"Electronic Devices & Circuits":"Devices","Analog Electronics":"Analog","Digital Electronics":"Digital","Communication Systems":"Communication","Microprocessors & Microcontrollers":"Microprocessors","Electronic Measurements & Instrumentation":"Measurements","Signals & Systems":"Signals","Control Systems":"Control","Network Theory":"Network Theory","Electromagnetic Fields & Waves":"EM Waves","Engineering Mathematics":"Maths"}
start = dt.date(2026,10,27)
mocks_p1 = {dt.date(2026,11,29),dt.date(2026,12,27),dt.date(2027,1,31),dt.date(2027,2,21)}
rev = subs + subs[:9]
old = json.load(open(OLD))['days']
byWd = {}
for d in old: byWd.setdefault(d['weekday'], []).append(d)
rows = []; li = ri = mk = wk = 0
for n in range(1,151):
    d = start + dt.timedelta(n-1)
    r = dict(n=n, date=d, wd=d.strftime('%a'))
    if n <= 120:
        if d in mocks_p1: mk += 1; r.update(t='MOCK', no=mk)
        elif d.weekday() == 6: wk += 1; r.update(t='TEST', no=wk)
        else: sj, tp = learn[li]; li += 1; r.update(t='LEARN', sj=sj, tp=tp)
    else:
        if (n-121) % 3 == 2: mk += 1; r.update(t='MOCK', no=mk)
        else: sj = rev[ri]; ri += 1; r.update(t='REVISE', sj=sj, tp=f"Revise {short[sj]}" + (" (2nd round)" if ri > 11 else ""))
    rows.append(r)
assert li == 103 and mk == 14 and ri == 20
learnByDay = {r['n']: r for r in rows if r['t'] == 'LEARN'}
cnt = {}; days = []; lastLearn = None; mockDays = []
for r in rows:
    n = r['n']; t = r['t']
    pool = byWd[r['wd']]; k = cnt.get(r['wd'], 0); cnt[r['wd']] = k + 1; o = pool[k % len(pool)]
    due = [dict(fromDay=m, subject=learnByDay[m]['sj'], topic=learnByDay[m]['tp']) for m in (n-1, n-4, n-7) if m in learnByDay]
    day = dict(day=n, weekday=r['wd'], date=r['date'].isoformat(), fullMock=False, due=due,
               dueNote=None if due else ("No earlier learning topic due; begin the Error Monster list." if n == 1 else None),
               weeklyReview=False, weeklyReviewText=None, mockPhase=None,
               gaTopic="None", gaQuestions=0, gaMinMinutes=0, gaMaxMinutes=0, setRMax=None, setE=None,
               mockQuestions=None, mockMarks=None, mockMinutes=None,
               workout=o['workout'], lifeCategory=o['lifeCategory'], lifeTask=o['lifeTask'],
               endOfDay="log topic status (green/yellow/red), three mistakes to reattempt and tomorrow's first task.")
    if t == 'LEARN':
        prev = lastLearn or r
        day.update(learnSubject=r['sj'], learnTopic=r['tp'], revisionSubject=prev['sj'], revisionTopic=prev['tp'],
                   setsText="P = 30 MCQs/numericals on today's topic (1 h, review every wrong answer); R = 10 questions on yesterday's topic (30 min).",
                   setP=30, setR=10)
        lastLearn = r
    elif t == 'REVISE':
        day.update(learnSubject=r['sj'], learnTopic=r['tp'] + ": notes, formulas and old wrong questions", revisionSubject=r['sj'], revisionTopic=r['tp'] + ": notes, formulas and old wrong questions",
                   setsText="R = 20 old wrong/weak questions on this subject (1 h 30 m revision); E = 40 timed MCQs/PYQs on the subject (1 h); then 30 min formula flashcards.",
                   setP=0, setR=20, setE=40)
    elif t == 'TEST':
        day.update(learnSubject="Mixed ECE", learnTopic=f"Weekly test {r['no']}: 40 timed questions and mistake review", revisionSubject="Mixed ECE", revisionTopic=f"Weekly test {r['no']} weak topics",
                   setsText="E = 40-question timed test of the week (1 h); review every mistake (1 h); R = 20 questions to redo weak topics (1 h).",
                   setP=0, setR=20, setE=40, weeklyReview=True,
                   weeklyReviewText="log the 40-question test score, accuracy, mistakes by reason (concept/formula/silly/guess) and the weakest topics to redo. If a day is missed, resume; do not double tomorrow's load.")
    else:
        mockDays.append(n)
        day.update(learnSubject="Mixed ECE", learnTopic=f"Full mock {r['no']}: 80 questions, 90 minutes", revisionSubject="Mixed ECE", revisionTopic=f"Mock {r['no']} five weakest concepts",
                   setsText="E = full 80-question, 80-mark, 90-minute mock with -0.33 negative marking (1 h 30 m); analyse each wrong or guessed question (1 h); relearn the 5 weakest concepts (30 min).",
                   setP=0, setR=5, fullMock=True, mockQuestions=80, mockMarks=80, mockMinutes=90, weeklyReview=(r['wd'] == 'Sun'),
                   weeklyReviewText="log the mock score, accuracy, unattempted easy questions and the five weakest concepts. Target 50+ early, 65+ by Mock 10, accuracy above 90%.",
                   mockPhase=f"Mock {r['no']}. Strict timing, no phone. Record score, accuracy, time left, attempted questions and top three recurring errors.")
    days.append(day)
json.dump(dict(source="VSSC TA ECE 150-Day Master Plan", start="2026-10-27", end="2027-03-25", mockDays=mockDays, days=days),
          open(OUT, 'w'), ensure_ascii=False, indent=1)
print(len(days), "days; mocks", mockDays)
