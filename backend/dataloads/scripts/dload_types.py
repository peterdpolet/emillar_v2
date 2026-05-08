import pandas as pd
from users.models import CustomUser
from skus.models import SkuType

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/Types.csv'
    print('The filepath is: ', csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        skutype = SkuType(
            st_wards_code=row['st_wards_code'],
            st_internal_code=row['st_internal_code'],
            st_desc=row['st_desc']
        )

        skutype.save()

    print("CSV data has been loaded into the Django database.")