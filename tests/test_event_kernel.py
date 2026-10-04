"""Analytic distribution tests for the scheduler, not Minecraft validation."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from event_kernel import EventKernel, Transition, analytic_competing_example


class EventKernelTests(unittest.TestCase):
    def test_competing_hazards_match_analytic_probability_and_mean(self):
        report = analytic_competing_example(draws=12_000)
        self.assertAlmostEqual(report['observed_probability_A'], .25, delta=.015)
        self.assertAlmostEqual(report['observed_mean_absorption_ticks'], .25, delta=.009)

    def test_importance_weighted_rare_event_and_survival(self):
        # Same legal edge, different clock: exercise event AND survival terms.
        def target(state):
            return [Transition('hit', .01, 'hit')] if state == 'start' else []
        def proposal(state):
            return [Transition('hit', 1., 'hit')] if state == 'start' else []
        kernel = EventKernel(71239)
        n = 18_000
        results = [kernel.run('start', target, 1., proposal) for _ in range(n)]
        estimate = math.fsum(r.weight for r in results if r.state == 'hit') / n
        self.assertAlmostEqual(estimate, -math.expm1(-.01), delta=.0004)
        self.assertAlmostEqual(math.fsum(r.weight for r in results) / n, 1., delta=.035)
        self.assertGreater(sum(r.state == 'hit' for r in results) / n, .60)

    def test_proposal_support_and_destination_are_checked(self):
        target = lambda state: [Transition('hit', 1., 'hit')]
        with self.assertRaisesRegex(ValueError, 'support'):
            EventKernel(1).run('start', target, 1., lambda state: [])
        with self.assertRaisesRegex(ValueError, 'destination'):
            EventKernel(1).run('start', target, 1.,
                               lambda state: [Transition('hit', 1., 'other')])

    def test_absorption_reproducibility_and_horizon(self):
        target = lambda state: [Transition('hit', 1., 'hit')] if state == 'start' else []
        first = EventKernel(31).run('start', target, 10., record_trace=True)
        second = EventKernel(31).run('start', target, 10., record_trace=True)
        self.assertEqual(first, second)
        self.assertEqual(first.status, 'absorbed')
        self.assertEqual(first.events, 1)
        censored = EventKernel(31).run('start', target, 0.)
        self.assertEqual(censored.status, 'horizon')
        self.assertEqual(censored.events, 0)
        self.assertEqual(censored.weight, 1.)

    def test_invalid_rates(self):
        for rate in [-1., math.inf, math.nan]:
            with self.assertRaises(ValueError):
                EventKernel(1).run('start', lambda state: [Transition('bad', rate, 'x')], 1.)


if __name__ == '__main__':
    unittest.main()
