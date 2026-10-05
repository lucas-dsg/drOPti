from __future__ import annotations

from dropit.timedata import TimeData


def solve_gurobi(td: TimeData, verbose: bool = False) -> int:
    """Modèle MIP : un seul point de dépose, contrainte de détour du conducteur."""
    import gurobipy as gp
    from gurobipy import GRB

    # Les candidats aux temps infinis (trajet introuvable) sont écartés avant le modèle.
    idx = [i for i in range(len(td.candidates)) if td.usable(i)]
    if not idx:
        raise ValueError("Aucun point de dépose utilisable")

    with gp.Env(empty=True) as env:
        env.setParam("OutputFlag", 1 if verbose else 0)
        env.start()
        with gp.Model("dropit", env=env) as m:
            x = m.addVars(idx, vtype=GRB.BINARY, name="x")
            m.addConstr(x.sum() == 1, name="un_seul_point")
            m.addConstr(
                gp.quicksum(td.detour(i) * x[i] for i in idx) <= td.max_detour_min,
                name="detour_max",
            )
            m.setObjective(gp.quicksum(td.passenger_time(i) * x[i] for i in idx), GRB.MINIMIZE)
            m.optimize()
            if m.Status == GRB.INFEASIBLE:
                raise ValueError("Aucun point de dépose réalisable")
            if m.Status != GRB.OPTIMAL:
                raise RuntimeError(f"Gurobi : statut {m.Status}")
            return max(idx, key=lambda i: x[i].X)
