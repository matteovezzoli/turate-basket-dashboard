# Youth Basketball Performance Analytics Dashboard 🏀

An interactive web application built with **Python**, **Streamlit**, and **Plotly** for tracking and analyzing performance metrics for a youth basketball team (Under 18).

This platform helps coaching staff and players monitor seasonal trends, providing objective insights into shot selection, offensive efficiency, and overall team performance.

---

## 📌 Key Features

* **📊 Game Center:** Detailed breakdown of individual games, including final scores, complete box scores, field goal percentages, and starter vs. bench contributions.
* **👤 Individual Player Profile:** Dedicated player cards with seasonal averages, shooting efficiency (2P, 3P, FT), turnover tracking, and game-by-game scoring progression charts.
* **📈 Advanced Roster Analysis:** High-level season overview featuring full roster metrics, points scored vs. conceded comparisons, and shooting percentage evolution over time.

---

## 🛠️ Tech Stack

* **Streamlit** - Web application framework
* **Pandas & NumPy** - Data processing and analytics
* **Plotly** - Interactive data visualization
* **OpenPyXL** - Excel data parsing

---

## 🚀 Data Pipeline

The application processes raw game logs from a structured Excel file (`Turate_Basket.xlsx`). It automatically handles inactive or missing players (`N/D` status), recalculates true shooting metrics, and updates team averages in real time as new games are added.
