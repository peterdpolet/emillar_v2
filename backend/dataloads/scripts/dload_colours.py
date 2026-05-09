import pandas as pd
from accounts.models import CustomUser
from inventory.models import Color

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './dataloads/csv/Colours.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        color = Color(
            code=row['code'],
            desc=row['desc']
        )

        color.save()

    print("CSV data has been loaded into the Django database.")

    # RUN: python manage.py runscript dload_colours