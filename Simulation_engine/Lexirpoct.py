# -*- coding: utf-8 -*-


import pandas
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

#try:
#    data=pandas.read_pickle("./failingsampleerfs.pkl")
#except:

nomfichier="openfisca_erfs_fpr_data_2014.h5"
try:
    data = pandas.read_hdf("./{}".format(nomfichier))
except:
    data = pandas.read_hdf("./Simulation_engine/{}".format(nomfichier))



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

tbs = FranceTaxBenefitSystem()
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
    dictionnaire_datagrouped[ofent]=data.groupby("id"+ent,as_index=False).first().sort_values(by="id"+ent)


varmenages=[]
simulation = sb.build(tbs)

#These variables should not be attributed to any OpenFisca Entity
columns_not_OF_variables = set(["idmen","idfoy","idfam","noindiv","level_0","quifam","quifoy","quimen","wprm","index",
                                "idmen_original","idfoy_original","idfam_original","quifamof","quifoyof","quimenof"])


period = '2014'
#Attribution des variables à la bonne entité OpenFisca
for colonne in data.columns:
    if colonne not in columns_not_OF_variables:
        simulation.set_input(colonne,period,dictionnaire_datagrouped[tbs.get_variable(colonne).entity.key][colonne])
        print("{} was attributed to {}".format(colonne,tbs.get_variable(colonne).entity.key))



for nomvariable in ["irpp","nbptr"]:
    dictionnaire_datagrouped["foyer_fiscal"][nomvariable] = simulation.calculate(nomvariable, period, max_nb_cycles=1)
    dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"]=dictionnaire_datagrouped["foyer_fiscal"][nomvariable]*dictionnaire_datagrouped["foyer_fiscal"]["wprm"]
    print("{} sum : {}  mean : {}".format(nomvariable,dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"].sum(),dictionnaire_datagrouped["foyer_fiscal"][nomvariable+"w"].sum()/datafoy["wprm"].sum()))

