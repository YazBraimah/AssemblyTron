''' A writer script for generating a Golden Gate Assembly Protocol Script with separate PCRs and digested entry plasmids in OpenTrons API.

This script allows users to perform Golden Gate assembly where fragments for each assembly are amplified in separate tubes and uses a gradient thermocycler or on deck thermocycler.

This script generates a text file that runs on the OT-2 via the run app. It calls CSVs to make a customized protocol script. This script is designed to run on a personal computer on the command line.

'''

import pandas
import numpy as np
import os
from os.path import exists


def write_pcr():

    def main():

        Input_values = pandas.read_csv('Input.csv') 
        # Input_values
        Date = str(int(Input_values.loc[0].at['Date']))
        Date
        Time = str(int(Input_values.loc[0].at['Time']))
        Time

        Q5 = (0.5*Input_values.loc[0].at['pcrvol'])
        diltemp = (Input_values.loc[0].at['templatengs'])*(Input_values.loc[0].at['pcrvol'])/1
        # DMSO = (0.03*Input_values.loc[0].at['pcrvol'])

        #os.chdir(Date+Time+'_GoldenGate')
        oligos = pandas.read_csv('oligo.csv')

        gradient = pandas.read_csv('gradient.csv')
        pcr = pandas.read_csv('pcr.csv')
        assembly = pandas.read_csv('assembly.csv')
        combinations = pandas.read_csv('combinations.csv')
        Length = pcr.nlargest(1,'Length')
        GG_dfs = pandas.read_csv('GG_dfs.csv')
        digests = pandas.read_csv('digests.csv')
        plasmid = pandas.read_csv('plasmid.csv')
        section = pandas.read_csv('section.csv')

        low_annealing_temp = pcr.nsmallest(1,'Mean Oligo Tm (3 only)').reset_index()
        high_annealing_temp = pcr.nlargest(1,'Mean Oligo Tm (3 only)').reset_index()

        delta = (float(high_annealing_temp.loc[0].at['Mean Oligo Tm (3 only)']) - float(low_annealing_temp.loc[0].at['Mean Oligo Tm (3 only)']))/34

                
        if exists('gg1.csv'):
            gg1 = pandas.read_csv('gg1.csv')
        if exists('gg2.csv'):
            gg2 = pandas.read_csv('gg2.csv')
        if exists('gg3.csv'):
            gg3 = pandas.read_csv('gg3.csv')
        if exists('gg4.csv'):
            gg4 = pandas.read_csv('gg4.csv')
        if exists('gg5.csv'):
            gg5 = pandas.read_csv('gg5.csv')
        if exists('gg6.csv'):
            gg6 = pandas.read_csv('gg6.csv')

        if '96well' in pcr.columns:
            pcr = pcr.rename(columns={"96well": "well", "96well2": "well2"})
            rackchanger = 'Y'
        else:
            rackchanger = 'N'

        f = open('GG_digests.py','w+')
        f.write(
            "from opentrons import protocol_api \r\n"
            "metadata = { \r\n"
            "    'protocolName': 'Golden Gate', \r\n"
            "    'author': 'John Bryant <jbryant2@vt.edu>', \r\n"
            "    'description': 'Protocol for performing Golden Gate assembly', \r\n"
            "    'apiLevel': '2.10' \r\n"
            "    } \r\n"
            "def run(protocol: protocol_api.ProtocolContext): \r\n"

            "    tiprack1 = protocol.load_labware('opentrons_96_tiprack_300ul', '9') \r\n"
            "    tiprack3 = protocol.load_labware('opentrons_96_tiprack_20ul', '5') \r\n"
            "    watertuberack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical','1') \r\n"
        )
        if rackchanger == 'Y':
            f.write("    tuberack2 = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul','2') \r\n")
        else:
            f.write("    tuberack2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','2') \r\n")
        f.write(
            "    secondarydils = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul','4') \r\n"
            "    tc_mod = protocol.load_module('thermocyclerModuleV2') \r\n"
            "    pcrplate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt') \r\n"
            "    temp_module = protocol.load_module('temperature module', 3) \r\n"
            "    cold_tuberack = temp_module.load_labware('opentrons_24_aluminumblock_nest_1.5ml_screwcap', label='Temperature-Controlled Tubes') \r\n"
            "    temp_module.set_temperature(4) \r\n"
            "    tc_mod.open_lid() \r\n"
            "    tc_mod.set_block_temperature(temperature=4) \r\n"

            "    p300_pipette = protocol.load_instrument('p300_single_gen2','left',tip_racks= [tiprack1]) \r\n"
            "    p20_pipette = protocol.load_instrument('p20_single_gen2','right',tip_racks = [tiprack3]) \r\n"
        )
        x = 'PCR Mix'
        if x in section['parts'].values:
            #add water first
            f.write(
                "    protocol.comment('Setting up PCR mixes') \r\n"
                "    p20_pipette.pick_up_tip() \r\n"
                )
            for j, row in pcr.iterrows():
                f.write(
                    "    p20_pipette.aspirate("+str(pcr.loc[j].at['total_water_toadd'])+", watertuberack['A1'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(pcr.loc[j].at['total_water_toadd'])+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
                )
            f.write(
                "    p20_pipette.blow_out() \r\n"
                "    p20_pipette.drop_tip() \r\n"
            )
            #add 1uL of BOTH (not each) primers
            for j, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding primer "+str(pcr.loc[j].at['Name'])+" to "+str(pcr.loc[j].at['Primary Template'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(pcr.loc[j].at['primervol_x'])+", tuberack2['"+str(pcr.loc[j].at['well'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(pcr.loc[j].at['primervol_x'])+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.mix(3,2,pcrplate['"+str(pcr.loc[j].at['tube'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"

                    "    protocol.comment('Adding primer "+str(pcr.loc[j].at['Name.1'])+" to "+str(pcr.loc[j].at['Primary Template'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(pcr.loc[j].at['primervol_y'])+", tuberack2['"+str(pcr.loc[j].at['well2'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(pcr.loc[j].at['primervol_y'])+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.mix(3,2,pcrplate['"+pcr.loc[j].at['tube']+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #add 1uL of each template
            for j, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding template "+str(pcr.loc[j].at['Primary Template'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(pcr.loc[j].at['amount of template to add'])+", tuberack2['"+str(pcr.loc[j].at['template_well'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(pcr.loc[j].at['amount of template to add'])+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.mix(3,3,pcrplate['"+str(pcr.loc[j].at['tube'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #Add DMSO
            # for j, row in pcr.iterrows():
            #     f.write(
            #         "    protocol.comment('Adding DMSO to "+str(pcr.loc[j].at['Primary Template'])+"') \r\n"
            #         "    p20_pipette.pick_up_tip() \r\n"
            #         "    p20_pipette.aspirate("+str(DMSO)+", cold_tuberack['D1'], rate=2.0) \r\n"
            #         "    p20_pipette.dispense("+str(DMSO)+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
            #         "    p20_pipette.blow_out() \r\n"
            #         "    p20_pipette.drop_tip() \r\n"
            #     )

            #add Q5 MM to each reaction
            for j, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding Q5 MM to "+str(pcr.loc[j].at['Primary Template'])+" PCR reaction') \r\n"
                    "    p20_pipette.transfer("+str(Q5)+", cold_tuberack['D6'], pcrplate['"+str(pcr.loc[j].at['tube'])+"'], new_tip=\"always\", blow_out=True, mix_after=(3, "+str(Q5+3)+")) \r\n"
                )

            # #add High-Fi polymerase to each reaction
            # for j, row in pcr.iterrows():
            #     f.write(
            #         "    p20_pipette.pick_up_tip() \r\n"
            #         "    p20_pipette.aspirate("+str(Q5)+", cold_tuberack['D6'], rate=2.0) \r\n"
            #         "    p20_pipette.dispense("+str(Q5)+", pcrplate['"+str(pcr.loc[j].at['tube'])+"'], rate=2.0) \r\n"
            #         "    p20_pipette.mix(3,"+str(Q5+3)+",pcrplate['"+str(pcr.loc[j].at['tube'])+"']) \r\n"
            #         "    p20_pipette.blow_out() \r\n"
            #         "    p20_pipette.drop_tip() \r\n"
            #     )
                
            # #mix up
            # for j, row in pcr.iterrows():
            #     f.write(
            #         "    p20_pipette.pick_up_tip() \r\n"
            #         "    p20_pipette.mix(3,"+str(Q5+3)+",pcrplate['"+str(pcr.loc[j].at['tube'])+"']) \r\n"
            #         "    p20_pipette.blow_out() \r\n"
            #         "    p20_pipette.drop_tip() \r\n"
            #     )
                
            if Input_values.loc[0].at['Combinatorial_pcr_params'] == 2:
                f.write(
                    "    protocol.comment('Starting gradient PCR reactions') \r\n"
                    "    tc_mod.deactivate() \r\n"
                    "    temp_module.deactivate() \r\n"
                    "    protocol.pause('move to gradient thermocycler. set gradiet to be between "+str(gradient.loc[0].at['temp'])+" and "+str(gradient.loc[7].at['temp'])+". Extension time should be "+str(float((Length['Length']/1000)*30))+" seconds. Follow normal parameters for everything else. A1 is cool, A8 is hot.') \r\n"
                    "    temp_module.set_temperature(4) \r\n"
                    "    tc_mod.set_block_temperature(4) \r\n"
                )
                
            if Input_values.loc[0].at['Combinatorial_pcr_params'] == 1:
                f.write(
                    "    protocol.comment('Starting touchdown PCR reactions') \r\n"
                    "    tc_mod.close_lid() \r\n"
                    "    tc_mod.set_lid_temperature(temperature = 105) \r\n"
                    "    tc_mod.set_block_temperature(98, hold_time_seconds=30, block_max_volume=25) \r\n"
                )
                    
                cycle = 1
                x = 0 
                while cycle < 35:

                    f.write(
                        "    tc_mod.set_block_temperature(98, hold_time_seconds=10, block_max_volume=25) \r\n"
                        "    tc_mod.set_block_temperature("+str(float(low_annealing_temp.loc[0].at['Mean Oligo Tm (3 only)'])+x)+", hold_time_seconds=30, block_max_volume=25) \r\n"
                        "    tc_mod.set_block_temperature(72, hold_time_seconds="+str(float((Length['Length'].iloc[0]/1000)*30))+", block_max_volume=25) \r\n"
                    ) 
                    cycle = cycle + 1
                    x = x + delta
                    print(cycle)
                    print(delta)

                f.write(
                    "    tc_mod.set_block_temperature(72, hold_time_minutes=5, block_max_volume=25) \r\n"
                    "    tc_mod.set_block_temperature(10) \r\n"
                    "    tc_mod.set_lid_temperature(temperature = 45) \r\n"
                    # "    protocol.pause('wait until ready to dispense assemblies') \r\n"
                    "    tc_mod.open_lid() \r\n"
                    # "    protocol.pause('just take them out manually...') \r\n"
                )            
                
        #######################################################################################################################################################
        x = 'DPNI Digest'
        if x in section['parts'].values:
                
            #water for digestion
            for i, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding H2O for DpnI digest of "+str(pcr.loc[i].at['Primary Template'])+" "+str(pcr.loc[i].at['tube'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(Input_values.loc[0].at['DPwater'])+", watertuberack['A1'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(Input_values.loc[0].at['DPwater'])+", pcrplate['"+str(pcr.loc[i].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #cutsmart for digestion
            for i, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding rCustsmart buffer for DpnI digest of "+str(pcr.loc[i].at['Primary Template'])+" "+str(pcr.loc[i].at['tube'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(Input_values.loc[0].at['cutsmart'])+", cold_tuberack['D4'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(Input_values.loc[0].at['cutsmart'])+", pcrplate['"+str(pcr.loc[i].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.mix(3,10,pcrplate['"+str(pcr.loc[i].at['tube'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #Add DpnI
            for i, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Adding DpnI for digest of "+str(pcr.loc[i].at['Primary Template'])+" "+str(pcr.loc[i].at['tube'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(Input_values.loc[0].at['DPNI'])+", cold_tuberack['D3'], rate=2.0) \r\n"
                    "    p20_pipette.dispense("+str(Input_values.loc[0].at['DPNI'])+", pcrplate['"+str(pcr.loc[i].at['tube'])+"'], rate=2.0) \r\n"
                    "    p20_pipette.mix(3,10,pcrplate['"+str(pcr.loc[i].at['tube'])+"']) \r\n"
                    # "    p20_pipette.mix(3,"+str(Q5+Input_values.loc[0].at['DPwater']+Input_values.loc[0].at['cutsmart'])+",pcrplate['"+str(pcr.loc[i].at['tube'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #mix up
            for i, row in pcr.iterrows():
                f.write(
                    "    protocol.comment('Mixing DpnI reaction of "+str(pcr.loc[j].at['Primary Template'])+" "+str(pcr.loc[j].at['tube'])+"') \r\n"
                    "    p300_pipette.pick_up_tip() \r\n"
                    "    p300_pipette.mix(3,"+str(Q5+Input_values.loc[0].at['DPwater']+Input_values.loc[0].at['cutsmart'])+",pcrplate['"+str(pcr.loc[i].at['tube'])+"']) \r\n"
                    "    p300_pipette.blow_out() \r\n"
                    "    p300_pipette.drop_tip() \r\n"
                )

            f.write(
                "    protocol.comment('Running DpnI digest') \r\n"
                "    tc_mod.close_lid() \r\n"
                "    tc_mod.set_lid_temperature(105) \r\n"
                "    tc_mod.set_block_temperature(37,0,30, block_max_volume = 50) \r\n"
                "    tc_mod.set_block_temperature(80,0,20, block_max_volume = 50) \r\n"
                "    tc_mod.set_block_temperature(4, block_max_volume = 50) \r\n"
                "    tc_mod.open_lid() \r\n"
                # "    temp_module.deactivate() \r\n"
                "    tiprack3.reset() \r\n"
                "    tiprack3 = protocol.load_labware('opentrons_96_tiprack_20ul', '6') \r\n"
                "    protocol.pause('REFILL TIP RACKS, and wait until its time to dispense the product') \r\n"
                "    temp_module.set_temperature(4) \r\n"
            )

        ##############################################################################################################################################################################
        #Dilutions for entry vectors

            #water
            for i, row in plasmid.iterrows():
                if plasmid.loc[i].at['Concentration'] > 1:
                    f.write(
                        "    protocol.comment('Diluting entry vector "+str(digests.loc[i].at['Sequence Source'])+": adding water') \r\n"
                        "    p300_pipette.pick_up_tip() \r\n"
                        "    p300_pipette.aspirate("+str(plasmid.loc[i].at['Volume of Water'])+",watertuberack['A1'],2) \r\n"
                        "    p300_pipette.dispense("+str(plasmid.loc[i].at['Volume of Water'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"'],2) \r\n"
                        "    p300_pipette.drop_tip() \r\n"
                    )

            #plasmid
            for i, row in plasmid.iterrows():
                if plasmid.loc[i].at['Volume of Plasmid'] < 20:
                    f.write(
                        "    protocol.comment('Diluting entry vector "+str(digests.loc[i].at['Sequence Source'])+": adding plasmid') \r\n"
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(plasmid.loc[i].at['Volume of Plasmid'])+",tuberack2['"+str(plasmid.loc[i].at['Plasmid Location'])+"'],2) \r\n"
                        "    p20_pipette.dispense("+str(plasmid.loc[i].at['Volume of Plasmid'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"'],2) \r\n"
                        "    p20_pipette.mix(3,"+str(plasmid.loc[i].at['Volume of Plasmid'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )

                if plasmid.loc[i].at['Volume of Plasmid'] in range(20, 100):
                    f.write(
                        "    protocol.comment('Diluting entry vector "+str(digests.loc[i].at['Sequence Source'])+": adding plasmid') \r\n"
                        "    p300_pipette.pick_up_tip() \r\n"
                        "    p300_pipette.aspirate("+str(plasmid.loc[i].at['Volume of Plasmid'])+",tuberack2['"+str(plasmid.loc[i].at['Plasmid Location'])+"'],2) \r\n"
                        "    p300_pipette.dispense("+str(plasmid.loc[i].at['Volume of Plasmid'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"'],2) \r\n"
                        "    p300_pipette.mix(3,"+str(plasmid.loc[i].at['Volume of Plasmid'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                        "    p300_pipette.drop_tip() \r\n"
                    )

                # #Cutsmart Buffer
                # for i, row in plasmid.iterrows():
                #     if plasmid.loc[i].at['Concentration'] > 1:
                #         f.write(
                #             "    p300_pipette.pick_up_tip() \r\n"
                #             "    p300_pipette.aspirate("+str(plasmid.loc[i].at['Buffer'])+",cold_tuberack['D4'],2) \r\n"
                #             "    p300_pipette.dispense("+str(plasmid.loc[i].at['Buffer'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"'],2) \r\n"
                #             "    p300_pipette.mix(3,"+str(plasmid.loc[i].at['Buffer'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                #             "    p300_pipette.drop_tip() \r\n"
                #         )

                # #Add BsaI
                # for i, row in plasmid.iterrows():
                #     if plasmid.loc[i].at['Concentration'] > 1:
                #         f.write(
                #             "    p300_pipette.pick_up_tip() \r\n"
                #             "    p300_pipette.aspirate("+str(plasmid.loc[i].at['BSA1'])+",cold_tuberack['D5'],2) \r\n"
                #             "    p300_pipette.dispense("+str(plasmid.loc[i].at['BSA1'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"'],2) \r\n"
                #             "    p300_pipette.mix(3,"+str(plasmid.loc[i].at['BSA1'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                #             "    p300_pipette.drop_tip() \r\n"
                #         )

            #mix
            for i, row in plasmid.iterrows():
                if plasmid.loc[i].at['Concentration'] > 1:
                    if plasmid.loc[i].at['total volume'] > float('20'):
                        f.write(
                            "    protocol.comment('Diluting entry vector "+str(digests.loc[i].at['Sequence Source'])+": mixing') \r\n"
                            "    p300_pipette.pick_up_tip() \r\n"
                            "    p300_pipette.mix(3,"+str(plasmid.loc[i].at['total volume'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                            "    p300_pipette.drop_tip() \r\n"
                        )
                    else:
                        f.write(
                            "    protocol.comment('Diluting entry vector "+str(digests.loc[i].at['Sequence Source'])+": mixing') \r\n"
                            "    p20_pipette.pick_up_tip() \r\n"
                            "    p20_pipette.mix(3,"+str(plasmid.loc[i].at['total volume'])+",pcrplate['"+str(digests.loc[i].at['frag_pcr_tube'])+"']) \r\n"
                            "    p20_pipette.drop_tip() \r\n"
                        )



        ###############################################################################################################################################################
        #Golden Gate Setup
        x = 'Golden Gate Setup'
        if x in section['parts'].values:
            # f.write(
            #     "    p300_pipette.flow_rate.aspirate = 50 \r\n"
            #     "    p20_pipette.flow_rate.aspirate = 50 \r\n"
            #     "    p20_pipette.pick_up_tip() \r\n"
            #     "    p20_pipette.aspirate(30,cold_tuberack['D2']) \r\n"
            #     "    p20_pipette.dispense(30,cold_tuberack['C4']) \r\n"
            #     "    p20_pipette.blow_out() \r\n"
            #     "    p20_pipette.drop_tip() \r\n"
            #     "    p300_pipette.flow_rate.aspirate = 10 \r\n"
            #     "    p300_pipette.pick_up_tip() \r\n"
            #     "    p300_pipette.aspirate(3,cold_tuberack['C6']) \r\n"
            #     "    p300_pipette.dispense(3,cold_tuberack['C4']) \r\n"
            #     "    p300_pipette.mix(3,10,cold_tuberack['C4']) \r\n"
            #     "    p300_pipette.flow_rate.aspirate = 50 \r\n"
            #     "    p300_pipette.drop_tip() \r\n"
            # )
            ####@@@@@@@@@@@
            
            ####@@@@@@@@@@@
            processed_fragments = set()

            for i, row in GG_dfs.iterrows():
                x = GG_dfs.loc[i].at['gg#']
                for i, row in locals()[x].iterrows():
                    frag_loc = locals()[x].loc[i].at['frag_loc']

                    if frag_loc in processed_fragments:
                        continue  # Skip if this fragment has already been processed

                    processed_fragments.add(frag_loc)  # Mark this fragment as processed

                    if locals()[x].loc[i].at['initial required amount'] <1:
                        #adding h20
                        f.write("    protocol.comment('Diluting Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding H2O') \r\n")
                        if locals()[x].loc[i].at['H20 to add to 1uL of fragment'] > 20:
                            f.write(
                                "    p300_pipette.pick_up_tip() \r\n"
                                "    p300_pipette.aspirate("+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+", watertuberack['A1']) \r\n"
                                "    p300_pipette.dispense("+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+", secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.drop_tip() \r\n"
                            )
                        if 8 < locals()[x].loc[i].at['H20 to add to 1uL of fragment'] < 20:
                            f.write(
                                "    p300_pipette.pick_up_tip() \r\n"
                                "    p300_pipette.aspirate("+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+", watertuberack['A1']) \r\n"
                                "    p300_pipette.dispense("+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+", secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.drop_tip() \r\n"
                            )
                        if 3< locals()[x].loc[i].at['H20 to add to 1uL of fragment'] < 8:
                            f.write(
                                "    p300_pipette.pick_up_tip() \r\n"
                                "    p300_pipette.aspirate("+str(4*(locals()[x].loc[i].at['H20 to add to 1uL of fragment']))+", watertuberack['A1']) \r\n"
                                "    p300_pipette.dispense("+str(4*(locals()[x].loc[i].at['H20 to add to 1uL of fragment']))+", secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.drop_tip() \r\n"
                            )
                        if locals()[x].loc[i].at['H20 to add to 1uL of fragment'] < 3:
                            f.write(
                                "    p20_pipette.pick_up_tip() \r\n"
                                "    p20_pipette.aspirate("+str(6*(locals()[x].loc[i].at['H20 to add to 1uL of fragment']))+", watertuberack['A1']) \r\n"
                                "    p20_pipette.dispense("+str(6*(locals()[x].loc[i].at['H20 to add to 1uL of fragment']))+", secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.drop_tip() \r\n"
                            )
                        
                        #add template
                        f.write("    protocol.comment('Diluting Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding template') \r\n")
                        if locals()[x].loc[i].at['H20 to add to 1uL of fragment'] > 20:
                            f.write(
                                "    p300_pipette.pick_up_tip() \r\n"
                                "    p300_pipette.aspirate(1, pcrplate['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.dispense(1, secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.mix(3,"+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+",secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p300_pipette.drop_tip() \r\n"
                            )
                        if 5< locals()[x].loc[i].at['H20 to add to 1uL of fragment'] < 20:
                            f.write(
                                "    p20_pipette.pick_up_tip() \r\n"
                                "    p20_pipette.aspirate(4, pcrplate['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.dispense(4, secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.mix(3,"+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+",secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.drop_tip() \r\n"
                            )
                        if locals()[x].loc[i].at['H20 to add to 1uL of fragment'] < 5:
                            f.write(
                                "    p20_pipette.pick_up_tip() \r\n"
                                "    p20_pipette.aspirate(6, pcrplate['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.dispense(6, secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.mix(3,"+str(locals()[x].loc[i].at['H20 to add to 1uL of fragment'])+",secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                                "    p20_pipette.drop_tip() \r\n"
                            )

                    else:
                        f.write(
                            "    protocol.comment('Diluting Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding template') \r\n"
                            "    p20_pipette.pick_up_tip() \r\n"
                            "    p20_pipette.aspirate(20, pcrplate['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                            "    p20_pipette.dispense(20, secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                            "    p20_pipette.blow_out() \r\n"
                            "    p20_pipette.drop_tip() \r\n"
                        )

            f.write(
                "    protocol.pause('Clear off PCR plate and set up final Golden Gate assembly Tubes') \r\n"
            )

            for i, row in GG_dfs.iterrows():
                x = GG_dfs.loc[i].at['gg#']
                for i, row in locals()[x].iterrows():
                    f.write(

                        #templates
                        "    protocol.comment('Combining Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding template from "+str(locals()[x].loc[i].at['frag_loc'])+"') \r\n"
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(locals()[x].loc[i].at['final amount to add'])+", secondarydils['"+str(locals()[x].loc[i].at['frag_loc'])+"']) \r\n"
                        "    p20_pipette.dispense("+str(locals()[x].loc[i].at['final amount to add'])+", pcrplate['"+str(locals()[x].loc[i].at['location_of_assembly'])+"']) \r\n"
                        # "    p20_pipette.blow_out() \r\n"
                        "    p20_pipette.drop_tip() \r\n"

                    )
                        
                        
                        
                        
                if Input_values.loc[0].at['paqCI'] == 1:
                    f.write(
                    #water
                        "    protocol.comment('Combining Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding H2O') \r\n"
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(15 - round(locals()[x]['final amount to add'].sum(),2) - 1 - 1 - 1)+", watertuberack['A1']) \r\n" #accounts for activator
                        "    p20_pipette.dispense("+str(15 - round(locals()[x]['final amount to add'].sum(),2) - 1 - 1 - 1)+", pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                        "    p20_pipette.blow_out() \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )
                    
                    
                if Input_values.loc[0].at['paqCI'] == 2:
                    f.write(
                    #water
                        "    protocol.comment('Combining Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding H2O') \r\n"
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(15 - round(locals()[x]['final amount to add'].sum(),2) - 1 -1  - 1 - 2)+", watertuberack['A1']) \r\n" #accounts for activator
                        "    p20_pipette.dispense("+str(15 - round(locals()[x]['final amount to add'].sum(),2) - 1 -1- 1 - 2)+", pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                        "    p20_pipette.blow_out() \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )
                        
                f.write(

                    # T4 buffer
                    "    protocol.comment('Combining Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding T4 buffer') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate(2,cold_tuberack['D2']) \r\n"
                    "    p20_pipette.dispense(2,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    "    p20_pipette.mix(3,8,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"

                    # NEBridge BsaI
                    "    protocol.comment('Combining Golden Gate components "+str(locals()[x].loc[i].at['location_of_assembly'])+": Adding NEBridge enzyme') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate(1,cold_tuberack['D5']) \r\n"
                    "    p20_pipette.dispense(1,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    "    p20_pipette.mix(3,9,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )
                    
                if Input_values.loc[0].at['paqCI'] == 2:
                    f.write(
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate(1,cold_tuberack['D1']) \r\n"
                        "    p20_pipette.dispense(1,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                        "    p20_pipette.mix(3,9,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )

                f.write(
                    # #T4 ligase
                    # "    p300_pipette.pick_up_tip() \r\n"
                    # "    p300_pipette.aspirate(1,cold_tuberack['C5']) \r\n"
                    # "    p300_pipette.dispense(1,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    # "    p300_pipette.mix(3,9,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    # "    p300_pipette.drop_tip() \r\n"

                    #one more mix
                    "    protocol.comment('Mixing Golden Gate components in "+str(locals()[x].loc[i].at['location_of_assembly'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.mix(3,18,pcrplate['"+str(locals()[x].loc[0].at['location_of_assembly'])+"']) \r\n"
                    "    p20_pipette.blow_out() \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )
            
        x = 'Golden Gate Run'
        if x in section['parts'].values:
            f.write(
                "    protocol.comment('Running Golden Gate reaction') \r\n"
                "    tc_mod.close_lid() \r\n"
                "    tc_mod.set_lid_temperature(temperature = 105) \r\n"
                "    profile = [ \r\n"
                "        {'temperature': 37, 'hold_time_seconds': 180}, \r\n"
                "        {'temperature': 16, 'hold_time_seconds': 240}] \r\n"
                "    tc_mod.execute_profile(steps=profile, repetitions=25, block_max_volume=15) \r\n"
                "    tc_mod.set_block_temperature(50, hold_time_minutes=5, block_max_volume=15) \r\n"
                "    tc_mod.set_block_temperature(80, hold_time_minutes=5, block_max_volume=15) \r\n"
                "    tc_mod.set_block_temperature(10) \r\n"
                # "    protocol.pause('wait until ready to dispense assemblies') \r\n"
                "    tc_mod.open_lid() \r\n"
                "    protocol.comment('All done!') \r\n"
            )

        f.close()   
                
    # if __name__== "__main__":
    main()
            
    # os.system("notepad.exe GG_digests.py")    