# PLC Fundamentals in CODESYS — Motor Control & Legacy Conveyor Debugging

**Platform:** CODESYS V3.5 · CODESYS Control Win V3 (soft PLC, simulation mode) · IEC 61131-3 (Ladder Diagram + Structured Text)

This repository documents a structured, hands-on walk through the core building blocks — and the classic failure modes — of industrial PLC programming. It is not a single finished machine but a deliberately incremental series: each step adds exactly one requirement, and several steps intentionally reproduce the bugs that PLC programmers spend real time chasing on site — the *double-coil*, *one-shot / edge detection*, *scan-order oscillation*, *fail-safe wiring*, and *requirements-vs-code* mismatches. Every program was built and verified in the CODESYS simulator against explicit acceptance criteria before moving on.

The intent is to demonstrate understanding of **why** ladder and Structured Text behave the way they do at the scan-cycle level — not just that a program happens to run.

---

## What this demonstrates

- **Ladder logic (LD):** contacts, coils, seal-in latches, parallel (OR) branches, mutual interlocks
- **Structured Text (ST):** latches, `IF` / `ELSIF`, function-block instances, edge triggers, `TON` timers
- **Fail-safe design:** normally-closed field wiring, and why an NC device correctly appears as an NO contact in the logic (a cut wire must read as "stop")
- **Edge detection / one-shots** (`R_TRIG`) — and, just as importantly, *choosing what an event should mean* (a button press vs. a contactor operation)
- **The scan cycle:** double-write bugs, statement/rung order, and why every output must be written in exactly one place
- **State vs. output:** separating a latch (memory) from the command that drives an actuator
- **Staged starting:** star-delta sequencing with a `TON` and a hard mutual interlock
- **Debugging methodology:** reproduce → isolate to a rung/line → diagnose the *mechanism* → fix — and writing acceptance tests that actually pin the intended behaviour down (including tests that wait out a timer)

---

## Part A — Motor control, built incrementally

### 1 · Start/Stop with seal-in and fail-safe stop

![Task 1 – seal-in start/stop](images/task1_seal_in.png)

A momentary **Start** latches the motor through a **seal-in** (hold) contact — the output feeds back to keep its own rung true after the button is released. **Stop**, or loss of the motor-protection signal, drops it immediately.

The subtlety: the Stop button is a **normally-closed** field device, so it is TRUE during normal operation and FALSE only when pressed *or when its wire is cut*. It therefore appears in the logic as a **normally-open** contact — the fail-safe convention, so a broken wire fails to the safe "stopped" state.

### 2 · Maintenance start counter — the one-shot

![Task 2 – edge-detected counter](images/task2_counter_edge.png)

Counts how many times the **motor** starts (i.e. contactor operations, which is what physically wears the contactor) and lights a service lamp at a threshold.

The naive version — *increment while Start is pressed* — counts once **per scan**, roughly +20 per press at a 10 ms scan. Fixed with **rising-edge detection** on the run command, so one press = one count. Which signal's edge is used is a genuine design decision: the counter models metal fatigue, so it counts the *contactor coil*, not the button.

### 3 · Jog, and separating latch from output — the double-coil

![Task 3 – latch/output separation](images/task3_jog_latch.png)

Adds a hold-to-run **jog**. The tempting implementation puts a *second coil* on the motor output — but two rungs writing one output is a **double-coil**, and only the last write of the scan survives. The result is insidious: the seal-in silently fails while jog *appears* to work, so the bug surfaces in a different feature than the one that causes it.

Fixed by computing a latch (`bRunLatch`) in one rung, and driving the **single** motor coil from `(bRunLatch OR bJogPB) AND interlocks` in another. State lives in exactly one place; the output is written exactly once. Jogging deliberately never engages the delta stage.

### 4 · Star-delta staged start — timers + interlock

![Task 4 – star-delta with TON](images/task4_star_delta.png)

Two contactor outputs (`bStarCon`, `bDeltaCon`) sequenced by a `TON`: run command → **star** → after 5 s → **delta**, held until the run command drops.

Hard safety requirement: star and delta must **never** be energised in the same scan — simultaneous closure is a phase-to-phase short. This is enforced in logic with **mutual normally-closed interlock contacts**, not merely by trusting the sequence. A single `TON` instance is used and called once; its `.Q` output is reused as a contact wherever the "elapsed" signal is needed.

---

## Part B — Debugging an inherited "legacy" conveyor (Structured Text)

