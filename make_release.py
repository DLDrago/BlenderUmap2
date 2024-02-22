from io import StringIO
from io import StringIO
import os
import zipfile
import glob

try:
    version = os.popen("git rev-list --count HEAD").read().strip()
    int(version)
    branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
except ValueError:
    print("not a git repository?")
    version = "0"
    branch = "unknown"

minor = version[-1:]
major = version[:-1]
version = f"{major}.{minor}"

print(f"version: {version}")

version_f = StringIO()
version_f.write(f"__version__ = '{version}'\n")
version_f.write(f"branch = '{branch}'")

def add_files_to_zip(zip_file: zipfile.ZipFile, base_path ,pattern, prefix='', recursive=True):
    for file in glob.glob(pattern, recursive=recursive):
        zipname = os.path.join(prefix, os.path.relpath(file, base_path))
        zip_file.write(file, zipname)

try: os.mkdir('release')
except FileExistsError: pass

for target in ["osx-x64", "win-x64", "linux-x64"]: # we can do this because we don't need CUE4Parse-Natives
    try:
        for f in glob.glob("./BlenderUmap/bin/Publish/**"):
            os.remove(f)
    except FileNotFoundError: pass

    code = os.system("dotnet publish BlenderUmap -c Release -r %s --no-self-contained -o \"./BlenderUmap/bin/Publish/\" -p:PublishSingleFile=true -p:DebugType=None -p:DebugSymbols=false -p:IncludeAllContentForSelfExtract=true -p:AssemblyVersion=%s -p:FileVersion=%s"%(target, version, version))
    if code != 0:
        raise Exception(f"dotnet publish failed with code {code}")
    zipf = zipfile.ZipFile(f'release/BlenderUmap-{version}-{target}.zip', 'w', zipfile.ZIP_LZMA, allowZip64=True, compresslevel=9)
    add_files_to_zip(zipf, "./BlenderUmap/bin/Publish/", "./BlenderUmap/bin/Publish/**", "BlenderUmap/", False)
    add_files_to_zip(zipf, "./Importers/Blender/", "./Importers/Blender/**/*.py", "BlenderUmap/", True)

    zipf.writestr("BlenderUmap/__version__.py", version_f.getvalue())
    zipf.close()
version_f.close()
