import os
import glob
import re
import subprocess
import tempfile
import sys

def get_script_version():
    """Extracts the latest version number from changelog.txt in the root dir."""
    # Since we run in 'temp', root is one level up
    changelog_path = os.path.join("..", "changelog.txt")
    version = "Unknown"
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Grabs the first version match it finds, which should be the latest 
                # at the top of a reverse-chronological changelog.
                match = re.search(r"v(\d+\.\d+)", content)
                if match:
                    version = "v" + match.group(1)
        except Exception as e:
            # Silent warning or print to stderr to avoid confusing dispatch output
            pass
    return version

def get_essential_version():
    """Executes SvtAv1EncApp.exe --version and parses the output."""
    exe_path = os.path.join("..", "tools", "SvtAv1EncApp.exe")
    if not os.path.exists(exe_path):
        return "SVT-AV1-Essential_Unknown"
    
    try:
        # Execute the app to get the version string
        result = subprocess.run([exe_path, "--version"], capture_output=True, text=True, check=True)
        # Capture stdout (or stderr if stdout is empty)
        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        
        # Take the first line in case of multi-line output
        first_line = output.split('\n')[0].strip()
        
        # Remove "-Essential (release)" from the tagging string
        clean_version = first_line.replace("-Essential (release)", "").strip()
        
        return clean_version if clean_version else "SVT-AV1-Essential_Unknown"
    except Exception:
        return "SVT-AV1-Essential_Unknown"

def get_active_batch_filename():
    """Scans ../tools/ for the marker file created by the .bat script."""
    # Marker format: ../tools/bat-used-[BATCH_FILENAME].txt
    tools_dir = os.path.join("..", "tools")
    pattern = os.path.join(tools_dir, "bat-used-*.txt")
    files = glob.glob(pattern)
    
    if not files:
        # This is expected if run manually or if marker was missed, but strict for dispatch
        return None
    
    marker_file = files[0]
    filename = os.path.basename(marker_file) 
    
    # Remove prefix "bat-used-" and suffix ".txt" to get the original batch name
    batch_name = filename.replace("bat-used-", "").replace(".txt", "")
    
    # Clean up the marker file immediately
    try:
        os.remove(marker_file)
    except OSError:
        pass
        
    return batch_name

