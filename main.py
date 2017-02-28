import os
import inflection

class CrossBuild():
    config = None
    output = []

    def loadConfig(self, config):
        self.config = config

    def build(self):
        for model in self.config.models:
            # models
            self.buildModel(model)

            # views
        for view in self.config.views:
            if(view.type == "listView"):
                self.buildListView(build.models, view)
            if(view.type == "detailView"):
                self.buildDetailView(build.models, view)

    def buildModel(self, model):
        pass

    def buildDetailView(self, model, view):
        pass

    def buildListView(self, model, view):
        pass

    def render(self):
        ret = ""
        for outType, outPath, outContent in self.output:
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

    def buildModel(self, model):
        self.output.append(("python", self.path+"models.py", self.buildModelFile(model)))

    def buildModelFile(self, model):
        ret = """
from __future__ import unicode_literals

from django.db import models

class Categorie (models.Model):"""
        for attr in model.attributes:
            if attr.type == "Char":
                ret += """
    """+attr.name+""" = models."""+attr.type+"""Field(max_length="""+attr.options["max_length"]+""")"""

            if attr.type == "Boolean":
                ret += """
    """+attr.name+""" = models."""+attr.type+"""Field(default=False)"""

        ret+= """

    def __str__(self):
        """
        ret += 'return ' + ', '.join([str(field) for field in model.display])

        return ret

class AndroidBuild(CrossBuild):
    ctype = {"Auto": "Integer", "BigAuto": "Long", "BigInteger": "Long", "Char": "String", "Boolean": "boolean", "Integer": "Integer"}

    def __init__(self, packageName):
        self.packageName = packageName

    def buildDetailView(self, model, view):
        self.output.append(("xml", "./android/res/"+model.name+".xml", self.buildUpdateLayout(model)))

    def buildListView(self, model, view):
        pass

    def buildModel(self, model):
        self.output.append(("java", "./android/model/"+model.name+".java", self.buidlModelEntity(model)))

    def buildUpdateLayout(self, model):
        ret = """
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    """
        for field in field.attributes:
            if field.type == "Char":
                ret+="""
    <EditText
        android:id="@+id/"""+field.name+"""\"
        android:hint="@string/"""+field["label"]+"""\"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:singleLine="true"/>"""

            if field.type == "Boolean":
                ret+="""
    <CheckBox
        android:id="@+id/"""+field.name+"""\"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/"""+field["label"]+"""\" />"""

        ret+="""

    <Button
        android:layout_width="fill_parent"
        android:layout_height="wrap_content"
        android:id="@+id/update"""+model.name+"""\"
        android:text="Modifier" />

</RelativeLayout>
        """
        return ret

    def buidlModelEntity(self, model):
        ret="""package com.efenua.courselocal.model;

import android.os.Parcel;
import android.os.Parcelable;

/**
 * Generate by crossCode.
 */

public class """ + model.name + """ implements Parcelable {"""

        for field in model.attributes:
            ret += """
    private """ + self.ctype.get(field.type) + """ """ + field.name + """;"""

        ret+="""
    public """ + model.name + """() {
        super();
    }

    public """ + model.name + """("""
        ret +=', '.join("??")
        ret +=  """) {"""

        for field in model.attributes:
            ret += """
        this.""" + field.name + """ = """ + field.name + """;"""
        ret+="""
    }

    protected """ + model.name + """(Parcel in) {"""

        for field in model.attributes:
            if(field.type == "Boolean"):
                ret += """
        """ + field.name + """ = in.readByte() != 0;"""
            else:
                ret += """
        """ + field.name + """ = in.read""" + self.ctype.get(field.type) + """(); """

        ret += """
    }

    public static final Creator<""" + model.name + """> CREATOR = new Creator<""" + model.name + """>() {
        @Override
        public """ + model.name + """ createFromParcel(Parcel in) {
            return new """ + model.name + """(in);
        }

        @Override
        public """ + model.name + """[] newArray(int size) {
            return new """ + model.name + """[size];
        }
    };

    """
        for field in model.attributes:
            ret += """
    public """ + self.ctype.get(field.type) + """ get""" + field.name + """() {
        return """ + field.name + """;
    }
    """

        for field in model.attributes:
            ret += """
    public void set""" + field.name + """(""" + self.ctype.get(field.type) + """ """ + field.name + """) {
        return """ + field.name + """;
    }
    """

        ret += """

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        """

        for field in model.attributes:
            if(field.type == "Boolean"):
                ret += """
        dest.writeByte((byte) ("""+field.name+""" ? 1 : 0)); """
            else:
                ret += """
        dest.write"""+self.ctype.get(field.type)+"""(field.name)"""
        ret += """
    }

    // TODO
    // Generate equals()
    // Generate hashCode()
}
"""
        return ret
        
class Attribute():
    options = {}
    def __init__(self, name, type):
        self.name = name
        self.type = type
        
    def addOption(self, key, value):
        self.options[key]= value

class Model():
    attributes = []
    
    def __init__(self, name):
        self.name = name
      
    def addAttribute(self, attribute):
        self.attributes.append(attribute)

class Config():
    models = []
    views = []
    
    def __init__(self):
        pass
        
    def addModel(self, model):
        self.models.append(model)


config = Config()

course = Model("Course")
course.display = "lib"
course.addAttribute(Attribute("id", "BigAuto"))
attrs = Attribute("lib", "Char")
attrs.addOption("max_length", "40")
course.addAttribute(attrs)
course.addAttribute(Attribute("panier", "Boolean"))

config.addModel(course)


if __name__ == "__main__":
    course = AndroidBuild("")
    course.loadConfig(config)
    course.build()
    print(course.render())
