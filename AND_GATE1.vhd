----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 11/02/2018 02:15:22 PM
-- Design Name: 
-- Module Name: AND_GATE - Behavioral
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



-- button led AND
--entity AND_GATE is
--   Port ( button1 : in STD_LOGIC;
--           button2 : in STD_LOGIC;
--           led1 : out STD_LOGIC);
--end AND_GATE;
--
--architecture Behavioral of AND_GATE is
--
--begin
--    led1 <= button1 AND button2;
--end Behavioral;




-- signal led AND (coincidence)
entity AND_GATE is
   Port (  
           sigout1 : out STD_LOGIC;
           sigout2 : out STD_LOGIC;
           sigout3 : out STD_LOGIC;
           GCLK  : in STD_LOGIC;
           FMC_LA12_P: in STD_LOGIC;
           FMC_LA12_N: in STD_LOGIC;
           FMC_LA13_P: in STD_LOGIC;
           FMC_LA13_N: in STD_LOGIC;
           FMC_LA14_P: in STD_LOGIC;
           FMC_LA14_N: in STD_LOGIC;
           FMC_LA15_P: in STD_LOGIC;
           FMC_LA15_N: in STD_LOGIC;
           FMC_LA16_P: in STD_LOGIC;
           FMC_LA16_N: in STD_LOGIC;
           FMC_LA01_CC_P: in STD_LOGIC;
           FMC_LA01_CC_N: in STD_LOGIC;
           FMC_LA02_P: in STD_LOGIC;
           FMC_LA02_N: in STD_LOGIC;
           FMC_LA03_P: in STD_LOGIC;
           FMC_LA03_N: in STD_LOGIC;
           --IN_STRING is the port corresponding to the input string from OutputString
           IN_STRING: in STD_LOGIC;
           JC1_P : out STD_LOGIC;
           JC1_N : out STD_LOGIC;
           JC2_P : out STD_LOGIC;
           JC2_N : out STD_LOGIC;
           FMC_LA06_P : out STD_LOGIC;
           FMC_LA06_N : out STD_LOGIC;
           FMC_LA07_P : out STD_LOGIC;
           FMC_LA07_N : out STD_LOGIC;
           FMC_LA08_P : out STD_LOGIC;
           FMC_LA08_N : out STD_LOGIC;
           FMC_LA09_P : out STD_LOGIC;
           FMC_LA09_N : out STD_LOGIC;
           FMC_LA23_P: out STD_LOGIC;
           FMC_LA23_N: out STD_LOGIC;
           FMC_LA19_N: out STD_LOGIC;
           FMC_LA19_P: out STD_LOGIC;
           FMC_LA20_N: out STD_LOGIC;
           FMC_LA20_P: out STD_LOGIC;
           FMC_LA22_N: out STD_LOGIC;
           FMC_LA22_P: out STD_LOGIC;
           FMC_LA17_CC_P: out STD_LOGIC;
           FMC_LA18_CC_P: out STD_LOGIC;
           FMC_LA18_CC_N: out STD_LOGIC 
           );
end AND_GATE;




   architecture Behavioral of AND_GATE is
type bulk_data is array(17 downto 0) of STD_LOGIC;
type bulk_sync is array(17 downto 0) of STD_LOGIC;


signal count: integer:=1;
signal dac_num: integer:=1;
signal state: integer:=0;
signal clk: STD_LOGIC := '0';
signal dataout1: bulk_data;
signal dataout2: bulk_data;
signal dataout3: bulk_data;
signal dataout4: bulk_data;
signal dataout5: STD_LOGIC;
signal dataout6: bulk_data;
signal dataout7: bulk_data;
signal dataout8: bulk_data;
signal syncout: bulk_sync;
signal dis1_result: integer:=0;
signal nim_input1: STD_LOGIC :='0';
signal nim_input2: STD_LOGIC :='0';
signal nim_input3: STD_LOGIC :='0';
signal nim_input4: STD_LOGIC :='0';
signal nim_input5: STD_LOGIC :='0';
signal nim_input6: STD_LOGIC :='0';
signal nim_input7: STD_LOGIC :='0';
signal nim_input8: STD_LOGIC :='0';

signal test_output: STD_LOGIC :='0';
signal test_output_int: integer:=0;



--- 2-fold coincidence
signal unsync_two_fold: STD_LOGIC :='1';
signal two_fold: STD_LOGIC :='1';
signal old_two_fold: STD_LOGIC :='1';
signal two_fold_block: STD_LOGIC :='1';
signal two_fold_block_count: integer:=0;
signal two_fold_block_trigger: integer:=0;
signal two_fold_wait_count: integer:=0;

