import datetime
from ..agents import ExternalAgent
from alive_progress import alive_bar


class Scheduler(ExternalAgent):
    """
        The Scheduler orchestrate the simulation.
    """

    def __init__(self, environment, factory, current_time=None):
        super().__init__("Scheduler", None, factory)

        if current_time is None:
            current_time = datetime.datetime.now()

        self._current_time = current_time
        self._environment = environment
        self._network = factory.build_network()

    @property
    def current_time(self):
        """
            Get the current simulation time
        """
        return self._current_time

    @property
    def environment(self):
        """
            Get the underlying environment
        """
        return self._environment

    def init(self):
        super().init(self.current_time)
        self._environment.init(self._date)

    def cleanup(self):
        super().cleanup()
        self._environment.cleanup()

    def step(self):
        """
            Take one "step" in the environment
        """
        message = self._network.get_next_message()
        self._current_time = message.date

        if message.recipient != self._environment.name:
            agent = self._environment.get_agent_by_name(message.recipient)
        else:
            agent = self._environment

        if agent is not None:
            agent.date = message.date
            agent.handle_message(message)

    def run(self, condition: callable, progress=None, init=True, cleanup=True):
        """
            Run the environment until the end condition is True
        """
        if init is True:
            self.init()

        last_update = datetime.datetime.now()
        update_delta = datetime.timedelta(seconds=1)

        with alive_bar(total=100, manual=True) as progress_bar:

            while self._network.has_message() and condition(self._environment) is True:
                self.step()

                if progress is not None and last_update + update_delta < datetime.datetime.now():
                    last_update = datetime.datetime.now()
                    progress_bar(percent=progress(self._environment))

            progress_bar(percent=1)

        if cleanup is True:
            self.cleanup()
