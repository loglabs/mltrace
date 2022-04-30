from mltrace import Component
from mltrace.db.utils import _load
import pandas as pd 


class BoyuanComponent(Component):
    def __init__(
        self,
        name="",
        owner="",
        description="",
        beforeTests=[],
        afterTests=[],
        tags=[],
    ):
        super().__init__(
            name, owner, description, beforeTests, afterTests, tags)

    # overwrite afterRun
    def afterRun(self):
        first_cr = self.history.get_runs_by_index(0, 1)[0]
        print("---first cr input ---")
        print(first_cr.inputs)
        print("---load .... ---")
        print(_load(first_cr.inputs[0]['name']))
        print("+++ close +++")


new_component = BoyuanComponent("test_dataframe_two", "boyuan")

students = pd.DataFrame({'Name': ['Rohan', 'Rahul', 'Gaurav',
                                 'Ananya', 'Vinay', 'Rohan',
                                 'Vivek', 'Vinay'],
                        'Score': [76, 69, 70, 88, 79, 64, 62, 57]})


def double(a):
    return 2*a

@new_component.run(auto_log=True)
def test_boyuan_component(df):
    return df['Score'].apply(double)


test_boyuan_component(students)
