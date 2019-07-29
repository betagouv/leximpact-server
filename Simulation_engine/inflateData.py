
import pandas as pd  # type: ignore
import numpy as np

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


def noise(inputfile, outputfile=None): #add gaussian noise
    if outputfile is None:
        outputfile = inputfile
    df = pd.read_hdf(inputfile)
    columns = df.columns
    print(columns)
    print(df)
    # list of variables to gaussiannoise
    to_noise = [
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
    sigma = 0.02

    for var_noised in to_noise:
        print("noising {}".format(var_noised))
        noise = np.random.normal(mu, sigma, [2,2]) 
        sig=df[var_noised]
        noise=np.random.lognormal(-sigma*sigma/2,sigma,[len(df)])
        adjed=sig*noise
        print(sum(sig),sum(noise)/len(noise),sum(adjed))
        df[var_noised]=adjed
    df.to_hdf(outputfile, key="input")


if __name__ == "__main__":
    inflate("dummy_data.h5", "dummy_data_inflated.h5")
    noise("dummy_data_inflated.h5", "dummy_data_inflated_noised.h5")
