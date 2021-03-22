from mltrace import create_component, register


# Create etl component
create_component('etl', 'clean the data', 'shreyashankar')


@register('etl', inputs=['raw_data.pq'], outputs=['clean_data.pq'])
def clean_data():
    print('Hey this cleans the data!')


clean_data()
