"""Exact event race for a stated finite-rate, time-homogeneous CTMC.

This module supplies numerical scheduling, not Minecraft physics or rates.
Times and hazards are expressed in ticks and inverse ticks respectively.
"""
from dataclasses import dataclass
import math
import random
from typing import Any, Callable, Iterable, Optional


@dataclass(frozen=True)
class Transition:
    name: str
    rate_per_tick: float
    destination: Any


@dataclass(frozen=True)
class Event:
    tick: float
    name: str
    source: Any
    destination: Any
    log_weight: float


@dataclass(frozen=True)
class Result:
    state: Any
    tick: float
    status: str
    events: int
    log_weight: float
    trace: tuple
    rng_seed: int

    @property
    def weight(self):
        return math.exp(self.log_weight)


Rates = Callable[[Any], Iterable[Transition]]


def _validate(transitions):
    result = {}
    for transition in transitions:
        if not isinstance(transition.name, str) or not transition.name:
            raise ValueError('Transition names must be nonempty strings')
        if transition.name in result:
            raise ValueError('Transition names must be unique within a state')
        if not math.isfinite(transition.rate_per_tick) or transition.rate_per_tick < 0:
            raise ValueError('Hazards must be finite and nonnegative')
        result[transition.name] = transition
    return result


class EventKernel:
    """Reusable seeded event kernel; subsequent runs continue the RNG stream.

    Callers must supply sufficient Markov state and immutable state snapshots
    when requesting traces. Rates must remain constant between transitions.
    A new EventKernel with the same seed reproduces the same random stream.
    """
    def __init__(self, rng_seed: int):
        self.rng_seed = rng_seed
        self.rng = random.Random(rng_seed)

    def run(self, initial_state: Any, target: Rates, horizon_ticks: float,
            proposal: Optional[Rates] = None, *, record_trace=False,
            max_events=1_000_000) -> Result:
        if not math.isfinite(horizon_ticks) or horizon_ticks < 0:
            raise ValueError('Horizon must be finite and nonnegative')
        if max_events < 1:
            raise ValueError('max_events must be positive')
        state, tick, log_weight, count = initial_state, 0.0, 0.0, 0
        trace = []
        while tick < horizon_ticks:
            target_map = _validate(target(state))
            proposed_map = _validate(proposal(state)) if proposal else target_map
            for name, event in target_map.items():
                if event.rate_per_tick > 0:
                    candidate = proposed_map.get(name)
                    if candidate is None or candidate.rate_per_tick <= 0:
                        raise ValueError('Proposal lacks support for target transition: ' + name)
            for name, candidate in proposed_map.items():
                event = target_map.get(name)
                if event is not None and candidate.destination != event.destination:
                    raise ValueError('Proposal changes destination for transition: ' + name)
            a_total = math.fsum(t.rate_per_tick for t in target_map.values())
            b_total = math.fsum(t.rate_per_tick for t in proposed_map.values())
            if not math.isfinite(a_total) or not math.isfinite(b_total):
                raise ValueError('Total hazard must be finite')
            if b_total == 0:
                return Result(state, tick, 'absorbed', count, log_weight,
                              tuple(trace), self.rng_seed)
            # random() lies in [0,1); log1p preserves small draws and avoids log(0).
            dt = -math.log1p(-self.rng.random()) / b_total
            remaining = horizon_ticks - tick
            if dt >= remaining:
                log_weight -= (a_total - b_total) * remaining
                return Result(state, horizon_ticks, 'horizon', count, log_weight,
                              tuple(trace), self.rng_seed)
            if count >= max_events:
                raise RuntimeError('Event budget exhausted before physical horizon')
            if tick + dt <= tick:
                raise ArithmeticError('Clock resolution exhausted; rescale time units')
            log_weight -= (a_total - b_total) * dt
            tick += dt
            draw = self.rng.random() * b_total
            choices = [t for t in proposed_map.values() if t.rate_per_tick > 0]
            selected = choices[-1]  # guards cumulative-rounding edge cases
            for candidate in choices:
                draw -= candidate.rate_per_tick
                if draw < 0:
                    selected = candidate
                    break
            target_event = target_map.get(selected.name)
            a_rate = target_event.rate_per_tick if target_event else 0.0
            if a_rate == 0:
                log_weight = -math.inf
            else:
                log_weight += math.log(a_rate) - math.log(selected.rate_per_tick)
            previous, state = state, selected.destination
            count += 1
            if record_trace:
                trace.append(Event(tick, selected.name, previous, state, log_weight))
        return Result(state, tick, 'horizon', count, log_weight, tuple(trace), self.rng_seed)


def analytic_competing_example(seed=2026, draws=12_000):
    """Synthetic benchmark: two absorbing hazards; these are not game rates."""
    def rates(state):
        return [Transition('A', 1.0, 'A'), Transition('B', 3.0, 'B')] if state == 'start' else []
    kernel = EventKernel(seed)
    results = [kernel.run('start', rates, 100) for _ in range(draws)]
    return {'label': 'synthetic CTMC benchmark, not Minecraft physics',
            'draws': draws, 'seed': seed,
            'expected_probability_A': 0.25,
            'observed_probability_A': sum(r.state == 'A' for r in results) / draws,
            'expected_mean_absorption_ticks': 0.25,
            'observed_mean_absorption_ticks': math.fsum(r.tick for r in results) / draws}


if __name__ == '__main__':
    import json
    print(json.dumps(analytic_competing_example(), indent=2))
