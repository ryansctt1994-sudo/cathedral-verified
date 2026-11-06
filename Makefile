.PHONY: test test-hw test-chronicle test-board

test: test-chronicle test-hw
	@echo "LOCAL SUITES COMPLETED; silicon and external authority not assessed."

test-chronicle:
	@cd chronicle && python3 test_chronicle.py

test-hw:
	@cd hardware/lucifer_latch && iverilog -g2012 -o sim_latch lucifer_latch.v tb_lucifer_latch.v && vvp sim_latch

test-board:
	@cd hardware/lucifer_latch && iverilog -g2012 -s tb_startup_reset -o sim_startup lucifer_latch.v arty_a7/sync_debounce.v arty_a7/lucifer_arty_a7.v arty_a7/tb_startup_reset.v && vvp sim_startup
	@cd hardware/lucifer_latch && iverilog -g2012 -s tb_arty_a7 -o sim_board lucifer_latch.v arty_a7/sync_debounce.v arty_a7/lucifer_arty_a7.v arty_a7/tb_arty_a7.v && vvp sim_board
	@cd hardware/lucifer_latch && iverilog -g2012 -s tb_debounce_default -o sim_debounce arty_a7/sync_debounce.v arty_a7/tb_debounce_default.v && vvp sim_debounce
