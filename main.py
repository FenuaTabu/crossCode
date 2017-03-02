import os
import inflection

class CrossBuild():
    config = None
    output = []

    def load_config(self, config):
        self.config = config

    def build(self):
        '''Construction des models et vues'''
        # models
        for model in self.config.models:
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

    def build_model(self, model):
        self.output.append(("python", self.path+"models.py", self.build_model_file(model)))

    def build_model_file(self, model):
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
    ctype = {"Auto": "Integer", "BigAuto": "Long", "BigInteger": "Long", "Char": "String", "Boolean": "boolean", "Integer": "Integer", "ForeignKey": "ForeignKey"}

    def __init__(self, packageName):
        self.packageName = packageName

    def build_detailview(self, model, view):
        self.output.append(("xml", "./android/res/"+model.name+".xml", self.build_update_layout(model)))

    def build_listview(self, model, view):
        self.output.append(("java", "./android/activity/"+model.name+"ListActivity.java", self.build_listview_activity(model, view)))
        self.output.append(("java", "./android/adapter/"+model.name+"Adapter.java", self.build_listview_adapter(model, view)))

    def build_model(self, model):
        self.output.append(("java", "./android/model/"+model.name+".java", self.build_model_entity(model)))

    def build_listview_adapter(self, model, view):
        ret = '''
package com.efenua.courselocal.adapter;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import com.efenua.courselocal.R;
import com.efenua.courselocal.model.'''+model.name+''';

import java.util.ArrayList;

/**
 * Generate by crossCode.
 */

public class '''+model.name+'''Adapter extends ArrayAdapter<'''+model.name+'''> {
    public '''+model.name+'''Adapter(Context context, ArrayList<'''+model.name+'''> list'''+model.name+''') {
        super(context, 0, list'''+model.name+''');
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        // Get the data item for this position
        '''+model.name+''' obj = getItem(position);
        // Check if an existing view is being reused, otherwise inflate the view
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate (R.layout.item_'''+inflection.underscore(model.name)+''', parent, false);
        }

        TextView textViewLib = (TextView) convertView.findViewById(R.id.textViewLib);
        textViewLib.setText(obj.getLib());

        return convertView;
    }
}

        '''
        return ret
        
    def build_listview_activity(self, model, view):
        ret = '''
package com.efenua.courselocal.activity;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;

import com.efenua.courselocal.R;
import com.efenua.courselocal.adapter.'''+model.name+'''Adapter;
import com.efenua.courselocal.model.'''+model.name+''';

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

public class '''+model.name+'''ListActivity extends AppCompatActivity {
    private static final String EXTRA_ADD_UPDATE = "com.efenua.courselocal.add_update";
    private ListView listView;
    private ArrayList<'''+model.name+'''> al'''+model.name+''';
    private '''+model.name+'''Adapter '''+inflection.camelize(model.name, False)+'''Adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_'''+inflection.underscore(model.name)+'''_list);


        listView = (ListView) findViewById(R.id.listView'''+model.name+''');
        reloadData();

        listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
            @Override
            public boolean onItemLongClick(AdapterView<?> arg0, View arg1,
                                           int pos, long id) {
                Intent i = new Intent('''+model.name+'''ListActivity.this, '''+model.name+'''DetailActivity.class);
                i.putExtra(EXTRA_ADD_UPDATE, "Update");
                i.putExtra("'''+inflection.underscore(model.name)+'''", ('''+model.name+''') al'''+model.name+'''.get(pos));
                startActivity(i);
                return true;
            }
        });

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent('''+model.name+'''ListActivity.this, '''+model.name+'''DetailActivity.class);
                i.putExtra(EXTRA_ADD_UPDATE, "Add");
                startActivity(i);
            }
        });
    }

    public void reloadData() {
        al'''+model.name+''' = new ArrayList<'''+model.name+'''>('''+model.name+'''.listAll('''+model.name+'''.class)) ;

        '''+inflection.camelize(model.name, False)+'''Adapter = new '''+model.name+'''Adapter(this, al'''+model.name+''');
        listView.setAdapter('''+inflection.camelize(model.name, False)+'''Adapter);
    }

}
        '''
        return ret
        
    def build_update_layout(self, model):
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

    def build_model_entity(self, model):
        ret="""package com.efenua.courselocal.model;

import android.os.Parcel;
import android.os.Parcelable;

import com.orm.SugarRecord;

/**
 * Generate by crossCode.
 */

public class """ + model.name + """  extends SugarRecord implements Parcelable {"""

        for field in model.attributes:
            if field.type == "ForeignKey":
                ret += """
    private """ + field.options["othermodel"] + """ """ + field.name + """;"""
            else:
                ret += """
    private """ + self.ctype.get(field.type) + """ """ + field.name + """;"""

        ret+="""
    public """ + model.name + """() {
        super();
    }

    public """ + model.name + """("""
        ret +=', '.join(self.ctype.get(x.type) + " " + x.name for x in model.attributes)
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
            if(field.type == "ForeignKey"):
                ret += """
        """ + field.name + """ = (""" + field.options["othermodel"] + """) in.readParcelable(""" + field.options["othermodel"] + """.class.getClassLoader()); """
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
            if(field.type == "ForeignKey"):
                ret += """
    public """ + field.options["othermodel"] + """ get""" + inflection.camelize(field.name) + """() {
        return """ + field.name + """;
    }
    """
            else:
                ret += """
    public """ + self.ctype.get(field.type) + """ get""" + inflection.camelize(field.name) + """() {
        return """ + field.name + """;
    }
    """

        for field in model.attributes:
            if(field.type == "ForeignKey"):
                ret += """
    public void set""" + inflection.camelize(field.name) + """(""" + field.options["othermodel"] + """ """ + field.name + """) {
        this.""" + field.name + """ = """ + field.name + """;
    }
    """
            else:
                ret += """
    public void set""" + inflection.camelize(field.name) + """(""" + self.ctype.get(field.type) + """ """ + field.name + """) {
        this.""" + field.name + """ = """ + field.name + """;
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
            if(field.type == "ForeignKey"):
                ret += """
        dest.writeParcelable("""+field.name+""", flags);"""
            else:
                ret += """
        dest.write"""+self.ctype.get(field.type)+"""("""+field.name+""");"""
        ret += """
    }

    // TODO
    // Generate equals()
    // Generate hashCode()
}
"""
        return ret
        
class Attribute(object):
    def __init__(self, name, type, options=None):
        self.name = name
        self.type = type
        self.options = {}
        if options is not None:
            for opt_key, opt_value in options.items():
                self.add_option(opt_key, opt_value)
        
    def add_option(self, key, value):
        self.options[key]= value

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


config = Config()

# Course
course = Model("Course")
course.display = "lib"
course.add_attribute("id", "BigAuto")
course.add_attribute("lib", "Char", {"max_length": "40"})
course.add_attribute("panier", "Boolean")

# Article
article = Model("Article")
article.display = "lib"
article.add_attribute("id", "BigAuto")
article.add_attribute("lib", "Char", {"max_length": "40"})
article.add_attribute("categorie", "ForeignKey", {"othermodel": "Categorie"})

list_view_course = View("listView", "Article")

config.add_model(course)
config.add_model(article)
config.add_view(list_view_course)

if __name__ == "__main__":
    course = AndroidBuild("")
    course.load_config(config)
    course.build()
    print(course.render())
