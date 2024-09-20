import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import logging
from rich.logging import RichHandler

def setup_logging(log_level: str):
    logger = logging.getLogger("mini_server")
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)],
    )
    return logger

async def run_python(program: Path, *args, env_vars: Optional[Dict[str, str]] = None, timeout: float = 200):
    """
    Run a Python program with the given arguments and optional environment variables.
    """
    try:
        # Use passed env_vars if provided, otherwise use the current environment
        custom_env = env_vars if env_vars is not None else os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            program,
            *args,
            env=custom_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Program execution timed out after {timeout} seconds")

        if process.returncode != 0:
            raise RuntimeError(f"Program execution failed: {stderr.decode()}")

        return stdout.decode(), stderr.decode()

    except Exception as e:
        raise RuntimeError(f"Error running Python program: {str(e)}")