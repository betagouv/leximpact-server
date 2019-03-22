# -*- coding: utf-8 -*-


import pandas
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem
from openfisca_core import periods
from openfisca_france.model.base import Reform
#try:
#    data=pandas.read_pickle("./failingsampleerfs.pkl")
#except:





#reform is the modifier function

import time
def simpop_reform(reform = None,nomfichier=None,period='2014'):
    starttime=time.time()
    if nomfichier is None:
        nomfichier="UCT-0001.csv"
    if reform is None:
        tbs=FranceTaxBenefitSystem()
    else:
        class apply_reform(Reform):
            def apply(self):
                self.modify_parameters(modifier_function=reform)
        tbs=apply_reform(FranceTaxBenefitSystem())
    if nomfichier[-3:]==".h5":
        fread=pandas.read_hdf
    else:
        fread=pandas.read_csv
    try:
        data = fread("./{}".format(nomfichier))
    except:
        try:
            data = fread("./Simulation_engine/{}".format(nomfichier))
        except:
            data= fread("C:/EIG/Leximpact_git/Simulation_engine/{}".format(nomfichier))
    print("Elapsed time : {:.2f}".format(time.time() - starttime))

    #Traduction des roles attribués au format openfisca
    data["quimenof"]="enfant"
    data.loc[data["quifoy"] == 1, 'quimenof'] = "conjoint"
    data.loc[data["quifoy"] == 0, 'quimenof'] = "personne_de_reference"

    data["quifoyof"]="personne_a_charge"
    data.loc[data["quifoy"] == 1, 'quifoyof'] = "conjoint"
    data.loc[data["quifoy"] == 0, 'quifoyof'] = "declarant_principal"

    data["quifamof"]="enfant"
    data.loc[data["quifam"] == 1, 'quifamof'] = "conjoint"
    data.loc[data["quifam"] == 0, 'quifamof'] = "demandeur"


    #print(data.pivot_table(values="activite",index="quifoyof",columns="quifoy",aggfunc="count", fill_value=0, margins=True))

    sb = SimulationBuilder()
    sb.create_entities(tbs)

    sb.declare_person_entity('individu',data.index)

    #Creates openfisca entities and generates grouped

    listentities={"foy":"foyer_fiscal","men":"menage","fam":"famille"}
    instances={}
    dictionnaire_datagrouped={"individu":data}

    for ent,ofent in listentities.items():
        persons_ent=data["id"+ent].values
        persons_ent_roles=data["qui"+ent+"of"].values
        ent_ids=data["id"+ent].unique()
        instances[ofent]=sb.declare_entity(ofent,ent_ids)
        sb.join_with_persons(instances[ofent],persons_ent,roles=persons_ent_roles)
        #The following ssumes data defined for an entity are the same for all rows in the same entity
        #Or at least that the first non null value found for an entity will always be the total value for an entity
        # (Which is the case for f4ba). These checks are performed in the checkdata function defined belowx
        dictionnaire_datagrouped[ofent]=data.groupby("id"+ent,as_index=False).first().sort_values(by="id"+ent)


    #These variables should not be attributed to any OpenFisca Entity
    columns_not_OF_variables = set(["idmen","idfoy","idfam","noindiv","level_0","quifam","quifoy","quimen","wprm","index",
                                    "idmen_original","idfoy_original","idfam_original","quifamof","quifoyof","quimenof"])

    simulation= sb.build(tbs)
    #Attribution des variables à la bonne entité OpenFisca
    for colonne in data.columns:
        if colonne not in columns_not_OF_variables:
            try:
                simulation.set_input(colonne,period,dictionnaire_datagrouped[tbs.get_variable(colonne).entity.key][colonne])
                print("{} was attributed to {}".format(colonne,tbs.get_variable(colonne).entity.key))
            except:
                print("{} failed to be attributed to {}".format(colonne,tbs.get_variable(colonne).entity.key))
                raise
    print("Elapsed time : {:.2f}".format(time.time()-starttime))
    return simulation,dictionnaire_datagrouped

