import pandas as pd
from mltrace import Component

# sample dataframe
students = pd.DataFrame({'Name': ['Rohan', 'Rahul', 'Gaurav',
                                  'Ananya', 'Vinay', 'Rohan',
                                  'Vivek', 'Vinay'],

                         'Score': [76, 69, 70, 88, 79, 64, 62, 57]})

# function to apply to dataframe


def double(a):
    return 2*a


new_component = Component("test_io_pointer_load_component", "boyuan")


@new_component.run(auto_log=True)
def doubleScore(df):
    df_copy = pd.DataFrame.copy(df)
    df_copy['Score'] = df_copy['Score'].apply(double)
    return df


doubleScore(students)

num_component_run = len(new_component.history)
last_component_run = new_component.history.get_runs_by_index(
    -1, num_component_run)

# expect no difference
print(last_component_run[0].inputs[0]['original_content'].compare(students))
