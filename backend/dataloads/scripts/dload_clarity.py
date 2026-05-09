import pandas as pd
from accounts.models import CustomUser
from inventory.models import Clarity
# Read CSV file into a DataFrame
def run():
    csv_file_path =  './dataloads/csv/Clarity.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        clarity = Clarity(
            code=row['code'],
            num_code=row['num_code'],
            desc=row['desc']
        )

        clarity.save()

    print("CSV data has been loaded into the Django database.")

    # run backend/scripts/dload_types.py