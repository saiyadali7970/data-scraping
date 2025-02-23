# Booking.com Data Scraper

This repository contains a script to scrape data from **Booking.com** and store it in a CSV file. The process is automated using **GitHub Actions**, ensuring the scraping task runs periodically without manual intervention.

## Features

- Scrapes data from Booking.com, such as:
  - Hotel names
  - Prices
  - Ratings
  - Reviews
- Saves the scraped data into a well-structured **CSV file**.
- Automated using **GitHub Actions** for periodic scraping.

## Technologies Used

- **Python** for web scraping.
- **BeautifulSoup** and **Selenium** for data extraction.
- **Pandas** for processing and saving data.
- **GitHub Actions** for automation.

## How It Works

1. The script scrapes data from Booking.com using BeautifulSoup or Selenium (depending on the dynamic nature of the page).
2. Extracted data is cleaned and stored in a CSV file.
3. A **GitHub Actions workflow** is set up to run the scraper periodically (e.g., daily/weekly) and push the updated CSV file to the repository.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/saiyadali7970/data-scraping.git
   cd data-scraping
   
