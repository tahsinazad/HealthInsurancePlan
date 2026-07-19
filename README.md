# Health Insurance Plan Advisor
## Overview

Health Insurance Plan Advisor is a decision support application that assists users in comparing health insurance plans based on their expected healthcare utilization. The application estimates annual healthcare costs by combining monthly premiums with projected out of pocket expenses, allowing users to compare multiple insurance plans and identify the most cost-effective option.

This project was developed for **CS 6795** as the Computational Model/Tool Track term project. The system demonstrates how cognitive science principles can be applied to support complex financial decision making.
---

## Features

- Compare multiple health insurance plans
- Estimate annual healthcare costs
- Account for:
  - Monthly premiums
  - Annual deductibles
  - Doctor visit copays
  - Prescription copays
  - Emergency room coinsurance
  - Hospital coinsurance
  - Out-of-pocket maximums
- Rank plans by estimated annual cost
- Generate plain-language explanations for recommendations
- Validate user input to prevent invalid insurance configurations

---

## Technologies

- Python 3
- Streamlit
- Pandas
---

## Running the Application

Install the required packages:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```

---

## Repository Structure

```
.
├── app.py
├── requirements.txt
├── README.md
└── documentation.md
```

---

## Disclaimer

This application is an academic proof-of-concept developed for educational purposes. Cost estimates are simplified and should not be interpreted as financial, medical, or insurance advice.