--- 3-fold coincidence
signal unsync_three_fold: STD_LOGIC :='1';
signal three_fold: STD_LOGIC :='1';
signal old_three_fold: STD_LOGIC :='1';
signal three_fold_block: STD_LOGIC :='1';
signal three_fold_block_count: integer:=0;
signal three_fold_block_trigger: integer:=0;
signal three_fold_wait_count: integer:=0;

--- T & M & (NOT B)
signal unsync_T_and_M: STD_LOGIC :='1';
signal T_and_M: STD_LOGIC :='1';
signal old_T_and_M: STD_LOGIC :='1';
signal T_and_M_block: STD_LOGIC :='1';
signal T_and_M_block_count: integer:=0;
signal T_and_M_block_trigger: integer:=0;
signal T_and_M_wait_count: integer:=0;

--- T & B & (NOT M)
signal unsync_T_and_B: STD_LOGIC := '1';
signal T_and_B: STD_LOGIC := '1';
signal old_T_and_B: STD_LOGIC :='1';
signal T_and_B_block: STD_LOGIC :='1';
signal T_and_B_block_count: integer:=0;
signal T_and_B_block_trigger: integer:=0;
signal T_and_B_wait_count: integer:=0;

begin

-- initialize unlatch value
FMC_LA23_P <= '1';
FMC_LA23_N <= '1';
FMC_LA19_N <= '1';
FMC_LA19_P <= '1';
FMC_LA20_N <= '1';
FMC_LA20_P <= '1';
FMC_LA22_N <= '1';
FMC_LA22_P <= '1';



