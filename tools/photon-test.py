import os
import subprocess
import sys
import json

def get_source_duration(mkvmerge_exe, source_file):
    """
    Uses mkvmerge -J to get the default_duration of the video track.
    """
    if not os.path.exists(source_file):
        return None
        
    cmd = [mkvmerge_exe, "-J", source_file]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        data = json.loads(result.stdout)
        for track in data.get("tracks", []):
            if track.get("type") == "video":
                props = track.get("properties", {})
                duration = props.get("default_duration")
                if duration:
                    return f"{duration}ns"
    except Exception as e:
        print(f"Warning: Could not detect FPS/Duration: {e}")
    return None

def main():
    # --- 1. SETUP PATHS ---
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)          # ...\tools
    root_dir = os.path.dirname(script_dir)             # ...\Auto-Boost-Essential-portable
    
    mkvmerge_exe = os.path.join(root_dir, "tools", "MKVToolNix", "mkvmerge.exe")
    
    # Files are expected in the current working directory (extras)
    source_file = "0source.mkv"
    
    # --- 2. DETECT FPS ---
    print("\n--- Post-Processing: Fixing Framerates ---")
    duration_str = get_source_duration(mkvmerge_exe, source_file)
    
    if duration_str:
        print(f"Source Duration Detected: {duration_str}")
    else:
        print("Warning: Source duration not found. Output may default to 24fps.")

    # --- 3. REMUX TEMP FILES ---
    # Levels correspond to grav1synth.bat output: temp2, temp4, temp6, temp8, temp10
    levels = [2, 4, 6, 8, 10]
    
    files_processed = 0

    for level in levels:
        # Input: temp2.mkv (from batch)
        # Output: photon02.mkv (zero padded)
        temp_file = f"temp{level}.mkv"
        final_file = f"photon{level:02d}.mkv"
        
        # Only process if the temp file exists
        if os.path.exists(temp_file):
            print(f"Remuxing {temp_file} -> {final_file}...")
            
            cmd_remux = [mkvmerge_exe, "-o", final_file]
            
            # Apply the source framerate to the grain file
            if duration_str:
                cmd_remux.extend(["--default-duration", f"0:{duration_str}"])
            
            cmd_remux.append(temp_file)
            
            res = subprocess.run(cmd_remux, capture_output=True, text=True)
            
            if res.returncode == 0:
                files_processed += 1
                # Delete the temp file to keep folder clean
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            else:
                print(f"Error remuxing {temp_file}:\n{res.stderr}")

    if files_processed == 0:
        print("No temp files found to process.")
    else:
        print(f"Successfully processed {files_processed} files.")

if __name__ == "__main__":
    main()