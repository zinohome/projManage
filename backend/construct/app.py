#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:19
# @Author  : ZhangJun
# @FileName: app.py

import os
import traceback
import simplejson as json
from jinja2 import Environment, FileSystemLoader

from utils.log import log as log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_DIR = os.path.join(BASE_DIR, 'construct')
DEF_PATH = os.path.join(DEF_DIR, 'app.json')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_DIR = os.path.join(BASE_DIR, 'construct')
DEF_PATH = os.path.join(DEF_DIR, 'app.json')

class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class App():
    def __init__(self):
        self.AppName = None
        self.AppTitle = None
        self.Description = None
        self.Version = None
        self.Author = None
        self.Cons = None
        self.Consdict = None
        self.AppVardicts = None
        self.readconfig()
        self.lod_models()

    def readconfig(self):
        try:
            with open(DEF_PATH, 'r', encoding="utf-8") as app_file:
                content = app_file.read()
            app_obj = json.loads(content, object_hook=obj)
            self.AppName = app_obj.AppName
            self.AppTitle = app_obj.AppTitle
            self.Description = app_obj.Description
            self.Version = app_obj.Version
            self.Author = app_obj.Author
            self.Cons = app_obj
            appdict = json.loads(content)
            self.Consdict = appdict
            self.Models = []
            self.Modeldicts = []
            self.AppVardicts = {item['name']: item for item in self.Consdict['AppVariables']}
        except Exception as exp:
            print('Exception at Appdef.readconfig() %s ' % exp)
            traceback.print_exc()

    def lod_models(self):
        try:
            for group in self.Cons.Groups:
                for model in group.models:
                    filepath = os.path.join(DEF_DIR,model.model_file)
                    with open(filepath, 'r', encoding="utf-8") as model_file:
                        content = model_file.read()
                        self.Models.append(json.loads(content, object_hook=obj))
                        self.Modeldicts.append(json.loads(content))
                    if len(model.submodels) > 0:
                        for submodel in model.submodels:
                            filepath = os.path.join(DEF_DIR, submodel.model_file)
                            with open(filepath, 'r', encoding="utf-8") as submodel_file:
                                content = submodel_file.read()
                                self.Models.append(json.loads(content, object_hook=obj))
                                self.Modeldicts.append(json.loads(content))
        except Exception as exp:
            print('Exception at Appdef.lodmodels() %s ' % exp)
            traceback.print_exc()

    def gen_models(self):
        # 定义文件目录 backend/construct
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        # 应用目录 backend
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        # 运行目录 backend/apps/admin
        runtimepath = os.path.abspath(os.path.join(apppath, 'apps/admin'))
        # 模版目录 backend/construct/tmpl
        tmplpath = os.path.abspath(os.path.join(basepath, 'tmpl'))
        # 输出目录 backend/construct/output
        outputpath = os.path.abspath(os.path.join(basepath, 'output'))
        log.debug("Generate models Starting ...")
        try:
            for model in self.Modeldicts:
                log.debug("Generate model for table: %s" % model['model_name'])
                env = Environment(loader=FileSystemLoader(tmplpath), trim_blocks=True, lstrip_blocks=True)
                template = env.get_template('model_tmpl.py')
                gencode = template.render(model)
                modelfilepath = os.path.abspath(os.path.join(outputpath, 'models/'+model['tablename'] + ".py"))
                with open(modelfilepath, 'w', encoding='utf-8') as gencodefile:
                    gencodefile.write(gencode)
                    gencodefile.close()
                #log.debug(gencode)
            log.debug("Generate models Completed ...")
        except Exception as exp:
            print('Exception at Appdef.gen_models() %s ' % exp)
            traceback.print_exc()

    def gen_groups(self):
        # 定义文件目录 backend/construct
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        # 应用目录 backend
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        # 运行目录 backend/apps/admin
        runtimepath = os.path.abspath(os.path.join(apppath, 'apps/admin'))
        # 模版目录 backend/construct/tmpl
        tmplpath = os.path.abspath(os.path.join(basepath, 'tmpl'))
        # 输出目录 backend/construct/output
        outputpath = os.path.abspath(os.path.join(basepath, 'output'))
        try:
            log.debug("Generate groups Starting ...")
            for group in self.Consdict['Groups']:
                log.debug("Generate group for group: %s" % group['group_name'])
                env = Environment(loader=FileSystemLoader(tmplpath), trim_blocks=True, lstrip_blocks=True)
                template = env.get_template('group_tmpl.py')
                gencode = template.render(group)
                groupfilepath = os.path.abspath(os.path.join(outputpath, 'groups/' + group['group_name'].strip().lower() + ".py"))
                with open(groupfilepath, 'w', encoding='utf-8') as gencodefile:
                    gencodefile.write(gencode)
                    gencodefile.close()
                # log.debug(gencode)
            log.debug("Generate groups Completed ...")

        except Exception as exp:
            print('Exception at Appdef.gen_groups() %s ' % exp)
            traceback.print_exc()

    def gen_pages(self):
        # 定义文件目录 backend/construct
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        # 应用目录 backend
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        # 运行目录 backend/apps/admin
        runtimepath = os.path.abspath(os.path.join(apppath, 'apps/admin'))
        # 模版目录 backend/construct/tmpl
        tmplpath = os.path.abspath(os.path.join(basepath, 'tmpl'))
        # 输出目录 backend/construct/output
        outputpath = os.path.abspath(os.path.join(basepath, 'output'))
        try:
            log.debug("Generate pages Starting ...")
            for group in self.Consdict['Groups']:
                for model in group['models']:
                    log.debug("Generate page for page: %s" % model['name'])
                    env = Environment(loader=FileSystemLoader(tmplpath), trim_blocks=True, lstrip_blocks=True)
                    template = env.get_template('page_tmpl.py')
                    gencode = template.render(model)
                    pagefilepath = os.path.abspath(
                        os.path.join(outputpath, 'pages/' + model['name'].strip().lower() + "admin.py"))
                    with open(pagefilepath, 'w', encoding='utf-8') as gencodefile:
                        gencodefile.write(gencode)
                        gencodefile.close()
                    #log.debug(gencode)
                    for submodel in model['submodels']:
                        log.debug("Generate page for page: %s" % submodel['name'])
                        env = Environment(loader=FileSystemLoader(tmplpath), trim_blocks=True, lstrip_blocks=True)
                        template = env.get_template('page_tmpl.py')
                        gencode = template.render(submodel)
                        pagefilepath = os.path.abspath(
                            os.path.join(outputpath, 'pages/' + submodel['name'].strip().lower() + "admin.py"))
                        with open(pagefilepath, 'w', encoding='utf-8') as gencodefile:
                            pass
                            gencodefile.write(gencode)
                            gencodefile.close()
                        #log.debug(gencode)
            log.debug("Generate pages Completed ...")
        except Exception as exp:
            print('Exception at Appdef.gen_pages() %s ' % exp)
            traceback.print_exc()


if __name__ == '__main__':
    app = App()
    print(app.Consdict)
    print(app.Consdict['Groups'])
    print(app.Modeldicts)
    app.gen_models()
    app.gen_groups()
    app.gen_pages()
    '''
    print(app.AppName)
    print(app.Cons.Settings)
    print(app.Cons.AppVariables[0].cname)
    print(app.Cons.Settings.language)
    print(app.Consdict)
    print(app.Cons.Groups[0].group_schema)
    print(app.Cons.Groups[0].models[0].name)
    print(app.Cons.Groups[0].models[0].submodels[0].name)
    print(app.Cons.Groups[0].models[0].submodels[0].model_file)
    '''
