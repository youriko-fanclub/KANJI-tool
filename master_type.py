#!/usr/bin/python3
#coding:utf-8

from pathlib import Path
import os
import shutil
import toml
from repository_path import KanjiPath
from logging import getLogger, basicConfig, DEBUG
logger = getLogger(__name__)

class HppGeneratorBase:
    def __init__(self, indent:str):
        self.indent = indent
        self.build_info:str
        self.preprocessor:str
        self.namespace_begin:str
        self.namespace_end:str
        self.class_body:str

    def generate(self, data_type_name:str, fields:dict) -> str:
        self.generate_class_body(data_type_name, fields)
        self.generate_build_info(data_type_name)
        self.generate_preprocessor(data_type_name, fields)
        self.generate_namespace_begin()
        self.generate_namespace_end()
        return self.concatenate()

    def concatenate(self) -> str:
        full_text  = self.build_info
        full_text += self.preprocessor + '\n'
        full_text += self.namespace_begin + '\n'
        full_text += self.class_body + '\n'
        full_text += self.namespace_end + '\n'
        return full_text

    def generate_build_info(self, data_type_name:str):
        self.build_info = '// This file is generated from %s.toml\n' % data_type_name

    def generate_preprocessor(self, data_type_name:str, fields:dict):
        pass

    def generate_namespace_begin(self):
        self.namespace_begin  = 'namespace kanji {\n'
        self.namespace_begin += 'namespace md {\n'

    def generate_namespace_end(self):
        self.namespace_end  = '}\n'
        self.namespace_end += '}\n'

    def generate_class_body(self, data_type_name:str, field_dict:dict):
        pass

    def to_camel_case(self, snake_str:str):
        first, *others = snake_str.split('_')
        return ''.join([first.lower(), *map(str.title, others)])


class DataHppGenerator(HppGeneratorBase):
    def generate_preprocessor(self, data_type_name:str, fields:dict):
        need_ids_hpp = False
        for field in fields.values():
            if field.is_id:
                need_ids_hpp = True
        self.preprocessor = '#pragma once\n'
        if need_ids_hpp:
            self.preprocessor += '#include "IDs.hpp"\n'

    def generate_class_body(self, data_type_name:str, field_dict:dict):
        getters = ''
        fields = ''
        ctor_declaration = self.indent + 'Master%s(' % data_type_name
        ctor_definition = ''
        for field in field_dict.values():
            field_type, pass_type = field.read_types()
            # e.g. const s3d::String& label() const { return m_label; }
            getters += self.indent + '%s %s() const { return m_%s; }\n' % (pass_type, self.to_camel_case(field.name), field.name)
            # e.g. s3d::String m_label;
            fields  += self.indent + '%s m_%s;\n' % (field_type, field.name)
            # e.g. MasterHoge(const s3d::String& label, ... ):
            ctor_declaration += '%s %s, ' % (pass_type, field.name)
            # e.g. m_label(label), ... {}
            ctor_definition += self.indent + 'm_%s(%s),\n' % (field.name, field.name)
        ctor_declaration = ctor_declaration.rstrip(', ')
        ctor_declaration += ') :\n'
        ctor_definition = ctor_definition.rstrip(',\n')
        ctor_definition += ' {}\n'
        self.generateClassBodyImpl(data_type_name, getters, fields, ctor_declaration + ctor_definition)

    def generateClassBodyImpl(self, data_type_name:str, getter:str, field:str, constructor:str):
        self.class_body  = 'class Master%s {\n' % data_type_name
        self.class_body += 'public: // public getter\n'
        self.class_body += getter
        self.class_body += 'private: // field\n'
        self.class_body += field
        self.class_body += 'public: // ctor\n'
        self.class_body += constructor
        self.class_body += '};\n'


class RepositoryHppGenerator(HppGeneratorBase):
    def generate_preprocessor(self, data_type_name:str, fields:dict):
        need_ids_hpp = False
        for field in fields.values():
            if field.is_id:
                need_ids_hpp = True
        self.preprocessor  = '#pragma once\n'
        self.preprocessor += '#include "Singleton.hpp"\n'
        self.preprocessor += '#include "MasterDataRepository.hpp"\n'
        self.preprocessor += '#include "Master%s.hpp"\n' % data_type_name
        if need_ids_hpp:
            self.preprocessor += '#include "IDs.hpp"\n'

    def generate_class_body(self, data_type_name:str, field_dict:dict):
        primary_key_type = None
        for field in field_dict.values():
            if field.is_primary_key:
                if field.is_id:
                    primary_key_type = field.type_name + 'ID'
                else:
                    primary_key_type = field.type_name
        self.class_body  = 'class Master%sRepository :\n' % data_type_name
        self.class_body += self.indent + 'public dx::md::MasterDataRepository<%s, %s>,\n' % (primary_key_type, data_type_name)
        self.class_body += self.indent + 'public dx::cmp::Singleton<Master%sRepository> {\n' % data_type_name
        self.class_body += 'protected function: // protected function\n'
        self.class_body += self.indent + 'void initialize();\n'
        self.class_body += 'public: // ctor\n'
        self.class_body += self.indent + 'Master%sRepository() { initialize(); }\n' % data_type_name
        self.class_body += '};\n'


