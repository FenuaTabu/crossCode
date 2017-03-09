import os
import inflection
from jinja2 import Environment, FileSystemLoader

ENV = Environment(loader=FileSystemLoader('./templates'))


class Attribute(object):
    def __init__(self, name, type, options=None):
        self.name = name
        self.type = type
        self.options = {}
        if options is not None:
            for opt_key, opt_value in options.items():
                self.add_option(opt_key, opt_value)

    def add_option(self, key, value):
        self.options[key] = value


class Model(object):
    def __init__(self, name):
        self.name = name
        self.attributes = []

    def add_attribute(self, attrs_name, attrs_type, options=None):
        new_attrs = Attribute(attrs_name, attrs_type, options)
        self.attributes.append(new_attrs)


class View(object):
    def __init__(self, type, model):
        self.type = type
        self.model = model
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)


class Config(object):
    def __init__(self):
        self.models = []
        self.views = []

    def add_model(self, model):
        self.models.append(model)

    def add_view(self, view):
        self.views.append(view)


class CrossBuild():
    config = None
    output = []

    def load_config(self, config):
        self.config = config

    def build(self):
        '''Construction des models et vues'''
        # models
        for model in self.config.models:
            model.name_underscore = inflection.underscore(model.name)
            model.name_camelize = inflection.camelize(model.name, False)
            for attrs in model.attributes:
                attrs.name_camelize = inflection.camelize(attrs.name, False)
            self.build_model(model)

        # views
        for view in self.config.views:
            if(view.type == "listView"):
                self.build_listview(next(x for x in self.config.models if x.name==view.model), view)
            if(view.type == "detailView"):
                self.build_detailview(next(x for x in self.config.models if x.name==view.model), view)

    def build_model(self, model):
        pass

    def build_detailview(self, model, view):
        pass

    def build_listview(self, model, view):
        pass

    def render_file(self, input_file, output_file, context):
        template = ENV.get_template(input_file + '.jinja')
        self.output.append((output_file, template.render(context)))

    def render(self):
        ret = ""
        for outPath, outContent in self.output:
            ret += outContent
            try:
                os.makedirs(os.path.dirname(outPath))
            except OSError:
                pass
            with open(outPath, "w") as f:
                f.write(outContent)
        return ret


class DjangoBuild(CrossBuild):
    path = "./django/"

    def build_model(self, model):
        self.output.append(("python", self.path + "models.py", self.build_model_file(model)))

    def build_model_file(self, model):
        ret = """
from __future__ import unicode_literals

from django.db import models

class Categorie (models.Model):"""
        for attr in model.attributes:
            if attr.type == "Char":
                ret += """
    """ + attr.name + """ = models.""" + attr.type + """Field(max_length=""" + attr.options["max_length"] + """)"""

            if attr.type == "Boolean":
                ret += """
    """ + attr.name + """ = models.""" + attr.type + """Field(default=False)"""

        ret += """

    def __str__(self):
        """
        ret += 'return ' + ', '.join([str(field) for field in model.display])

        return ret


class AndroidBuild(CrossBuild):

    def __init__(self, packageName):
        self.packageName = packageName

    def build(self):
        # models
        for model in self.config.models:
            for attrs in model.attributes:
                attrs.name_camelize = inflection.camelize(attrs.name, False)
                if attrs.type == "Auto":
                    attrs.ctype = "Integer"
                if attrs.type == "BigAuto":
                    attrs.ctype = "Long"
                if attrs.type == "Char":
                    attrs.ctype = "String"
                if attrs.type == "Boolean":
                    attrs.ctype = "boolean"
                if attrs.type == "Integer":
                    attrs.ctype = "Integer"
                if attrs.type == "ForeignKey":
                    attrs.ctype = attrs.options.get("othermodel")

        super(AndroidBuild, self).build()

    def build_detailview(self, model, view):
        self.render_file("android/activity_detail_layout", "./android/res/activity_detail_" + model.name_underscore + "_layout.xml", {"model": model, "view": view})
        self.render_file("android/detail_activity", "./android/activity/" + model.name + "DetailActivity.java", {"model": model, "view": view})

    def build_listview(self, model, view):
        self.render_file("android/activity_list_layout", "./android/res/activity_list_" + model.name_underscore + "_layout.xml", {"model": model})
        self.render_file("android/content_list_layout", "./android/res/content_list_" + model.name_underscore + "_layout.xml", {"model": model})
        self.render_file("android/content_list_item_layout", "./android/res/content_list_item_" + model.name_underscore + "_layout.xml", {"model": model, "view": view})
        self.render_file("android/listview_activity", "./android/activity/" + model.name + "ListActivity.java", {"model": model, "view": view})
        self.render_file("android/listview_adapter", "./android/adapters/" + model.name + "ListAdapter.java", {"model": model, "view": view})

    def build_model(self, model):
        self.render_file("android/entity", "./android/models/" + model.name + ".java", {"model": model})


config = Config()

# Course
course = Model("Course")
course.display = "lib"
course.add_attribute("id", "BigAuto")
course.add_attribute("lib", "Char", {"max_length": "40"})
course.add_attribute("panier", "Boolean")
config.add_model(course)

list_view_course = View("listView", "Course")
config.add_view(list_view_course)

detail_view_course = View("detailView", "Course")
config.add_view(detail_view_course)

# Article
article = Model("Article")
article.display = "lib"
article.add_attribute("id", "BigAuto")
article.add_attribute("lib", "Char", {"max_length": "40"})
article.add_attribute("categorie", "ForeignKey", {"othermodel": "Categorie"})
config.add_model(article)

list_view_article = View("listView", "Article")
config.add_view(list_view_article)

detail_view_article = View("detailView", "Article")
config.add_view(detail_view_article)

if __name__ == "__main__":
    course = AndroidBuild("")
    course.load_config(config)
    course.build()
    print(course.render())
