// One asynchronous bit only. This is not a coherent multi-bit bus crossing.
module sync_debounce #(
    parameter integer STABLE_CYCLES = 500000
) (
    input wire clk,
    input wire async_in,
    output reg stable_out = 1'b0
);
    (* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) reg sync_meta = 1'b0;
    (* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) reg sync_value = 1'b0;
    localparam integer WIDTH = (STABLE_CYCLES < 2) ? 1 : $clog2(STABLE_CYCLES);
    reg [WIDTH-1:0] count = 0;
    always @(posedge clk) begin
        sync_meta <= async_in;
        sync_value <= sync_meta;
        if (sync_value == stable_out) count <= 0;
        else if (count == STABLE_CYCLES-1) begin
            stable_out <= sync_value;
            count <= 0;
        end else count <= count + 1'b1;
    end
endmodule