class MDField:
    TYPE_DICT = { 'string': 's3d::String'}
    HEAVY_OBJECT = [ 'string' ]

    def __init__(self, name:str, type_attribute:str):
        self.name = name
        type_name, *attributes = type_attribute.split(':')
        self.type_name = type_name
        self.is_id = False
        self.is_primary_key = False
        for attribute in attributes:
            if attribute == 'ID':
                self.is_id = True
            if attribute == 'PKey':
                self.is_primary_key = True

    def read_types(self) -> (str, str):
        # メンバ変数の型
        if self.is_id:
            field_type = self.type_name + 'ID'
        else:
            if self.type_name in MDField.TYPE_DICT:
                field_type = MDField.TYPE_DICT[self.type_name]
            else:
                field_type = self.type_name
        # 引数/返り値の型
        if self.type_name in MDField.HEAVY_OBJECT:
            pass_type = 'const %s&' % field_type
        else:
            pass_type = field_type
        return (field_type, pass_type)


class MasterDataTypeInfo:
    def __init__(self, toml:dict):
        self.data_type_name = toml['data_type_name']
        self.primary_key = None
        self.fields = self.read_fields(toml['field'])

    def read_fields(self, field_toml:dict) -> dict:
        fields = dict()
        for name, type_attribute in field_toml.items():
            field = MDField(name, type_attribute)
            fields[name] = field
            if field.is_primary_key:
                if self.primary_key != None:
                    logger.critical('There are multiple primary keys.')
                self.primary_key = field.name
        if self.primary_key == None:
            logger.critical('There is no primary key.')
        return fields

    def log(self):
        print('// %s --------------------' % self.data_type_name)
        for field in self.fields.values():
            if field.is_primary_key:
                primary_icon = '*'
            else:
                primary_icon = ' '
            if field.is_id:
                constraint = ' (ID: ranged)'
            else:
                constraint = ''
            print('%s%s %s%s' % (primary_icon, field.type_name, field.name, constraint))
        print('// --------------------')

    def create_hpp(self, path:Path, key:str):
        indent = '    '
        # MasterHoge.hpp
        data_hpp_generator = DataHppGenerator(indent)
        data_full_text = data_hpp_generator.generate(self.data_type_name, self.fields)
        self.output(path / 'class' / key, self.data_type_name + ".hpp", data_full_text)
        # MasterHogeRepository.hpp
        repo_hpp_generator = RepositoryHppGenerator(indent)
        repo_full_text = repo_hpp_generator.generate(self.data_type_name, self.fields)
        self.output(path / 'repository' / key, self.data_type_name + "Repository.hpp", repo_full_text)

    def output(self, path:Path, filename:str, text:str):
        os.makedirs(path, exist_ok=True)
        file_path = path / filename
        logger.info('create file: %s' % file_path.relative_to(KanjiPath.absolute('md_header')))
        with open(file_path,'w') as f:
            f.write(text)


class MasterDataTypeManager:
    def __init__(self):
        self.dict_toml = None
        self.dict_info = dict()
        self.load()
        self.read()

    def load(self):
        with open(KanjiPath.absolute('md_toml')) as f:
            self.dict_toml = toml.load(f)

    def read(self):
        for key in self.dict_toml['masterdata']:
            self.dict_info[key] = dict()
            for md_toml in self.dict_toml['masterdata'][key].values():
                md = MasterDataTypeInfo(md_toml)
                self.dict_info[key][md.data_type_name] = md

    def at(self, type_name:str, key:str) -> MasterDataTypeInfo:
        return self.dict_info[key][type_name]

    def create_hpp(self, path_dst:Path):
        for key in self.dict_info:
            for value in self.dict_info[key].values():
                value.create_hpp(path_dst, key)

if __name__ == "__main__":
    basicConfig(level=DEBUG)
    dest_dir = KanjiPath.absolute('md_header')
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    mgr = MasterDataTypeManager()
    mgr.create_hpp(dest_dir)

