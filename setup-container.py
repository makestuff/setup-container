#!/usr/bin/env python3
import errno
import os
import io
import re
import sys
import shutil
import zipfile
import tarfile
import glob
import json
import urllib.request
from jsmin import jsmin
from pathlib import Path

# Get code-server
def fetch_code_server(version):
  url = "http://makestuff.de/extensions/code-server-{}-linux-amd64.tar.gz".format(version)
  targz = urllib.request.urlopen(url).read()
  archive = tarfile.open(fileobj=io.BytesIO(targz))
  archive.extractall()

# Read the devcontainer.json file, and extract the list of URLs for the extensions, and the
# settings as a string.
def extract_from_devcontainer_json():
  with open('.devcontainer/devcontainer.json') as js_file:
    minified = jsmin(js_file.read())
  data = json.loads(minified)
  settings = json.dumps(data["settings"], indent=4, sort_keys=True)
  extensions = []
  for i in data["extensions"]:
    (name, version) = i.split("@")
    url = "http://makestuff.de/extensions/{0}-{1}.vsix".format(name, version)
    extensions.append(url)
  postCreateCommand = data["postCreateCommand"]
  return (settings, extensions, postCreateCommand)

# Get a VSIX blob from a URL, and install it in todir
def install_from_url(url, todir):
  vsix = urllib.request.urlopen(url).read()
  zipdata = zipfile.ZipFile(io.BytesIO(vsix))
  with zipdata.open("extension/package.json") as pj:
    metadata = json.loads(pj.read())
    name = "{}.{}".format(metadata["publisher"], metadata["name"])
    version = metadata["version"]
  print("{}-{}".format(name, version))
  existing = glob.glob(os.path.join(todir, name + "-*"))
  for dir in existing:
    shutil.rmtree(dir)
  shutil.rmtree(os.path.join(todir, "extension"), ignore_errors=True)
  for file in zipdata.namelist():
    if file.startswith('extension/'):
      zipdata.extract(file, todir)
  os.rename(os.path.join(todir, "extension"), os.path.join(todir, "{}-{}".format(name, version)))

# Main entry point
if len(sys.argv) != 2:
  print("Synopsis: {} <git-url>".format(sys.argv[0]))
  sys.exit(1)

repo_url = sys.argv[1]
repo_name = os.path.splitext(os.path.basename(repo_url))[0]
home_dir = str(Path.home())
ready_file = os.path.join(home_dir, ".container-ready")
cs_ver = "3.8.1"

if not os.path.exists(ready_file):
  #EXTENSIONS_DIR = ".vscode-server/extensions"
  #SETTINGS_DIR   = ".vscode-server/data/Machine"
  EXTENSIONS_DIR = ".local/share/code-server/extensions"
  SETTINGS_DIR   = ".local/share/code-server/User"
  os.chdir("/var/tmp")
  print(u"\u001b[32mFetching code-server...\u001b[0m");
  fetch_code_server(cs_ver)
  print(u"\n\u001b[32mCloning repository...\u001b[0m");
  os.system("git clone --recursive {}".format(repo_url))
  os.chdir(repo_name)
  print(u"\n\u001b[32mInstalling extensions and settings...\u001b[0m");
  (settings, extensions, postCreateCommand) = extract_from_devcontainer_json()
  for url in extensions:
    install_from_url(url, os.path.join(home_dir, EXTENSIONS_DIR))
  os.makedirs(os.path.join(home_dir, SETTINGS_DIR))
  with open(os.path.join(home_dir, SETTINGS_DIR, "settings.json"), "w") as settings_file:
    settings_file.write(settings)
  print(u"\n\u001b[32mRunning postCreateCommand...\u001b[0m");
  os.system(postCreateCommand)
  Path(ready_file).touch()
  print()

print(u"\u001b[32mLaunching code-server...\u001b[0m");
os.system("/var/tmp/code-server-{}-linux-amd64/bin/code-server --bind-addr 0.0.0.0:8080 --auth none /var/tmp/{}".format(cs_ver, repo_name))