A deliberately messy conveyor program — commented *"last edited 2011"*, junk tag names (`MERKER_1`, `HILF_MERKER_2`, `M13_4`), German comments including a *"DO NOT TOUCH!!"* on the broken block — arrives with four field complaints from the night shift. The task was to reproduce each in simulation, isolate it to specific lines, and explain the **mechanism** before touching anything.

| Symptom (operator complaint) | Root cause | Fix |
|---|---|---|
| Piece count showed **400** after ~12 boxes | Counter incremented *every scan* the outfeed beam was blocked (no edge) | `R_TRIG` on the outfeed sensor — count on the rising edge only |
| **FULL lamp flickers** instead of latching | Runaway count interacting with the reset-on-start below, slamming the value around the threshold | Dissolved automatically by the edge-count + dedicated-reset fixes — a *symptom* of the two real root causes, not a separate bug |
| Belt **restarts by itself** seconds after loading stops | **Double write / scan-order oscillation** — run-on cleared the *output* (`A_BAND`), but `A_BAND := latch` at the top of the scan re-asserted it every scan → belt toggled on/off on alternating scans | Run-on clears the *latch*, not just the output |
| Piece count **resets to 0 on its own** | The counter reset was tied to the Start button | Moved to a dedicated acknowledge button |

The centrepiece is the third one. The "spontaneous restart" is really a **one-scan oscillation**: an output written in two places while it is recomputed from the latch every scan is the exact Structured-Text twin of the double-coil in Part A. The lesson generalises to the rule used throughout the rewrite — *every output gets one statement that sets it true; stops and timeouts may stack as conditional clears.*

### A documented design decision (not a bug)

The rewrite lets a fresh box at the infeed **auto-resume** the belt after a run-on stop — but a manual **Stop overrides any arriving box** (e.g. a lunch break must keep the belt stopped, even with material sitting on the infeed). This is achieved by folding the infeed edge into the *single* latch expression and gating the whole thing with the (NC) Stop:

```iecst
R_TRIG_LS1(CLK := E_LS1);
bRunLatch := (E_START OR R_TRIG_LS1.Q OR bRunLatch) AND E_STOP;
```

so there is still exactly one statement that sets the latch true, and Stop wins over everything. This distinction — *clearing state* vs. *gating an output* — is the thread running under most of the design choices in this project.

---

## Code

Full fixed program: **[`conveyor_control.st`](conveyor_control.st)**

**Before** (the inherited program — reproduced verbatim, bugs intact):

```iecst
MERKER_1 := (E_START OR MERKER_1) AND E_STOP;
A_BAND := MERKER_1;

IF E_LS2 THEN                       (* counts every scan -> runs away *)
    Z_STUECK := Z_STUECK + 1;
END_IF

IF Z_STUECK >= 10 THEN
    A_LAMPE_VOLL := TRUE;
ELSE
    A_LAMPE_VOLL := FALSE;
END_IF

T_NACHLAUF(IN := NOT E_LS1, PT := T#3S);
M13_4 := T_NACHLAUF.Q;
IF M13_4 THEN
    A_BAND := FALSE;                (* clears OUTPUT, not latch -> oscillates *)
END_IF

HILF_MERKER_2 := E_START AND E_STOP;
IF HILF_MERKER_2 THEN               (* reset tied to Start -> count vanishes *)
    Z_STUECK := 0;
END_IF
```

**After** (core logic — see the `.st` file for full declarations and comments):

```iecst
(* Belt run latch: Start OR fresh infeed box; Stop (NC) overrides *)
R_TRIG_LS1(CLK := E_LS1);
bRunLatch := (E_START OR R_TRIG_LS1.Q OR bRunLatch) AND E_STOP;

(* Run-on: 3 s after infeed clear, clear the LATCH (single tolerated clear) *)
T_NACHLAUF(IN := NOT E_LS1, PT := T#3S);
IF T_NACHLAUF.Q THEN
    bRunLatch := FALSE;
END_IF

A_BAND := bRunLatch;                            (* single output write *)

(* Piece count on rising edge only *)
R_TRIG_LS2(CLK := E_LS2);
IF R_TRIG_LS2.Q THEN
    nStueck := nStueck + 1;
END_IF

A_LAMPE_VOLL := (nStueck >= 10);

(* Acknowledge via dedicated button, not Start *)
IF E_RESET THEN
    nStueck := 0;
END_IF
```

---

## Notes

Built for learning; the scenarios are intentionally elementary. The point is not the machines but the **failure modes** and the **debugging discipline** behind each fix — the kind of scan-cycle reasoning that separates code that runs in a simulator from code that survives on a real panel.

**Environment:** all logic runs on the free CODESYS Control Win V3 soft PLC in simulation mode — no hardware required to reproduce any of it.
