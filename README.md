# 🏆 2026 FIFA World Cup Predictive Modeling Studio

An end-to-end Python analytics application that simulates the **2026 FIFA World Cup** using **Historical Elo Ratings** and **Monte Carlo Simulations**. Powered by asynchronous multi-threaded execution and a clean Tkinter GUI, the engine simulates up to 100,000+ full tournament iterations to generate statistical win probabilities for participating national teams.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-00599C?style=for-the-badge&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/Library-NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Library-Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Data%20Viz-Matplotlib-11557c?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Project Overview

Predicting international soccer tournaments involves high variance, non-linear team performance, and knockout-stage volatility. This project solves this challenge by building an explicit **Elo-driven simulation engine** backed by vectorized Monte Carlo runs:

1. **Historical Elo Rating Computation:** Processes full international match history, applying dynamic weighting (K-factors) based on match importance (World Cup matches vs. Qualifiers vs. Friendlies).
2. **Vectorized Monte Carlo Bracket Engine:** Simulates the complete tournament—from Group Stage points tallying to single-elimination Knockout rounds—tens or hundreds of thousands of times in seconds.
3. **Interactive Graphical Studio:** A responsive desktop dashboard built with `tkinter`, `matplotlib`, and `seaborn` that runs simulations in worker threads without freezing the user interface.

---

## 📊 Key Results (100,000 Iteration Benchmark)

Running **100,000 simulation passes** produced the following expected trophy win probability distribution across top contenders:

| Rank | Country | Win Expectancy (%) | Model Insights |
| :---: | :--- | :---: | :--- |
| 🥇 | **Spain** | **15.1%** | Highest baseline rating based on recent international form |
| 🥈 | **Argentina** | **14.5%** | Reigning champions retain top-tier knockout resilience |
| 🥉 | **France** | **13.3%** | Deep squad depth drives high win consistency |
| 4 | **England** | **7.6%** | Solid path stability into Quarter/Semi-Finals |
| 5 | **Mexico** | **5.3%** | Benefits from host seeding and home-continent group pairing |
| 6 | **Netherlands** | **4.9%** | Competitive bracket progression profile |
| 7 | **Morocco** | **4.9%** | Strong rating retention following recent major tournaments |
| 8 | **Brazil** | **4.6%** | Strong individual strength rating; variance in single-elimination paths |
| 9 | **Germany** | **3.2%** | Moderate run expectancy in single-elimination paths |
| 10 | **Colombia** | **3.2%** | Rounds out top 10 national contenders |

---

## ⚡ Mathematical & Algorithmic Architecture

### 1. Match Importance K-Factor Strategy
To capture true team strength, historical match results are processed sequentially using variable $K$-factors:
```math
K = egin{cases} 
60 & 	ext{FIFA World Cup Matches} \
40 & 	ext{World Cup Qualifiers \& Continental Cup Matches} \
30 & 	ext{Other Competitive Tournaments} \
20 & 	ext{International Friendlies}
\end{cases}
```

### 2. Expected Match Result Formula
The expected outcome $E_A$ for Team A against Team B is calculated via the standard logistic Elo curve:
```math
E_A = rac{1}{1 + 10^{(R_B - R_A) / 400}}
```
Where $R_A$ and $R_B$ represent the current Elo ratings of Team A and Team B.

### 3. Group Stage Points Distribution
In group matches, probabilities are adjusted for draws:
* **Team A Win:** $P(A) = E_A 	imes 0.75 \implies +3 	ext{ points}$
* **Team B Win:** $P(B) = (1 - E_A) 	imes 0.75 \implies +3 	ext{ points}$
* **Draw:** Remaining probability balance $\implies +1 	ext{ point each}$

---

## 🛠️ Data Pipeline & Cleaning

The application automatically cleans and normalizes data across historical files:
* **Entity Resolution:** Maps historical country names (e.g., *West Germany* $	o$ *Germany*, *Soviet Union* $	o$ *Russia*) using `former_names.csv`.
* **String Standardizations:** Resolves naming mismatches across datasets (e.g., *United States* $	o$ *USA*, *Turkey* $	o$ *Türkiye*, *Czech Republic* $	o$ *Czechia*).
* **Score Validation:** Drops unplayed or incomplete fixture rows and sorts historical matches chronologically to calculate sequential Elo adjustments.

---

## 🗂️ Project Directory Structure

```text
├── check_files.py          # Environment verification & data check script
├── world_cup_app.py        # Main Tkinter Application & Simulation Engine
├── results.csv             # Historical international match results
├── wc_2026_fixtures.csv    # Official World Cup 2026 match schedule
├── Fifa world cup data.csv # World Cup team metadata & statistics
├── former_names.csv        # Country name historical mapping dictionary
├── teams.csv               # Team list & confederation metadata
├── shootouts.csv           # Historical penalty shootout records
└── goalscorers.csv         # Detailed individual goalscorer records
```

---

## 🚀 Quick Start & Installation

### Prerequisites
Make sure you have **Python 3.9+** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/2026-world-cup-predictive-model.git
cd 2026-world-cup-predictive-model
```

### 2. Install Dependencies
Install the required packages using `pip`:
```bash
pip install pandas numpy matplotlib seaborn
```
*(Note: `tkinter` is bundled with standard Python installations on Windows and macOS. Linux users can install it via `sudo apt install python3-tk`).*

### 3. Verify Required Data Files
Run the diagnostic script to ensure all `.csv` files are present in your workspace:
```bash
python check_files.py
```

### 4. Launch the Simulation Studio
```bash
python world_cup_app.py
```

---

## 🖥️ Application UI Features

* **Custom Simulation Volume:** Enter any iteration count (e.g., `1,000` for rapid testing or `100,000` for high-precision statistical convergence).
* **Asynchronous Multi-Threading:** Runs heavy matrix calculations on background daemon threads (`threading.Thread`) to keep the UI smooth and responsive.
* **Embedded Analytics Plotting:** Embeds Seaborn & Matplotlib horizontal bar plots directly within the Tkinter window using `FigureCanvasTkAgg`.

---

## 🔮 Roadmap & Future Enhancements

- [ ] **Expanded 48-Team Format:** Upgrade group stage qualifying logic to accommodate 12 groups of 4 and 32 knockout teams (including best 3rd-place qualifiers).
- [ ] **Home Advantage & Travel Distance Factors:** Incorporate stadium location penalties and host country advantage offsets into expected match win probabilities.
- [ ] **Goal Difference Tiebreakers:** Implement explicit goal-scoring simulations to resolve group stage ties via simulated goal margins rather than raw points.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

⭐ **If you find this project useful or interesting, feel free to give it a star on GitHub!**
