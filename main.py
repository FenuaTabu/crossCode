import json
import os
import inflection

class CrossBuild():
    config = None
    output = []

    def loadConfig(self, config):
        with open(config) as data_file:
            self.config = json.load(data_file)

    def build(self):
        for build in self.config:
            # models
            for model in build["models"]:
                self.buildModel(model)

            # views
            for view in build["views"]:
                if(view["type"] == "listView"):
                    self.buildListView(build["models"], view)
                if(view["type"] == "detailView"):
                    self.buildDetailView(build["models"], view)

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
    def build(self):
        pass

    def buildModel(self):
        pass


class AndroidBuild(CrossBuild):
    ctype = {"Auto": "Integer", "Char": "String", "Boolean": "boolean"}

    def __init__(self, packageName):
        self.packageName = packageName

    def buildDetailView(self, model, view):
        pass

    def buildListView(self, model, view):
        pass

    def buildModel(self, model):
        self.output.append(("java", "./android/model/"+model["name"], self.buidlModelEntity(model)))

    def buidlModelEntity(self, model):
        ret="""package com.efenua.courselocal.model;

import android.os.Parcel;
import android.os.Parcelable;

/**
 * Generate by crossCode.
 */

public class """ + model["name"] + """ implements Parcelable {"""

        for field in model["attributes"]:
            ret += """
    private """ + self.ctype.get(field["type"]) + """ """ + field["name"] + """;"""

        ret+="""
    public """ + model["name"] + """() {
        super();
    }

    public """ + model["name"] + """("""
        ret +=', '.join([str(self.ctype.get(field["type"]) + ' ' + field["name"]) for field in model["attributes"]])
        ret +=  """) {"""

        for field in model["attributes"]:
            ret += """
        this.""" + field["name"] + """ = """ + field["name"] + """;"""
        ret+="""
    }

    protected """ + model["name"] + """(Parcel in) {"""

        for field in model["attributes"]:
            if(field["type"] == "Boolean"):
                ret += """
        """ + field["name"] + """ = in.readByte() != 0;"""
            else:
                ret += """
        """ + field["name"] + """ = in.read""" + self.ctype.get(field["type"]) + """(); """

        ret += """
    }

    public static final Creator<""" + model["name"] + """> CREATOR = new Creator<""" + model["name"] + """>() {
        @Override
        public """ + model["name"] + """ createFromParcel(Parcel in) {
            return new """ + model["name"] + """(in);
        }

        @Override
        public """ + model["name"] + """[] newArray(int size) {
            return new """ + model["name"] + """[size];
        }
    };

    """
        for field in model["attributes"]:
            ret += """
    public """ + self.ctype.get(field["type"]) + """ get""" + field["name"] + """() {
        return """ + field["name"] + """;
    }
    """

        for field in model["attributes"]:
            ret += """
    public void set""" + field["name"] + """(""" + self.ctype.get(field["type"]) + """ """ + field["name"] + """) {
        return """ + field["name"] + """;
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

        for field in model["attributes"]:
            if(field["type"] == "Boolean"):
                ret += """
        dest.writeByte((byte) ("""+field["name"]+""" ? 1 : 0)); """
            else:
                ret += """
        dest.write"""+self.ctype.get(field["type"])+"""(field["name"])"""
        ret += """
    }

    // TODO
    // Generate equals()
    // Generate hashCode()
}
"""
        return ret


if __name__ == "__main__":
    course = AndroidBuild("fr.efenua.course")
    course.loadConfig("../crossCodeData/config.json")
    course.build()
    print(course.render())
