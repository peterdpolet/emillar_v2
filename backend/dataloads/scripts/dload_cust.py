import pandas as pd
from users.models import CustomUser
from partners.models import BusinessPartner

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/Partners.csv'
    print(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        buspartner = BusinessPartner(
            bp_type=row['bp_type'],
            bp_name=row['bp_name'],
            bp_int_ref=row['bp_int_ref']

        )

        buspartner.save()

    print("CSV data has been loaded into the Django database.")