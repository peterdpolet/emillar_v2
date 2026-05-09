import pandas as pd
from accounts.models import CustomUser
from inventory.models import Type

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './dataloads/csv/Types.csv'
    print('The filepath is: ', csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        type = Type(
            desc=row['desc'],
            code_wards=row['code_wards'],
            code_internal=row['code_internal'],
        )

        type.save()

    print("CSV data has been loaded into the Django database.")