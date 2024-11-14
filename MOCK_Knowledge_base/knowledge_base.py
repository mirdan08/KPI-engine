# simulate checking with the ontology if calculations requested are actually possible
class KnowledgeBase:
    def __init__(self, KB):
        self.__KB = KB

    def get_machine(self, machine_id):
        machines = [
            (key, machine)
            for key, machine in self.__KB.nodes(data=True)
            if (
                (machine.get("node_type") == "Machine")
                and (machine.get("id") == machine_id)
            )
        ]
        return machines[0] if len(machines) != 0 else None

    def get_kpi(self, kpi):
        KPIs = [
            (key, kpi_v)
            for key, kpi_v in self.__KB.nodes(data=True)
            if (kpi_v.get("node_type") == "KPI" and key == kpi)
        ]
        return KPIs[0] if len(KPIs) != 0 else None

    def check_validity(self, machine_id, kpi, operation):
        machine_key, machine_node = self.get_machine(machine_id)
        if machine_node is None:
            return False
        kpi_key, kpi_node = self.get_kpi(kpi)
        if kpi_node is None:
            return False
        operations_available = self.__KB.get_edge_data(
            machine_key, kpi_key, "operation"
        )
        print(operations_available)
        if not operations_available:
            return False
        if operations_available["operation"] != operation:
            return False
        return True
