import pandas as pd
import numpy as np
from skus.models import Sku, SkuShape, SkuColour
from partners.models import BusinessPartner

# Read CSV file into a DataFrame
def run():
    csv_file_path =  './csv/SkusCopy.csv'
    print(csv_file_path)
    base_df = pd.read_csv(csv_file_path)
    df = base_df.replace({np.nan: ''})



    print(df)

    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

        skus = Sku(
            sku_type_id =row['sku_type_id'],
            sku_supplier_id = row['sku_supplier_id'],
            sku_internal_code = row['sku_internal_code'],
            sku_code = row['sku_code'],
            sku_origin = row['sku_origin'],
            sku_size_d = row['sku_size_d'],
            sku_size_w = row['sku_size_w'],
            sku_size_h = row['sku_size_h'],
            sku_shape_id = row['sku_shape_id'],
            sku_colour_id = row['sku_colour_id'],
            sku_weight = row['sku_weight'],
            # sku_image = row['sku_image']
        )

        skus.save()

    print("CSV data has been loaded into the Django database.")

    # RUN: python manage.py runscript dload_colours