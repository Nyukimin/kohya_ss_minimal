import subprocess
import psutil
import time
import threading
import gradio as gr
from collections import deque

from .custom_logging import setup_logging

# Set up logging
log = setup_logging()


class CommandExecutor:
    """
    A class to execute and manage commands.
    """

    def __init__(self, headless: bool = False):
        """
        Initialize the CommandExecutor.
        """
        self.headless = headless
        self.process = None
        self.output_buffer = deque(maxlen=500)  # 最大500行のログを保持
        self.output_lock = threading.Lock()
        self._reader_thread = None
        
        with gr.Row():
            self.button_run = gr.Button("Start training", variant="primary")

            self.button_stop_training = gr.Button(
                "Stop training", visible=self.process is not None or headless, variant="stop"
            )

    def execute_command(self, run_cmd: str, **kwargs):
        """
        Execute a command if no other command is currently running.

        Parameters:
        - run_cmd (str): The command to execute.
        - **kwargs: Additional keyword arguments to pass to subprocess.Popen.
        """
        if self.process and self.process.poll() is None:
            log.info("The command is already running. Please wait for it to finish.")
        else:
            # Clear output buffer
            with self.output_lock:
                self.output_buffer.clear()

            # Reconstruct the safe command string for display
            command_to_run = " ".join(run_cmd)
            log.info(f"Executing command: {command_to_run}")

            # 出力キャプチャを無効化（元の動作）
            # 注: 出力はコンソールに直接表示され、UIには表示されません
            # kwargs.setdefault('stdout', subprocess.PIPE)
            # kwargs.setdefault('stderr', subprocess.STDOUT)
            # kwargs.setdefault('bufsize', 1)
            # kwargs.setdefault('universal_newlines', True)
            # kwargs.setdefault('encoding', 'utf-8')
            # kwargs.setdefault('errors', 'replace')

            # Execute the command securely
            self.process = subprocess.Popen(run_cmd, **kwargs)
            log.debug("Command executed.")
            
            # Background thread disabled (output capture is off)
            # self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            # self._reader_thread.start()
    
    def _read_output(self):
        """Background thread to read process output."""
        try:
            if self.process and self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    if not line:
                        break
                    line = line.rstrip('\n\r')
                    # ログにも出力
                    print(line)
                    # バッファに追加
                    with self.output_lock:
                        self.output_buffer.append(line)
        except Exception as e:
            log.debug(f"Output reader error: {e}")
        finally:
            if self.process and self.process.stdout:
                self.process.stdout.close()
    
    def get_output(self, last_n_lines: int = 50) -> str:
        """Get the last N lines of output."""
        with self.output_lock:
            lines = list(self.output_buffer)
            if last_n_lines > 0:
                lines = lines[-last_n_lines:]
            return '\n'.join(lines)

    def kill_command(self):
        """
        Kill the currently running command and its child processes.
        """
        if self.is_running():
            try:
                # Get the parent process and kill all its children
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                log.info("The running process has been terminated.")
            except psutil.NoSuchProcess:
                # Explicitly handle the case where the process does not exist
                log.info(
                    "The process does not exist. It might have terminated before the kill command was issued."
                )
            except Exception as e:
                # General exception handling for any other errors
                log.info(f"Error when terminating process: {e}")
        else:
            self.process = None
            log.info("There is no running process to kill.")

        return gr.Button(visible=True), gr.Button(visible=False or self.headless)

    def wait_for_training_to_end(self):
        while self.is_running():
            time.sleep(1)
            log.debug("Waiting for training to end...")
        log.info("Training has ended.")
        return gr.Button(visible=True), gr.Button(visible=False or self.headless)

    def is_running(self):
        """
        Check if the command is currently running.

        Returns:
        - bool: True if the command is running, False otherwise.
        """
        return self.process is not None and self.process.poll() is None
