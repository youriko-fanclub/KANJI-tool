#!/usr/bin/python3
#coding:utf-8


import sys
import os
import toml

class HppGenerator:
    TYPE_DICT = { 'string': 's3d::String'}

    def __init__(self, indent:str):
        self.indent = indent
        self.header:str
        self.namespace_begin:str
        self.namespace_end:str
        self.class_body:str

    def concatenate(self) -> str:
        full_text  = self.header + '\n'
        full_text += self.namespace_begin + '\n'
        full_text += self.class_body + '\n'
        full_text += self.namespace_end + '\n'
        return full_text

    def generateHeader(self, need_ids_hpp:bool):
        self.header = '#pragma once\n'
        if need_ids_hpp:
            self.header += '#include "IDs.hpp"\n'

    def generateNameSpaceBegin(self):
        self.namespace_begin  = 'namespace kanji {\n'
        self.namespace_begin += 'namespace md {\n'

    def generateNameSpaceEnd(self):
        self.namespace_end  = '}\n'
        self.namespace_end += '}\n'

    def generateClassBody(self, data_type_name:str, fields:dict):
        getter = ''
        field = ''
        ctor_declaration = self.indent + 'Master%s(' % data_type_name
        ctor_definition = ''
        for key in fields:
            field_type, return_type = self.read_type(fields[key])
            getter += self.indent + '%s %s() const { return m_%s; }\n' % (return_type, key, key)
            field  += self.indent + '%s m_%s;\n' % (field_type, key)
            ctor_declaration += '%s %s, ' % (field_type, key)
            ctor_definition += self.indent + 'm_%s(%s),\n' % (key, key)
        ctor_declaration = ctor_declaration.rstrip(', ')
        ctor_declaration += ') :\n'
        ctor_definition = ctor_definition.rstrip(',\n')
        ctor_definition += ' {}\n'
        self.generateClassBodyImpl(data_type_name, getter, field, ctor_declaration + ctor_definition)

    def generateClassBodyImpl(self, data_type_name:str, getter:str, field:str, constructor:str):
        self.class_body  = 'class Master%s {\n' % data_type_name
        self.class_body += 'public: // public getter\n'
        self.class_body += getter
        self.class_body += 'private: // field\n'
        self.class_body += field
        self.class_body += 'public: // ctor\n'
        self.class_body += constructor
        self.class_body += '};\n'

    def read_type(self, type_string:str):
        prefix_id = 'ID:'
        heavy_object = [ 'string' ]
        if type_string.startswith(prefix_id):
            field_type = type_string.lstrip(prefix_id) + 'ID'
        else:
            if type_string in HppGenerator.TYPE_DICT:
                field_type = HppGenerator.TYPE_DICT[type_string]
            else:
                field_type = type_string
        if type_string in heavy_object:
            return_type = 'const %s&' % field_type
        else:
            return_type = field_type
        return (field_type, return_type)


class MasterDataTypeInfo:
    INDENT = '    '

    def __init__(self, toml:dict, directory:str):
        self.directory = directory
        self.data_type_name = toml['data_type_name']
        self.fields = toml['field']

    def log(self):
        print('// %s --------------------' % self.data_type_name)
        for key in self.fields:
            print('%s %s' % (self.fields[key], key))
        print('// --------------------')

    def output(self, directory:str, filename:str, text:str):
        file_path = directory + '/' + filename
        print('create file:%s' % file_path)
        print(text)
        # f = open(file_path,'w') # なければ生成/あれば上書き
        # f.write(text)
        # f.close()

    def createHpp(self):
        hpp_generator = HppGenerator('    ')
        hpp_generator.generateHeader(False)
        hpp_generator.generateNameSpaceBegin()
        hpp_generator.generateClassBody(self.data_type_name, self.fields)
        hpp_generator.generateNameSpaceEnd()
        full_text = hpp_generator.concatenate()
        self.output(self.directory, self.data_type_name + ".hpp", full_text)


class MasterDataTypeManager:
    MASTER_DATA_DIRECTORY = 'KANJI-asset/schema/master/'
    MASTER_DATA_TOML = 'masterdata.toml'

    def __init__(self):
        self.dict_toml = self.load()
        self.dict_info = dict()
        self.read()

    def load(self):
        filepath = MasterDataTypeManager.MASTER_DATA_DIRECTORY + MasterDataTypeManager.MASTER_DATA_TOML
        return toml.load(open(filepath))

    def read(self):
        for key in self.dict_toml['masterdata']:
            self.dict_info[key] = dict()
            for md_toml in self.dict_toml['masterdata'][key].values():
                md = MasterDataTypeInfo(md_toml, key)
                self.dict_info[key][md.data_type_name] = md

if __name__ == "__main__":
    mgr = MasterDataTypeManager()
    mgr.read()


