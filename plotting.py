import matplotlib.pyplot as plt
import pandas as pd

def plot_efficiency_over_processes(df):
    plt.figure(figsize=(10, 6))
    for (method, threads), group in df.groupby(['METHOD', 'THREADS']):
        plt.plot(group['PROCESSES'], group['EFFICIENCY'], marker='o', label=f"{method} (Threads: {threads})")

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Efficiency')
    plt.title('Efficiency per Method')
    plt.legend()
    plt.grid()
    plt.show()

def plot_time_over_processes(df):
    # Do a line plot where each method is a different line and each value is the number of PROCESSES, on the y axis we have time
    plt.figure(figsize=(10, 6))
    for (method, threads), group in df.groupby(['METHOD', 'THREADS']):
        plt.plot(group['PROCESSES'], group['TIME'], marker='o', label=f"{method} (Threads: {threads})")

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Time (seconds)')
    plt.title('Time per Method')
    plt.legend()
    plt.grid()
    plt.show()

def plot_time_over_threads(df):
    # Do a line plot where each method is a different line and each value is the number of threads, on the y axis we have time
    plt.figure(figsize=(10, 6))
    for (method, PROCESSES), group in df.groupby(['METHOD', 'PROCESSES']):
        plt.plot(group['THREADS'], group['TIME'], marker='o', label=f"{method} (PROCESSES: {PROCESSES})")

    plt.xlabel('Number of Threads')
    plt.ylabel('Time (seconds)')
    plt.title('Time per Method')
    plt.legend()
    plt.grid()
    plt.show()

def plot_speed_up_over_processes(df):
    plt.figure(figsize=(10, 6))
    for (method, threads), group in df.groupby(['METHOD', 'THREADS']):
        plt.plot(group['PROCESSES'], group['SPEEDUP'], marker='o', label=f"{method} (Threads: {threads})")

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Speedup')
    plt.title('Speedup per Method')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    df = pd.read_csv('results.csv',
        sep=',',
        header=None,
        names=['METHOD', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS', 'TIME', 'TOUR LEN']
    )
    # Compute speedup as serial time/parallel time
    serial_time = df[df['METHOD'] == 'SERIAL']['TIME'].values[0]
    df['SPEEDUP'] = serial_time / df['TIME']
    # Compute efficiency as speedup/number of processes
    df['EFFICIENCY'] = df['SPEEDUP'] / df['PROCESSES']

    # For each method, group if the following columns are the same:
    # IMPLEMENTATION	CITIES	ANTS	PROCESSES	THREADS
    # After grouping, update 'TIME' and 'TOUR LEN' columns to be the mean of the grouped values
    # Ensure 'TIME' and 'TOUR LEN' are numeric
    df['TIME'] = pd.to_numeric(df['TIME'], errors='coerce')
    df['TOUR LEN'] = pd.to_numeric(df['TOUR LEN'], errors='coerce')
    df = df.groupby(['METHOD', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS'], as_index=False)[['TIME', 'TOUR LEN']].mean().merge(
        df.drop(['TIME', 'TOUR LEN'], axis=1).drop_duplicates(), 
        on=['METHOD', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS']
    )

    plot_time_over_processes(df)

    # only plot results run on 64 PROCESSES
    tmp_df = df[df['PROCESSES'] == 32]
    tmp_df1 = df[df['METHOD'] == 'OMP']
    plot_time_over_threads(pd.concat([tmp_df, tmp_df1]))

    plot_speed_up_over_processes(df)
    plot_efficiency_over_processes(df)