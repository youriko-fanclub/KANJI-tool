#!/usr/bin/python3
#coding:utf-8

import toml
from repository_path import KanjiPath
from logging import getLogger, basicConfig, DEBUG
logger = getLogger(__name__)


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
        self.raw_type, self.pass_type = self.read_types()

    def read_types(self) -> (str, str):
        # メンバ変数の型
        if self.is_id:
            raw_type = self.type_name + 'ID'
        else:
            if self.type_name in MDField.TYPE_DICT:
                raw_type = MDField.TYPE_DICT[self.type_name]
            else:
                raw_type = self.type_name
        # 引数/返り値の型
        if self.type_name in MDField.HEAVY_OBJECT:
            pass_type = 'const %s&' % raw_type
        else:
            pass_type = raw_type
        return (raw_type, pass_type)


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


if __name__ == "__main__":
    basicConfig(level=DEBUG)
    mgr = MasterDataTypeManager()

