`timescale 1ns/1ps
module tb_startup_reset;
reg clk=0;
always #5 clk=~clk;
reg reset_button=1;
wire permit,tripped,ready;
lucifer_arty_a7 dut(.clk(clk),.reset_button(reset_button),.trigger_async(1'b0),.run_permit(permit),.tripped_led(tripped),.ready_led(ready));
initial begin
 #1000;
 $display("time_ns=%0t raw_reset=%b permit=%b qualified_reset=%b", $time,reset_button,permit,dut.reset_pressed);
 if (permit !== 1'b0) begin
  $display("OBSERVED_FAILURE: startup with held physical reset permits before debounce qualification");
  $finish_and_return(1);
 end
 $finish;
end
endmodule