#Checks that all the data have the same value in columns (required for doing our first() groupby
def checkdata(nomfichier=None):
    import numpy as np
    if True:
        if nomfichier is None:
            nomfichier="openfisca_erfs_fpr_data_2014.h5"
        if nomfichier[-3:]==".h5":
            fread=pandas.read_hdf
        else:
            fread=pandas.read_csv
        try:
            data = fread("./{}".format(nomfichier))
        except:
            data = fread("./Simulation_engine/{}".format(nomfichier))
        columns_not_OF_variables = set(["idmen","idfoy","idfam","noindiv","level_0","quifam","quifoy","quimen","wprm","index",
                                        "idmen_original","idfoy_original","idfam_original","quifamof","quifoyof","quimenof"])
        dwat = {"foyer_fiscal":"idfoy","famille":"idfam","menage":"idmen"}
        for k in data.columns:
            if k not in columns_not_OF_variables:
                wh=FranceTaxBenefitSystem().get_variable(k).entity.key
                if wh !="individu":
                    lencples = len(np.unique(data[[k,dwat[wh]]].values))
                    lenormal= len(data[dwat[wh]].unique())
                    print("for : ",k,wh,lencples,lenormal)


def reform_from_bareme(mvt=15000):
    def TheReform(parameters):
        #if seuilsthreshold is None:
        # print(parameters.impot_revenu.bareme.brackets[1].threshold)
        myinstant = periods.instant("2014")
        print("bareme avant modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(myinstant))
        seuilsthreshold=(parameters.impot_revenu.bareme.get_at_instant(myinstant))
       # if mvt>=seuilsthreshold.thresholds[2]:
        #    print("on a cappé le seuil")
        #    mvt=min(seuilsthreshold.thresholds[2]-1,mvt)
        reform_period = periods.period("year:1900:200")  # Pour le moment mes réformes sont sur l'éternité
        for i in range(len(seuilsthreshold.rates)):
             parameters.impot_revenu.bareme.brackets[i].threshold.update(period=reform_period,
                                                                         value=seuilsthreshold.thresholds[i] if i!=1 else min(mvt,seuilsthreshold.thresholds[i+1]))
             parameters.impot_revenu.bareme.brackets[i].rate.update(period=reform_period, value=seuilsthreshold.rates[i])
        for i in range(len(seuilsthreshold.rates),15):
            try:
                 parameters.impot_revenu.bareme.brackets[i].threshold.update(period=reform_period,
                                                                             value=seuilsthreshold.thresholds[-1]+i)
                 parameters.impot_revenu.bareme.brackets[i].rate.update(period=reform_period, value=seuilsthreshold.rates[-1])
            except:
                pass
        # #plafonds sécu :
        # parameters.impot_revenu.plafond_qf.maries_ou_pacses.update(period=reform_period, value=1600)
        parameters.impot_revenu.bareme.brackets[1].threshold.update(period=reform_period,value=mvt)
        print("bareme après modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(myinstant))
        return parameters
    return TheReform

def CompareOldNew(Mavaleurtaux):
    period="2014"
    tablesims=[simpop_reform(),simpop_reform(reform_from_bareme(Mavaleurtaux))]
    res=[]
    for simulation,dictionnaire_datagrouped in tablesims:
        for nomvariable in ["irpp","nbptr"]:
            st = time.time()
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable] = simulation.calculate(nomvariable, period, max_nb_cycles=1)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"]=dictionnaire_datagrouped["foyer_fiscal"][nomvariable]*dictionnaire_datagrouped["foyer_fiscal"]["wprm"]
            print("{} sum : {}  mean : {}".format(nomvariable,dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"].sum(),dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"].sum()/dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()))
            print("Elapsed : {:.2f}".format(time.time()-st))
            if nomvariable=="irpp":
                res+=[-dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"].sum()/dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]
    print("Je suis CompareOldNew et j'ai été lancé avec un parametre de {} et oui j'ai fini {}".format(Mavaleurtaux,res))
    return res


