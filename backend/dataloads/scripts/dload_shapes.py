import pandas as pd
from accounts.models import CustomUser
from inventory.models import Cut

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './dataloads/csv/Shapes.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        cut= Cut(
            desc=row['shape'],
            code=row['code'],
        )

        cut.save()

    print("CSV data has been loaded into the Django database.")