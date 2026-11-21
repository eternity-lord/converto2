"""Conservative execution policy and sustained-load guard (no Qt or OS mutations)."""
import os
from dataclasses import dataclass

LOW_RAM_BYTES = 3 * 1024 ** 3
RAM_PAUSE_PERCENT = 92
CPU_THROTTLE_PERCENT = 97


def encoding_threads(safe_mode=True, logical_cores=None):
    cores = logical_cores or os.cpu_count() or 2
    return max(2, cores - 2) if safe_mode else 0


def reserved_affinity(allowed):
    """Leave two allowed logical CPUs free, or one on a three-core system."""
    if len(allowed) > 2:
        return allowed[:-min(2, len(allowed) - 2)]
    return None  # Cannot reserve cores while honoring the two-thread minimum.


@dataclass
class SustainedLoadGuard:
    """Escalating resource policy.

    A video encoder legitimately uses every CPU core, so CPU saturation must not
    pause the queue: pausing the encoder cannot free the CPU it is asking for and
    would leave the batch waiting on an operator forever. CPU pressure therefore
    only throttles concurrency. Memory exhaustion is different: it can make the
    whole desktop unstable, so sustained high RAM pauses active processes until
    the user frees memory and resumes.
    """

    since: float = None
    notified: bool = False
    cpu_since: float = None
    cpu_notified: bool = False

    def observe(self, ram_percent, cpu_percent, now, enabled=True, active=True):
        """Return ``('pause'|'throttle', message)`` once per episode, else None."""
        if not enabled or not active:
            self.reset()
            return None
        overloaded = ram_percent > RAM_PAUSE_PERCENT
        if not overloaded:
            self.since = None
            self.notified = False
        else:
            if self.since is None:
                self.since = now
            if now - self.since >= 10 and not self.notified:
                self.notified = True
                return ('pause', f'Safety guard paused the queue: RAM {ram_percent:.1f}% '
                                 'stayed above the limit for 10 seconds. '
                                 'Free memory, then explicitly Resume.')
        busy = cpu_percent > CPU_THROTTLE_PERCENT
        if not busy:
            self.cpu_since = None
            self.cpu_notified = False
        else:
            if self.cpu_since is None:
                self.cpu_since = now
            if now - self.cpu_since >= 15 and not self.cpu_notified:
                self.cpu_notified = True
                return ('throttle', f'CPU {cpu_percent:.0f}% is saturated: limiting the queue '
                                    'to one job until the load drops.')
        return None

    def reset(self):
        self.since = None
        self.notified = False
        self.cpu_since = None
        self.cpu_notified = False
