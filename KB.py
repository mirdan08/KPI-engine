import networkx as nx
""""
The knowledge is base is simulated as a graph for the first milestone.
We have to kind of nodes:
    - KPI nodes
    - Machine nodes
edges are bidirectional and hold informations on which machine can calculate using a ceratin operation on some KPIs.
"""
def get_KB():
    G = nx.DiGraph()
    G.add_node("LaserCutter_1", node_type="Machine", model="LC-200",id='ast-xpimckaf3dlf', manufacturer="Brand A",machine_type="LaserCutter")
    G.add_node("LaserCutter_2", node_type="Machine", model="LC-300",id='m2', manufacturer="Brand B",machine_type="LaserCutter")

    G.add_node("MetalCutter_1", node_type="Machine", model="MC-200",id='m3', manufacturer="Brand A",machine_type="MetalCutter")
    G.add_node("MetalCutter_2", node_type="Machine", model="MC-300",id='m4', manufacturer="Brand B",machine_type="MetalCutter")

    G.add_node("AssemblyMachine_1", node_type="Machine", model="AM-200",id='m5', manufacturer="Brand A",machine_type="AssemblyMachine")
    G.add_node("AssemblyMachine_2", node_type="Machine", model="AM-300",id='m6', manufacturer="Brand B",machine_type="AssemblyMachine")

    G.add_node("LaserWelding_1", node_type="Machine", model="LW-200",id='m7', manufacturer="Brand A",machine_type="LaserWelding")
    G.add_node("LaserWelding_2", node_type="Machine", model="LW-300",id='m8', manufacturer="Brand B",machine_type="LaserWelding")

    # Add KPI Nodes with Descriptions and Normal Ranges
    G.add_node("working_time", 
               node_type="KPI",
               description="Time actively working", 
               unit="seconds", 
               normal_min=6, 
               normal_max=10
    )
    G.add_node("idle_time",
                node_type="KPI",
                description="Time idle but available",
                unit="seconds",
                normal_min=1,
                normal_max=4
     )
    G.add_node("offline_time",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("good_cycles",
                node_type="KPI",
                description="Time idle but available",
                unit="seconds",
                normal_min=1,
                normal_max=4
     )
    G.add_node("bad_cycles",
                node_type="KPI",
                description="Time idle but available",
                unit="seconds",
                normal_min=1,
                normal_max=4
     )
    G.add_node("cycles",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("average_cycle_time",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("consumption",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("consumption_working",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("consumption_idle",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("power",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    G.add_node("cost",
                node_type="KPI",
                description="Time offline and not available",
                unit="seconds",
                normal_min=0, 
                normal_max=2
     )
    # Add Directed Relationships (Edges) Between Machines and KPIs

    G.add_edge("LaserCutter_1", "good_cycles", relationship="measures",operation='sum')
    G.add_edge("LaserCutter_1", "cycles", relationship="measures",operation='sum')
    G.add_edge("LaserCutter_1", "working_time", relationship="measures",operation='sum')
    G.add_edge("LaserCutter_1", "idle_time", relationship="measures",operation='sum')

    G.add_edge("LaserCutter_1", "offline_time", relationship="measures",operation='sum')
    G.add_edge("LaserCutter_1", "working_time", relationship="measures",operation='max')
    G.add_edge("LaserCutter_1", "idle_time", relationship="measures",operation='max')
    G.add_edge("LaserCutter_1", "offline_time", relationship="measures",operation='max')

    G.add_edge("LaserCutter_1", "working_time", relationship="measures",operation='mean')
    G.add_edge("LaserCutter_1", "idle_time", relationship="measures",operation='mean')
    G.add_edge("LaserCutter_1", "offline_time", relationship="measures",operation='mean')


    G.add_edge("LaserCutter_2", "working_time", relationship="measures",operation='min')
    G.add_edge("LaserCutter_2", "idle_time", relationship="measures",operation='min')
    G.add_edge("LaserCutter_2", "offline_time", relationship="measures",operation='min')
    G.add_edge("LaserCutter_2", "working_time", relationship="measures",operation='var')
    
    G.add_edge("LaserCutter_2", "idle_time", relationship="measures",operation='var')
    G.add_edge("LaserCutter_2", "offline_time", relationship="measures",operation='var')

    return G