import os
import subprocess
import glob
import sys

# Path to mkvmerge executable (Running from temp, so tools is one level up)
MKVMERGE = os.path.join("..", "tools", "MKVToolNix", "mkvmerge.exe")
SOURCE_EXTENSIONS = (".mkv", ".mp4", ".m2ts")

def run_mkvmerge(cmd, status_label):
    """
    Runs mkvmerge hidden, parsing output to update a single progress line.
    """
    # Ensure the executable path is absolute or correct relative to CWD
    cmd[0] = os.path.abspath(cmd[0])
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
    except FileNotFoundError:
        print(f"\n[ERROR] mkvmerge not found at: {cmd[0]}")
        raise

    # Print initial status with extra spaces to reserve the line
    print(f"{status_label}: Starting...          ", end="\r")
    sys.stdout.flush()

    for line in process.stdout:
        line = line.strip()
        # mkvmerge output standard: "Progress: 10%"
        if line.startswith("Progress:"):
            percent = line.split(":")[-1].strip()
            # Update the line with the percentage + padding spaces
            print(f"{status_label}: {percent}          ", end="\r")
            sys.stdout.flush()

    process.wait()
    
    if process.returncode != 0:
        print(f"\n[ERROR] Command failed: {' '.join(cmd)}")
        raise subprocess.CalledProcessError(process.returncode, cmd)
    
    # Finalize the line with explicit spaces to overwrite "Starting..." or percentages
    print(f"{status_label}: Done.          ")

def mux_files():
    ivf_files = glob.glob("*.ivf")

    if not ivf_files:
        print("[ERROR] No .ivf files found to mux.")
        return False

    print(f"Found {len(ivf_files)} .ivf files. Starting muxing process...\n")

    all_succeeded = True

    for ivf_file in ivf_files:
        base_name = os.path.splitext(ivf_file)[0]
        
        # Match every source type accepted by dispatch.py. Also support the
        # legacy "-source" filename used by older workflow versions.
        possible_sources = []
        for extension in SOURCE_EXTENSIONS:
            possible_sources.append(f"{base_name}{extension}")
            possible_sources.append(f"{base_name}-source{extension}")
        source_file = next((f for f in possible_sources if os.path.isfile(f)), None)

        if not source_file:
            print(f"[FAIL] Source video not found for: {ivf_file}")
            all_succeeded = False
            continue

        temp_mkv = f"{base_name}_temp_no_video.mkv"
        final_output = f"{base_name}-output.mkv"

        try:
            # Step 1: Extract Audio/Subs (No Video)
            cmd_step1 = [MKVMERGE, "-o", temp_mkv, "--no-video", source_file]
            run_mkvmerge(cmd_step1, f"[{base_name}] Step 1/2 (Extract)")

            # Step 2: Mux IVF + Audio/Subs
            cmd_step2 = [MKVMERGE, "-o", final_output, ivf_file, temp_mkv]
            run_mkvmerge(cmd_step2, f"[{base_name}] Step 2/2 (Merge)  ")

            # Cleanup temp file
            if os.path.exists(temp_mkv):
                os.remove(temp_mkv)

        except subprocess.CalledProcessError:
            print(f"\n[FAIL] Could not process {base_name}. Skipping.")
            all_succeeded = False
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            all_succeeded = False
        finally:
            if os.path.exists(temp_mkv):
                try:
                    os.remove(temp_mkv)
                except OSError:
                    pass

    return all_succeeded

if __name__ == "__main__":
    sys.exit(0 if mux_files() else 1)