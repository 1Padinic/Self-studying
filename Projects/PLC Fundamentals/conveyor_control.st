(* ============================================================================
   FOERDER_PRG  --  Conveyor belt control
   Refactored from an undocumented 2011 legacy program.

   Design rule enforced throughout:
     * every output has exactly ONE statement that sets it TRUE;
     * stops / timeouts may stack as conditional CLEARs (FALSE-writes).
   This is what prevents the double-write / scan-order oscillation bugs that
   the original program suffered from.

   Naming: E_ = Eingang (input), A_ = Ausgang (output) -- European convention.
   ============================================================================ *)


(* ---------------------------------------------------------------------------
   DECLARATION
   --------------------------------------------------------------------------- *)
PROGRAM FOERDER_PRG
VAR
    (* ---- Inputs ---- *)
    E_START       : BOOL;         (* Start pushbutton (NO)                              *)
    E_STOP        : BOOL := TRUE;  (* Stop pushbutton (NC / Oeffner: TRUE = not pressed) *)
    E_RESET       : BOOL;         (* Counter acknowledge pushbutton (NO)                *)
    E_LS1         : BOOL;         (* Infeed light barrier  (TRUE = beam blocked)        *)
    E_LS2         : BOOL;         (* Outfeed light barrier (TRUE = beam blocked)        *)

    (* ---- Outputs ---- *)
    A_BAND        : BOOL;         (* Belt motor                                         *)
    A_LAMPE_VOLL  : BOOL;         (* FULL lamp                                          *)

    (* ---- Internal ---- *)
    bRunLatch     : BOOL;         (* Belt run latch (was MERKER_1)                      *)
    nStueck       : INT;          (* Piece count   (was Z_STUECK)                       *)
    T_NACHLAUF    : TON;          (* 3 s run-on timer                                   *)
    R_TRIG_LS1    : R_TRIG;       (* Infeed rising edge  -> auto-resume trigger         *)
    R_TRIG_LS2    : R_TRIG;       (* Outfeed rising edge -> piece count                 *)
END_VAR


(* ---------------------------------------------------------------------------
   IMPLEMENTATION
   --------------------------------------------------------------------------- *)

(* ---- Belt run latch -------------------------------------------------------
   Latch on Start OR a fresh box arriving at the infeed; hold via seal-in.
   The whole expression is gated by E_STOP (NC), so a manual Stop overrides
   any arriving box -- e.g. the belt stays stopped over a lunch break.        *)
R_TRIG_LS1(CLK := E_LS1);
bRunLatch := (E_START OR R_TRIG_LS1.Q OR bRunLatch) AND E_STOP;

(* ---- Run-on: drop the belt 3 s after the infeed goes clear ----------------
   Timer runs while the infeed is clear; a new box (E_LS1 = TRUE) resets it.
   Clearing the LATCH here (not just the output) is the single tolerated
   conditional FALSE-write. In the original, run-on cleared only the output
   while 'A_BAND := latch' re-asserted it every scan -> the belt toggled
   on/off on alternating scans and looked like a spontaneous restart.         *)
T_NACHLAUF(IN := NOT E_LS1, PT := T#3S);
IF T_NACHLAUF.Q THEN
    bRunLatch := FALSE;
END_IF

(* ---- Belt output (single write) ---------------------------------------- *)
A_BAND := bRunLatch;

(* ---- Piece counter at the outfeed (rising edge only) ----------------------
   Original counted every scan the beam was blocked -> ran away to hundreds
   from a handful of boxes.                                                   *)
R_TRIG_LS2(CLK := E_LS2);
IF R_TRIG_LS2.Q THEN
    nStueck := nStueck + 1;
END_IF

(* ---- FULL lamp from 10 pieces (single expression, no flicker) ---------- *)
A_LAMPE_VOLL := (nStueck >= 10);

(* ---- Counter acknowledge (dedicated button, NOT the Start button) --------
   Original tied the reset to Start, so the count vanished on every start.    *)
IF E_RESET THEN
    nStueck := 0;
END_IF
