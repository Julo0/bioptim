from pathlib import Path

import pytest
import numpy as np
import biorbd

from biorbd_optim import (
    OptimalControlProgram,
    DynamicsTypeList,
    DynamicsType,
    BoundsOption,
    InitialConditionsOption,
)


def test_penalty_minimize_time():
    PROJECT_FOLDER = Path(__file__).parent / ".."
    biorbd_model = biorbd.Model(str(PROJECT_FOLDER) + "/examples/align/cube_and_line.bioMod")
    nq = biorbd_model.nbQ()

    dynamics = DynamicsTypeList()
    dynamics.add(DynamicsType.TORQUE_DRIVEN)
    ocp = OptimalControlProgram(biorbd_model, dynamics, 10, 1.0)

    X_bounds = BoundsOption([-np.ones((nq * 2, 1)), np.ones((nq * 2, 1))])
    U_bounds = BoundsOption([-2.0 * np.ones((nq, 1)), 2.0 * np.ones((nq, 1))])
    ocp.update_bounds(X_bounds, U_bounds)

    expected = np.append(np.tile(np.append(-np.ones((nq * 2, 1)), -2.0 * np.ones((nq, 1))), 10), -np.ones((nq * 2, 1)))
    np.testing.assert_almost_equal(ocp.V_bounds.min, expected.reshape(128, 1))
    expected = np.append(np.tile(np.append(np.ones((nq * 2, 1)), 2.0 * np.ones((nq, 1))), 10), np.ones((nq * 2, 1)))
    np.testing.assert_almost_equal(ocp.V_bounds.max, expected.reshape(128, 1))

    X_init = InitialConditionsOption(0.5 * np.ones((nq * 2, 1)))
    U_init = InitialConditionsOption(-0.5 * np.ones((nq, 1)))
    ocp.update_initial_guess(X_init, U_init)
    expected = np.append(
        np.tile(np.append(0.5 * np.ones((nq * 2, 1)), -0.5 * np.ones((nq, 1))), 10), 0.5 * np.ones((nq * 2, 1))
    )
    np.testing.assert_almost_equal(ocp.V_init.init, expected.reshape(128, 1))

    X_bounds = BoundsOption([-2.0 * np.ones((nq * 2, 1)), 2.0 * np.ones((nq * 2, 1))])
    U_bounds = BoundsOption([-4.0 * np.ones((nq, 1)), 4.0 * np.ones((nq, 1))])
    ocp.update_bounds(X_bounds=X_bounds)
    ocp.update_bounds(U_bounds=U_bounds)

    expected = np.append(
        np.tile(np.append(-2.0 * np.ones((nq * 2, 1)), -4.0 * np.ones((nq, 1))), 10), -2.0 * np.ones((nq * 2, 1))
    )
    np.testing.assert_almost_equal(ocp.V_bounds.min, expected.reshape(128, 1))
    expected = np.append(
        np.tile(np.append(2.0 * np.ones((nq * 2, 1)), 4.0 * np.ones((nq, 1))), 10), 2.0 * np.ones((nq * 2, 1))
    )
    np.testing.assert_almost_equal(ocp.V_bounds.max, expected.reshape(128, 1))

    X_init = InitialConditionsOption(0.25 * np.ones((nq * 2, 1)))
    U_init = InitialConditionsOption(-0.25 * np.ones((nq, 1)))
    ocp.update_initial_guess(X_init, U_init)
    expected = np.append(
        np.tile(np.append(0.25 * np.ones((nq * 2, 1)), -0.25 * np.ones((nq, 1))), 10), 0.25 * np.ones((nq * 2, 1))
    )
    np.testing.assert_almost_equal(ocp.V_init.init, expected.reshape(128, 1))

    with pytest.raises(
        RuntimeError, match="X_init should be built from a InitialConditionsOption or InitialConditionsList"
    ):
        ocp.update_initial_guess(X_bounds, U_bounds)
    with pytest.raises(RuntimeError, match="X_bounds should be built from a BoundsOption or BoundsList"):
        ocp.update_bounds(X_init, U_init)
