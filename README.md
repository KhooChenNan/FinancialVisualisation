## Financial Visualisation

Welcome to the Financial Visualization Project! This project is designed to provide a comprehensive portfolio management system with an AI-driven rebalancing bot, and analysis tools for chartings. The goal is to empower users with a sophisticated platform for managing their financial portfolios and making informed investment decisions.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

## Introduction

This research endeavor is poised to furnish readers with a detailed overview of the project's inception, implementation, and the subsequent assessment of the proposed financial visualization tools. Readers will gain insights into the potential advantages and disadvantages of the system, as well as how it can be effectively utilized in the dynamic landscape of the financial market.

Moreover, this approach introduces a novel perspective on the effectiveness of various technical indicators in making informed trading decisions. By evaluating the agent's performance across multiple strategies, we aim to pinpoint the most successful techniques, providing users with valuable insights into optimizing their trading strategies.


## Getting Started

Install all of the requierd libraries by running the following command:
    <pre>
    pip install -r requirements.txt
    </pre>

### Prerequisites

Software/dependencies that users need to have installed in order to run this project include the following:
1. Streamlit
2. xlrd
3. db-sqlite3
4. vega-datasets
5. Pillow
6. yfinance
7. yahoo-finance
8. altair
9. plotly
10. pandas
11. numpy
12. yahoo_fin

### Installation

Step-by-step guide on how to install the project.

1. Clone the repository:
   ```sh
   git clone https://github.com/KhooChenNan/FinancialVisualisation.git
2. Install all of the requirements as mentioned prior.
3. Open "mainmenu.py" in Visual Studio Code and run by typing "streamlit run mainmenu.py"

### Descriptions

<details>
<summary>Dip Finder View</summary>
<p>A tool designed to pinpoint potential buying opportunities for financial assets based on their current market prices and corresponding moving averages. This feature facilitates informed investment decisions by analyzing whether the current price is significantly below the relevant moving average, identifying potential market dips or undervaluations. Providing a user-friendly interface with visual representations, the "Dip Finder View" empowers users to quickly assess and capitalize on favorable entry points, making it a valuable asset for both novice and experienced investors seeking to optimize their trading strategies.</p>
</details>
![dip_finder_view](https://github.com/KhooChenNan/FinancialVisualisation/assets/93215251/6a757225-cf24-4272-bf54-353ea0067162)

<details>
<summary>AI rebalancing bot</summary>
<p>A hard-coded heuristic agent, this intelligent bot is designed to elevate portfolio management by leveraging advanced algorithms for automatic optimization of holdings. Seamlessly adapting to dynamic market conditions, the AI Rebalancing Bot minimizes manual intervention, ensuring portfolios remain strategically aligned.</p>
</details>
![ai_rebalancing_bot](https://github.com/KhooChenNan/FinancialVisualisation/assets/93215251/1c8b293c-06d2-45d6-9da9-faab3777552a)

<details>
<summary>Portfolio Management System</summary>
<p>Empowering users with robust portfolio management capabilities, the Portfolio Management System is equipped with a sophisticated algorithmic agent. This intelligent tool goes beyond conventional approaches, utilizing advanced algorithms to automatically optimize portfolio holdings. In the face of dynamic market conditions, the system seamlessly adapts, significantly reducing the need for manual intervention. By strategically aligning portfolios, it provides users with a resilient and responsive approach to navigate the complexities of the financial landscape.</p>
</details>
![portfolio_management_system](https://github.com/KhooChenNan/FinancialVisualisation/assets/93215251/47f86661-a636-4e0f-8478-c07924b558d4)

### Note

Make sure you are in a country that is not listed by Binance as banned as it utilizes the Binance API for the cryptocurrencies' data.  You may refer to the GIF and compare if it works for you.  If an error pops out or says that the connection has timed out, it is most likely due to your country not available to access Binance.
