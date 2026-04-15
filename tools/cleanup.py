import os
import glob
import shutil

def cleanup_workspace():
    # Get the current working directory (should be root when called from dispatch)
    cwd = os.getcwd()
    print(f"Cleaning workspace in: {cwd}")

    # 1. Delete files matching *.ffindex and *.json in root
    file_extensions = ['*.ffindex', '*.json']
    for ext in file_extensions:
        files = glob.glob(os.path.join(cwd, ext))
        for file_path in files:
            try:
                os.remove(file_path)
            except OSError:
                pass

    # 2. Delete 'logs' directory
    logs_dir = os.path.join(cwd, 'logs')
    if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
        try:
            shutil.rmtree(logs_dir)
            print("Deleted folder: logs")
        except OSError as e:
            print(f"Error deleting logs folder: {e}")

    # 3. Clean 'videos-input' folder (remove specific files and all subfolders)
    videos_input_dir = os.path.join(cwd, 'videos-input')
    if os.path.exists(videos_input_dir) and os.path.isdir(videos_input_dir):
        # Remove specific files
        files_to_remove = ['Auto-Boost-Essential.py', 'SvtAv1EncApp.exe', 'ffms2.dll']
        for file_name in files_to_remove:
            file_path = os.path.join(videos_input_dir, file_name)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_name} from videos-input")
                except OSError as e:
                    print(f"Error deleting file {file_name}: {e}")
        
        # Remove all subfolders
        for item in os.listdir(videos_input_dir):
            item_path = os.path.join(videos_input_dir, item)
            if os.path.isdir(item_path):
                try:
                    shutil.rmtree(item_path)
                    print(f"Deleted subfolder: {item} from videos-input")
                except OSError as e:
                    print(f"Error deleting subfolder {item}: {e}")
    else:
        print("Directory 'videos-input' not found; skipping its cleanup.")

    # 4. Standard cleanup for leftover folders (like *-source in root if any)
    for item in os.listdir(cwd):
        item_path = os.path.join(cwd, item)
        if os.path.isdir(item_path):
            if (item.endswith("-source") or 
                item.endswith("-source_scenedetect.scene-detection.tmp") or 
                (item.startswith(".") and item != ".git")): # safety check
                
                try:
                    shutil.rmtree(item_path)
                    print(f"Deleted temp folder: {item}")
                except OSError:
                    pass

if __name__ == "__main__":
    cleanup_workspace()