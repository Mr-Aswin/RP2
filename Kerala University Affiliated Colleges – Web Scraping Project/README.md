# University of Kerala Affiliated Colleges --- Web Scraping Project

A beginner-friendly Python web scraping project that collects publicly
displayed information about colleges listed in the University of
Kerala's affiliated-colleges directory and stores the results in a CSV
dataset.

**Official source:**
https://www.keralauniversity.ac.in/affiliated-colleges

> **Data note:** The included CSV is a snapshot of the information
> returned by the website when the scraper was run. Missing values mean
> that a value was not captured in this dataset; they do not prove that
> the college has no such contact information. Contact details have not
> been independently verified for current accuracy.

## Project objectives

-   Inspect the structure of a real-world website.
-   Extract college names and identifiers from the directory.
-   Submit each college identifier to the college-details endpoint to
    retrieve available contact information.
-   Parse HTML using Python.
-   Organize the results in a Pandas DataFrame and export them to CSV.
-   Review missing values, duplicate records, and basic email/URL
    formatting.

## Technologies used

-   Python
-   Requests
-   BeautifulSoup (`bs4`)
-   Pandas
-   Regular expressions (`re`)
-   Google Colab / Jupyter Notebook
-   CSV

## Dataset

The included file is `kerala_university_colleges (1).csv` (you may
rename it to `kerala_university_colleges.csv` for convenience).

It contains **204 records and 7 columns**:

  -----------------------------------------------------------------------
  Column                              Description
  ----------------------------------- -----------------------------------
  `College Name`                      Name of the college as captured
                                      from the directory

  `College ID`                        Identifier used to request the
                                      college details page

  `Address`                           Address captured from the college
                                      details page, when available

  `Contact Number`                    Phone number or numbers captured,
                                      when available

  `Email Address`                     Email address captured, when
                                      available

  `Website URL`                       College website URL captured, when
                                      available

  `Status`                            Status assigned by the scraper for
                                      that record
  -----------------------------------------------------------------------

### Snapshot summary

The supplied CSV has 204 records. All 204 rows have `Status = Success`.
In this project, that status indicates that the scraper completed its
processing path for the record; it does **not** mean that every contact
field is populated or independently verified.

  Field              Missing values   Missing percentage
  ---------------- ---------------- --------------------
  Address                        67                32.8%
  Contact Number                 13                 6.4%
  Email Address                  26                12.7%
  Website URL                    31                15.2%

The current CSV has no duplicate college IDs, duplicate college names,
or exact duplicate rows. These are checks of this dataset only, not
proof that the source directory itself contains no duplicate
institutions.

## How the scraper works

1.  Send an HTTP request to the affiliated-colleges directory.
2.  Parse the HTML response using BeautifulSoup.
3.  Extract each college name and its college identifier.
4.  Submit each identifier to the college-details endpoint using a POST
    request.
5.  Parse the returned HTML and look for address, phone, email, and
    website fields.
6.  Store one result per college, including missing fields where data
    could not be extracted.
7.  Export the collected results to CSV.

The scraper uses a delay between requests to reduce request frequency.
The website's HTML structure may change, so selectors and extraction
rules may need maintenance.

## Getting started

### Option A: Run in Google Colab

1.  Open Google Colab: https://colab.research.google.com/

2.  Create a new notebook.

3.  Copy the scraping code into notebook cells, or upload your `.ipynb`
    file.

4.  Install the required libraries if they are not already available:

    ``` python
    !pip install requests beautifulsoup4 pandas
    ```

5.  Run the notebook cells in order: imports and URLs, directory
    extraction, detail extraction function, scraping loop, and CSV
    export.

6.  Download the resulting CSV from the Colab file panel.

### Option B: Run locally

1.  Install Python 3.

2.  Clone or download this repository.

3.  Open a terminal in the project directory.

4.  Install dependencies:

    ``` bash
    pip install requests beautifulsoup4 pandas
    ```

5.  Run the Python script (replace the example filename with the actual
    script name in your repository):

    ``` bash
    python scraper.py
    ```

The script name above is an example. Update it to match the `.py` file
you commit to the repository.

## Example CSV export

Once the scraper has created `all_results`, use Pandas to export it:

``` python
import pandas as pd

df = pd.DataFrame(all_results)
df.to_csv(
    "kerala_university_colleges.csv",
    index=False,
    encoding="utf-8-sig"
)

display(df.head())
```

## Data quality and limitations

-   Some contact fields are missing in the exported dataset.
-   A missing value may mean that the source page did not display the
    information, that the page structure differed, or that the
    extraction rule did not capture it. The cause should be checked
    before drawing conclusions.
-   Basic email-format checks do not confirm that an email inbox exists
    or can receive messages.
-   A URL beginning with `http://` or `https://` is not proof that the
    website is reachable or current.
-   The `Success` status is the scraper's processing status, not an
    independent quality rating.
-   The current CSV does not have separate district or college-type
    columns, so district-wise or college-type summaries should not be
    claimed without additional extraction and validation.
-   Website structure, contact information, and college listings can
    change over time.

## Responsible scraping

-   Review the website's terms and access rules before running the
    scraper.
-   Use reasonable delays between requests.
-   Avoid unnecessary repeated requests.
-   Handle request errors and timeouts.
-   Do not treat the extracted contact details as permanently current;
    verify important information against the official source.

## Suggested repository structure

``` text
kerala-university-college-scraper/
├── README.md
├── kerala_university_colleges.csv
└── notebook.ipynb
```

Use the actual filenames in your repository. Commit only the files you
have created and tested.

## Future improvements

-   Improve extraction robustness when the page's HTML structure varies.
-   Add a cleaning step for phone-number spacing and URL normalization.
-   Validate records against the official pages and document any
    corrections.
-   Extract district or college type only when supported by reliable
    source data.
-   Add charts for contact-field completeness and missing values.
-   Record the collection date so future dataset versions can be
    compared.

## License

Choose a license appropriate for your project before distributing the
code. The scraped data comes from the official website; review the
source website's terms before redistributing it.
