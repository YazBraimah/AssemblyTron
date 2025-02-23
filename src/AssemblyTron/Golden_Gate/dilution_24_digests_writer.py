'''A writer script that creates a Dilution Script in OpenTrons API for up to 24 primers and templates for the digested entry plasmid Golden Gate 

This script contains a protocol for diluting up to 24 primers and templates to concentrations specified in the AssemblyTron.Golden_Gate.Setup_digests_gradient module. 

This script generates a text file that runs on the OT-2 via the run app. It calls CSVs to make a customized protocol script. This script is designed to run on a personal computer on the command line.

'''

import pandas
import numpy as np
import os


    # paths = pandas.read_csv('/data/user_storage/robotpaths.csv')
    # paths
def write_dilution():



    def main():

        Input_values = pandas.read_csv('Input.csv') 
        Date = str(int(Input_values.loc[0].at['Date']))
        Date
        Time = str(int(Input_values.loc[0].at['Time']))
        Time
            #os.chdir('/Golden_Gate/'+Date+Time+'_GoldenGate')
        oligos = pandas.read_csv('oligo.csv')
        assembly = pandas.read_csv('assembly.csv')
        pcr = pandas.read_csv('pcr.csv')
        combinations = pandas.read_csv('combinations.csv')
        df = pandas.read_csv('templates.csv')
        digests = pandas.read_csv('digests.csv')
        section = pandas.read_csv('section.csv')

        f = open('GG_dilutions.py','w+')
        f.write(
            "from opentrons import protocol_api \r\n"
            "metadata = { \r\n"
            "    'protocolName': 'Golden Gate Primer and Template Dilutions', \r\n"
            "    'author': 'John Bryant <jbryant2@vt.edu>', \r\n"
            "    'description': 'Protocol for performing PCR reactions and Plasmid assembly', \r\n"
            "    'apiLevel': '2.10' \r\n"
            "    } \r\n"

            "def run(protocol: protocol_api.ProtocolContext): \r\n"

            "    tiprack1 = protocol.load_labware('opentrons_96_tiprack_300ul', '9') \r\n"
            "    tiprack3 = protocol.load_labware('opentrons_96_tiprack_20ul', '5') \r\n"
            "    watertuberack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical','1') \r\n"
            "    tuberack2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','2') \r\n"
            "    tc_mod = protocol.load_module('Thermocycler Module') \r\n"
            "    pcrplate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt') \r\n"
            "    temp_module = protocol.load_module('temperature module', 3) \r\n"
            "    cold_tuberack = temp_module.load_labware('opentrons_24_aluminumblock_nest_1.5ml_screwcap', label='Temperature-Controlled Tubes') \r\n"
            "    temp_module.set_temperature(4) \r\n"
            "    tc_mod.open_lid() \r\n"

            "    p300_pipette = protocol.load_instrument('p300_single_gen2','left',tip_racks=[tiprack1]) \r\n"
            "    p20_pipette = protocol.load_instrument('p20_single_gen2','right',tip_racks = [tiprack3]) \r\n"       
        )

        x = 'Dilution'
        if x in section['parts'].values:
            f.write(
                "    protocol.comment('Diluting templates: adding H2O') \r\n"
                "    p20_pipette.pick_up_tip() \r\n"
            )
            for i, row in df.iterrows():
                if df.loc[i].at['water to add'] > 20:
                    f.write(
                        "    p20_pipette.aspirate(volume = "+str(df.loc[i].at['water to add'])+", location = watertuberack['A1'], rate=1.0) \r\n"
                        "    p20_pipette.dispense("+str(df.loc[i].at['water to add'])+", tuberack2['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                    )
                if df.loc[i].at['water to add'] < 8:
                    f.write(
                        "    p20_pipette.aspirate(volume = "+str(3*(df.loc[i].at['water to add']))+", location = watertuberack['A1'], rate=1.0) \r\n"
                        "    p20_pipette.dispense("+str(3*(df.loc[i].at['water to add']))+", tuberack2['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                    )
            f.write(
                "    p20_pipette.drop_tip() \r\n"
            )
            # Unnecessary to dilute digest templates    
            # for i, row in digests.iterrows():
            #     f.write(
            #         "    p300_pipette.aspirate(volume = "+str(digests.loc[i].at['water to add'])+", location = watertuberack['A1'], rate=1.0) \r\n"
            #         "    p300_pipette.dispense("+str(digests.loc[i].at['water to add'])+", tuberack2['"+str(digests.loc[i].at['well'])+"'], rate=1.0) \r\n"
            #     )
            f.write(
                "    p300_pipette.pick_up_tip() \r\n"
            )
            for i, row in oligos.iterrows():
                f.write(
                    "    protocol.comment('Diluting primers: adding H2O for primer "+str(oligos.loc[i].at['Name'])+"') \r\n"
                    "    p300_pipette.aspirate("+str(oligos.loc[i].at['volume of diluted primer']-oligos.loc[i].at['volume of stock primer to add'])+", watertuberack['A1'], rate=1.0) \r\n"
                    "    p300_pipette.dispense("+str(oligos.loc[i].at['volume of diluted primer']-oligos.loc[i].at['volume of stock primer to add'])+", tuberack2['"+str(oligos.loc[i].at['well'])+"'], rate=1.0) \r\n"
                )
            f.write(
                "    p300_pipette.drop_tip() \r\n"
            )

            #add stock templates to dilution tubes
            for i, row in df.iterrows():
                f.write("    protocol.comment('Diluting templates: adding "+str(df.loc[i].at['Primary Template'])+" template') \r\n")
                if df.loc[i].at['water to add'] > 8:
                    f.write(
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(df.loc[i].at['amount of template to add'])+", cold_tuberack['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                        "    p20_pipette.dispense("+str(df.loc[i].at['amount of template to add'])+", tuberack2['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                        "    p20_pipette.mix(3,8,tuberack2['"+str(df.loc[i].at['template_well'])+"']) \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )
                if df.loc[i].at['water to add'] < 8:
                    f.write(
                        "    p20_pipette.pick_up_tip() \r\n"
                        "    p20_pipette.aspirate("+str(3*(df.loc[i].at['amount of template to add']))+", cold_tuberack['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                        "    p20_pipette.dispense("+str(3*(df.loc[i].at['amount of template to add']))+", tuberack2['"+str(df.loc[i].at['template_well'])+"'], rate=1.0) \r\n"
                        "    p20_pipette.mix(3,5,tuberack2['"+str(df.loc[i].at['template_well'])+"']) \r\n"
                        "    p20_pipette.drop_tip() \r\n"
                    )
            #add stock templates for digests:
            # for i, row in digests.iterrows():
            #     f.write(
            #         "    p20_pipette.pick_up_tip() \r\n"
            #         "    p20_pipette.aspirate("+str(digests.loc[i].at['amount of template to add'])+", cold_tuberack['"+str(digests.loc[i].at['well'])+"'], rate=1.0) \r\n"
            #         "    p20_pipette.dispense("+str(digests.loc[i].at['amount of template to add'])+", tuberack2['"+str(digests.loc[i].at['well'])+"'], rate=1.0) \r\n"
            #         "    p20_pipette.drop_tip() \r\n"
            #     )

            #add stock primers to dilution tube
            for i, row in oligos.iterrows():
                f.write(
                    "    protocol.comment('Diluting primers: adding stock primer "+str(oligos.loc[i].at['Name'])+"') \r\n"
                    "    p20_pipette.pick_up_tip() \r\n"
                    "    p20_pipette.aspirate("+str(oligos.loc[i].at['volume of stock primer to add'])+", cold_tuberack['"+str(oligos.loc[i].at['well'])+"'], rate=1.0) \r\n"
                    "    p20_pipette.dispense("+str(oligos.loc[i].at['volume of stock primer to add'])+", tuberack2['"+str(oligos.loc[i].at['well'])+"'], rate=1.0) \r\n"
                    "    p20_pipette.mix(5,20,tuberack2['"+str(oligos.loc[i].at['well'])+"']) \r\n"
                    "    p20_pipette.drop_tip() \r\n"
                )

            #mix contents with pipette tip (reps, max volume, location) for templates and primers
            # for i, row in df.iterrows():
            #     if df.loc[i].at['water to add'] > 8:
            #         f.write(
            #             "    p300_pipette.pick_up_tip() \r\n"
            #             "    p300_pipette.mix(3,"+str(df.loc[i].at['water to add'])+",tuberack2['"+str(df.loc[i].at['template_well'])+"']) \r\n"
            #             "    p300_pipette.drop_tip() \r\n"
            #         )
            #     if df.loc[i].at['water to add'] < 8:
            #         f.write(
            #             "    p300_pipette.pick_up_tip() \r\n"
            #             "    p300_pipette.mix(3,"+str(3*(df.loc[i].at['water to add']))+",tuberack2['"+str(df.loc[i].at['template_well'])+"']) \r\n"
            #             "    p300_pipette.drop_tip() \r\n"
            #         )
                    
            # for i, row in digests.iterrows():
            #     f.write(
            #         "    p300_pipette.pick_up_tip() \r\n"
            #         "    p300_pipette.mix(3,"+str(digests.loc[i].at['water to add'])+",tuberack2['"+str(digests.loc[i].at['well'])+"']) \r\n"
            #         "    p300_pipette.drop_tip() \r\n"
            #     )

            # for i, row in oligos.iterrows():
            #     f.write(
            #         "    p300_pipette.pick_up_tip() \r\n"
            #         "    p300_pipette.mix(3,"+str(oligos.loc[i].at['volume of diluted primer']-oligos.loc[i].at['volume of stock primer to add'])+",tuberack2['"+str(oligos.loc[i].at['well'])+"']) \r\n"
            #         "    p300_pipette.drop_tip() \r\n"
            #     )
            f.write(
                "    protocol.pause('Take all stock primers and templates out. Add Q5 MM to D6, NEBridge to D5, rCutsmart to D4, DpnI to D3, T4 buffer to D2') \r\n"
            )

        f.close()
        # if __name__== "__main__":
    main()
            
    # os.system("notepad.exe GG_dilutions.py")