# Lucifer Latch — Verification Report
**Module:** `lucifer_latch` (ZOREL-717 hardware safety veto)
**Date:** 2026-06-22 · **Tool:** Icarus Verilog 12.0 (stable), `-g2012`
**Status:** ✅ Safety-critical behavior VERIFIED in simulation (8/8 checks pass)

This report describes the source as it stands in this repository (fixed).
Reproduce: `iverilog -g2012 -o sim_latch lucifer_latch.v tb_lucifer_latch.v && vvp sim_latch`

---

## What was tested
The self-contained `lucifer_latch` core FSM. The `uart_bridge` module is excluded:
its TX path is explicitly stubbed in the original source and is not safety-critical.

| # | Claim under test | Result |
|---|------------------|--------|
| T1 | Reset → ARMED; `latch_state` & `veto_signal` deasserted | PASS |
| T2 | `threat_level=190` (sub-threshold) does **not** trigger | PASS |
| T3 | `trigger_in` pulse arms countdown; latch fires | PASS |
| T3b | Fires at the timing floor — measured **68001 cycles ≈ 680 µs** @100 MHz | PASS |
| T4 | **Irreversibility:** stays TRIGGERED with all inputs low | PASS |
| T4b | **Irreversibility:** stays TRIGGERED under max-threat + trigger toggling | PASS |
| T5 | Only physical reset (`rst_n`) clears the latch | PASS |
| T6 | `threat_level≥191` path also arms & fires | PASS |

**Core safety guarantee holds:** once TRIGGERED, no software signal returns the latch
to ARMED. Only `rst_n` does.

---

## Findings

1. **`status_led` drive — found and FIXED in this source.**
   The original draft sampled the clock as data (`status_led <= clk;`), which does not
   synthesize as an intended blink. It is corrected here: `status_led` is driven from a
   free-running 24-bit `blink_counter` (`status_led <= blink_counter[23];`, ~6 Hz @100 MHz),
   which is clean, synthesizable RTL. `status_led` is not a safety output, so `latch_state`
   and `veto_signal` were never affected; the testbench confirms 8/8 before and after the fix.

2. **Timing is a *floor*, not a fast-trip.** The design intentionally waits ~680 µs before
   the veto becomes irreversible — a deliberation window, not a fast emergency stop.
   Confirm this matches intent; most kill switches minimize latency rather than impose a delay.

3. **Not yet verified (out of simulation scope):**
   - Synthesis + place-and-route timing closure on real Artix-7 silicon
   - Physical `rst_n` debounce on the Arty A7 button
   - UART bridge end-to-end (TX path unimplemented in original source)
   - Metastability hardening on async `trigger_in` / `uart_rx` inputs

---

## Files
- `lucifer_latch.v`    — safety core (fixed source)
- `tb_lucifer_latch.v` — testbench (8 assertions)
- `sim_results.log`    — captured run from this source (8/8)
- `lucifer_latch.vcd`  — generated waveform from the test run; ignored by git
