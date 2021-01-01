#!/usr/bin/python3
#coding:utf-8


class CppSourceGeneratorBase:
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


class DataHppGenerator(CppSourceGeneratorBase):
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


class RepositoryHppGenerator(CppSourceGeneratorBase):
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


class RepositoryCppGenerator(CppSourceGeneratorBase):
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
