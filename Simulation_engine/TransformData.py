from inflateData import inflate, noise
from agg_pop import ajustement_h5, test_useless_variables


if __name__ == "__main__":
    # print(test_useless_variables("dummy_data.h5", "dummy_data_step1.h5"))
    inflate("dummy_data_step1.h5", "dummy_data_step2.h5")
    noise("dummy_data_step2.h5", "dummy_data_step3.h5")
    ajustement_h5(
        input_h5="dummy_data_step3.h5",
        output_h5="dummy_data_final.h5",
        distribution_rfr_population="./Simulation_Engine/Calib/ResFinalCalibSenat.csv",
    )
