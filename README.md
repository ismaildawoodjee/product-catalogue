# Industrial Equipment Catalogue

## Instructions

Clone this repository:

```sh
git clone https://github.com/ismaildawoodjee/product-catalogue
cd product-catalogue
```

Set up a Python virtual environment (Windows OS) and activate it:

```sh
python -m venv .venv
.venv/Scripts/activate
```

On Linux and Mac OS:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```sh
python -m pip install -U pip
python -m pip install -U wheel setuptools
pip install -r requirements.txt
```

Run the Python scripts in this order:

```sh
python main.py
python data_preparation.py
```

Wait until the scripts have finished running, then check inside the `data` directory
to see that raw CSV data has been extracted (with the name `equipment_data_raw.csv`),
and several smaller files for each type of industrial equipment are also produced.

When running the data preparation script, four warnings will say that some strings
cannot be converted to a float, but that's OK, they can be ignored.

Check inside the `images` directory to see that 103 images with their proper names
(`equipment_type` underscore `equipment_id`) are downloaded.

## Using Scrapy Spider to Crawl Product Specifications

**Setup:** Start a Scrapy project and go inside the folder using the commands:

```sh
scrapy startproject catalogue
cd catalogue
```

**Create:** Generate a Scrapy spider called `komatsu` (and a start url) using the command:

```sh
scrapy genspider komatsu 'www.komatsu.com.au/equipment'
```

This will generate boilerplate code in the `spiders/komatsu.py` script, which can
then be modified accordingly.

**List:** To list all spiders, use the command:

```sh
scrapy list
```

**Crawl:** To start crawling using the spider, run the command `scrapy crawl spider_name`:

```sh
scrapy crawl komatsu
```

**Headers:** To specify headers and parse them as a dictionary, use the `scraper-helper`
module, and specify the `DEFAULT_REQUEST_HEADERS` in the `settings.py` file. Using headers
will make it look like the request is coming from a real browser instead of a bot.

**Shell:** To explore the website within Scrapy Shell, enter the shell with the command
`scrapy shell website_url`:

```sh
scrapy shell 'www.komatsu.com.au/equipment/excavators'
```
