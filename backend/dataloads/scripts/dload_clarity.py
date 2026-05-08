import pandas as pd
from users.models import CustomUser
from skus.models import SkuClarity
# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/Clarity.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        skuclarity = SkuClarity(
            scl_code=row['scl_code'],
            scl_desc=row['scl_desc']
        )

        skuclarity.save()

    print("CSV data has been loaded into the Django database.")

    # run backend/scripts/dload_types.py