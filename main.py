import json

class CrossBuild():
    config = None

    def loadConfig(self, config):
        with open(config) as data_file:
            self.config = json.load(data_file)

    def build(self):
        for model in self.config:
            for build in model["model"]["builds"]:
                for buildView in build:
                    if(buildView == "listView"):
                        self.buildListView(model)
                    if(buildView == "detailView"):
                        self.buildDetailView(model)

    def buildDetailView(self, model):
        pass

    def buildListView(self, model):
        pass


class DjangoBuild(CrossBuild):
    def build(self):
        pass


class AndroidBuild(CrossBuild):
    def __init__(self, packageName):
        self.packageName = packageName

    def buildDetailView(self, model):
        print(self.buildObjectDetailFragment(model))

    def buildListView(self, model):
        print(self.buildObjectListFragment(model))
        print(self.buildObjectListAdapter(model))

    def buildObjectDetailFragment(self, model):
        ret="""
        package """+model["model"]["name"]+""";

        import android.app.Fragment;
        import android.os.Bundle;
        import android.view.LayoutInflater;
        import android.view.View;
        import android.view.ViewGroup;
        import android.widget.TextView;


        public class """+model["model"]["name"]+"""DetailFragment extends Fragment {
            public static final String EXTRA_URL = "url";

            @Override
            public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                     Bundle savedInstanceState) {
                View view = inflater.inflate(R.layout."""+model["model"]["name"]+"""_detail_fragment,
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
    
    def buildObjectListAdapter(self, model):
        ret="""
        package """+model["model"]["name"]+""";
        
        public class """+model["model"]["name"]+"""Adapter extends ArrayAdapter<"""+model["model"]["name"]+"""> {

        private static class ViewHolder {
            private TextView itemView;
        }

        public """+model["model"]["name"]+"""Adapter(Context context, int textViewResourceId, ArrayList<"""+model["model"]["name"]+"""> items) {
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

    def buildObjectListFragment(self, model):
        ret = """
        package """+model["model"]["name"]+""";

        import android.app.Activity;
        import android.app.Fragment;
        import android.os.Bundle;
        import android.view.LayoutInflater;
        import android.view.View;
        import android.view.ViewGroup;
        import android.widget.Button;

        public class """+model["model"]["name"]+"""ListFragment extends Fragment {
                private OnItemSelectedListener listener;

                @Override
                public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                Bundle savedInstanceState) {
                        View view = inflater.inflate(R.layout."""+model["model"]["name"]+"""_list_fragment,
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



if __name__ == "__main__":
    course = AndroidBuild("fr.efenua.course")
    course.loadConfig("../crossCodeData/config.json")
    course.build()
