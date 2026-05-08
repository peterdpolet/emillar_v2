import pandas as pd
from users.models import CustomUser
from skus.models import SkuShape

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/Shapes.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        skushape = SkuShape(
            ss_desc=row['ss_shape'],
            ss_code=row['ss_code'],
        )

        skushape.save()

    print("CSV data has been loaded into the Django database.")