#!/usr/bin/python3
#coding:utf-8

from pathlib import Path
import os
import shutil
import toml
from repository_path import KanjiPath
from cpp_source_generator import DataHppGenerator, RepositoryHppGenerator, RepositoryCppGenerator
from master_type import MasterDataTypeInfo, MasterDataTypeManager
from logging import getLogger, basicConfig, DEBUG, INFO
logger = getLogger(__name__)

def output(file_path:Path, text:str):
    os.makedirs(file_path.parent.absolute(), exist_ok=True)
    logger.info('create file: %s' % file_path.relative_to(KanjiPath.absolute('md_header')))
    with open(file_path,'w') as f:
        f.write(text)


def create_cpp_source(generator, type_info:MasterDataTypeInfo, file_path:Path):
    full_text = generator.generate(type_info.data_type_name, type_info.fields)
    output(file_path, full_text)

def create_cpp_sources_impl(type_info:MasterDataTypeInfo, path:Path, key:str):
    indent = '    '
    # MasterHoge.hpp
    create_cpp_source(
        DataHppGenerator(indent),
        type_info,
        path / 'class' / key / (type_info.data_type_name + '.hpp'))
    # MasterHogeRepository.hpp
    create_cpp_source(
        RepositoryHppGenerator(indent),
        type_info,
        path / 'repository' / key / (type_info.data_type_name + 'Repository.hpp'))
    # MasterHogeRepository.cpp
    create_cpp_source(
        RepositoryCppGenerator(indent),
        type_info,
        path / 'repository' / key / (type_info.data_type_name + 'Repository.cpp'))

def create_cpp_sources(mgr:MasterDataTypeManager, path_dst:Path):
    for key in mgr.dict_info:
        for value in mgr.dict_info[key].values():
            create_cpp_sources_impl(value, path_dst, key)

if __name__ == "__main__":
    basicConfig(level=INFO)
    dest_dir = KanjiPath.absolute('md_header')
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    mgr = MasterDataTypeManager()
    # mgr.create_cpp_source(dest_dir)
    create_cpp_sources(mgr, dest_dir)
