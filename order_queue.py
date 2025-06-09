from stage import Stage
from flag import Flag

class OrderQueue(Stage):
    """Stage subclass managing an ordered list of Flag objects."""

    def __init__(self):
        super().__init__()
        self._queue = []

    # ------------------------------------------------------------------
    # Basic list operations
    # ------------------------------------------------------------------
    def add_flag(self, flag):
        """Add ``flag`` to the end of the queue and as a child stage."""
        if not isinstance(flag, Flag):
            raise TypeError("flag must be a Flag instance")
        self._queue.append(flag)
        self.add_stage(flag)

    def pop(self, index=-1):
        """Remove and return a flag from the queue."""
        if not self._queue:
            return None
        flag = self._queue.pop(index)
        self.remove_stage(flag)
        return flag

    def remove(self, flag):
        """Remove ``flag`` from the queue."""
        self._queue.remove(flag)
        self.remove_stage(flag)

    def clear(self):
        """Remove all flags from the queue."""
        for flag in list(self._queue):
            self.remove_stage(flag)
        self._queue.clear()

    # ------------------------------------------------------------------
    # Container protocol helpers
    # ------------------------------------------------------------------
    def __len__(self):
        return len(self._queue)

    def __getitem__(self, item):
        return self._queue[item]

    def __iter__(self):
        return iter(self._queue)
