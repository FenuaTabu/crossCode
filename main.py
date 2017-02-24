import json
import os
import inflection

class CrossBuild():
    config = None
    output = []
    
    def convert(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def loadConfig(self, config):
        with open(config) as data_file:
            self.config = json.load(data_file)

    def build(self):
        for build in self.config:
            for view in build["views"]:
                if(view["type"] == "listView"):
                    self.buildListView(build["model"], view)
                if(view["type"] == "detailView"):
                    self.buildDetailView(build["model"], view)

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
    def __init__(self, packageName):
        self.packageName = packageName

    def buildDetailView(self, model, view):
        self.output.append(("java", "./android/detail_fragment.java", self.buildObjectDetailFragment(model, view)))
        self.output.append(("xml", "./android/detail_layout.xml", self.buildLayoutDetail(model, view)))

    def buildListView(self, model, view):
        self.output.append(("java", "./android/list_fragment.java", self.buildObjectListFragment(model, view)))
        self.output.append(("java", "./android/list_adapter.java", self.buildObjectListAdapter(model, view)))

    def buildObjectDetailFragment(self, model, view):
        ret="""
        package """+model["name"]+""";

        import android.app.Fragment;
        import android.os.Bundle;
        import android.view.LayoutInflater;
        import android.view.View;
        import android.view.ViewGroup;
        import android.widget.TextView;


        public class """+model["name"]+"""DetailFragment extends Fragment {
            public static final String EXTRA_URL = "url";

            @Override
            public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                     Bundle savedInstanceState) {
                View view = inflater.inflate(R.layout."""+inflection.underscore(model["name"])+"""_detail_fragment,
                        container, false);
                returrn view;
            }

            @Override
            public void onActivityCreated(Bundle savedInstanceState) {
                super.onActivityCreated(savedInstanceState);
                Bundle bundle = getArguments();

                //TODO
                //if (bundle != null) {
                //    String link = bundle.getString("url");
                //    setText(link);
                //}
            }


                public void setText(String url) {
                        // TODO
                        //TextView view = (TextView) getView().findViewById(R.id.detailsText);
                        //view.setText(url);
                }
        }"""
        return ret
    
    def buildObjectListAdapter(self, model, view):
        ret="""
        package """+model["name"]+""";
        
        public class """+model["name"]+"""Adapter extends ArrayAdapter<"""+model["name"]+"""> {

        private static class ViewHolder {
            private TextView itemView;
        }

        public """+model["name"]+"""Adapter(Context context, int textViewResourceId, ArrayList<"""+model["name"]+"""> items) {
            super(context, textViewResourceId, items);
        }

        public View getView(int position, View convertView, ViewGroup parent) {

            if (convertView == null) {
                convertView = LayoutInflater.from(this.getContext())
                .inflate(R.layout.listview_association, parent, false);

                viewHolder = new ViewHolder();
                viewHolder.itemView = (TextView) convertView.findViewById(R.id.ItemView);

                convertView.setTag(viewHolder);
            } else {
                viewHolder = (ViewHolder) convertView.getTag();
            }

            MyClass item = getItem(position);
            if (item!= null) {
                // My layout has only one TextView
                    // do whatever you want with your string and long
                viewHolder.itemView.setText(String.format("%s %d", item.reason, item.long_val));
            }

            return convertView;
        }
        } """
        return ret

    def buildObjectListFragment(self, model, view):
        ret = """
        package """+model["name"]+""";

        import android.app.Activity;
        import android.app.Fragment;
        import android.os.Bundle;
        import android.view.LayoutInflater;
        import android.view.View;
        import android.view.ViewGroup;
        import android.widget.Button;

        public class """+model["name"]+"""ListFragment extends Fragment {
                private OnItemSelectedListener listener;

                @Override
                public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                Bundle savedInstanceState) {
                        View view = inflater.inflate(R.layout."""+inflection.underscore(model["name"])+"""_list_fragment,
                                        container, false);
                        Button button = (Button) view.findViewById(R.id.button1);
                        button.setOnClickListener(new View.OnClickListener() {
                                @Override
                                public void onClick(View v) {
                                        updateDetail("fake");
                                }
                        });
                        return view;
                }

                public interface OnItemSelectedListener {
                        public void onRssItemSelected(String link);
                }


                @Override
                public void onAttach(Context context) {
                        super.onAttach(context);
                        if (context instanceof OnItemSelectedListener) {
                                listener = (OnItemSelectedListener) context;
                        } else {
                                throw new ClassCastException(context.toString()
                                                + " must implemenet MyListFragment.OnItemSelectedListener");
                        }
                }

                @Override
                public void onDetach() {
                        super.onDetach();
                        listener = null;
                }

                // may also be triggered from the Activity
                public void updateDetail(String uri) {
                        // create a string just for testing
                        String newTime = String.valueOf(System.currentTimeMillis());
                        // inform the Activity about the change based
                        // interface defintion
                        listener.onRssItemSelected(newTime);
                }
        }"""
        return ret
    
    def buildLayoutDetail(self, model, view):
        ret = """
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
        android:orientation="vertical" 
        android:layout_width="fill_parent"
        android:layout_height="fill_parent" >
        """
        for field in view["fields"]:
            for attribute in model["attributes"]:
                if attribute["name"] == field:
                    if attribute["type"] == "charField":
                        ret+="""
                         <TextView android:layout_width="match_parent" 
                             android:id="@+id/"""+inflection.underscore(attribute["name"])+"""\"
                             android:layout_height="wrap_content" 
                             android:textSize="14dp" android:gravity="center"
                             android:layout_gravity="center" android:layout_marginLeft="10dp"
                             android:layout_marginRight="10dp">
                         </TextView>
                        """
        ret+="""

        </LinearLayout>
        """
        return ret


if __name__ == "__main__":
    course = AndroidBuild("fr.efenua.course")
    course.loadConfig("../crossCodeData/config.json")
    course.build()
    print(course.render())
