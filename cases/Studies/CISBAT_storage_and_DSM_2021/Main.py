from cases.Studies.CISBAT_storage_and_DSM_2021.Script import simulation

DSM_proportion = [0, 0.2, 0.4, 0.6, 0.8, 1]
storage_sizing = [0, 0.2, 0.4, 0.6, 0.8, 1]

# simulation
for proportion in DSM_proportion:
    for sizing in storage_sizing:
        simulation(proportion, sizing)





