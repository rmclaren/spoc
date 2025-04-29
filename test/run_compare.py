import os
import subprocess

def run_compare(result_file, expected_file):
    if not os.path.isfile(result_file):
        raise FileNotFoundError(f"Result file not found: {result_file}")
    if not os.path.isfile(expected_file):
        raise FileNotFoundError(f"Expected file not found: {expected_file}")

    # Check if nccmp is available
    def check_nccmp():
        try:
            subprocess.run(["nccmp", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # Try to find nccmp
    if not check_nccmp():
        # Attempt to load nccmp module
        try:
            # Run 'module load nccmp/1.9.0.1' in a shell
            subprocess.run(
                "module load nccmp/1.9.0.1",
                shell=True,
                executable="/bin/bash",  # Ensure bash is used
                capture_output=True,
                text=True,
                check=True
            )
            print("Successfully loaded nccmp/1.9.0.1 module.")
        except subprocess.CalledProcessError as e:
            raise FileNotFoundError(
                f"Failed to load nccmp/1.9.0.1 module: {e.stderr}"
            ) from None
        except FileNotFoundError:
            raise FileNotFoundError(
                "nccmp not found and module command not available."
            ) from None

        # Verify nccmp is now available
        if not check_nccmp():
            raise FileNotFoundError(
                "nccmp still not found after attempting to load module nccmp/1.9.0.1."
            )

    # Run nccmp with -d (data comparison) and -f (force, no user prompt)
    # Use -t for tolerance if needed (e.g., -t 1e-5 for floating-point)
    cmd = ["nccmp", "-d", "-m", "-g", "-f", "-S", result_file, expected_file]
    print(f'Testing: {cmd}')
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"nccmp comparison passed: {result_file} matches {expected_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"nccmp comparison failed: {e.stderr}")
        return False
