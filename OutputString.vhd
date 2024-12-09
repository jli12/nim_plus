----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 11/18/2019 06:09:49 PM
-- Design Name: 
-- Module Name: OutputString - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
Library UNISIM;
use UNISIM.vcomponents.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity OutputString is
 --Port ( FMC_LA06_P: out STD_LOGIC_VECTOR (17 DOWNTO 0) );
 --Every item listed below will show up as either an input pin or an output pin
 -- on any block diagram created using this piece of code
 Port ( 
        GCLK: in STD_LOGIC;
        outstring: out STD_LOGIC
         );
end OutputString;

architecture Behavioral of OutputString is


--signals operate kind of like local variables
--signal outputBit: STD_LOGIC :='0';
signal outputString: STD_LOGIC_VECTOR (17 DOWNTO 0);
signal state: integer:=0;
signal clk: STD_LOGIC := '0';
signal count: integer:=1;
signal delay: integer:=0;



begin
--FMC_LA06_P <= ('0','0','0','0','0','0','0','1','0','1','1','1','1','1','0','0','0','0');
--FMC_LA06_P <= outputBit;
outstring <= '1';
--outputString <= ('0','0','0','0','0','0','0','0','1','1','1','1','1','1','0','0','0','0'); channel 1
outputString <= ('0','0','0','1','0','0','0','1','0','1','1','1','1','1','0','0','0','0');

--process (GCLK,clk) begin
    --if (GCLK' event and GCLK = '1') then
        --count <= count + 1;
    --if(count = 501) then
        --clk <= NOT clk;
        --count <= 1;
    --end if;
    --end if;
--end process;

process (GCLK,clk) begin
    if (GCLK' event and GCLK = '1') then
        count <= count + 1;
    if(delay = 0) then
        if(count = 251) then
            clk <= NOT clk;
            count <= 1;
            delay <= 1;
        end if;
    end if;
    if(delay = 1) then
        if(count = 501) then
            clk <= NOT clk;
            count <= 1;
        end if;
    end if;
    end if;
end process;


--this process constantly updates outstring with one of the values of outputString
process(clk)
        begin
        --sigout1 <= nim_input1;       
        outstring <= outputString(17 - state);
end process;
       
       
-- this process uses a local clock to iterate through the elements of outputString by modifying the the index "state"
process (clk)
    begin
        if clk' event and clk = '1' then
            if state < 17 then
                state <= state + 1;
            end if;
        if state = 17 then
            state <= 0;
            end if;
        end if;        
end process;

--  OBUFDS: output differential buffer
--OBUFDS_CHAN1 : OBUFDS
--generic map (
-- IOSTANDARD => "DEFAULT")
-- port map (
--  O => FMC_LA06_P, -- Diff_p output (connect directly to top-level port)
-- OB => FMC_LA06_N, -- Diff_n output (connect directly to top-level port)
--  I => outputBit -- Buffer input
-- );
             
end Behavioral;