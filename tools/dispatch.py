import sys
import subprocess
import os
import shutil
import glob
from wakepy import keep

def main():
    # --- Configuration ---
    script_path = os.path.abspath(__file__)
    tools_dir = os.path.dirname(script_path)
    root_dir = os.path.dirname(tools_dir)
    
    input_dir = os.path.join(root_dir, "videos-input")
    output_dir = os.path.join(root_dir, "videos-output")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # --- Setup Tools in Input Folder (Silent) ---
    # Copy the worker script and required tools directly to the videos-input folder
    tools_to_copy = ["Auto-Boost-Essential.py", "ffms2.dll", "SvtAv1EncApp.exe"]
    for tool in tools_to_copy:
        src = os.path.join(tools_dir, tool)
        dst = os.path.join(input_dir, tool)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass 

    # --- Scan for Files (Silent) ---
    extensions = ('.mp4', '.mkv', '.m2ts')
    files_to_process = []
    
    if os.path.exists(input_dir):
        for f in os.listdir(input_dir):
            if f.lower().endswith(extensions) and os.path.isfile(os.path.join(input_dir, f)):
                if "-output" in f: 
                    continue
                files_to_process.append(os.path.join(input_dir, f))
    
    files_to_process = list(set(files_to_process))
    
    if not files_to_process:
        print("[Dispatch] No video files found to process.")
        sys.exit(0)

    # --- Processing Loop ---
    mediainfo_exe = os.path.join(tools_dir, "MediaInfo_CLI", "MediaInfo.exe")
    python_exe = sys.executable 
    main_script_target = os.path.join(input_dir, "Auto-Boost-Essential.py")

    for file_path in files_to_process:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)

        # --- CHECK: Output Exists ---
        # Checks if [Filename]-output.mkv already exists in the output directory
        expected_output = os.path.join(output_dir, f"{name}-output.mkv")
        
        # Also check for -source-output in case previous runs left it that way
        expected_output_alt = os.path.join(output_dir, f"{name}-source-output.mkv")

        if os.path.exists(expected_output):
            print(f"[Dispatch] Skipping {filename}: Output file already exists -> {os.path.basename(expected_output)}")
            continue
        elif os.path.exists(expected_output_alt):
            print(f"[Dispatch] Skipping {filename}: Output file already exists -> {os.path.basename(expected_output_alt)}")
            continue
        
        # --- UI Update ---
        # Handle the display name cleanly (remove -source from the end of the name if present)
        name_root = name 
        if name_root.endswith("-source"):
            display_name = name_root[:-7] + ext
        else:
            display_name = filename.replace("-source", "") # Fallback for mid-string occurrences
        
        print("Starting Auto-Boost-Essential Dispatch...")
        print(f"Current file: {display_name}")
        print("-" * 79)
        sys.stdout.flush()

        # 1. Color Space Detection (Silent)
        is_bt709 = False
        is_bt601 = False
        f_prim_709 = False; f_trans_709 = False; f_mat_709 = False
        f_prim_601 = False; f_trans_601 = False; f_mat_601 = False
        
        if os.path.exists(mediainfo_exe) and os.path.exists(file_path):
            try:
                cmd = [mediainfo_exe, file_path]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if ":" not in line: continue
                        key, value = line.split(":", 1)
                        key = key.strip(); value = value.strip()
                        if key == "Color primaries":
                            if value == "BT.709": f_prim_709 = True
                            elif "BT.601" in value: f_prim_601 = True
                        elif key == "Transfer characteristics":
                            if value == "BT.709": f_trans_709 = True
                            elif "BT.601" in value: f_trans_601 = True
                        elif key == "Matrix coefficients":
                            if value == "BT.709": f_mat_709 = True
                            elif "BT.601" in value: f_mat_601 = True
                    
                    if f_prim_709 and f_trans_709 and f_mat_709:
                        is_bt709 = True
                    elif f_prim_601 and f_trans_601 and f_mat_601:
                        is_bt601 = True
            except Exception:
                pass

        # 2. Construct Command
        final_cmd = [python_exe, main_script_target]
        bt709_flags = " --color-primaries 1 --transfer-characteristics 1 --matrix-coefficients 1"
        bt601_flags = " --color-primaries 6 --transfer-characteristics 6 --matrix-coefficients 6"
        current_flags = ""
        if is_bt709: current_flags = bt709_flags
        elif is_bt601: current_flags = bt601_flags
        
        final_cmd.extend(["-i", filename])
        input_args = sys.argv[1:]
        skip_next = False
        for idx, arg in enumerate(input_args):
            if skip_next:
                skip_next = False
                continue
            
            # Filter out arguments that Auto-Boost-Essential doesn't understand
            if arg == "--photon-noise":
                skip_next = True
                continue
                
            if arg in ("-i", "--input"):
                if idx + 1 < len(input_args): skip_next = True
                continue
            if arg in ("--fast-params", "--final-params"):
                final_cmd.append(arg)
                if idx + 1 < len(input_args):
                    param_str = input_args[idx + 1]
                    if current_flags: param_str += current_flags
                    final_cmd.append(param_str)
                    skip_next = True
                else:
                    final_cmd.append("")
            else:
                final_cmd.append(arg)

        # 3. Execute Auto-Boost (Silent Dispatch)
        # We rely on Auto-Boost-Essential.py's own progress bars for visibility
        encoding_success = False
        try:
            sys.stdout.flush()
            with keep.running():
                subprocess.check_call(final_cmd, cwd=input_dir)
            encoding_success = True
        except subprocess.CalledProcessError:
            print("[Dispatch] Encoding failed for this file.")
        except Exception as e:
            print(f"[Dispatch] Execution error: {e}")

        if encoding_success:
            # 4. External Scripts
            mux_script = os.path.join(tools_dir, "mux.py")
            tag_script = os.path.join(tools_dir, "tag.py")
            
            print("[Dispatch] Starting Muxing Process...")
            try:
                # Muxing output is allowed to pass through (it handles its own formatting)
                subprocess.run([python_exe, mux_script], cwd=input_dir, check=False)
            except Exception as e:
                print(f"[Dispatch] Mux error: {e}")

            print("[Dispatch] Starting Tagging Process...")
            try:
                for ivf in glob.glob(os.path.join(input_dir, "*.ivf")):
                    os.remove(ivf)
                # Tagging is silent
                subprocess.run([python_exe, tag_script], cwd=input_dir, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"[Dispatch] Tag error: {e}")
                
            # 5. Move Output (Silent)
            found_outputs = glob.glob(os.path.join(input_dir, "*-output.mkv"))
            for out_file in found_outputs:
                out_name = os.path.basename(out_file)
                try:
                    shutil.move(out_file, os.path.join(output_dir, out_name))
                except Exception as e:
                    print(f"[Dispatch] Error moving output: {e}")

    # --- Final Cleanup ---
    print("[Dispatch] All files processed. Running Cleanup...")
    cleanup_script = os.path.join(tools_dir, "cleanup.py")
    try:
        # Cleanup is silent
        subprocess.run([python_exe, cleanup_script], cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Dispatch] Cleanup error: {e}")
        
    print("[Dispatch] Done.")

if __name__ == "__main__":
    main()