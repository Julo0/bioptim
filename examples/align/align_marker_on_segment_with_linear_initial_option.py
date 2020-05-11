import biorbd

from biorbd_optim import (
    Instant,
    Axe,
    OptimalControlProgram,
    ProblemType,
    Objective,
    Constraint,
    Bounds,
    QAndQDotBounds,
    InitialConditions,
    ShowResult,
    OdeSolver,
)


def prepare_ocp(
    biorbd_model_path, final_time, number_shooting_points, ode_solver, initialize_near_solution, show_online_optim=False
):
    # --- Options --- #
    # Model path
    biorbd_model = biorbd.Model(biorbd_model_path)

    # Problem parameters
    number_shooting_points = 30
    final_time = 2
    torque_min, torque_max, torque_init = -100, 100, 0

    # Add objective functions
    objective_functions = {"type": Objective.Lagrange.MINIMIZE_TORQUE, "weight": 100}

    # Dynamics
    problem_type = ProblemType.torque_driven

    # Constraints
    constraints = (
        {"type": Constraint.ALIGN_MARKERS, "instant": Instant.START, "first_marker_idx": 0, "second_marker_idx": 4,},
        {"type": Constraint.ALIGN_MARKERS, "instant": Instant.END, "first_marker_idx": 0, "second_marker_idx": 5,},
        {
            "type": Constraint.ALIGN_MARKER_WITH_SEGMENT_AXIS,
            "instant": Instant.ALL,
            "marker_idx": 1,
            "segment_idx": 2,
            "axis": (Axe.X),
        },
    )

    # Path constraint
    X_bounds = QAndQDotBounds(biorbd_model)

    for i in range(1, 8):
        if i != 3:
            X_bounds.min[i, [0, -1]] = 0
            X_bounds.max[i, [0, -1]] = 0
    X_bounds.min[2, -1] = 1.57
    X_bounds.max[2, -1] = 1.57

    # Initial guess
    # X_init = InitialConditions([0] * (biorbd_model.nbQ() + biorbd_model.nbQdot()))
    x_initi_start = 1
    x_initi_end = -1
    init_lineaire = True
    X_init = InitialConditions(
        [x_initi_start, x_initi_end] * biorbd_model.nbQ() +
            [2 * x_initi_start, 0.5 * x_initi_end] * biorbd_model.nbQdot(),
        init_lineaire
    )

    if initialize_near_solution:
        for i in range(2):
            X_init.init[i] = 1.5
        for i in range(4, 6):
            X_init.init[i] = 0.7
        for i in range(6, 8):
            X_init.init[i] = 0.6

    # Define control path constraint
    U_bounds = Bounds(
        [torque_min] * biorbd_model.nbGeneralizedTorque(), [torque_max] * biorbd_model.nbGeneralizedTorque(),
    )
    # U_init = InitialConditions([torque_init] * biorbd_model.nbGeneralizedTorque())
    u_initi_start = 25
    u_initi_end = -25
    init_lineaire = True
    U_init = InitialConditions(
        [u_initi_start, u_initi_end] * biorbd_model.nbGeneralizedTorque(),
        init_lineaire
    )

    # ------------- #

    return OptimalControlProgram(
        biorbd_model,
        problem_type,
        number_shooting_points,
        final_time,
        objective_functions,
        X_init,
        U_init,
        X_bounds,
        U_bounds,
        constraints,
        ode_solver=ode_solver,
        show_online_optim=show_online_optim,
    )


if __name__ == "__main__":
    ocp = prepare_ocp(
        biorbd_model_path="cube_and_line.bioMod",
        number_shooting_points=30,
        final_time=1,
        ode_solver=OdeSolver.RK,
        initialize_near_solution=True,
        show_online_optim=False,
    )

    # --- Solve the program --- #
    sol = ocp.solve()

    # --- Show results --- #
    result = ShowResult(ocp, sol)
    result.animate()
