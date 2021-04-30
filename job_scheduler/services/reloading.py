import logging
import multiprocessing
import os
import signal
import sys
import threading
import typing as t

from watchgod import PythonWatcher

from job_scheduler.logging import setup_logging

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


logger = logging.getLogger(__name__)
spawn = multiprocessing.get_context("spawn")

setup_logging()


class AppReloader:
    def __init__(self, target: t.Callable):
        self.watchers = [PythonWatcher(os.getcwd())]
        self.reload_delay = 0.25
        self.target = target
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        self.reloader_name = PythonWatcher.__name__

    def signal_handler(self, sig, frame):
        """
        A signal handler that is registered with the parent process.
        """
        self.should_exit.set()

    def run(self):
        self.startup()
        while not self.should_exit.wait(self.reload_delay):
            if self.should_restart():
                self.restart()

        self.shutdown()

    def startup(self):
        logger.info(f"Started reloader process [{self.pid}] using {self.reloader_name}")

        for sig in HANDLED_SIGNALS:
            signal.signal(sig, self.signal_handler)

        self.process = get_subprocess(target=self.target)
        self.process.start()

    def restart(self):
        self.process.terminate()
        self.process.join()

        self.process = get_subprocess(target=self.target)
        self.process.start()

    def shutdown(self):
        self.process.join()
        logger.info("Stopping reloader process [{}]".format(str(self.pid)))

    def should_restart(self):
        for watcher in self.watchers:
            change = watcher.check()
            if change:
                files = [c[1] for c in change]
                logger.warning(
                    f"{self.reloader_name} detected file change in {files}. Reloading..."
                )
                return True
        return False


def get_subprocess(target: t.Callable):
    # We pass across the stdin fileno, and reopen it in the child process.
    # This is required for some debugging environments.
    stdin_fileno: t.Optional[int]
    try:
        stdin_fileno = sys.stdin.fileno()
    except OSError:
        stdin_fileno = None

    kwargs = {
        "target": target,
        "stdin_fileno": stdin_fileno,
    }
    return spawn.Process(target=subprocess_started, kwargs=kwargs)


def subprocess_started(target, stdin_fileno):
    """
    Called when the child process starts.
    * target - A callable to run.
    * stdin_fileno - The file number of sys.stdin, so that it can be reattached
                     to the child process.
    """
    # Re-open stdin.
    if stdin_fileno is not None:
        sys.stdin = os.fdopen(stdin_fileno)

    target()


def with_reloading(func: t.Callable):
    AppReloader(func).run()
