import pandas as pd
import matplotlib.pyplot as plt


# CSV data extracted from breadprice.csv
csv_data = '''
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec
2012,1.423,1.442,1.395,1.426,1.412,1.403,1.427,1.407,1.401,1.422,1.418,1.436
2013,1.422,1.411,1.412,1.409,1.401,1.439,1.434,1.408,1.419,1.358,1.382,1.385
2014,1.365,1.388,1.359,1.388,1.401,1.400,1.413,1.396,1.405,1.414,1.420,1.466
2015,1.479,1.435,1.440,1.454,1.463,1.467,1.447,1.420,1.432,1.418,1.409,1.428
2016,1.425,1.407,1.416,1.406,1.382,1.333,1.349,1.341,1.329,1.343,1.362,1.362
'''


from io import StringIO
data = pd.read_csv(StringIO(csv_data))


data['Average_Price'] = data.iloc[:, 1:].mean(axis=1)


plt.figure(figsize=(10, 6))
plt.plot(data['Year'], data['Average_Price'], marker='o', linestyle='-', color='b', label='Average Price of Bread')
plt.title('Average Price of Bread Over Time')
plt.xlabel('Year')
plt.ylabel('Price (in USD)')
plt.grid(True)
plt.legend()
plt.tight_layout()


plt.show()
