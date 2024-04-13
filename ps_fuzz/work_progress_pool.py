from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import colorama
import logging
logger = logging.getLogger(__name__)

# Define color shortcuts
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
GREEN = colorama.Fore.GREEN
BLUE = colorama.Fore.BLUE
RESET = colorama.Style.RESET_ALL

class ProgressWorker:
    def __init__(self, worker_id, progress_bar=False):
        self.worker_id = worker_id
        self.progress_bar = None
        if progress_bar:
            self.progress_bar = tqdm(total=1, desc=f"Worker #{worker_id:02}: {'(idle)':50}", position=worker_id, leave=True)

    def shutdown(self):
        # When worker is destroyed, ensure the corresponding progress bars closes properly.
        if self.progress_bar:
            self.progress_bar.close()

    def update(self, task_name: str, progress: float, total: float, colour="BLACK"):
        if not self.progress_bar:
            return
        # Update the progress bar
        with self.progress_bar.get_lock(): # Ensure thread-safe updates
            self.progress_bar.set_description(f"Worker #{self.worker_id:02}: {task_name + ' ':.<50}{RESET}", refresh=True)
            self.progress_bar.colour = colour # valid choices according to tqdm docs: [hex (#00ff00), BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
            self.progress_bar.n = int(progress) # Directly set progress value
            self.progress_bar.total = int(total) # And total value too
            self.progress_bar.refresh() # Refresh to update the UI

class WorkProgressPool(object):
    def __init__(self, num_workers):
        enable_per_test_progress_bars = False # the feature is not tested well
        self.num_workers = num_workers
        self.progress_workers = [ProgressWorker(worker_id, progress_bar=enable_per_test_progress_bars) for worker_id in range(self.num_workers)]
        self.queue_progress_bar = tqdm(total=1, desc=f"{colorama.Style.BRIGHT}{'Test progress ':.<54}{RESET}")
        self.semaphore = threading.Semaphore(self.num_workers) # Used to ensure that at most this number of tasks are immediately pending waiting for free worker slot

    def worker_function(self, worker_id, tasks):
        progress_worker = self.progress_workers[worker_id]
        progress_bar = progress_worker.progress_bar
        for task in tasks:
            self.semaphore.acquire()  # Wait until a worker slot is available
            if task is None:
                break
            try:
                if progress_bar:
                    progress_bar.n = 0
                    progress_bar.total = 1
                    progress_bar.refresh()
                task(progress_worker)
            except Exception as e:
                # Task caused exception. We can't print it now, as it would interfere with the progress bar. We could log it to a file or similar.
                logger.error(f"Task caused exception: {e}", exc_info=True)
                raise
            finally:
                self.semaphore.release() # Release the worker slot (this is crucial to do always, even if task thrown an exception, otherwise deadlocks or hangs could occur)
                if self.tasks_count:
                    self.queue_progress_bar.n += 1
                    self.queue_progress_bar.total = self.tasks_count
                    self.queue_progress_bar.refresh()
        """
        # Setting progress bar to a state indicating it is free and doesn't do any task right now...
        with progress_bar.get_lock():
            progress_bar.set_description(f"Worker #{worker_id:02}: {RESET}{'(idle)':50}{RESET}", refresh=True)
            progress_bar.n = 0
            progress_bar.total = 1
            progress_bar.refresh()
        """

    def run(self, tasks, tasks_count=None):
        self.tasks_count = tasks_count

        if self.tasks_count:
            self.queue_progress_bar.n = 0
            self.queue_progress_bar.total = self.tasks_count
            self.queue_progress_bar.refresh()

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Pass each worker its own progress bar reference
            futures = [executor.submit(self.worker_function, worker_id, tasks) for worker_id in range(self.num_workers)]
            # Wait for all workers to finish
            for future in futures:
                future.result()

        # Shut down the worker properly
        for pw in self.progress_workers:
            pw.shutdown()

        # Close the additional queue_progress_bar
        self.queue_progress_bar.close()


class ThreadSafeTaskIterator:
    "This is a thread-safe iterator for tasks"
    def __init__(self, generator):
        self.generator = generator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.generator)
