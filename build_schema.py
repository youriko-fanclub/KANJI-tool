#!/usr/bin/python3
#coding:utf-8

from pathlib import Path
import sys
import os
import toml
import master_type

class PathStr:
    ROOT = '/Users/kazuaki/Documents/develop/youriko/KANJI/'
    CLIENT = 'KANJI-client/'
    DX4SIV3D = 'KANJI-client/Game/KANJI/dx4siv3d/'
    ASSET = 'KANJI-client/Game/KANJI/KANJI-asset/'
    SCHEMA = 'schema/'
    TOOL = 'tool/'

class MasterDataActual:
    def __init__(self, toml):
        self.fields = toml

if __name__ == '__main__':
    path_schema = Path(PathStr.ROOT + PathStr.ASSET + PathStr.SCHEMA)
    path_src = path_schema / 'master' / 'class'
    path_dst = path_schema / 'master_header'
    md_type_mgr = master_type.MasterDataTypeManager()

    for path_toml in path_src.glob('**/*.toml'): # e.g. 'class/kanji/KanjiParam'
        type_name = path_toml.stem # 'KanjiParam'
        directories = path_toml.parent.relative_to(path_src) # kanji
        type_info = md_type_mgr.at(type_name, str(directories))
        file_dst = path_dst / directories
        os.makedirs(file_dst, exist_ok=True)
        os.chmod(file_dst, 0o755)
        type_info.createHpp(file_dst)
