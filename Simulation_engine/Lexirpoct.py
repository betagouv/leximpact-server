# -*- coding: utf-8 -*-


import pandas
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

#try:
#    data=pandas.read_pickle("./failingsampleerfs.pkl")
#except:

data = pandas.read_hdf("./openfisca_erfs_fpr_data_2014.h5")


persons_ids = data.index

persons_feufiscal = data["idfoy"].values
persons_menage = data["idmen"].values
persons_famille = data["idfam"].values

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

persons_feufiscal_roles = data["quifoyof"].values
persons_menages_roles = data["quimenof"].values
persons_familles_roles = data["quifamof"].values

tbs = FranceTaxBenefitSystem()
sb = SimulationBuilder()
sb.create_entities(tbs)


feufiscal_ids = data["idfoy"].unique()
menages_ids = data["idmen"].unique()
familles_ids= data["idfam"].unique()

sb.declare_person_entity('individu', persons_ids)
feufiscal_instance = sb.declare_entity('foyer_fiscal', feufiscal_ids)
menages_instance = sb.declare_entity('menage', menages_ids)
familles_instance = sb.declare_entity('famille', familles_ids)

# Join csv data on persons (roles are optional):
sb.join_with_persons(feufiscal_instance, persons_feufiscal, roles = persons_feufiscal_roles)

print(feufiscal_instance.members_entity_id)



sb.join_with_persons(menages_instance, persons_menage,roles=persons_menages_roles)#
sb.join_with_persons(familles_instance,persons_famille ,roles=persons_familles_roles)#


varmenages=[]
simulation = sb.build(tbs)
period = '2014'
#data["nbptr"]=1

columns_not_OF_variables= set(["idmen","idfoy","idfam","noindiv","level_0","quifam","quifoy","quimen","wprm","idmen_original","idfoy_original","idfam_original","index","quifamof","quifoyof","quimenof"])

datamen= data.groupby("idmen",as_index=False).first().sort_values(by="idmen")
datafoy= data.groupby("idfoy",as_index=False).first().sort_values(by="idfoy")
datafam= data.groupby("idfam",as_index=False).first().sort_values(by="idfam")
dictionnaire_datagrouped = {'menage':datamen,"foyer_fiscal":datafoy,"famille":datafam,'individu':data}

for k in data.columns:
    if k not in columns_not_OF_variables:
        simulation.set_input(k,period,dictionnaire_datagrouped[tbs.get_variable(k).entity.key][k])
        print("{} was attributed to {}".format(k,tbs.get_variable(k).entity.key))


datafoy["irpp"]=simulation.calculate('irpp', period,max_nb_cycles=1)
datafoy["nbptr"]=simulation.calculate('nbptr', period,max_nb_cycles=1)


#print(data_persons)
#print(data_households)
#print("Household ids", household_instance.ids)
#print("total_taxes", total_taxes)