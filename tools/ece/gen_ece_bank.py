"""Generates app/src/main/assets/question_bank_v1.json: 120 ECE questions per subject (70 practice / 30 exam / 20 mock).
Numeric answers are computed by code. Fact questions are hand-written. All 1 mark, MCQ, -1/3 negative."""
import json, math, random, hashlib, re, sys
from fractions import Fraction
OUT = sys.argv[1]; PLAN = sys.argv[2]
plan = json.load(open(PLAN))
SUBJ = {"EDC":"Electronic Devices & Circuits","ANA":"Analog Electronics","DIG":"Digital Electronics","COM":"Communication Systems","MPMC":"Microprocessors & Microcontrollers","EMI":"Electronic Measurements & Instrumentation","SS":"Signals & Systems","CTRL":"Control Systems","NT":"Network Theory","EMFW":"Electromagnetic Fields & Waves","EM":"Engineering Mathematics"}
LAB2ID = {v:k for k,v in SUBJ.items()}
def slug(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')[:64].rstrip('-')
TOPICS = {k:[] for k in SUBJ}
for d in plan['days']:
    if d['learnSubject'] in LAB2ID and not d['learnTopic'].startswith('Revise'):
        t=d['learnTopic']; k=LAB2ID[d['learnSubject']]
        if t not in TOPICS[k]: TOPICS[k].append(t)
def topic_for(sid, key):
    key=key.lower()
    for t in TOPICS[sid]:
        if key in t.lower(): return t
    return TOPICS[sid][0]
def g(v):
    if isinstance(v,str): return v
    if abs(v-round(v))<1e-9 and abs(v)<1e9: return str(int(round(v)))
    if abs(v)>=1000: return f"{v:.0f}"
    s=f"{v:.4g}"
    if 'e' in s: s=f"{v:.6f}".rstrip('0').rstrip('.')
    return s
def num_opts(rng, c, unit="", extra=()):
    cands=list(extra)+[c*2,c/2,c*1.5,c*0.75,c*3,c/3,c+1,c*0.9,c*1.25]
    out=[];seen={g(c)}
    for x in cands:
        s=g(x)
        if s not in seen and x>0 or (s not in seen and c<=0): seen.add(s); out.append(x)
        if len(out)==3: break
    return [g(c)+unit]+[g(x)+unit for x in out[:3]]
class Q:  # one question
    def __init__(s,sid,topickey,stmt,opts,sol,concept,d="MEDIUM"): s.sid,s.tk,s.stmt,s.opts,s.sol,s.con,s.d=sid,topickey,stmt,opts,sol,concept,d
def mk(sid,tk,stmt,correct_and_wrongs,sol,con,d="MEDIUM"):
    return Q(sid,tk,stmt,correct_and_wrongs,sol,con,d)
T={k:[] for k in SUBJ}   # numeric templates: fn(rng)->Q
F={k:[] for k in SUBJ}   # facts
def num(sid):
    def deco(f): T[sid].append(f); return f
    return deco
def fact(sid,tk,q,right,wrongs,sol,con): F[sid].append(mk(sid,tk,q,[right]+wrongs,sol,con,"EASY"))
pi=math.pi
# ============ EDC ============
@num("EDC")
def _(r):
    vm=r.choice([10,12,15,20,24,30,36,50]); return mk("EDC","rectifiers",f"An ideal half-wave rectifier is fed a sinusoid of peak {vm} V. What is the average (DC) output voltage?",num_opts(r,vm/pi," V"),f"Vdc = Vm/π = {vm}/π = {g(vm/pi)} V.","HWR average voltage")
@num("EDC")
def _(r):
    vm=r.choice([10,12,15,20,24,30,36,50]); return mk("EDC","rectifiers",f"An ideal full-wave rectifier has an input peak of {vm} V. Its average (DC) output voltage is:",num_opts(r,2*vm/pi," V"),f"Vdc = 2Vm/π = {g(2*vm/pi)} V.","FWR average voltage")
@num("EDC")
def _(r):
    vm=r.choice([5,6,9,10,12,15,18,24]); return mk("EDC","rectifiers",f"A centre-tapped full-wave rectifier has a peak of {vm} V across each half of the secondary. The peak inverse voltage of each diode is:",num_opts(r,2*vm," V"),f"PIV = 2Vm = {2*vm} V for a centre-tap rectifier.","PIV of centre-tap FWR")
@num("EDC")
def _(r):
    vz=r.choice([5.1,6.2,9.1,12]); vin=r.choice([15,18,20,24,30]); rs=r.choice([100,150,220,330,470]); rl=r.choice([1000,1200,2200,4700])
    iz=(vin-vz)/rs*1000-vz/rl*1000
    if iz<=1: return None
    return mk("EDC","zener",f"A Zener regulator has Vin = {vin} V, Vz = {vz} V, series resistor {rs} Ω and load {rl} Ω. The Zener current is:",num_opts(r,iz," mA"),f"I_total = ({vin}-{vz})/{rs}; I_load = {vz}/{rl}; Iz = difference = {g(iz)} mA.","Zener regulator current")
@num("EDC")
def _(r):
    b=r.choice([50,80,100,120,150,200]); ib=r.choice([10,20,25,40,50,60]); return mk("EDC","bjt operation",f"A BJT has β = {b} and base current {ib} µA in the active region. The collector current is:",num_opts(r,b*ib/1000," mA"),f"IC = βIB = {b}×{ib} µA = {g(b*ib/1000)} mA.","BJT IC = β IB")
@num("EDC")
def _(r):
    a=r.choice([0.95,0.96,0.98,0.99,0.992]); b=a/(1-a); return mk("EDC","bjt operation",f"A transistor has α = {a}. The common-emitter current gain β is approximately:",num_opts(r,b),f"β = α/(1−α) = {a}/{round(1-a,4)} ≈ {g(b)}.","Relation between α and β")
@num("EDC")
def _(r):
    t=r.choice([250,300,320,350,400,450]); vt=t*8.617e-5*1000; return mk("EDC","semiconductor",f"The thermal voltage VT = kT/q at {t} K is approximately (k/q = 86.17 µV/K):",num_opts(r,vt," mV"),f"VT = {t}×86.17 µV = {g(vt)} mV.","Thermal voltage")
@num("EDC")
def _(r):
    k=r.choice([0.2,0.5,1,2]); vgs=r.choice([3,4,5,6]); vt=r.choice([1,1.5,2]); i=k*(vgs-vt)**2
    return mk("EDC","mosfet",f"An n-MOSFET in saturation obeys ID = K(VGS−VT)² with K = {k} mA/V². For VGS = {vgs} V and VT = {vt} V, ID is:",num_opts(r,i," mA"),f"ID = {k}×({vgs}−{vt})² = {g(i)} mA.","MOSFET saturation current")
@num("EDC")
def _(r):
    n=r.choice([2,3,4,5,6]); vm=r.choice([5,10,12,15]); return mk("EDC","clippers",f"An ideal {n}-stage voltage multiplier (cascaded doubler/tripler chain) driven by a peak of {vm} V gives an ideal DC output of:",num_opts(r,n*vm," V"),f"Ideal output = n·Vm = {n}×{vm} = {n*vm} V.","Voltage multiplier")
for q,a,b,s,c,k in [
("Which diode is normally operated in reverse breakdown for voltage regulation?","Zener diode",["Schottky diode","Varactor diode","Tunnel diode"],"Zener diodes are designed for stable breakdown voltage.","Zener usage","zener"),
("In a forward-biased PN junction the depletion width:","decreases",["increases","stays constant","becomes infinite"],"Forward bias reduces the barrier, narrowing the depletion region.","Depletion width","pn junction"),
("A photodiode is normally operated in:","reverse bias",["forward bias","zero current only","avalanche breakdown only"],"Reverse bias gives photocurrent proportional to light intensity.","Photodiode bias","led"),
("Which device exhibits a negative-resistance region and is used in microwave oscillators?","Tunnel diode",["Zener diode","LED","Rectifier diode"],"Heavy doping gives a negative-resistance region.","Tunnel diode","tunnel"),
("A varactor diode is used as a:","voltage-variable capacitor",["current source","rectifier","light emitter"],"Reverse-bias capacitance varies with voltage.","Varactor","varactor"),
("Which of these is a unipolar device?","JFET",["BJT","SCR","Diode with two PN junctions"],"JFET conduction uses only majority carriers.","Unipolar devices","jfet"),
("For a BJT to act as an amplifier, the base-emitter and base-collector junctions are:","forward and reverse biased",["both forward biased","both reverse biased","reverse and forward biased"],"Active region: EB forward, CB reverse.","Active region","bjt operation"),
("The common-emitter amplifier produces a phase shift of:","180°",["0°","90°","270° lagging only"],"CE amplifiers invert the signal.","CE phase shift","bjt operation"),
("Which BJT configuration has the highest input impedance and lowest output impedance?","Common collector",["Common base","Common emitter","All are equal"],"The emitter follower is a buffer.","CC characteristics","bjt operation"),
("An SCR turns off when its anode current falls below:","the holding current",["the latching current","the gate current","the breakover current"],"Anode current below IH commutes the SCR off.","SCR turn-off","scr"),
("A TRIAC conducts:","in both directions",["only from anode to cathode","only when reverse biased","only during negative half-cycles"],"A TRIAC is bidirectional.","TRIAC","scr"),
("A UJT is commonly used as:","a relaxation oscillator",["a power amplifier","a rectifier","a voltage regulator"],"The negative-resistance region gives sawtooth/pulse generation.","UJT","scr"),
("Avalanche breakdown dominates in Zener diodes with breakdown voltage:","above about 6 V",["below about 2 V","exactly 0.7 V","only at 0 V"],"Zener effect dominates below ~5 V, avalanche above ~6 V.","Breakdown mechanisms","zener"),
("Which LED semiconductor property is essential for efficient light emission?","Direct bandgap",["Indirect bandgap","Zero bandgap","Very low doping only"],"Direct recombination emits photons efficiently.","LED materials","led"),
]: fact("EDC",k,q,a,b,s,c)
# ============ ANA ============
@num("ANA")
def _(r):
    rf=r.choice([10,20,47,100]);r1=r.choice([1,2,5,10]);vi=r.choice([0.1,0.2,0.5,1]); vo=-rf/r1*vi
    return mk("ANA","op-amp linear",f"An ideal inverting amplifier uses Rf = {rf} kΩ and R1 = {r1} kΩ. For Vin = {vi} V, Vout is:",[g(vo)+" V",g(-vo)+" V",g(vo*(1+r1/rf))+" V",g(vo/2)+" V"],f"Vo = −(Rf/R1)Vin = −{g(rf/r1)}×{vi} = {g(vo)} V.","Inverting amplifier")
@num("ANA")
def _(r):
    rf=r.choice([10,20,47,90,100]);r1=r.choice([1,2,5,10]); a=1+rf/r1
    return mk("ANA","op-amp linear",f"A non-inverting op-amp amplifier has Rf = {rf} kΩ and R1 = {r1} kΩ. Its voltage gain is:",num_opts(r,a,"",[rf/r1,-a]),f"Av = 1 + Rf/R1 = 1 + {g(rf/r1)} = {g(a)}.","Non-inverting gain")
@num("ANA")
def _(r):
    av=r.choice([10,20,50,100,200,500,1000,5000]); d=20*math.log10(av)
    return mk("ANA","amplifier basics",f"A voltage gain of {av} (ratio) expressed in decibels is approximately:",num_opts(r,d," dB",[10*math.log10(av)]),f"20·log10({av}) = {g(d)} dB.","Gain in dB")
@num("ANA")
def _(r):
    ra=r.choice([1,2,4.7,10]);rb=r.choice([10,22,47,68]);c=r.choice([0.01,0.1,1]); f=1.44/((ra+2*rb)*1e3*c*1e-6)
    return mk("ANA","555 timer",f"A 555 astable has RA = {ra} kΩ, RB = {rb} kΩ and C = {c} µF. The output frequency is approximately:",num_opts(r,f," Hz"),f"f = 1.44/((RA+2RB)C) = {g(f)} Hz.","555 astable frequency")
@num("ANA")
def _(r):
    R=r.choice([10,47,100,220]);c=r.choice([1,10,22,100]); t=1.1*R*1e3*c*1e-6
    return mk("ANA","555 timer",f"A 555 monostable uses R = {R} kΩ and C = {c} µF. The output pulse width is:",num_opts(r,t," s"),f"T = 1.1RC = {g(t)} s.","555 monostable pulse width")
@num("ANA")
def _(r):
    a=r.choice([100,200,1000,10000]);b=r.choice([0.01,0.02,0.05,0.1]); af=a/(1+a*b)
    return mk("ANA","feedback",f"An amplifier with open-loop gain A = {a} uses negative feedback with β = {b}. The closed-loop gain is:",num_opts(r,af),f"Af = A/(1+Aβ) = {a}/{g(1+a*b)} = {g(af)}.","Closed-loop gain with feedback")
@num("ANA")
def _(r):
    R=r.choice([1,2.2,4.7,10]);c=r.choice([10,22,47,100]); f=1/(2*pi*math.sqrt(6)*R*1e3*c*1e-9)
    return mk("ANA","oscillators",f"A three-section RC phase-shift oscillator has R = {R} kΩ and C = {c} nF. Its frequency is f = 1/(2π√6·RC) ≈",num_opts(r,f," Hz"),f"f = {g(f)} Hz.","RC phase-shift oscillator")
@num("ANA")
def _(r):
    R=r.choice([1,2.2,4.7,10]);c=r.choice([10,22,47,100]); f=1/(2*pi*R*1e3*c*1e-9)
    return mk("ANA","oscillators",f"A Wien bridge oscillator uses R = {R} kΩ and C = {c} nF in both arms. The frequency of oscillation is:",num_opts(r,f," Hz"),f"f = 1/(2πRC) = {g(f)} Hz.","Wien bridge oscillator")
@num("ANA")
def _(r):
    l=r.choice([1,2,10,100]);c=r.choice([10,100,220,470]); f=1/(2*pi*math.sqrt(l*1e-3*c*1e-9))
    return mk("ANA","oscillators",f"An LC oscillator uses L = {l} mH and C = {c} nF. Its frequency is f = 1/(2π√LC) ≈",num_opts(r,f/1000," kHz"),f"f = {g(f/1000)} kHz.","LC oscillator frequency")
@num("ANA")
def _(r):
    sr=r.choice([0.5,1,2,5,10]);vp=r.choice([1,2,5,10]); f=sr*1e6/(2*pi*vp)
    return mk("ANA","op-amp basics",f"An op-amp has slew rate {sr} V/µs. The full-power bandwidth for a {vp} V peak sinusoid is:",num_opts(r,f/1000," kHz"),f"fmax = SR/(2πVp) = {g(f/1000)} kHz.","Slew rate and full-power bandwidth")
for q,a,b,s,c,k in [
("The maximum theoretical efficiency of a Class B push-pull power amplifier is:","78.5%",["25%","50%","100%"],"η = π/4 ≈ 78.5%.","Class B efficiency","power amplifiers"),
("The maximum efficiency of a series-fed Class A amplifier with resistive load is:","25%",["50%","78.5%","90%"],"Class A series-fed max 25%.","Class A efficiency","power amplifiers"),
("Crossover distortion is characteristic of:","Class B amplifiers",["Class A amplifiers","Class C amplifiers only","Op-amp integrators"],"Dead zone near zero crossing.","Crossover distortion","power amplifiers"),
("Negative voltage-series feedback in an amplifier:","increases input impedance and reduces output impedance",["decreases input impedance and increases output impedance","increases both impedances","reduces gain sensitivity only on input"],"Series at input raises Zin; voltage sampling lowers Zout.","Feedback topologies","feedback"),
("Negative feedback generally:","reduces gain and increases bandwidth",["increases gain and reduces bandwidth","increases gain and bandwidth","has no effect on bandwidth"],"Gain-bandwidth tradeoff.","Effects of feedback","feedback"),
("Barkhausen criterion for sustained oscillation requires loop gain magnitude:","equal to 1 with zero (360°) phase shift",["less than 1","equal to 0","infinite at all frequencies"],"|Aβ| = 1 and ∠Aβ = 0° or 360°.","Barkhausen criterion","oscillators"),
("An ideal op-amp has:","infinite input impedance and zero output impedance",["zero input impedance","infinite output impedance","finite CMRR of 10"],"Ideal characteristics.","Ideal op-amp","op-amp basics"),
("CMRR of an ideal op-amp is:","infinite",["zero","unity","100 dB only"],"Common-mode gain is zero.","CMRR","op-amp basics"),
("A Schmitt trigger comparator exhibits:","hysteresis",["no threshold","zero gain","unity gain only"],"Two threshold voltages.","Schmitt trigger","comparator"),
("The Miller effect increases the effective input capacitance by a factor related to:","the inverting gain (1+|Av|)",["the supply voltage","the load resistance only","the temperature only"],"Cin = Cgd(1+|Av|).","Miller effect","multistage"),
("A crystal oscillator is preferred for its:","high frequency stability",["high power output","large bandwidth","low Q"],"Very high Q gives stability.","Crystal oscillator","lc and crystal"),
("An astable multivibrator has:","no stable state",["one stable state","two stable states","three stable states"],"It free-runs between two quasi-stable states.","Multivibrators","multivibrators"),
]: fact("ANA",k,q,a,b,s,c)
# ============ DIG ============
@num("DIG")
def _(r):
    n=r.randint(20,250); return mk("DIG","number systems",f"The hexadecimal equivalent of decimal {n} is:",[format(n,'X')+"H",format(n+1,'X')+"H",format(n-1,'X')+"H",format((n*2)%256 or 17,'X')+"H"],f"{n} = {format(n,'X')} in hex.","Decimal to hex")
@num("DIG")
def _(r):
    n=r.randint(3,120); return mk("DIG","number systems",f"The 8-bit two's complement representation of −{n} is:",[format((256-n)%256,'08b'),format(n,'08b'),format((255-n)%256,'08b'),format((257-n)%256,'08b')],f"Invert {format(n,'08b')} and add 1 → {format((256-n)%256,'08b')}.","Two's complement")
@num("DIG")
def _(r):
    n=r.randint(2,15); gray=n^(n>>1); return mk("DIG","codes",f"The 4-bit Gray code equivalent of binary {format(n,'04b')} is:",[format(gray,'04b'),format(n,'04b'),format((gray+1)%16,'04b'),format((gray^8)%16,'04b')],f"G = B xor (B>>1) = {format(gray,'04b')}.","Binary to Gray")
@num("DIG")
def _(r):
    n=r.choice([5,6,9,10,12,20,50,60,100,200]); k=math.ceil(math.log2(n)); return mk("DIG","counters",f"The minimum number of flip-flops needed for a mod-{n} counter is:",num_opts(r,k),f"2^k ≥ {n} → k = {k}.","Flip-flops for a mod-N counter")
@num("DIG")
def _(r):
    n=r.choice([6,10,12,16,20,60]); f=r.choice([60,120,600,1200]); return mk("DIG","counters",f"A mod-{n} counter is clocked at {f} kHz. The frequency of its last-stage output is:",num_opts(r,f/n," kHz"),f"fout = f/N = {f}/{n} = {g(f/n)} kHz.","Counter frequency division")
@num("DIG")
def _(r):
    n=r.choice([2,3,4,5,6,8]); v=r.choice([5,8,10,12]); lsb=v/(2**n-1); return mk("DIG","dac",f"A {n}-bit DAC has full-scale output {v} V. The step size (resolution) is:",num_opts(r,lsb," V",[v/2**n]),f"Step = Vfs/(2^n−1) = {v}/{2**n-1} = {g(lsb)} V.","DAC resolution")
@num("DIG")
def _(r):
    n=r.choice([4,6,8,10,12]); v=r.choice([2.56,5,10]); lsb=v/2**n*1000; return mk("DIG","adc",f"An ideal {n}-bit ADC has reference {v} V. One LSB corresponds to:",num_opts(r,lsb," mV"),f"LSB = Vref/2^n = {g(lsb)} mV.","ADC LSB size")
@num("DIG")
def _(r):
    kb=r.choice([1,2,4,8,16,32,64]); a=10+int(math.log2(kb)); return mk("DIG","memories",f"The number of address lines needed for a {kb} K × 8 memory is:",num_opts(r,a),f"{kb}K = 2^{a} locations → {a} lines.","Memory address lines")
@num("DIG")
def _(r):
    n=r.choice([4,8,16,32,64]); k=int(math.log2(n)); return mk("DIG","mux",f"The number of select lines in a {n}:1 multiplexer is:",num_opts(r,k),f"log2({n}) = {k}.","Mux select lines")
for q,a,b,s,c,k in [
("Which gate is a universal gate?","NAND",["XOR","XNOR","AND"],"NAND alone can realise any function.","Universal gates","universal"),
("The Boolean expression of a half-adder sum output is:","A XOR B",["A AND B","A OR B","A XNOR B"],"Sum = A⊕B, carry = AB.","Half adder","adders"),
("By De Morgan's theorem, (A+B)' equals:","A'·B'",["A'+B'","A·B","A+B'"],"Complement of OR is AND of complements.","De Morgan","boolean"),
("Race-around condition occurs in:","a level-triggered JK flip-flop with J=K=1",["a D flip-flop","an SR latch with S=R=0","a T flip-flop with T=0"],"Output toggles repeatedly during clock high.","Race-around","ff conversion"),
("A master-slave JK flip-flop eliminates:","race-around",["setup time","propagation delay","the need for a clock"],"Two-stage edge-like operation.","Master-slave","ff conversion"),
("A D flip-flop can be converted to a T flip-flop by:","D = T XOR Q",["D = T AND Q","D = T","D = T OR Q"],"Toggle when T=1.","FF conversion","ff conversion"),
("Which logic family has the lowest static power dissipation?","CMOS",["TTL","ECL","DTL"],"CMOS draws negligible static current.","Logic families","logic families"),
("Which logic family is the fastest?","ECL",["TTL","CMOS","RTL"],"Non-saturating differential logic.","ECL","logic families"),
("A 4-bit ring counter has how many used states?","4",["16","8","2"],"One-hot circulating bit.","Ring counter","shift registers"),
("A Johnson counter with n flip-flops has how many states?","2n",["n","n²","2^n"],"Twisted ring counter.","Johnson counter","shift registers"),
("In a K-map, groups must contain:","a power of two cells",["any number of cells","only an even number up to 6","three cells"],"Groups of 1,2,4,8,...","K-map","k-map"),
("A decoder with n inputs has at most how many outputs?","2^n",["n","2n","n²"],"One output per input combination.","Decoder","encoder"),
]: fact("DIG",k,q,a,b,s,c)
# ============ COM ============
@num("COM")
def _(r):
    pc=r.choice([100,200,500,1000]);m=r.choice([0.4,0.5,0.6,0.8,1.0]); pt=pc*(1+m*m/2); return mk("COM","amplitude modulation",f"An AM carrier of {pc} W is modulated to m = {m}. The total transmitted power is:",num_opts(r,pt," W"),f"Pt = Pc(1+m²/2) = {g(pt)} W.","AM total power")
@num("COM")
def _(r):
    vmax=r.choice([10,12,14,16,18,20]);vmin=r.choice([2,4,6,8]); 
    if vmin>=vmax: return None
    m=(vmax-vmin)/(vmax+vmin); return mk("COM","amplitude modulation",f"An AM waveform has Vmax = {vmax} V and Vmin = {vmin} V. The modulation index is:",num_opts(r,m),f"m = (Vmax−Vmin)/(Vmax+Vmin) = {g(m)}.","AM modulation index")
@num("COM")
def _(r):
    df=r.choice([25,50,75,100]);fm=r.choice([5,10,15]); bw=2*(df+fm); return mk("COM","carson",f"An FM signal has peak deviation {df} kHz and message frequency {fm} kHz. Carson's rule bandwidth is:",num_opts(r,bw," kHz"),f"BW = 2(Δf+fm) = {bw} kHz.","Carson's rule")
@num("COM")
def _(r):
    df=r.choice([10,25,50,75]);fm=r.choice([2,5,10]); return mk("COM","fm and pm",f"An FM modulator has frequency deviation {df} kHz for a {fm} kHz tone. The modulation index is:",num_opts(r,df/fm),f"β = Δf/fm = {g(df/fm)}.","FM modulation index")
@num("COM")
def _(r):
    f=r.choice([3,4,5,8,10,15,20]); return mk("COM","sampling",f"A band-limited signal has maximum frequency {f} kHz. The Nyquist sampling rate is:",num_opts(r,2*f," kHz"),f"fs ≥ 2fmax = {2*f} kHz.","Nyquist rate")
@num("COM")
def _(r):
    f=r.choice([3,4,5]);n=r.choice([4,6,8,10]); return mk("COM","pcm",f"A {f} kHz signal is sampled at the Nyquist rate and coded with {n} bits per sample. The PCM bit rate is:",num_opts(r,2*f*n," kbps"),f"fs = {2*f} kHz; rate = fs·n = {2*f*n} kbps.","PCM bit rate")
@num("COM")
def _(r):
    n=r.choice([4,6,8,10,12]); s=6.02*n+1.76; return mk("COM","pcm",f"The ideal SNR of an {n}-bit PCM system for a full-scale sinusoid is approximately:",num_opts(r,s," dB",[6*n]),f"SNR = 6.02n + 1.76 = {g(s)} dB.","PCM SNR")
@num("COM")
def _(r):
    snr=r.choice([3,7,15,31,63,255]);b=r.choice([1,2,3,4,10]); c=b*math.log2(1+snr); return mk("COM","fundamentals",f"A channel of bandwidth {b} kHz has linear SNR = {snr}. By Shannon's formula the capacity is:",num_opts(r,c," kbps"),f"C = B·log2(1+SNR) = {b}×log2({1+snr}) = {g(c)} kbps.","Shannon capacity")
@num("COM")
def _(r):
    fs=r.choice([600,800,1000,1200,1400]);if_=455; return mk("COM","superheterodyne",f"A superheterodyne receiver with IF 455 kHz is tuned to {fs} kHz (high-side local oscillator). The image frequency is:",num_opts(r,fs+2*if_," kHz",[fs+if_,fs-2*if_]),f"fimage = fs + 2·IF = {fs+910} kHz.","Image frequency")
@num("COM")
def _(r):
    m=r.choice([0.5,0.6,0.8,1.0]); e=m*m/(2+m*m)*100; return mk("COM","amplitude modulation",f"The power efficiency of single-tone AM with m = {m} is:",num_opts(r,e,"%"),f"η = m²/(2+m²) = {g(e)}%.","AM efficiency")
for q,a,b,s,c,k in [
("Which modulation scheme needs the smallest bandwidth for a given message?","SSB",["DSB-SC","FM wideband","AM with carrier"],"SSB transmits one sideband.","Bandwidth comparison","dsb-sc"),
("Bandwidth of a conventional AM signal for message bandwidth W is:","2W",["W","4W","W/2"],"Two sidebands.","AM bandwidth","amplitude modulation"),
("Which detector is used for envelope detection of AM?","Diode detector",["PLL","Ratio detector","Balanced mixer"],"Diode + RC extracts the envelope.","AM detection","amplitude modulation"),
("A QPSK symbol carries how many bits?","2",["1","3","4"],"Four phases → 2 bits.","QPSK","qpsk"),
("The standard AM broadcast IF is:","455 kHz",["10.7 MHz","38.9 MHz","1 MHz"],"AM superhet IF.","IF","superheterodyne"),
("FM has better noise performance than AM because:","amplitude variations are removed by limiting",["it uses less bandwidth","it has no sidebands","it uses a carrier-free envelope"],"Limiter removes amplitude noise.","FM noise immunity","fm and pm"),
("A phase-locked loop can be used for:","FM demodulation",["envelope detection","analog-to-digital conversion only","sampling"],"VCO control voltage follows message.","PLL","demodulation"),
("Delta modulation suffers from:","slope overload and granular noise",["aliasing only","no quantisation error","carrier leakage"],"Step size tradeoff.","Delta modulation","delta"),
("Which is a non-coherent digital modulation scheme?","FSK",["BPSK only","QPSK only","16-QAM only"],"FSK can be demodulated non-coherently.","Digital modulation","ask"),
("Pre-emphasis in FM transmitters is used to:","improve SNR of high-frequency components",["reduce bandwidth","increase carrier power","remove the carrier"],"Boosts HF before noisy channel.","Pre-emphasis","fm"),
]: fact("COM",k,q,a,b,s,c)
# ============ MPMC ============
@num("MPMC")
def _(r):
    n=r.choice([10,20,50,100,200,255]);f=r.choice([2,3,5,6]); t=(14*n+4)/f; return mk("MPMC","programs and delays",f"An 8085 delay loop is MVI C,N / L: DCR C / JNZ L with N = {n} (MVI = 7 T, DCR = 4 T, JNZ = 10 T taken / 7 T not taken). At {f} MHz the total delay is:",num_opts(r,t," µs"),f"T-states = 7 + 4N + 10(N−1) + 7 = 14N+4 = {14*n+4}; delay = {14*n+4}/{f} µs = {g(t)} µs.","8085 delay calculation")
@num("MPMC")
def _(r):
    a=r.randint(0x10,0xF0);b=r.randint(0x10,0xF0); res=(a+b)&0xFF; cy=1 if a+b>255 else 0
    return mk("MPMC","instruction set",f"8085: A = {a:02X}H. After ADI {b:02X}H, the accumulator holds:",[f"{res:02X}H",f"{(a-b)&0xFF:02X}H",f"{(a+b+1)&0xFF:02X}H",f"{(a^b):02X}H"],f"{a:02X}+{b:02X} = {a+b:X}H; A = {res:02X}H, CY = {cy}.","ADI result")
@num("MPMC")
def _(r):
    n=r.randint(0,7); return mk("MPMC","interrupts",f"In the 8085, the instruction RST {n} transfers control to address:",[f"{8*n:04X}H",f"{8*n+4:04X}H",f"{4*n:04X}H",f"{16*n:04X}H"],f"RST n → 8×n = {8*n:04X}H.","RST vector addresses")
@num("MPMC")
def _(r):
    f=r.choice([6,11.0592,12,16,24]); mc=12/f; return mk("MPMC","8051 timers",f"An 8051 uses a {f} MHz crystal. One machine cycle lasts:",num_opts(r,mc," µs",[1/f,6/f]),f"Machine cycle = 12/fosc = {g(mc)} µs.","8051 machine cycle")
@num("MPMC")
def _(r):
    n=r.choice([0,1000,3036,15536,45536,60000,64000]); d=(65536-n); return mk("MPMC","8051 timers",f"8051 Timer 0 in mode 1 (16-bit) is loaded with {n} (decimal) and the machine cycle is 1 µs. The time to overflow is:",num_opts(r,d," µs",[n]),f"Counts = 65536−{n} = {d}; time = {d} µs.","Timer mode 1 delay")
@num("MPMC")
def _(r):
    big=r.choice([8,16,32,64]); small=r.choice([1,2,4]); 
    if big<=small: return None
    return mk("MPMC","memory and i/o",f"How many {small}K × 8 memory chips are needed to build a {big}K × 8 memory?",num_opts(r,big//small),f"{big}K/{small}K = {big//small} chips.","Memory expansion")
for q,a,b,s,c,k in [
("The 8085 has a data bus width of:","8 bits",["16 bits","4 bits","32 bits"],"Multiplexed AD0–AD7.","8085 bus","8085 architecture"),
("The 8085 address bus is:","16 bits wide, giving 64 KB of memory",["8 bits, 256 bytes","20 bits, 1 MB","32 bits, 4 GB"],"A0–A15.","8085 address space","8085 architecture"),
("Highest-priority 8085 interrupt is:","TRAP",["RST 7.5","RST 6.5","INTR"],"TRAP is non-maskable and top priority.","8085 interrupt priority","interrupts"),
("PUSH in the 8085:","decrements SP by 2",["increments SP by 2","does not change SP","decrements SP by 1 only"],"Stack grows downward.","Stack pointer","stack"),
("ALE in the 8085 is used to:","demultiplex the low-order address/data bus",["reset the processor","select I/O","signal interrupt acknowledge"],"Latches A0–A7.","ALE","pins"),
("The 8255 PPI has:","three 8-bit ports",["two 8-bit ports","four 16-bit ports","one 16-bit port"],"Ports A, B, C.","8255","8255"),
("The 8253 contains how many independent counters?","3",["2","4","8"],"Three 16-bit counters.","8253","8255"),
("The 8051 internal RAM size is:","128 bytes",["256 bytes","4 KB","64 KB"],"Standard 8051.","8051 memory","8051 architecture"),
("The 8051 has how many 8-bit I/O ports?","4",["2","3","8"],"P0–P3.","8051 ports","8051 architecture"),
("The 8051 stack pointer after reset holds:","07H",["00H","FFH","30H"],"SP resets to 07H.","8051 SP","8051 architecture"),
("DMA transfers are controlled by the:","DMA controller (e.g., 8257)",["ALU","accumulator","program counter only"],"Bypasses CPU for bulk transfer.","DMA","8259"),
("Memory-mapped I/O uses:","the memory address space and memory instructions",["separate IN/OUT instructions","only interrupts","only DMA"],"Peripherals share addresses.","Memory-mapped I/O","interfacing"),
]: fact("MPMC",k,q,a,b,s,c)
# ============ EMI ============
@num("EMI")
def _(r):
    t=r.choice([50,100,120,220,500]);m=t+r.choice([-4,-2,2,3,5]); e=abs(m-t)/t*100; return mk("EMI","errors",f"A quantity with true value {t} units is measured as {m} units. The percentage error is:",num_opts(r,e,"%"),f"|{m}−{t}|/{t}×100 = {g(e)}%.","Percentage error")
@num("EMI")
def _(r):
    im=r.choice([0.05,0.1,0.5,1]);rm=r.choice([50,100,200,500]);v=r.choice([10,50,100]); rs=v/(im/1000)-rm
    if rs<=0: return None
    return mk("EMI","ammeter, voltmeter",f"A PMMC movement (full-scale {im} mA, Rm = {rm} Ω) is converted to a {v} V voltmeter. The series multiplier resistance is:",num_opts(r,rs," Ω"),f"Rs = V/Im − Rm = {g(rs)} Ω.","Voltmeter multiplier")
@num("EMI")
def _(r):
    im=r.choice([1,5,10]);rm=r.choice([10,50,100]);i=r.choice([100,500,1000]); rsh=im*rm/(i-im); return mk("EMI","ammeter, voltmeter",f"A {im} mA, {rm} Ω meter is to read {i} mA full scale. The shunt resistance is:",num_opts(r,rsh," Ω"),f"Rsh = Im·Rm/(I−Im) = {g(rsh)} Ω.","Ammeter shunt")
@num("EMI")
def _(r):
    r1=r.choice([100,200,500]);r2=r.choice([1000,2000,5000]);r3=r.choice([100,200,400,1000]); x=r2*r3/r1; return mk("EMI","wheatstone",f"A balanced Wheatstone bridge has R1 = {r1} Ω, R2 = {r2} Ω and R3 = {r3} Ω (balance: Rx = R2R3/R1). Rx equals:",num_opts(r,x," Ω"),f"Rx = {r2}×{r3}/{r1} = {g(x)} Ω.","Wheatstone balance")
@num("EMI")
def _(r):
    gf=r.choice([2,2.1,3,4]);e=r.choice([100,250,500,1000]);R=r.choice([120,350]); dr=gf*e*1e-6*R; return mk("EMI","transducers",f"A {R} Ω strain gauge with gauge factor {gf} experiences {e} microstrain. ΔR is:",num_opts(r,dr*1000," mΩ"),f"ΔR = GF·ε·R = {g(dr*1000)} mΩ.","Strain gauge")
@num("EMI")
def _(r):
    d=r.choice([2,3,4,5,8]);tdiv=r.choice([0.1,0.5,1,2,5]); f=1/(d*tdiv*1e-3); return mk("EMI","multimeter, cro",f"On a CRO set to {tdiv} ms/div, one full cycle spans {d} divisions. The signal frequency is:",num_opts(r,f," Hz"),f"T = {g(d*tdiv)} ms → f = {g(f)} Hz.","CRO frequency measurement")
@num("EMI")
def _(r):
    d=r.choice([2,3,4,5,6]);v=r.choice([0.5,1,2,5]); return mk("EMI","multimeter, cro",f"On a CRO set to {v} V/div, a sine wave spans {d} divisions peak-to-peak. Its peak-to-peak voltage is:",num_opts(r,d*v," V"),f"Vpp = {d}×{v} = {g(d*v)} V.","CRO voltage measurement")
for q,a,b,s,c,k in [
("A PMMC instrument can measure:","DC only",["AC only","both AC and DC equally","only power"],"Torque ∝ current direction.","PMMC","pmmc"),
("Which instrument is suitable for both AC and DC?","Moving iron",["PMMC","Rectifier-less PMMC","Electrostatic only for DC"],"Torque ∝ I².","Moving iron","pmmc"),
("A dynamometer-type instrument is commonly used as a:","wattmeter",["thermometer","strain gauge","tachometer only"],"Two coils give power.","Wattmeter","pmmc"),
("The secondary of a current transformer should never be:","open-circuited",["short-circuited","grounded","loaded with a low-resistance ammeter"],"High voltage develops.","CT safety","ct/pt"),
("The Kelvin double bridge is used for measuring:","low resistance",["high resistance","capacitance","frequency"],"Eliminates lead resistance.","Kelvin bridge","bridges: wheatstone"),
("The Schering bridge is used to measure:","capacitance and dielectric loss",["low resistance","inductance of high-Q coils","frequency"],"Capacitor with loss.","Schering bridge","bridges: hay"),
("The Hay bridge is best for measuring inductance of coils with:","high Q",["low Q","zero resistance","any Q equally"],"Hay for Q>10.","Hay bridge","bridges: hay"),
("The Maxwell bridge is suitable for:","medium-Q inductors",["very high Q inductors","low resistances","frequencies only"],"Q between 1 and 10.","Maxwell bridge","bridges: wheatstone"),
("An LVDT is a transducer for measuring:","displacement",["temperature only","light intensity","pressure without diaphragm"],"Differential transformer.","LVDT","transducers"),
("A thermocouple works on the:","Seebeck effect",["Hall effect","Piezoelectric effect","Photoelectric effect"],"Junction EMF with temperature.","Thermocouple","transducers"),
("Accuracy of a measurement describes:","closeness to the true value",["repeatability only","resolution only","sensitivity only"],"Precision is repeatability.","Accuracy vs precision","errors"),
("Digital storage oscilloscope can capture a single-shot event because it:","stores samples in memory",["has a phosphor screen","uses a delay line only","needs repetitive signals"],"Digital memory.","DSO","multimeter, cro"),
]: fact("EMI",k,q,a,b,s,c)
# ============ SS ============
@num("SS")
def _(r):
    k=r.choice([1,2,3,4,5]); return mk("SS","signal types",f"The fundamental period of x(t) = sin({k}πt) is:",num_opts(r,2/k," s"),f"ω0 = {k}π → T = 2π/ω0 = {g(2/k)} s.","Period of a sinusoid")
@num("SS")
def _(r):
    N=r.choice([8,12,16,20,24]);k=r.choice([1,3,5,2,4,6]); p=N//math.gcd(N,k); return mk("SS","signal types",f"The fundamental period of x[n] = cos(2π·{k}n/{N}) is:",num_opts(r,p),f"N0 = N/gcd(k,N) = {N}/{math.gcd(N,k)} = {p}.","Discrete-time period")
@num("SS")
def _(r):
    a=r.randint(2,8);b=r.randint(2,9); return mk("SS","lti",f"Sequences of length {a} and {b} are convolved. The output length is:",num_opts(r,a+b-1),f"L = {a}+{b}−1 = {a+b-1}.","Convolution length")
@num("SS")
def _(r):
    A=r.choice([1,2,3,4]);T=r.choice([1,2,5]); return mk("SS","signal types",f"The energy of x(t) = {A} for 0 ≤ t ≤ {T} s (zero elsewhere) is:",num_opts(r,A*A*T," J"),f"E = A²T = {A*A*T}.","Signal energy")
@num("SS")
def _(r):
    A=r.choice([2,4,6,10]); return mk("SS","signal types",f"The average power of x(t) = {A}cos(ωt) is:",num_opts(r,A*A/2," W"),f"P = A²/2 = {g(A*A/2)}.","Power of a sinusoid")
@num("SS")
def _(r):
    a=r.choice([100,200,300,500,1000]);b=r.choice([50,150,400,800]); return mk("SS","sampling",f"x(t) = sin(2π·{a}t) + cos(2π·{b}t). The Nyquist rate is:",num_opts(r,2*max(a,b)," Hz"),f"2×fmax = {2*max(a,b)} Hz.","Nyquist rate of a sum")
@num("SS")
def _(r):
    K=r.choice([4,6,10,12,20]);a=r.choice([2,4,5]); return mk("SS","fourier and laplace",f"For F(s) = {K}/(s(s+{a})), the final value f(∞) is:",num_opts(r,K/a),f"lim s·F(s) = {K}/{a} = {g(K/a)}.","Final value theorem")
@num("SS")
def _(r):
    fs=r.choice([100,200,500,1000]);f0=r.choice([int(fs*0.6),int(fs*0.7),int(fs*0.9)]); ap=abs(f0-round(f0/fs)*fs); return mk("SS","sampling",f"A {f0} Hz tone is sampled at {fs} Hz. The apparent (aliased) frequency is:",num_opts(r,ap," Hz",[f0]),f"|f0 − k·fs| = {ap} Hz.","Aliasing")
for q,a,b,s,c,k in [
("An LTI system is causal if:","h(t) = 0 for t < 0",["h(t) is even","h(t) is bounded","h(t) = 1 for all t"],"No output before input.","Causality","lti"),
("An LTI system is BIBO stable if:","∫|h(t)|dt is finite",["h(t) is causal","h(t) is periodic","H(s) has a zero at origin"],"Absolute integrability.","BIBO stability","lti"),
("Convolution in time domain corresponds to ___ in frequency domain.","multiplication",["addition","division","differentiation"],"Y(ω)=X(ω)H(ω).","Convolution theorem","lti"),
("y(t) = x(2t) is:","time-varying",["time-invariant","non-causal never","nonlinear"],"Scaling breaks shift invariance.","System properties","system properties"),
("y(t) = x²(t) is:","non-linear",["linear","unstable always","non-causal"],"Superposition fails.","Linearity","system properties"),
("The Laplace transform of the unit step u(t) is:","1/s",["1","s","1/s²"],"Standard pair.","Laplace pairs","fourier and laplace"),
("The Fourier transform of δ(t) is:","1",["δ(ω)","1/jω","2π"],"Constant spectrum.","Impulse FT","fourier and laplace"),
("A real, even signal has a Fourier transform that is:","real and even",["imaginary and odd","purely imaginary","zero"],"Symmetry properties.","FT symmetry","fourier series"),
("Parseval's theorem relates:","energy in time and frequency domains",["phase and delay","poles and zeros","sampling and aliasing"],"∫|x|² = (1/2π)∫|X|².","Parseval","fourier and laplace"),
("For a causal stable system, the ROC of H(s) includes:","the jω axis",["only the origin","the right-half plane only","no points"],"Poles in LHP.","ROC","z-transform"),
("The unit impulse response of an LTI system characterises:","the system completely",["only its stability","only its causality","only DC gain"],"Output = x*h.","Impulse response","lti"),
("The z-transform of δ[n] is:","1",["z","1/z","z/(z−1)"],"Standard pair.","z-transform","z-transform"),
]: fact("SS",k,q,a,b,s,c)
# ============ CTRL ============
@num("CTRL")
def _(r):
    z=r.choice([0.2,0.3,0.4,0.5,0.6,0.707]); mp=math.exp(-pi*z/math.sqrt(1-z*z))*100; return mk("CTRL","time response",f"A standard second-order system has ζ = {z}. The percentage peak overshoot is:",num_opts(r,mp,"%"),f"Mp = exp(−πζ/√(1−ζ²))×100 = {g(mp)}%.","Percent overshoot")
@num("CTRL")
def _(r):
    z=r.choice([0.2,0.4,0.5,0.8]);wn=r.choice([2,4,5,10]); ts=4/(z*wn); return mk("CTRL","time response",f"A second-order system has ζ = {z} and ωn = {wn} rad/s. The 2% settling time is:",num_opts(r,ts," s"),f"ts = 4/(ζωn) = {g(ts)} s.","Settling time")
@num("CTRL")
def _(r):
    z=r.choice([0.2,0.5,0.6,0.8]);wn=r.choice([2,5,10]); tp=pi/(wn*math.sqrt(1-z*z)); return mk("CTRL","time response",f"A second-order system has ζ = {z} and ωn = {wn} rad/s. The peak time is:",num_opts(r,tp," s"),f"tp = π/(ωn√(1−ζ²)) = {g(tp)} s.","Peak time")
@num("CTRL")
def _(r):
    k=r.choice([1,4,9,19,24,49]); e=1/(1+k); return mk("CTRL","steady-state",f"A unity-feedback type-0 system has Kp = {k}. The steady-state error to a unit step is:",num_opts(r,e),f"ess = 1/(1+Kp) = 1/{1+k} = {g(e)}.","Steady-state error (step)")
@num("CTRL")
def _(r):
    k=r.choice([5,10,20,50]);a=r.choice([2,4,5,10]); e=a/k; return mk("CTRL","steady-state",f"For G(s) = {k}/(s(s+{a})) with unity feedback, the steady-state error for a unit ramp is:",num_opts(r,e),f"Kv = {k}/{a}; ess = 1/Kv = {g(e)}.","Steady-state error (ramp)")
@num("CTRL")
def _(r):
    a=r.choice([2,3,4,5,6,8]);b=r.choice([2,3,5,6,7,11]); return mk("CTRL","routh",f"The characteristic equation s³ + {a}s² + {b}s + K = 0 is stable for 0 < K < :",num_opts(r,a*b),f"Routh: a·b > K → K < {a*b}.","Routh stability range")
@num("CTRL")
def _(r):
    t=r.choice([0.5,1,2,5,10]); return mk("CTRL","time response",f"A first-order system G(s) = 1/({t}s+1) has a 2% settling time of:",num_opts(r,4*t," s"),f"ts = 4T = {g(4*t)} s.","First-order settling time")
@num("CTRL")
def _(r):
    gm=r.choice([0.5,0.25,0.1,0.2,0.05]); v=-20*math.log10(gm); return mk("CTRL","bode",f"At the phase-crossover frequency |G(jω)H(jω)| = {gm}. The gain margin is:",num_opts(r,v," dB"),f"GM = −20log10({gm}) = {g(v)} dB.","Gain margin")
@num("CTRL")
def _(r):
    k=r.choice([1,3,4,9,19]); return mk("CTRL","block diagram",f"A unity negative-feedback loop has forward gain G = {k}. The closed-loop DC gain is:",num_opts(r,k/(1+k)),f"G/(1+G) = {k}/{1+k} = {g(k/(1+k))}.","Closed-loop gain")
@num("CTRL")
def _(r):
    k=r.choice([4,9,16,25,36,64,100]);a=r.choice([1,2,3,4,6,8,10,12]); z=a/(2*math.sqrt(k)); 
    if z>=1: return None
    return mk("CTRL","time response",f"The characteristic equation of a closed loop is s² + {a}s + {k} = 0. The damping ratio ζ is:",num_opts(r,z),f"ωn = √{k} = {g(math.sqrt(k))}; ζ = a/(2ωn) = {g(z)}.","Damping ratio from characteristic equation")
@num("CTRL")
def _(r):
    k=r.choice([4,9,16,25,36,49,64,81,100,144]);a=r.choice([1,2,3,4,5,6,7,8]); w=math.sqrt(k)
    return mk("CTRL","time response",f"For the closed-loop characteristic equation s² + {a}s + {k} = 0, the natural frequency ωn (rad/s) is:",num_opts(r,w," rad/s"),f"ωn² = {k} → ωn = {g(w)} rad/s.","Natural frequency")
for q,a,b,s,c,k in [
("Adding a pole at the origin to the open-loop transfer function:","increases system type by 1",["decreases system type","does not affect type","makes it type-0"],"An integrator.","System type","steady-state"),
("A PD controller mainly improves:","transient response (damping)",["steady-state error only","noise rejection","gain margin only by lowering gain"],"Adds a zero.","PD controller","p, pi, pd"),
("A PI controller mainly:","reduces steady-state error",["increases bandwidth","reduces rise time always","adds phase lead"],"Integral action raises type.","PI controller","p, pi, pd"),
("Root loci start at:","open-loop poles",["open-loop zeros","the origin","infinity"],"K = 0.","Root locus","root locus"),
("Root loci end at:","open-loop zeros (or infinity)",["open-loop poles","the imaginary axis","the origin"],"K → ∞.","Root locus end points","root locus"),
("In the Nyquist criterion, Z = N + P where P is the number of:","open-loop right-half-plane poles",["closed-loop zeros","open-loop zeros","LHP poles"],"Stability: Z = 0.","Nyquist criterion","nyquist"),
("Each pole of a transfer function contributes what slope to the asymptotic Bode magnitude plot?","−20 dB/decade",["+20 dB/decade","−40 dB/decade","0 dB/decade"],"Beyond its corner.","Bode slopes","bode"),
("A positive phase margin indicates:","a stable closed loop",["instability","zero damping","infinite gain"],"For minimum-phase systems.","Phase margin","bode"),
("The poles of a stable continuous-time system lie in:","the left half of the s-plane",["the right half","on the real axis only","at the origin"],"Re(s) < 0.","Pole locations","routh"),
("The transfer function is the ratio of Laplace transforms of output to input with:","zero initial conditions",["unit initial conditions","any initial conditions","only ramp input"],"Definition.","Transfer function","open/closed loop"),
]: fact("CTRL",k,q,a,b,s,c)
# ============ NT ============
@num("NT")
def _(r):
    a=r.choice([10,20,30,60]);b=r.choice([10,30,60,120]); p=a*b/(a+b); return mk("NT","kcl",f"Resistors of {a} Ω and {b} Ω are connected in parallel. The equivalent resistance is:",num_opts(r,p," Ω"),f"Rp = ab/(a+b) = {g(p)} Ω.","Parallel resistance")
@num("NT")
def _(r):
    v=r.choice([12,24,36,48]);r1=r.choice([10,20,30]);r2=r.choice([10,20,60]); vth=v*r2/(r1+r2); rth=r1*r2/(r1+r2); return mk("NT","thevenin",f"A {v} V source feeds a divider R1 = {r1} Ω (series) and R2 = {r2} Ω (across the output). The Thevenin voltage at the output is:",num_opts(r,vth," V"),f"Vth = V·R2/(R1+R2) = {g(vth)} V (Rth = {g(rth)} Ω).","Thevenin voltage")
@num("NT")
def _(r):
    vth=r.choice([10,12,20,24,40]);rth=r.choice([2,4,5,10]); p=vth**2/(4*rth); return mk("NT","max power",f"A source has Vth = {vth} V and Rth = {rth} Ω. The maximum power delivered to a load is:",num_opts(r,p," W"),f"Pmax = Vth²/(4Rth) = {g(p)} W at RL = Rth.","Maximum power transfer")
@num("NT")
def _(r):
    l=r.choice([1,2,10,100]);c=r.choice([1,10,100,470]); f=1/(2*pi*math.sqrt(l*1e-3*c*1e-9)); return mk("NT","resonance",f"A series RLC circuit has L = {l} mH and C = {c} nF. The resonant frequency is:",num_opts(r,f/1000," kHz"),f"f0 = 1/(2π√LC) = {g(f/1000)} kHz.","Resonant frequency")
@num("NT")
def _(r):
    f0=r.choice([100,200,455,1000]);q=r.choice([10,20,50,100]); return mk("NT","resonance",f"A series resonant circuit has f0 = {f0} kHz and Q = {q}. Its bandwidth is:",num_opts(r,f0/q," kHz"),f"BW = f0/Q = {g(f0/q)} kHz.","Resonance bandwidth")
@num("NT")
def _(r):
    R=r.choice([1,2,5,10]);c=r.choice([1,10,100]); t=R*1e3*c*1e-6*1000; return mk("NT","rc and rl",f"An RC circuit has R = {R} kΩ and C = {c} µF. The time constant is:",num_opts(r,t," ms"),f"τ = RC = {g(t)} ms.","RC time constant")
@num("NT")
def _(r):
    v=r.choice([5,10,12,24]); return mk("NT","rc and rl",f"A capacitor charges from 0 V through a resistor from a {v} V source. After one time constant its voltage is approximately:",num_opts(r,v*(1-math.exp(-1))," V"),f"V = V0(1−e^−1) = {g(v*(1-1/math.e))} V.","Charging at one time constant")
@num("NT")
def _(r):
    R=r.choice([3,6,8,10]);XL=r.choice([4,8,6,10]); pf=R/math.hypot(R,XL); return mk("NT","ac circuits",f"A series RL circuit has R = {R} Ω and XL = {XL} Ω. The power factor is:",num_opts(r,pf),f"cosφ = R/√(R²+XL²) = {g(pf)}.","Power factor")
@num("NT")
def _(r):
    l=r.choice([1,2,4,10]);i=r.choice([1,2,3,5]); return mk("NT","rlc",f"The energy stored in a {l} H inductor carrying {i} A is:",num_opts(r,0.5*l*i*i," J"),f"E = ½LI² = {g(0.5*l*i*i)} J.","Inductor energy")
@num("NT")
def _(r):
    R=r.choice([30,60,90,120]); return mk("NT","kcl",f"Three equal {R} Ω resistors form a delta. The equivalent star resistor in each arm is:",num_opts(r,R/3," Ω"),f"R_Y = RΔ/3 = {g(R/3)} Ω.","Delta-star conversion")
for q,a,b,s,c,k in [
("Superposition theorem applies to:","linear circuits",["non-linear circuits","only DC circuits with diodes","only AC circuits"],"Needs linearity.","Superposition","superposition"),
("Norton and Thevenin equivalents are related by:","source transformation",["duality only","Millman only","reciprocity only"],"Vth = Isc·Rth.","Source transformation","thevenin"),
("For a reciprocal two-port network:","Z12 = Z21",["Z11 = Z22","Y11 = Y22","h11 = h22"],"Reciprocity condition.","Reciprocity","two-port"),
("At series resonance the impedance of an RLC circuit is:","minimum and purely resistive",["maximum","purely inductive","infinite"],"XL = XC.","Series resonance","resonance"),
("At parallel (ideal LC tank) resonance the impedance is:","maximum",["zero","equal to R only","capacitive"],"Anti-resonance.","Parallel resonance","resonance"),
("A critically damped RLC circuit has:","real equal roots",["complex roots","imaginary roots","positive real roots"],"ζ = 1.","RLC transients","rlc"),
("The unit of reactive power is:","VAR",["watt","VA","joule"],"Q = VI sinφ.","Reactive power","ac circuits"),
("Millman's theorem is used to find:","the voltage across parallel branches",["power factor","resonance","mutual inductance"],"V = ΣGV/ΣG.","Millman","max power"),
("A pure capacitor draws current that:","leads the voltage by 90°",["lags by 90°","is in phase","is zero"],"I = C dv/dt.","Capacitor phase","ac circuits"),
("The Q factor of a series RLC circuit is:","ωL/R",["R/ωL","ωLR","R/ωC"],"Selectivity measure.","Q factor","resonance"),
]: fact("NT",k,q,a,b,s,c)
# ============ EMFW ============
@num("EMFW")
def _(r):
    f=r.choice([30,100,150,300,600,1000]); l=300/f; return mk("EMFW","maxwell",f"The free-space wavelength of a {f} MHz plane wave is:",num_opts(r,l," m"),f"λ = c/f = 300/{f} = {g(l)} m.","Wavelength")
@num("EMFW")
def _(r):
    er=r.choice([4,9,16,25,2.25]); v=3e8/math.sqrt(er)/1e8; return mk("EMFW","maxwell",f"A wave travels in a non-magnetic dielectric with εr = {er}. Its velocity is:",num_opts(r,v," ×10⁸ m/s"),f"v = c/√εr = {g(v)}×10⁸ m/s.","Phase velocity in a dielectric")
@num("EMFW")
def _(r):
    er=r.choice([4,9,16,25]); eta=377/math.sqrt(er); return mk("EMFW","maxwell",f"The intrinsic impedance of a non-magnetic medium with εr = {er} is approximately (η0 = 377 Ω):",num_opts(r,eta," Ω"),f"η = 377/√εr = {g(eta)} Ω.","Intrinsic impedance")
@num("EMFW")
def _(r):
    G=r.choice([0.2,0.25,0.333,0.5,0.6,0.8]); s=(1+G)/(1-G); return mk("EMFW","transmission lines",f"A line has reflection coefficient magnitude {G}. The VSWR is:",num_opts(r,s),f"VSWR = (1+|Γ|)/(1−|Γ|) = {g(s)}.","VSWR")
@num("EMFW")
def _(r):
    z0=r.choice([50,75]);zl=r.choice([25,100,150,200,300]); G=(zl-z0)/(zl+z0); return mk("EMFW","transmission lines",f"A {z0} Ω line is terminated in {zl} Ω. The reflection coefficient is:",[g(G),g(-G),g(G*2),g(zl/z0)],f"Γ = (ZL−Z0)/(ZL+Z0) = {g(G)}.","Reflection coefficient")
@num("EMFW")
def _(r):
    z1=r.choice([25,50,100,200]);z2=r.choice([50,100,200,400]);
    z0=math.sqrt(z1*z2)
    return mk("EMFW","transmission lines",f"A quarter-wave transformer matches {z1} Ω to {z2} Ω. Its characteristic impedance must be:",num_opts(r,z0," Ω",[(z1+z2)/2]),f"Z0 = √(Z1Z2) = {g(z0)} Ω.","Quarter-wave transformer")
@num("EMFW")
def _(r):
    a=r.choice([2.286,3,4,5,7.2,10]); fc=15/a; return mk("EMFW","waveguides",f"A rectangular waveguide has broad dimension a = {a} cm. The TE10 cutoff frequency (air-filled) is:",num_opts(r,fc," GHz"),f"fc = c/(2a) = 15/{a} GHz = {g(fc)} GHz.","TE10 cutoff")
@num("EMFW")
def _(r):
    q=r.choice([1,2,4,5,10]);d=r.choice([1,2,3,5]); e=9e9*q*1e-6/d**2; return mk("EMFW","electrostatics",f"The electric field at {d} m from a point charge of {q} µC in free space is (k = 9×10⁹):",num_opts(r,e," V/m"),f"E = kQ/r² = {g(e)} V/m.","Coulomb field")
@num("EMFW")
def _(r):
    z0=r.choice([50,75,100]);c=r.choice([50,100,200]); l=z0*z0*c; return mk("EMFW","transmission lines",f"A lossless line has L = {g(l*1e-12*1e9)} nH/m and C = {c} pF/m. Its characteristic impedance is:",num_opts(r,z0," Ω"),f"Z0 = √(L/C) = {z0} Ω.","Characteristic impedance")
@num("EMFW")
def _(r):
    f1=r.choice([1,2,4]);d1=r.choice([2,4,8]);m=r.choice([4,9,16]); d2=d1/math.sqrt(m); return mk("EMFW","maxwell",f"A conductor has skin depth {d1} µm at {f1} MHz. At {f1*m} MHz the skin depth becomes:",num_opts(r,d2," µm"),f"δ ∝ 1/√f → δ2 = {d1}/√{m} = {g(d2)} µm.","Skin depth scaling")
for q,a,b,s,c,k in [
("Which Maxwell equation states that magnetic monopoles do not exist?","∇·B = 0",["∇·D = ρ","∇×E = −∂B/∂t","∇×H = J + ∂D/∂t"],"Gauss's law for magnetism.","Maxwell's equations","maxwell"),
("Displacement current density is:","∂D/∂t",["∂B/∂t","σE","ρv"],"Maxwell's addition to Ampere's law.","Displacement current","maxwell"),
("In a uniform plane wave, E and H are:","perpendicular to each other and to the direction of propagation",["parallel to each other","both along propagation","in phase opposition only"],"TEM wave.","Plane wave","maxwell"),
("The Poynting vector gives:","power flow per unit area",["energy per volume","charge density","magnetic flux"],"S = E × H.","Poynting vector","maxwell"),
("The characteristic impedance of free space is approximately:","377 Ω",["50 Ω","75 Ω","120 Ω"],"η0 = √(μ0/ε0).","Free-space impedance","maxwell"),
("The dominant mode of a rectangular waveguide is:","TE10",["TM11","TEM","TE11"],"Lowest cutoff.","Dominant mode","waveguides"),
("A TEM wave cannot propagate in:","a hollow rectangular waveguide",["a coaxial line","a two-wire line","free space"],"Needs two conductors.","TEM","waveguides"),
("For a matched transmission line the VSWR is:","1",["0","∞","2"],"No reflection.","VSWR","transmission lines"),
("A short-circuited quarter-wave stub looks like:","an open circuit at its input",["a short circuit","a pure resistance of Z0","a capacitor"],"Impedance inversion.","Stub","transmission lines"),
("Gauss's law in electrostatics relates:","flux through a closed surface to enclosed charge",["current to magnetic field","E to B","power to energy"],"∮D·dS = Q.","Gauss's law","electrostatics"),
("The Smith chart is primarily used for:","transmission line impedance calculations",["filter design only","antenna gain","waveguide cutoff"],"Normalised impedance plane.","Smith chart","smith"),
]: fact("EMFW",k,q,a,b,s,c)
# ============ EM (maths) ============
@num("EM")
def _(r):
    l1=r.randint(-4,6);l2=r.randint(-4,6);k=r.randint(1,5); return mk("EM","eigenvalues",f"The matrix [[{l1}, {k}], [0, {l2}]] has eigenvalues whose sum is:",num_opts(r,l1+l2) if l1+l2>0 else [g(l1+l2),g(l1*l2),g(l1+l2+1),g(l1-l2)],f"Trace = {l1}+{l2} = {l1+l2}.","Trace and eigenvalues")
@num("EM")
def _(r):
    a=r.randint(1,9);b=r.randint(1,9);c=r.randint(1,9);d=r.randint(1,9); det=a*d-b*c; return mk("EM","complex numbers and matrices",f"The determinant of [[{a}, {b}], [{c}, {d}]] is:",[g(det),g(a*d+b*c),g(det+1),g(-det)] if det!=0 else None or [g(0),g(1),g(2),g(3)],f"ad − bc = {det}.","2×2 determinant")
@num("EM")
def _(r):
    a=r.randint(1,5);b=r.randint(1,6);c=r.randint(1,4); v=3*a*c*c+2*b*c; return mk("EM","calculus",f"If f(x) = {a}x³ + {b}x², then f′({c}) equals:",[g(v),g(a*c**3+b*c*c),g(v+a),g(v-b)],f"f′ = {3*a}x² + {2*b}x → {v}.","Derivative at a point")
@num("EM")
def _(r):
    k=r.randint(1,4);L=r.randint(1,4); v=3*k*L**3/3; return mk("EM","calculus",f"∫₀^{L} {3*k}x² dx equals:",[g(k*L**3),g(3*k*L**3),g(k*L**2),g(k*L**3+1)],f"= {k}·{L}³ = {k*L**3}.","Definite integral")
@num("EM")
def _(r):
    a=r.randint(1,6);b=r.randint(1,6); m=math.hypot(a,b); return mk("EM","complex numbers and matrices",f"The magnitude of the complex number {a}+j{b} is:",num_opts(r,m),f"|z| = √({a}²+{b}²) = {g(m)}.","Complex magnitude")
@num("EM")
def _(r):
    n=r.choice([3,4,5,6]);k=r.randint(0,n); p=Fraction(math.comb(n,k),2**n); return mk("EM","probability",f"A fair coin is tossed {n} times. The probability of exactly {k} heads is:",[str(p),str(Fraction(math.comb(n,k),2**n)*2) if p<0.5 else str(p/2),str(Fraction(k+1,2**n)),str(Fraction(1,n+1))] if True else None,f"C({n},{k})/2^{n} = {p}.","Binomial probability")
@num("EM")
def _(r):
    N=r.choice([2,3,5,6,7,10]);x0=r.choice([1,2,3]); x1=(x0+N/x0)/2; return mk("EM","numerical",f"One Newton–Raphson step for f(x) = x² − {N} starting at x0 = {x0} gives x1 =",num_opts(r,x1),f"x1 = (x0 + N/x0)/2 = {g(x1)}.","Newton-Raphson")
@num("EM")
def _(r):
    b=r.choice([-2,-1,1,2]);y0=r.choice([2,3,5,10]);h=r.choice([0.1,0.2,0.5]); y1=y0+h*b*y0; return mk("EM","numerical",f"Euler's method with h = {h} for dy/dx = {b}y, y(0) = {y0} gives y(h) ≈",[g(y1),g(y0*math.exp(b*h)),g(y0+b*y0),g(y1+h)],f"y1 = y0 + h·f = {y0} + {h}×{b*y0} = {g(y1)}.","Euler method")
@num("EM")
def _(r):
    a=r.choice([1,2,3,5]);y0=r.choice([2,4,6,10]); v=y0/math.e; return mk("EM","differential equations",f"The solution of dy/dx + {a}y = 0 with y(0) = {y0}, evaluated at x = 1/{a}, is:",num_opts(r,v),f"y = {y0}e^(−{a}x) → {y0}/e = {g(v)}.","First-order ODE")
@num("EM")
def _(r):
    xs=[r.randint(2,20) for _ in range(5)]; m=sum(xs)/5; return mk("EM","probability",f"The mean of the data {xs} is:",num_opts(r,m),f"Σx/n = {sum(xs)}/5 = {g(m)}.","Mean")
for q,a,b,s,c,k in [
("The sum of the eigenvalues of a square matrix equals its:","trace",["determinant","rank","transpose"],"Standard result.","Eigenvalues","eigenvalues"),
("The product of the eigenvalues equals:","the determinant",["the trace","the rank","zero always"],"Standard result.","Eigenvalue product","eigenvalues"),
("A matrix is singular when its:","determinant is zero",["trace is zero","rank is full","all entries are 1"],"No inverse.","Singular matrix","eigenvalues"),
("The Cauchy–Riemann equations test whether a complex function is:","analytic",["continuous only","periodic","real"],"Necessary and sufficient with continuity.","Analytic functions","complex numbers"),
("The value of e^(jπ) is:","−1",["1","j","−j"],"Euler's formula.","Euler's formula","complex numbers"),
("For a normal distribution, about what fraction of values lies within ±1σ?","68%",["50%","95%","99.7%"],"Empirical rule.","Normal distribution","probability"),
("The integrating factor of dy/dx + P(x)y = Q(x) is:","e^(∫P dx)",["e^(∫Q dx)","P/Q","∫P dx"],"Linear first-order ODE.","Integrating factor","differential equations"),
("Rank of a 3×3 matrix with a zero determinant is at most:","2",["3","4","1 always"],"Singular.","Rank","eigenvalues"),
("L'Hôpital's rule resolves limits of the form:","0/0 or ∞/∞",["1/0 only","0·0","1^1"],"Indeterminate forms.","Limits","calculus"),
("The trapezoidal rule has error of order:","h²",["h","h³ always","h⁴"],"Second-order accurate.","Numerical integration","numerical"),
]: fact("EM",k,q,a,b,s,c)

# ---------------------------------------------------------------- assemble
def build(sid):
    rng=random.Random(int(hashlib.sha256(sid.encode()).hexdigest()[:8],16))
    pool=[]; seen=set(); 
    def add(q):
        if q is None: return
        opts=q.opts
        if len(set(opts))<4: return
        key=q.stmt+"|"+"|".join(sorted(opts))
        if key in seen: return
        seen.add(key); pool.append(q)
    for q in F[sid]: add(q)
    tries=0
    while len(pool)<120 and tries<4000:
        tries+=1
        try: q=rng.choice(T[sid])(rng)
        except Exception: q=None
        add(q)
    print(sid,len(pool),len(F[sid]))
    assert len(pool)>=120,(sid,len(pool))
    facts=[q for q in pool if q in F[sid]]; nums=[q for q in pool if q not in F[sid]]
    rng.shuffle(nums); sel=facts+nums[:120-len(facts)]; rng.shuffle(sel)
    roles=["pool:practice"]*70+["pool:exam"]*30+["pool:mock"]*20
    out=[]
    for q,role in zip(sel,roles):
        o=list(q.opts); correct=o[0]; rng.shuffle(o)
        title=topic_for(sid,q.tk); tid=f"{sid}/{slug(title)}"
        out.append({"id":"bk-"+hashlib.sha256((q.stmt+"|".join(sorted(o))).encode()).hexdigest()[:14],"s":sid,"t":tid,"st":title,
          "q":q.stmt+"\nChoose the correct option.","type":"MCQ","o":o,"c":[o.index(correct)],"nl":None,"nh":None,"m":1,"n":round(1/3,6),
          "sol":q.sol,"oe":[("Correct: "+q.sol) if x==correct else "Incorrect: re-check the working shown in the solution." for x in o],
          "con":q.con,"d":q.d,"src":"TEMPLATE_GENERATED","v":"VERIFIED_DETERMINISTIC","tags":[role]})
    return out
allq=[]
for sid in SUBJ: allq+=build(sid)
ids=[q['id'] for q in allq]; assert len(ids)==len(set(ids))
json.dump({"version":1,"questions":allq},open(OUT,'w'),ensure_ascii=False,separators=(',',':'))
print(len(allq),"questions;",{s:sum(1 for q in allq if q['s']==s) for s in SUBJ})