-- DAC value assignment string
dataout1 <= ('0','0','0','0','0','0','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC A 
--dataout1 <= IN_STRING;
dataout2 <= ('0','0','0','0','0','1','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC B 
dataout3 <= ('0','0','0','0','1','0','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC C 
dataout4 <= ('0','0','0','0','1','1','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC D 
--dataout5 <= ('0','0','0','1','0','0','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC E
-- assign input string value to dataout5 which'll become threshold voltage
dataout5 <= IN_STRING; 
dataout6 <= ('0','0','0','1','0','1','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC F 
dataout7 <= ('0','0','0','1','1','0','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC G 
dataout8 <= ('0','0','0','1','1','1','0','1','0','1','1','1','1','1','0','0','0','0'); -- DAC H 

-- data out is the dac data string, th first 6 entries are setting bits, following 12 are data 
syncout <= ('0','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0');
-- sync out sinply controls sync (required for NIM+ t8 on documentation page 5 of 24)
-- the following proces is a clock divider which is set by changing count
    process (GCLK,clk) begin
        if (GCLK' event and GCLK = '1') then
            count <= count + 1;
        if(count = 500) then
            clk <= NOT clk;
            count <= 1;
        end if;
        end if;
        JC2_P <= clk;
        FMC_LA18_CC_P <= clk;
    end process;
-- the following process serialy outputs both dataout and syncout using previously defined aray and divided clock
dac_proc: process(clk)
        begin
        --sigout1 <= nim_input1;       
        sigout2 <= syncout(17 - state);
--  Assign DAC values
       if dac_num = 1 then
            FMC_LA17_CC_P <= dataout1(17 - state);
            --FMC_LA17_CC_P <= dataout1;
        end if;
       if dac_num = 2 then
        end if;
       if dac_num = 3 then
            FMC_LA17_CC_P <= dataout3(17 - state);
       end if;
       if dac_num = 4 then
            FMC_LA17_CC_P <= dataout4(17 - state);
       end if;
        if dac_num = 5 then
             --FMC_LA17_CC_P <= dataout5(17 - state);
             FMC_LA17_CC_P <= dataout5;
        end if;
        if dac_num = 6 then
              FMC_LA17_CC_P <= dataout6(17 - state);
        end if;
        if dac_num = 7 then
              FMC_LA17_CC_P <= dataout7(17 - state);
         end if;
         if dac_num = 8 then
               FMC_LA17_CC_P <= dataout8(17 - state);
         end if;
        
        FMC_LA18_CC_N <= syncout(17 - state);
         
        end process;
-- the following process cycles states for the serial output to continously loop
    process (clk)
        begin
            if clk' event and clk = '1' then
                if state < 17 then
                    state <= state + 1;
                end if;
            if state = 17 then
                state <= 0;
                dac_num <=dac_num + 1;
                if dac_num = 8 then
                    dac_num <= 1;
                end if;
            end if;
            end if;
            --FMC_LA17_CC_P <= sigout 1;
            --FMC_LA18_CC_N <= sigout 2;
                            
        end process;
--- AND/OR logic from input channel 1 & 2
--- Due to De Morgan's law, and Not is required on both input/output since they are inverted by NIM+ 
    process (GCLK)
       begin
             unsync_two_fold <= not ((not nim_input4) and (not nim_input5) );   --- This is unsync 2-fold
             unsync_three_fold <= not ((not nim_input4) and (not nim_input5)and (not nim_input6)); --- This is unsync 3-fold
             unsync_T_and_M <= not ((not nim_input4) and (not nim_input6) and nim_input5 );   --- This is T & M & (NOT B)
             unsync_T_and_B <= not ((not nim_input4) and (not nim_input5) and nim_input6 );   --- This is T & B & (NOT M)  
            
            
            if GCLK' event and GCLK = '1' then
                                 --------- 2-fold width block--------------------
                                 old_two_fold <= two_fold;
                                 --- This is sync 2-fold
                                 two_fold <= not ((not nim_input4) and (not nim_input5) );   
                                 -- trigger 
                                 if two_fold = '0' and two_fold /= old_two_fold and two_fold_wait_count = 0 then
                                    two_fold_block_trigger <= 1;
                                 end if;
                                 -- let the block start
                                 if two_fold_block_count = 0 and two_fold_block_trigger = 1 and two_fold_wait_count = 0 then
                                    two_fold_block_count <= two_fold_block_count + 1;
                                    two_fold_block <= '0';
                                 end if; 
                                 -- block continue
                                 if two_fold_block_count > 0 and two_fold_wait_count = 0 then
                                     two_fold_block_count <= two_fold_block_count + 1;
                                 end if;
                                 -- block down
                                 -- currently at 50ns for testing, 5*(10ns), GCLK speed at 10ns/period
                                  if two_fold_block_count > 5 and two_fold_wait_count = 0 then
                                      two_fold_block_count <= 0;
                                      two_fold_block <= '1';
                                      two_fold_block_trigger <= 0;
                                      two_fold_wait_count <= 1; 
                                  end if;
                                  if two_fold_wait_count > 0 then
                                        two_fold_wait_count <= two_fold_wait_count +1;
                                  end if;
                                  if two_fold_wait_count >1000000 then --- wait time: multiples of 10ns
                                        two_fold_wait_count <= 0;
                                  end if;
                         --------- 3-fold width block--------------------
                              old_three_fold <= three_fold;
                               --- This is sync 3-fold
                              three_fold <= not ((not nim_input4) and (not nim_input5)and (not nim_input6));  
                              -- trigger 
                              if three_fold = '0' and three_fold /= old_three_fold and three_fold_wait_count = 0 then
                                     three_fold_block_trigger <= 1;
                              end if;
                              -- let the block start
                              if three_fold_block_count = 0 and three_fold_block_trigger = 1 and three_fold_wait_count = 0 then
                                    three_fold_block_count <= three_fold_block_count + 1;
                                    three_fold_block <= '0';
                              end if; 
                              -- block continue
                              if three_fold_block_count > 0 and three_fold_wait_count = 0 then
                                    three_fold_block_count <= three_fold_block_count + 1;
                              end if;
                              -- block down
                              -- currently at 50ns for testing, 5*(10ns), GCLK speed at 10ns/period
                              if three_fold_block_count > 5 and three_fold_wait_count = 0 then
                                      three_fold_block_count <= 0;
                                      three_fold_block <= '1';
                                      three_fold_block_trigger <= 0;
                                      three_fold_wait_count <= 1; 
                              end if;
                              if three_fold_wait_count > 0 then
                                      three_fold_wait_count <= three_fold_wait_count +1;
                              end if;
                              if three_fold_wait_count >1000000 then --- wait time: multiples of 10ns
                                      three_fold_wait_count <= 0;
                              end if;
                         --------- T & M & (NOT B) width block--------------------
                              old_T_and_M <= T_and_M;
                              --- This is sync T & M & (NOT B)
                              T_and_M <= not ((not nim_input4) and (not nim_input6) and nim_input5 );  
                              -- trigger 
                              if T_and_M = '0' and T_and_M /= old_T_and_M and T_and_M_wait_count = 0 then
                                   T_and_M_block_trigger <= 1;
                              end if;
                              -- let the block start
                              if T_and_M_block_count = 0 and T_and_M_block_trigger = 1 and T_and_M_wait_count = 0 then
                                    T_and_M_block_count <= T_and_M_block_count + 1;
                               T_and_M_block <= '0';
                               end if; 
                               -- block continue
                               if T_and_M_block_count > 0 and T_and_M_wait_count = 0 then
                                      T_and_M_block_count <= T_and_M_block_count + 1;
                               end if;
                               -- block down
                               -- currently at 50ns for testing, 5*(10ns), GCLK speed at 10ns/period
                                if T_and_M_block_count > 5 and T_and_M_wait_count = 0 then
                                       T_and_M_block_count <= 0;
                                       T_and_M_block <= '1';
                                        T_and_M_block_trigger <= 0;
                                        T_and_M_wait_count <= 1; 
                                 end if;
                                 if T_and_M_wait_count > 0 then
                                        T_and_M_wait_count <= T_and_M_wait_count +1;
                                 end if;
                                 if T_and_M_wait_count >1000000 then --- wait time: multiples of 10ns
                                          T_and_M_wait_count <= 0;
                                 end if;
                        ---------  T & B & (NOT M) width block--------------------
                               old_T_and_B <= T_and_B;
                               --- This is sync T & B & (NOT M)
                               T_and_B <= not ((not nim_input4) and (not nim_input5) and nim_input6 );  
                               -- trigger 
                               if T_and_B = '0' and T_and_B /= old_T_and_B and T_and_B_wait_count = 0 then
                                      T_and_B_block_trigger <= 1;
                               end if;
                               -- let the block start
                               if T_and_B_block_count = 0 and T_and_B_block_trigger = 1 and T_and_B_wait_count = 0 then
                                        T_and_B_block_count <= T_and_B_block_count + 1;
                               T_and_B_block <= '0';
                               end if; 
                               -- block continue
                               if T_and_B_block_count > 0 and T_and_B_wait_count = 0 then
                                         T_and_B_block_count <= T_and_B_block_count + 1;
                               end if;
                               -- block down
                                -- currently at 50ns for testing, 5*(10ns), GCLK speed at 10ns/period
                                if T_and_B_block_count > 5 and T_and_B_wait_count = 0 then
                                        T_and_B_block_count <= 0;
                                        T_and_B_block <= '1';
                                        T_and_B_block_trigger <= 0;
                                        T_and_B_wait_count <= 1; 
                                 end if;
                                 if T_and_B_wait_count > 0 then
                                        T_and_B_wait_count <= T_and_B_wait_count +1;
                                 end if;
                                 if T_and_B_wait_count >1000000 then --- wait time: multiples of 10ns
                                        T_and_B_wait_count <= 0;
                                 end if;
             -----------------------------------------------            
             end if;                
             
             
    end process;
           
--  IBUFDS: input differential buffer
        IBUFDS_CHAN1: IBUFDS
            generic map (
                    DIFF_TERM =>TRUE, -- Differential Termination 
                    IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                    IOSTANDARD => "DEFAULT")
            port map (
              O => nim_input1,  -- Buffer output
              I => FMC_LA12_P,  -- Diff_p buffer input (connect directly to top-level port)
              IB => FMC_LA12_N -- Diff_n buffer input (connect directly to top-level port)
             );
        IBUFDS_CHAN2: IBUFDS
         generic map (
                 DIFF_TERM =>TRUE, -- Differential Termination 
                 IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                 IOSTANDARD => "DEFAULT")
         port map (
           O => nim_input2,  -- Buffer output
           I => FMC_LA13_P,  -- Diff_p buffer input (connect directly to top-level port)
           IB => FMC_LA13_N -- Diff_n buffer input (connect directly to top-level port)
          );
        IBUFDS_CHAN3: IBUFDS
          generic map (
                  DIFF_TERM =>TRUE, -- Differential Termination 
                  IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                  IOSTANDARD => "DEFAULT")
          port map (
            O => nim_input3,  -- Buffer output
            I => FMC_LA14_P,  -- Diff_p buffer input (connect directly to top-level port)
            IB => FMC_LA14_N -- Diff_n buffer input (connect directly to top-level port)
           );
        IBUFDS_CHAN4: IBUFDS
            generic map (
                DIFF_TERM =>TRUE, -- Differential Termination 
                IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                IOSTANDARD => "DEFAULT")
             port map (
                 O => nim_input4,  -- Buffer output
                 I => FMC_LA15_P,  -- Diff_p buffer input (connect directly to top-level port)
                 IB => FMC_LA15_N -- Diff_n buffer input (connect directly to top-level port)
                                  );
         IBUFDS_CHAN5: IBUFDS
             generic map (
                DIFF_TERM =>TRUE, -- Differential Termination 
                 IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                 IOSTANDARD => "DEFAULT")
              port map (
                  O => nim_input5,  -- Buffer output
                   I => FMC_LA16_P,  -- Diff_p buffer input (connect directly to top-level port)
                    IB => FMC_LA16_N -- Diff_n buffer input (connect directly to top-level port)  
                     );
         IBUFDS_CHAN6: IBUFDS
           generic map (
                 DIFF_TERM =>TRUE, -- Differential Termination 
                 IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                 IOSTANDARD => "DEFAULT")
            port map (
                 O => nim_input6,  -- Buffer output
                 I => FMC_LA01_CC_P,  -- Diff_p buffer input (connect directly to top-level port)
                 IB => FMC_LA01_CC_N -- Diff_n buffer input (connect directly to top-level port)
                 );
         IBUFDS_CHAN7: IBUFDS
           generic map (
                 DIFF_TERM =>TRUE, -- Differential Termination 
                 IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                 IOSTANDARD => "DEFAULT")
           port map (
                 O => nim_input7,  -- Buffer output
                 I => FMC_LA02_P,  -- Diff_p buffer input (connect directly to top-level port)
                 IB => FMC_LA02_N -- Diff_n buffer input (connect directly to top-level port)
                 );
         IBUFDS_CHAN8: IBUFDS
           generic map (
                 DIFF_TERM =>TRUE, -- Differential Termination 
                 IBUF_LOW_PWR => TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
                 IOSTANDARD => "DEFAULT")
            port map (
                  O => nim_input8,  -- Buffer output
                  I => FMC_LA03_P,  -- Diff_p buffer input (connect directly to top-level port)
                  IB => FMC_LA03_N -- Diff_n buffer input (connect directly to top-level port)
                  );
                  
    -- This code is for a test where test_output is output as alternating 1,0 booleans              
 --    process (clk)
 --       begin
   --         if clk' event and clk = '1' then
   --             if test_output_int /= 1 then
    --                test_output_int <= 1;
    --                test_output <= '1';
    --            end if;
    --            if test_output_int /= 0 then
    --                test_output_int <= 0;
    --                test_output <= '0';
    --            end if;
    --        end if;               
   --   end process;            
                  
-- this section determines what the output into the oscilloscope is
--            
--  OBUFDS: output differential buffer
         OBUFDS_CHAN1 : OBUFDS
             generic map (
             IOSTANDARD => "DEFAULT")
             port map (
             O => FMC_LA06_P, -- Diff_p output (connect directly to top-level port)
             OB => FMC_LA06_N, -- Diff_n output (connect directly to top-level port)
             I => IN_STRING
             -- Currently set to IN_STRING for testing but it should be set to two_fold_block
             --I => two_fold_block -- Buffer input
             );
         OBUFDS_CHAN2 : OBUFDS
             generic map (
             IOSTANDARD => "DEFAULT")
             port map (
             O => FMC_LA07_P, -- Diff_p output (connect directly to top-level port)
             OB => FMC_LA07_N, -- Diff_n output (connect directly to top-level port)
             I => IN_STRING
             -- Currently set to IN_STRING for testing but it should be set to three_fold_block
             --I => three_fold_block -- Buffer input
             );
         OBUFDS_CHAN3 : OBUFDS
             generic map (
             IOSTANDARD => "DEFAULT")
             port map (
             O => FMC_LA08_P, -- Diff_p output (connect directly to top-level port)
             OB => FMC_LA08_N, -- Diff_n output (connect directly to top-level port)
             I => IN_STRING
             --I => T_and_M_block -- Buffer input
             -- Currently set to IN_STRING for testing but it should be set to T_and_M_block
             );
         OBUFDS_CHAN4 : OBUFDS
             generic map (
             IOSTANDARD => "DEFAULT")
             port map (
             O => FMC_LA09_P, -- Diff_p output (connect directly to top-level port)
             OB => FMC_LA09_N, -- Diff_n output (connect directly to top-level port)
             I => IN_STRING
             --I => T_and_B_block -- Buffer input
             -- Currently set to IN_STRING for testing but it should be set to T_and_B_block
             );                     
end Behavioral;