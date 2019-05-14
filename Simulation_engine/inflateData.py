import pandas as pd


def inflate(inputfile, outputfile=None):
    if outputfile is None:
        outputfile = inputfile
    df = pd.read_hdf(inputfile)
    columns = df.columns
    print(columns)
    print(df)
    startp = 2014
    endp = 2018
    rateinfla = 0.016
    # list of variables to inflate
    to_inflate = [
        "chomage_brut",
        "pensions_alimentaires_percues",
        "rag",
        "ric",
        "rnc",
        "salaire_de_base",
        "f4ba",
        "loyer",
        "taxe_habitation",
    ]
    final = df.copy()
    adjrate = pow(1 + rateinfla, endp - startp)
    for vartoinflate in to_inflate:
        final[vartoinflate] = final[vartoinflate] * adjrate
    InflaFF = 1.03181
    # augmentation du nombre de FF de 2012 à 2016.
    final["wprm"] = final["wprm"] * InflaFF
    final.to_hdf(outputfile, key="input")


if __name__ == "__main__":
    inflate("dummy_data.h5", "dummy_data_inflated.h5")
