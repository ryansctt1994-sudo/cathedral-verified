.PHONY: test test-bootstrap test-hw test-chronicle test-integration

test: test-bootstrap test-chronicle test-integration test-hw
	@echo "ALL DISCLOSED CHECKS PASSED."

test-bootstrap:
	@PYTHONPATH=src:. python3 -m unittest tests.test_bootstrap -v

test-chronicle:
	@cd chronicle && python3 test_chronicle.py

test-integration:
	@PYTHONPATH=src:. python3 -m unittest discover -s tests -v

test-hw:
	@cd hardware/lucifer_latch && iverilog -g2012 -o sim_latch lucifer_latch.v tb_lucifer_latch.v && vvp sim_latch
