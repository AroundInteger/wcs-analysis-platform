"""Numeric checks for movsum with Endpoints "shrink".

The published R2025b example is movsum(A, 3), which is centred on the
current sample and shortened at both ends. An even window is centred on
the current sample and the previous one. Ties in the WCS search use
ceil(mean(centre index)), as in discover_dynamics_WCS_APP_1.m.
"""

import sys

import numpy as np
import pytest

sys.path.append("src")
from wcs_analysis import calculate_wcs_period, movsum_shrink


def _period(velocity, epoch_samples=4):
    """10 Hz series whose epoch rounds to `epoch_samples`."""
    return calculate_wcs_period(
        np.asarray(velocity, dtype=float),
        epoch_duration=epoch_samples / 600.0,
        sampling_rate=10,
        threshold_min=0.0,
        threshold_max=100.0,
    )


def test_published_three_point_shrink_example():
    """R2025b centred example. Endpoints "shrink" is the default.

    The first sum uses [4, 8] and the last uses [4, 5]. The full
    three-point windows sit in between. Discarding partial windows is a
    different option and is not applied here.
    """
    series = np.array([4, 8, 6, -1, -2, -3, -1, 3, 4, 5], dtype=float)
    expected = np.array([12, 18, 13, 3, -6, -6, -1, 6, 12, 9], dtype=float)

    np.testing.assert_array_equal(movsum_shrink(series, 3), expected)


def test_even_window_matches_matlab_r2025b():
    """Four-point window, centred on the current sample and the previous one.

    Expected values are movsum(A, 4) from MATLAB R2025b. Endpoints "shrink"
    is the default there, and naming it does not change the result.
    """
    series = np.array([4, 8, 6, -1, -2, -3, -1, 3, 4, 5], dtype=float)
    expected = np.array([12, 18, 17, 11, 0, -7, -3, 3, 11, 12], dtype=float)

    np.testing.assert_array_equal(movsum_shrink(series, 4), expected)


def test_interior_even_window_uses_current_and_previous():
    """Epoch of 4 samples. Centres 4 and 5 both sum to 15; ceil(mean) selects 5.

    The chosen window is samples [3, 7): the current sample, the previous
    one, one further sample before that pair, and one sample after it.
    """
    distance, time_in_band, start, end = _period([0, 0, 0, 5, 5, 5, 0, 0, 0])

    assert (start, end) == (3, 7)
    assert end - start == 4
    assert distance == pytest.approx(1.5)
    assert time_in_band == pytest.approx(0.4)


def test_window_lengthens_at_the_start():
    """A leading spike ties while the backward side is still short.

    Centres 0, 1 and 2 all sum to 9. ceil(mean) selects 1, whose window
    has only three of the four epoch samples.
    """
    distance, time_in_band, start, end = _period([9, 0, 0, 0, 0, 0, 0])

    assert (start, end) == (0, 3)
    assert end - start == 3
    assert distance == pytest.approx(0.9)
    assert time_in_band == pytest.approx(0.3)


def test_window_shortens_at_the_end():
    """A trailing spike ties on the centres that still include it.

    Centres 5 and 6 sum to 9. ceil(mean) selects 6, and the forward sample
    is missing, so the window has three samples.
    """
    distance, time_in_band, start, end = _period([0, 0, 0, 0, 0, 0, 9])

    assert (start, end) == (4, 7)
    assert end - start == 3
    assert distance == pytest.approx(0.9)
    assert time_in_band == pytest.approx(0.3)
