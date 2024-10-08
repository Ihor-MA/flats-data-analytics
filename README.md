# Flats data analytics
Here is a project based on the analysis date, which will help you
understand the real estate market situation, namely about the purchase
of apartments throughout Ukraine. The data was collected asynchronously
from the website dom.ria, after which it was clarified, processed and
subsequently converted into visually acceptable graphs, where we draw
conclusions and make the right decisions by analyzing the market.

## Check it out!

> 👉 **Step 1** - Download the code from the GH repository (using `GIT`) 
 

```bash
$ git clone https://github.com/Ihor-MA/flats-data-analytics.git
$ cd flats-data-analytics
```

> 👉 **Step 2** - Installation

`python -m venv venv`

`venv\Scripts\activate (on Windows)`

`source venv/bin/activate (on macOS)`

`pip install -r requirements.txt`


> 👉 **Step 3** - Run scraping file(choose page which you want to start and end)

`python dom_ria_scraping.py`

> 👉 **Step 4** - Run jupyter file for data processing(use the Jupyter Notebook
> pandas_data_processing.ipynb to pre-process the data. Launch Jupyter Notebook
> and follow the processing steps)

`jupyter notebook pandas_data_processing.ipynb`

> 👉 **Step 5** - Run jupyter file for visualization(after processing the data,
> open Jupyter Notebook visualization.ipynb to create graphs and visualize the data)

`jupyter notebook visualization.ipynb`
