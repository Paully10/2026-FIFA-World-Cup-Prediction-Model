import os

import threading
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


class SimulationEngine:
    def __init__(self):
        self.elo_ratings = {}
        self.name_cleanup_map = {
            "United States": "USA", "Turkey": "Türkiye", 
            "Czech Republic": "Czechia", "Cura?o": "Curaçao", "Curacao": "Curaçao"
        }
        
    def load_and_clean_data(self):
        try:
            results = pd.read_csv('results.csv')
            fixtures = pd.read_csv('wc_2026_fixtures.csv')
            wc_data = pd.read_csv('Fifa world cup data.csv')
            former_names = pd.read_csv('former_names.csv')
            shootouts = pd.read_csv('shootouts.csv')
            
            for df, cols in [(results, ['home_team', 'away_team']), 
                             (wc_data, ['team']), 
                             (shootouts, ['home_team', 'away_team', 'winner'])]:
                for col in cols:
                    df[col] = df[col].replace(self.name_cleanup_map)
            
            historical_map = dict(zip(former_names['former'], former_names['current']))
            results['home_team'] = results['home_team'].replace(historical_map)
            results['away_team'] = results['away_team'].replace(historical_map)
            
            results = results.dropna(subset=['home_score', 'away_score'])
            results['date'] = pd.to_datetime(results['date'])
            results = results.sort_values(by='date').reset_index(drop=True)
            
            return results, fixtures, wc_data, shootouts
        except Exception as e:
            raise FileNotFoundError(f"Data loading failed. Check files in directory.\nError: {str(e)}")

    def compute_historical_elo(self, results_df):
        self.elo_ratings = {}
        
        def get_k_factor(tournament):
            if 'FIFA World Cup' in tournament: return 60
            elif 'Qualifiers' in tournament: return 40
            elif 'Friendly' in tournament: return 20
            return 30

        for idx, row in results_df.iterrows():
            home, away = row['home_team'], row['away_team']
            h_score, a_score = int(row['home_score']), int(row['away_score'])
            
            r_home = self.elo_ratings.get(home, 1500.0)
            r_away = self.elo_ratings.get(away, 1500.0)
            
            exp_home = 1 / (1 + 10 ** ((r_away - r_home) / 400))
            act_home = 1.0 if h_score > a_score else (0.0 if h_score < a_score else 0.5)
            k = get_k_factor(row['tournament'])
            
            self.elo_ratings[home] = r_home + k * (act_home - exp_home)
            self.elo_ratings[away] = r_away + k * ((1.0 - act_home) - (1.0 - exp_home))

    def run_monte_carlo(self, fixtures_df, iterations=1000):
        group_fixtures = fixtures_df[fixtures_df['stage'] == 'Group Stage'].copy()
        
        # Optimize execution loop by mapping structural entries to simple arrays
        match_tuples = list(zip(group_fixtures['team1'].tolist(), group_fixtures['team2'].tolist()))
        teams_in_scope = list(set(group_fixtures['team1'].tolist() + group_fixtures['team2'].tolist()))
        
        # Pull pre-computed elo elements directly to bypass function overhead loops
        team_elos = {team: self.elo_ratings.get(team, 1500.0) for team in teams_in_scope}
        
        # Pre-calculate win/loss probabilities between all group pairs
        match_probs = {}
        for t1, t2 in match_tuples:
            r1, r2 = team_elos[t1], team_elos[t2]
            match_probs[(t1, t2)] = 1 / (1 + 10 ** ((r2 - r1) / 400))

        # Tally matrices using primitive dictionaries (super fast in RAM)
        trophy_counts = {team: 0 for team in teams_in_scope}
        final_counts = {team: 0 for team in teams_in_scope}
        
        # Pre-generate random matrix dimensions to speed up thread execution loops
        rand_matrix = np.random.rand(iterations, len(match_tuples))
        knockout_rand_matrix = np.random.rand(iterations, 15) # 15 knockout matches total per cup run

        for sim in range(iterations):
            group_points = {team: 0 for team in teams_in_scope}
            
            # Vector execution step for Group matches
            for idx, (t1, t2) in enumerate(match_tuples):
                prob = match_probs[(t1, t2)]
                rand_val = rand_matrix[sim, idx]
                
                if rand_val < prob * 0.75:
                    group_points[t1] += 3
                elif rand_val > (1 - (1 - prob) * 0.75):
                    group_points[t2] += 3
                else:
                    group_points[t1] += 1
                    group_points[t2] += 1

            # Determine who qualifies
            sorted_teams = sorted(group_points.items(), key=lambda x: x[1], reverse=True)
            knockout_contenders = [t[0] for t in sorted_teams[:16]]
            
            while len(knockout_contenders) < 16:
                knockout_contenders.append(teams_in_scope[0])

            # Knockout round simulation sequence using cached array references
            k_idx = 0
            
            # Round of 16
            r8 = []
            for i in range(0, 16, 2):
                tA, tB = knockout_contenders[i], knockout_contenders[i+1]
                pA = 1 / (1 + 10 ** ((team_elos[tB] - team_elos[tA]) / 400))
                winner = tA if knockout_rand_matrix[sim, k_idx] < pA else tB
                r8.append(winner)
                k_idx += 1
                
            # Quarterfinals
            r4 = []
            for i in range(0, 8, 2):
                tA, tB = r8[i], r8[i+1]
                pA = 1 / (1 + 10 ** ((team_elos[tB] - team_elos[tA]) / 400))
                winner = tA if knockout_rand_matrix[sim, k_idx] < pA else tB
                r4.append(winner)
                k_idx += 1

            # Semifinals
            finalists = []
            for i in range(0, 4, 2):
                tA, tB = r4[i], r4[i+1]
                pA = 1 / (1 + 10 ** ((team_elos[tB] - team_elos[tA]) / 400))
                winner = tA if knockout_rand_matrix[sim, k_idx] < pA else tB
                finalists.append(winner)
                k_idx += 1

            # Final Match
            f1, f2 = finalists[0], finalists[1]
            final_counts[f1] += 1
            final_counts[f2] += 1
            
            pF1 = 1 / (1 + 10 ** ((team_elos[f2] - team_elos[f1]) / 400))
            winner = f1 if knockout_rand_matrix[sim, k_idx] < pF1 else f2
            trophy_counts[winner] += 1

        # Format output structures cleanly after the loop finishes
        summary_data = [
            {
                "Team": team,
                "Winner (%)": (trophy_counts[team] / iterations) * 100,
                "Make Finals (%)": (final_counts[team] / iterations) * 100
            } for team in teams_in_scope
        ]
            
        return pd.DataFrame(summary_data).sort_values(by="Winner (%)", ascending=False).head(10)



