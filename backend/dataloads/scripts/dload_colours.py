import pandas as pd
from users.models import CustomUser
from skus.models import SkuColour

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/Colours.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        skucolour = SkuColour(
            sc_code=row['sc_code'],
            sc_desc=row['sc_desc']
        )

        skucolour.save()

    print("CSV data has been loaded into the Django database.")

    # RUN: python manage.py runscript dload_colours