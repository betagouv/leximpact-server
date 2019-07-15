from server.services.openfisca import cas_types


def test_cas_types():
    reform = {"variable": "name", "operation": "*", "times": "2"}
    cas_type = {"name": "Augustin"}
    impact = cas_types(reform=reform, cas_types=[cas_type])
    assert {"name": "AugustinAugustin"} in impact
