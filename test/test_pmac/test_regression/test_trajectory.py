from unittest import TestCase
from test.brick.testbrick import TBrick
from test.test_pmac.test_system.trajectories import (
    trajectory_fast_scan,
    trajectory_scan_appending,
)
from cothread import catools as ca


# Tests for historical issues with trajectory scanning


# @pytest.mark.skipif(os.environ.get('PPMAC') == 'True', reason="not supported on PPMAC yet")
class TestTrajectory(TestCase):
    def test_cs_switched_trajectory(self):
        """ test problem seen on VMXI where switching CS right after a traj
            scan causes the CS to immediately go into 'No motors in CS'
            error (err code 10)
            """
        tb = TBrick()
        for iteration in range(20):
            trajectory_fast_scan(self, tb, 1)
            # todo this is required because the CS may be still decelerating after it
            # todo   reports it delivered the last point and completed
            # todo   VMXI needed just this sleep - I feel that fixing it will slow those scans
            # todo   that do not require CS group switching (but only by a tiny bit)
            # Sleep(1) todo it turns out this is not required here but that just means we
            # todo       cannot reproduce the VMXi issue on the test equipment (probably)
            self.assertAlmostEqual(tb.m1.pos, 1, 1)

            tb.set_cs_group(tb.g2)
            tb.height.go(0)

    def test_appending(self):
        """ ensure that appended points are not added twicen_axes
        (due to busy record handling)
        """

        tb2 = TBrick()
        trajectory_scan_appending(self, tb2)

    def test_mres_offsets_trajectory(self):
        tb = TBrick()
        tb.set_cs_group(tb.g1)
        ca.caput(tb.m1.mres, 0.009)
        ca.caput(tb.m2.mres, 0.008)
        ca.caput(tb.m3.mres, 0.007)
        ca.caput(tb.m4.mres, 0.006)
        ca.caput(tb.m5.mres, 0.005)
        ca.caput(tb.m6.mres, 0.004)
        ca.caput(tb.m1.off, 10)
        ca.caput(tb.m2.off, 20)
        ca.caput(tb.m3.off, 20)
        ca.caput(tb.m4.off, 40)
        ca.caput(tb.m5.off, 50)
        ca.caput(tb.m6.off, 60)
        trajectory_fast_scan(self, tb, 6, "CS2", microsecs=50000)
        self.assertAlmostEqual(tb.m1.pos, 1, 1)
        self.assertAlmostEqual(tb.m2.pos, 1, 1)
        self.assertAlmostEqual(tb.m3.pos, 1, 1)
        self.assertAlmostEqual(tb.m4.pos, 1, 1)
        self.assertAlmostEqual(tb.m5.pos, 1, 1)
        self.assertAlmostEqual(tb.m6.pos, 1, 1)

        # reset all the mres etc.
        TBrick()
