
class WarmUp(object):
    def load_tax_benefits_system(**params: dict) -> tuple:
        # import the TBS at handler call only
        from Simulation_engine.simulate_pop_from_reform import TBS
        version = TBS.get_package_metadata()['version']
        return {"status": f"A chargé en mémoire OpenFisca-France v{version}"}, 200
