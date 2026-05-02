# Researches Web Scraping API 📚🔍

A backend API built with Python to extract academic publications data from Google Scholar using the **Scholarly** library, with advanced handling to bypass common scraping limitations.

---

## 🚀 Overview

This project provides a simple and scalable API for retrieving research data such as:

* Publications
* Authors
* Citation counts
* Publication years

The API is designed to be integrated into other systems (e.g., dashboards, research tools, or analytics platforms).

---

## ✨ Features

* Fetch author data from Google Scholar
* Retrieve publication details (title, year, citations)
* RESTful API structure
* Clean and structured JSON responses
* Built with scalability in mind

---

## 🛠️ Tech Stack

* Python
* Django
* Scholarly
* Requests
* Redis
* Rabbitmq
* Celerly

---

## ▶️ How It Works

1. Provide a Google Scholar Author ID
2. The API fetches the author profile using **Scholarly**
3. Data is processed and returned as structured JSON

---

## ⚡ Handling Google Scholar Limitations

Google Scholar enforces strict anti-scraping protections such as:

* Rate limiting
* CAPTCHA challenges
* Temporary IP blocking

### ✅ In this project, these limitations were handled by:

* Using **Scholarly** as an abstraction layer
* Implementing **request delays** to avoid detection
* Adding **retry mechanisms** for failed requests
* Structuring requests to mimic normal user behavior
* Designing the system to be **extendable with proxies if needed**

This ensures more stable and reliable data extraction compared to basic scraping approaches.

---

## 📦 Installation

```bash
git clone https://github.com/AhmedEhab5006/ResearchesWebScrapingAPI.git
cd ResearchesWebScrapingAPI
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the server:

```bash
python app.py
```

Example request:

```
GET /api/author/{author_id}
```

Example response:

```json
{
  "name": "Author Name",
  "affiliation": "University",
  "publications": [
    {
      "title": "Paper Title",
      "year": 2023,
      "citations": 15
    }
  ]
}
```

---

## ⚠️ Disclaimer

* This project is for educational purposes only
* Respect Google Scholar terms of service
* Avoid sending excessive requests

---

## 🔧 Future Improvements

* Proxy rotation system
* Caching layer for performance
* Pagination support
* Frontend dashboard integration

---

## 👨‍💻 Author

Ahmed Ehab Abdulhamid
Full Stack .NET Developer

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
