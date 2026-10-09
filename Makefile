.PHONY: test test-hw test-chronicle test-chronicle-hardening

test: test-chronicle test-chronicle-hardening test-hw
	@echo "ALL VERIFIED."

test-chronicle:
	cd chronicle && python3 test_chronicle.py

test-chronicle-hardening:
	cd chronicle && python3 -m unittest -v test_chronicle_hardening

test-hw:
	cd hardware/lucifer_latch && iverilog -g2012 -o sim_latch lucifer_latch.v tb_lucifer_latch.v && vvp sim_latch
