# SPX PDF Visualizer

## Overview
SPX PDF Visualizer is a Python tool to analyze and visualize the risk-neutral probability density function (PDF) for SPX options using the Breeden-Litzenberger formula.
It generates an interactive 3D surface plot showing the PDF across strike prices and expiration dates.

---

## Features
- Fetches SPX option data for a specified strike range and expirations.
- Computes the approximate risk-neutral PDF from call option prices.
- Generates smooth, interactive 3D surface plots with Plotly.
- Handles multiple expirations and customizable strike ranges.

---

## Project Structure

- spx_chain.py: Fetches SPX call options from Yahoo Finance, filters strikes, and saves to CSV.
- spx_pdf_surface.py: Loads CSV data, computes PDFs, and generates the 3D surface plot.
- /SPX_options_next5_6000_7000_mid_actual_interpolated.csv: Sample CSV of options data (can be regenerated using spx_chain.py).

---

## Installation

1. Clone the repository:
git clone https://github.com/ProbablyCodingRightNow/SPX-PDF.git
cd SPX-PDF


2. Set up a virtual environment (recommended):
python3 -m venv venv
source venv/bin/activate # Mac/Linux
venv\Scripts\activate # Windows

3. Install dependencies:
pip install -r requirements.txt


---

## Usage

1. Fetch SPX options data:
python3 spx_chain.py
Output: CSV file (default: SPX_options_next5_6000_7000.csv) with call options data.

2. Generate the PDF surface visualization:
python3 spx_pdf_surface.py
Opens an interactive 3D Plotly graph in your browser:
- X-axis: Strike price
- Y-axis: Expiration date
- Z-axis: Risk-neutral PDF

---

## How It Works

1. **Data Acquisition:** Fetches SPX call options for the specified strike range and nearest expirations.

2. **PDF Computation:** Uses the Breeden-Litzenberger formula: risk-neutral PDF ≈ second derivative of call prices with respect to strike prices.

3. **Visualization:** Interpolates PDF values across strikes and expirations to create a smooth 3D surface using Plotly.

> Note: Only call options are used. Strikes with no open interest still contribute via the midprice between bid and ask.

---

## Customization

- Strike Range: Adjust `strike_min` and `strike_max` in spx_chain.py.
- Number of Expirations: Adjust `num_expirations` in spx_chain.py.
- Interpolation & Visualization: Adjust grid resolution in spx_pdf_surface.py.

---

## License

MIT License — free to use, modify, and share.

---

## Acknowledgements
- Yahoo Finance / yfinance for options data.
- Plotly for interactive visualizations.
- Inspired by research on risk-neutral densities and the Breeden-Litzenberger formula.
