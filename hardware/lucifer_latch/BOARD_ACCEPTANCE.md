# Lucifer Latch board acceptance procedure — unexecuted

Status: BLOCKED / simulation only / no board evidence / production prohibited.
Target: Artix-7, Arty A7-35T. No board is attached to this environment. This
procedure is a candidate acceptance plan, not a flash record or certification.

## Before a flash can count

Freeze RTL, board revision/serial, FPGA part, wrapper, constraints, synthesis and
place/route tools, tool versions and command lines. Include SHA-256 for all inputs
and the bitstream. A pin-mapped wrapper, reviewed XDC, metastability treatment,
reset deassertion synchronization and physical button debounce are required.
Retain timing/CDC/DRC reports, constraint coverage, and programming logs. Do not
invent a pin map. Any UART/status stub must be completed or excluded explicitly
from the tested interface and claim. Missing inputs or failed timing are BLOCKED.

Review the actual electrical path: rst_n must not be controllable by the software
under test. Check schematic, physical routing, debugger/programmer access and
power control. FPGA reconfiguration, power cycling and physical reset are reset
boundaries; this volatile design does not establish persistence across them.
"Irreversible" means no tested software input clears the latch while reset,
configuration, power and clock assumptions hold. If software controls these,
that broader physical irreversibility claim fails.

## Instrumentation and procedure

Use a benign indicator/load, not an operational safety system. Capture trigger,
threat bus, clock, reset, latch_state and veto_signal with a logic analyzer or
scope; record instrument model, sampling rate, calibration and probe mapping.
Preserve raw captures alongside human-readable plots and timestamped board photos.

1. Program the pinned bitstream. Record board identity, programmer output and
   observed physical reset. Confirm latch_state and veto_signal are low when armed.
2. Exercise trigger_in independently and threat levels 190, 191 and 255; for 190
   with trigger low verify no trip, and for the two qualifying levels verify trip.
   Start each independent trial from a recorded physical reset. Test a short
   qualifying trigger as well as a held trigger. Use at least 20 trials per case.
3. Measure qualifying sampled edge to veto assertion in cycles and physical time.
   Derive the expected cycle interval from the exact frozen RTL/testbench,
   including synchronizer latency and counter off-by-one behavior. The local
   report's 68001-cycle figure is not a substitute for this measurement. Record
   minimum/maximum, uncertainty and clock frequency. Fail if earlier than the
   68000-cycle design floor or outside the predeclared RTL-derived interval.
4. Once tripped, drive trigger high/low and threat 0..255, including sustained zero
   and rapid alternation. Run at least 10000 input transitions over 60 seconds;
   log seed/stimulus and capture veto continuously. Fail on any deassertion of
   latch_state or veto without a recorded permitted physical reset.
5. Attempt every available software command and software reset. Verify none can
   toggle physical rst_n, reconfigure the FPGA or clear veto within the declared
   threat boundary. Record inaccessible paths as excluded, never as passes.
6. Apply the physical reset, verify clearing, and repeat the trip. Separately
   document power-cycle and reprogramming behavior as limitations. Exercise
   button bounce and asynchronous input transitions under the reviewed wrapper.

## Acceptance and publication

Each case records PASS/FAIL/BLOCKED, raw capture hashes, stimulus identity,
measurement interval, uncertainty, environment, observer and deviations. Publish
schematic/pin evidence, wrapper/XDC, bitstream and tool reports, flash log, photos,
raw captures, annotated measurements and a complete hash manifest. Authenticate
an independent operator receipt over that manifest via separate identity checks.
No board acceptance exists until these artifacts are present and reviewed. A
successful bounded board test grants no portfolio or production authority.
