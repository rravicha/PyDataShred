import pandas as pd
from deltalake.writer import write_deltalake

# df = pd.DataFrame({"x": [1, 2, 3]})
df = pd.read_csv("tests_data/a.csv")
# write_deltalake("emp_delta_format/employee_data", df)

df.to_parquet("tests_data/emp.parquet",index=False)