class WorldCupApp:
    def __init__(self, window):
        self.window = window
        self.window.title("2026 FIFA World Cup Predictive Modeling Studio")
        self.window.geometry("1100x700")
        self.window.configure(bg="#f4f6f9")
        
        self.engine = SimulationEngine()
        self.build_ui_layout()

    def build_ui_layout(self):
        header = tk.Frame(self.window, bg="#1e293b", height=80)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="🏆 2026 WORLD CUP SIMULATION HUB", font=("Helvetica", 16, "bold"), fg="white", bg="#1e293b")
        lbl_title.pack(pady=25, padx=20, side="left")

        self.body_frame = tk.Frame(self.window, bg="#f4f6f9")
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        left_panel = tk.LabelFrame(self.body_frame, text=" Engine Controls ", font=("Helvetica", 11, "bold"), bg="white", bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=(0, 15), ipadx=15, ipady=15)
        
        lbl_info = tk.Label(left_panel, text="Simulation Running Volume:", bg="white", font=("Helvetica", 10))
        lbl_info.pack(anchor="w", padx=10, pady=(15, 5))
        
        self.txt_iterations = ttk.Entry(left_panel, font=("Helvetica", 11))
        self.txt_iterations.insert(0, "100000")
        self.txt_iterations.pack(fill="x", padx=10, pady=5)
        
        self.btn_run = tk.Button(left_panel, text="🚀 Run Simulation Engine", font=("Helvetica", 11, "bold"), bg="#10b981", fg="white", activebackground="#059669", activeforeground="white", cursor="hand2", command=self.start_simulation_thread)
        self.btn_run.pack(fill="x", padx=10, pady=25)
        
        self.lbl_status = tk.Label(left_panel, text="Status: Ready", font=("Helvetica", 10, "bold"), fg="#475569", bg="white")
        self.lbl_status.pack(fill="x", padx=10, pady=10)
        
        self.right_panel = tk.LabelFrame(self.body_frame, text=" Predictive Graphics Display Grid ", font=("Helvetica", 11, "bold"), bg="white", bd=1, relief="solid")
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        self.placeholder_lbl = tk.Label(self.right_panel, text="Configure controls and hit run to map target probabilities.", font=("Helvetica", 11, "italic"), fg="#64748b", bg="white")
        self.placeholder_lbl.pack(expand=True)

    def start_simulation_thread(self):
        try:
            iters = int(self.txt_iterations.get())
            if iters <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Format Error", "Please provide a valid positive integer count for simulations.")
            return

        self.btn_run.config(state="disabled", bg="#cbd5e1", text="⚡ Processing Matrix...")
        self.lbl_status.config(text="Status: Loading Data Layer...", fg="#d97706")
        
        worker = threading.Thread(target=self.execute_async_simulation, args=(iters,))
        worker.daemon = True
        worker.start()

    def execute_async_simulation(self, iters):
        try:
            results_df, fixtures_df, wc_data, shootouts = self.engine.load_and_clean_data()
            
            self.window.after(0, lambda: self.lbl_status.config(text="Status: Computing Elo Ratings..."))
            self.engine.compute_historical_elo(results_df)
            
            self.window.after(0, lambda: self.lbl_status.config(text=f"Status: Simulating Bracket ({iters:,} runs)..."))
            df_plot = self.engine.run_monte_carlo(fixtures_df, iterations=iters)
            
            self.window.after(0, lambda: self.process_completed_simulation(df_plot))
            
        except Exception as err:
            self.window.after(0, lambda: self.handle_async_error(str(err)))

    def process_completed_simulation(self, df_plot):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        self.render_graphics(df_plot)
        self.btn_run.config(state="normal", bg="#10b981", text="🚀 Run Simulation Engine")
        self.lbl_status.config(text="Status: Calculation Complete!", fg="#16a34a")

    def handle_async_error(self, error_msg):
        self.btn_run.config(state="normal", bg="#10b981", text="🚀 Run Simulation Engine")
        self.lbl_status.config(text="Status: Execution Error", fg="#dc2626")
        messagebox.showerror("Execution Fault", error_msg)

    def render_graphics(self, df):
        df_sorted = df.sort_values(by="Winner (%)", ascending=True)
        
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=100)
        sns.set_theme(style="whitegrid")
        
        colors = sns.color_palette("viridis", len(df_sorted))
        bars = ax.barh(df_sorted["Team"], df_sorted["Winner (%)"], color=colors, height=0.55)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.grid(True, linestyle='--', alpha=0.5)
        ax.yaxis.grid(False)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    va='center', ha='left', fontsize=9, fontweight='bold', color='#1e293b')
            
        ax.set_title("Probability Distribution of Lifting the 2026 World Cup Trophy", fontdict={'weight':'bold', 'size':11}, pad=15)
        ax.set_xlabel("Win Expectancy Percentage (%)", fontdict={'weight':'semibold', 'size':9})
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldCupApp(root)
    root.mainloop()