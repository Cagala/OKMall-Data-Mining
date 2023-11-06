# OKMall Data Scraping Project

This repository is dedicated to a data mining project that leverages API scraping from the OKMall website. The project allows asynchronous scraping of up to 5 pages simultaneously, collecting data in a structured format within HTML div elements. 

The scraped data is stored in a database, offering users the flexibility to export it to Excel at their convenience. Users with limited time or slower computing resources can break down the process into separate stages: scraping, data cleaning, data parsing, and Excel export.

## Features

- Asynchronous scraping of OKMall website using API.
- Structured data collection within HTML <div> elements.
- Database storage for scraped data.
- Export data to Excel with flexible options.
- Support for breaking down the scraping process.
- 'isProcessed' flag prevents reprocessing of exported data.
- Data processing timestamps are recorded.

## Getting Started

To get started with this project, follow these steps:

1. Clone the repository to your local machine.
2. Install the necessary dependencies (list dependencies and how to install them).
3. Configure the project settings as needed.
4. Run the main script to start scraping.

## Usage

Describe how to use the project, provide examples, and any other relevant information.

```python
python main.py
```
