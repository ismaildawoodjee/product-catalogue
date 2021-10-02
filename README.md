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
to see that raw CSV data has been extracted, and several smaller files for each
equipment are also produced.

Check inside the `images` directory to see that 103 images with their proper names
(equipment type underscore equipment ID) are downloaded.
