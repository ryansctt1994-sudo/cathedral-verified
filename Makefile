.PHONY: test test-hw test-chronicle

test: test-chronicle test-hw
	@echo "ALL TEST COMMANDS PASSED."

test-chronicle:
	@cd chronicle && python3 -m pytest -q test_chronicle.py

test-hw:
	@cd hardware/lucifer_latch && iverilog -g2012 -o sim_latch lucifer_latch.v tb_lucifer_latch.v && vvp sim_latch