def parse_batch_settings(batch_filename):
    """Reads the .bat file and extracts arguments."""
    settings = {
        "quality": "medium", 
        "ssimu2": False,
        "resume": False,
        "verbose": False,
        "fast_speed": None,
        "final_speed": None,
        "photon_noise": None,
        "final_params": ""
    }
    
    # The batch file is likely in the Root directory (..), not in tools or temp
    batch_path = os.path.join("..", batch_filename)
    
    if not os.path.exists(batch_path):
        # Fallback: check inside tools if not in root
        batch_path_tools = os.path.join("..", "tools", batch_filename)
        if os.path.exists(batch_path_tools):
            batch_path = batch_path_tools
        else:
            return settings

    batch_vars = {}

    try:
        with open(batch_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                
                # 1. Parse 'set' variables
                set_match = re.match(r'set\s+"?([^"=]+)=([^"]*)"?', stripped, re.IGNORECASE)
                if set_match:
                    key = set_match.group(1).upper()
                    val = set_match.group(2)
                    batch_vars[key] = val

                # 2. Parse flags present in the dispatch.py call
                if "dispatch.py" in stripped:
                    if "--ssimu2" in stripped: settings["ssimu2"] = True
                    if "--resume" in stripped: settings["resume"] = True
                    if "--verbose" in stripped: settings["verbose"] = True
                    
                    pn_match = re.search(r'--photon-noise\s+(\d+)', stripped)
                    if pn_match: settings["photon_noise"] = pn_match.group(1)

        # 3. Map captured variables
        if "QUALITY" in batch_vars: settings["quality"] = batch_vars["QUALITY"]
        if "FAST_SPEED" in batch_vars: settings["fast_speed"] = batch_vars["FAST_SPEED"]
        if "FINAL_SPEED" in batch_vars: settings["final_speed"] = batch_vars["FINAL_SPEED"]
        if "FINAL_PARAMS" in batch_vars: 
            settings["final_params"] = batch_vars["FINAL_PARAMS"].strip()
            # If photon_noise is in final_params but wasn't caught in dispatch call, extract it
            pn_match = re.search(r'--photon-noise\s+(\d+)', settings["final_params"])
            if pn_match and not settings["photon_noise"]:
                settings["photon_noise"] = pn_match.group(1)
                
        if "PHOTON_NOISE" in batch_vars: settings["photon_noise"] = batch_vars["PHOTON_NOISE"]

    except Exception:
        pass
        
    return settings

def get_crf_string(quality):
    """Maps quality string to CRF display string."""
    q = quality.lower()
    if q == "higher":
        return "--crf 20(variable)"
    elif q == "high":
        return "--crf 25(variable)"
    elif q == "medium":
        return "--crf 30(variable)"
    elif q == "low":
        return "--crf 35(variable)"
    elif q == "lower":
        return "--crf 40(variable)"
    elif q.isdigit():
        return f"--crf {q}(variable)"
    else:
        return "--crf 30(variable)"

def apply_tag_to_file(filepath, encoding_settings):
    """Writes a temp XML and applies it to the MKV file via mkvpropedit."""
    # We create the xml in the current temp dir
    
    xml_template = f"""<?xml version="1.0"?>
<Tags>
  <Tag>
    <Targets>
      <TrackUID>1</TrackUID>
    </Targets>
    <Simple>
      <Name>ENCODING_SETTINGS</Name>
      <String>{encoding_settings}</String>
    </Simple>
  </Tag>
</Tags>
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="w", encoding="utf-8", dir=".") as tmp:
        tmp.write(xml_template)
        tmp_path = tmp.name
    
    # Path to mkvpropedit needs to step out of temp to tools
    mkvpropedit_path = os.path.join("..", "tools", "MKVToolNix", "mkvpropedit.exe")
    
    try:
        subprocess.run(
            [mkvpropedit_path, filepath, "--tags", "track:v1:" + tmp_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        # Tagging is non-critical
        pass
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

def main():
    # 1. Identify which batch file launched this script
    batch_file = get_active_batch_filename()
    if not batch_file:
        return 

    # 2. Parse that specific batch file for settings
    args = parse_batch_settings(batch_file)
    
    # 3. Gather dynamic data
    script_version = get_script_version()
    essential_version = get_essential_version()
    
    # 4. Build the Info String
    info_parts = [f"Auto-Boost-Essential Portable {script_version}"]
    
    if args["quality"] != "medium":
        info_parts.append(f"--quality {args['quality']}")
    
    if args["ssimu2"]: info_parts.append("--ssimu2")
    if args["resume"]: info_parts.append("--resume")
    if args["verbose"]: info_parts.append("--verbose")
    if args["fast_speed"]: info_parts.append(f"--fast-speed {args['fast_speed']}")
    if args["final_speed"]: info_parts.append(f"--final-speed {args['final_speed']}")
    if args["photon_noise"]: info_parts.append(f"--photon-noise {args['photon_noise']}")
    
    info_parts.append(essential_version)
    
    # 5. Build the Settings String
    settings_parts = ["settings:"]
    
    if args["final_speed"]:
        settings_parts.append(f"--preset {args['final_speed']}")
    
    settings_parts.append(get_crf_string(args["quality"]))
    
    if args["final_params"]:
        settings_parts.append(args["final_params"])

    full_string = " ".join(info_parts) + " " + " ".join(settings_parts)

    # 6. Apply to files
    # dispatch.py runs this inside 'temp', and files have not been moved to output yet.
    # They are named "*-output.mkv" inside the current folder.
    files = glob.glob("*-output.mkv")
    
    for f in files:
        apply_tag_to_file(f, full_string)

if __name__ == "__main__":
    main()