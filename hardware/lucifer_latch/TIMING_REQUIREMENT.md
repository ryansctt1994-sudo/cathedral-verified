# Lucifer Latch Timing Requirement — Ambiguity Gate

Status date: 2026-09-04
Status: requirement semantics **not frozen; promotion blocked**

## Observed implementation

The current RTL assumes a 100 MHz clock (10 ns/cycle) and defines:

```verilog
localparam TIMING_FLOOR_CYCLES = 17'd68000;
```

The retained simulation report measures the transition at 68,001 cycles, approximately 680.01 µs.

## Requirement ambiguity

Historical project material has used a value near 670 µs in connection with the latch. Two materially different requirements are possible:

### A. Maximum response deadline

```text
trigger_to_veto <= 670 µs
```

Under this interpretation, the current simulated 680.01 µs behavior **FAILS** by approximately 10.01 µs, before adding any physical input synchronization, debounce, routing, clock tolerance, or board-level latency.

### B. Minimum deliberation floor

```text
trigger_to_veto >= 670 µs
```

Under this interpretation, the current simulated 680.01 µs behavior **PASSES** the lower bound, but an upper bound is still required if the veto is safety-relevant.

These interpretations are not interchangeable. A lower-bound delay is unusual for an emergency-stop style mechanism; a maximum latency is typical for a response deadline. The engineering owner must freeze the intended semantics before the timing result can be described as `on spec`.

## Required frozen contract

The specification should state, at minimum:

- event that starts the timer;
- event that ends the timer;
- whether the bound is minimum, maximum, or a closed interval;
- nominal and allowed clock frequency/tolerance;
- whether synchronizer/debounce/UART/input-processing latency is included;
- behavior on counter overflow or clock fault;
- acceptable jitter;
- target device/board;
- physical measurement method;
- fail-safe behavior if the timing requirement cannot be met.

## Current claim boundary

Allowed:

```text
The current RTL simulation reaches the latched veto state after approximately 680.01 µs at an ideal 100 MHz simulation clock.
```

Not allowed until the requirement is frozen:

```text
The latch meets the 670 µs timing specification.
The latch is a verified emergency-stop response mechanism.
```

Simulation remains separate from synthesis timing closure and physical FPGA validation.
