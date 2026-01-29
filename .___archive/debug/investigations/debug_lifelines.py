import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print("Sys Path:")
for p in sys.path:
    print(f"  - {p}")

print("\nAttempting to import lifelines...")
try:
    import lifelines
    print(f"SUCCESS: lifelines imported from {lifelines.__file__}")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"FAILURE (Other): {e}")

# Check if the user path exists
user_site = r"c:\users\sinas\appdata\roaming\python\python313\site-packages"
print(f"\nChecking user site: {user_site}")
if os.path.exists(user_site):
    print("  - Exists")
    print(f"  - Contents: {os.listdir(user_site)[:10]}")
    
    # Try appending and importing again if failed
    if user_site not in sys.path:
        print("  - Appending to sys.path...")
        sys.path.append(user_site)
        try:
            import lifelines
            print(f"SUCCESS (After append): lifelines imported from {lifelines.__file__}")
            print("lifelines dir:", dir(lifelines))
            
            # Check fitters submodule
            if 'fitters' in dir(lifelines):
                from lifelines import fitters
                print("lifelines.fitters dir:", dir(fitters))
                
                # Check for fine_gray_fitter submodule or class
                if 'fine_gray_fitter' in dir(fitters):
                    from lifelines.fitters import fine_gray_fitter
                    print("fine_gray_fitter module found!")
                    print("module dir:", dir(fine_gray_fitter))
                elif 'FineGrayFitter' in dir(fitters):
                     print("FineGrayFitter found in lifelines.fitters")

        except Exception as e:
            print(f"FAILURE (After append): {e}")
else:
    print("  - Does NOT exist")
