#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import os
import pathlib
import shutil
import stat
import sys
import urllib.request
import zipfile

HOME_DIR = pathlib.Path.home()
SOURCE_DIR = HOME_DIR.joinpath("sources")
ES_FILE = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.7.zip"
ES_SHA = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.7.zip.sha512"
CHUNK_SIZE = 16 * 1024
ES_LOCAL_FILE = SOURCE_DIR.joinpath(ES_FILE.split("/")[-1])
ES_SHA_LOCAL_FILE = SOURCE_DIR.joinpath(ES_SHA.split("/")[-1])
ES_LOCAL_DIR = SOURCE_DIR.joinpath("".join(ES_FILE.split("/")[-1].split(".zip")[:-1]))
ES_SCRIPT_PATH = ES_LOCAL_DIR.joinpath("bin/elasticsearch")


def create_source_dir():
    if not SOURCE_DIR.is_dir():
        pathlib.Path.mkdir(SOURCE_DIR)


def download_file(file_url, local_file):
    with open(local_file, 'wb') as my_file:
        with urllib.request.urlopen(file_url) as response:  # nosec
            shutil.copyfileobj(response, my_file, CHUNK_SIZE)


def unzip_file(file_path, dest_dir):
    with zipfile.ZipFile(file_path) as myzip:
        myzip.extractall(dest_dir)


def verify_sha(file_path, sha512_file):

    with open(file_path, 'rb') as my_file:
        file_content = my_file.read()
    with open(sha512_file) as my_sha_file:
        sha_file_content = my_sha_file.read()

    file_sha = hashlib.sha512(file_content).hexdigest()

    return file_sha == sha_file_content


def setup_symlink(src, dest):
    os.symlink(src, dest)


def make_scripts_executable(script_path):
    st = os.stat(str(script_path))
    os.chmod(str(script_path), st.st_mode | stat.S_IEXEC)


def install_es():
    try:
        create_source_dir()
        download_file(ES_FILE, ES_LOCAL_FILE)
        download_file(ES_SHA, ES_SHA_LOCAL_FILE)
        verify_sha(ES_LOCAL_FILE, ES_SHA_LOCAL_FILE)
        unzip_file(ES_LOCAL_FILE, SOURCE_DIR)
        setup_symlink(ES_LOCAL_DIR, SOURCE_DIR.joinpath("current"))
        make_scripts_executable(ES_SCRIPT_PATH)
        print("Elasticsearch has been installed in {0}".format(ES_LOCAL_DIR))
        sys.exit(0)
    except Exception as myException:
        print("Failed to installed, error is: {0}".format(myException))
        sys.exit(1)


if __name__ == "__main__":
    install_es()
