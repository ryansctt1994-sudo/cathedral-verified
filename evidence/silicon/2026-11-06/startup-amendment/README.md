# Startup-reset finding and amendment — 2026-11-06

The prior source permitted the bench output before initial reset qualification.
`startup-reset.log` records the first held-reset diagnostic at 1000 ns;
`initial-diagnostic.v` is its source. `original-regression.log` is the same new
full startup regression run against original commit `49fc0fd`, failing at cycle 32.
The new full regression source is committed in `arty_a7/tb_startup_reset.v`.

The revised filter qualifies its initial stable input, and the wrapper requires
that qualification before releasing reset/permit. `revised-rtl.log` preserves all
local suite outputs; `revised-synthesis.log` and `revised-netlist.v` preserve
successful xc7 mapping. `receipt.json` pins source and evidence bytes.

These are same-author digital observations, not board measurements. No Vivado
routing, programming, video or independent timing/reproduction occurred. The old
Rekor checkpoint still describes the old source; a new actual-build checkpoint is
required before physical qualification. Hardware E3.1 remains NOT_READY.
