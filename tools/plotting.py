from glob import glob
import matplotlib.pyplot as plt
import pandas as pd
import os

RES_DIR = 'data/results/plots'

# Create the plots directory if it doesn't exist
os.makedirs(RES_DIR, exist_ok=True)

def get_marker(nodes):
    if nodes == 1:
        return '.'
    elif nodes == 2:
        return '^'
    elif nodes == 4:
        return '*'
    else:
        raise ValueError(f"Unsupported number of nodes: {nodes}")

def get_color(method):
    if method == 'SERIAL':
        return 'black'
    elif method == 'OMP':
        return 'blue'
    elif method == 'MPI':
        return 'red'
    elif method == 'HYBRID':
        return 'green'
    else:
        raise ValueError(f"Unsupported method: {method}")

def plot_efficiency_over_processes(df, strategy=None):
    plt.figure(figsize=(10, 6))
    for (method, nodes), group in df.groupby(['METHOD', 'NODES']):
        if method == 'HYBRID':
            group['EFFICIENCY'] = group['EFFICIENCY'] / 4
        plt.plot(group['PROCESSES'], group['EFFICIENCY'], color=get_color(method), marker=get_marker(nodes), label=f"{method} (Nodes: {nodes})")
    plt.axhline(y=1, color='gray', linestyle='--', label='Ideal Efficiency')
    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Efficiency')
    plt.title(
        f'Efficiency per Method - (Strategy: {strategy})'
        if strategy
        else 'Efficiency per Method'
    )
    plt.legend()
    plt.grid()
    
    # Save the plot
    filename = f'efficiency_over_processes_{strategy}.png' if strategy else 'efficiency_over_processes.png'
    plt.savefig(os.path.join(RES_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def plot_time_over_processes(df, strategy=None):
    # Do a line plot where each method is a different line and each value is the number of PROCESSES, on the y axis we have time
    plt.figure(figsize=(10, 6))
    for (method, nodes), group in df.groupby(['METHOD', 'NODES']):
        plt.plot(group['PROCESSES'], group['TIME'], color=get_color(method), marker=get_marker(nodes), label=f"{method} (Nodes: {nodes})")

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Time (seconds)')
    plt.title(
        f'Time per Method - (Strategy: {strategy})'
        if strategy
        else 'Time per Method'
    )
    plt.legend()
    plt.grid()
    
    # Save the plot
    filename = f'time_over_processes_{strategy}.png' if strategy else 'time_over_processes.png'
    plt.savefig(os.path.join(RES_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def plot_time_over_threads(df, strategy=None):
    # Do a line plot where each method is a different line and each value is the number of threads, on the y axis we have time
    plt.figure(figsize=(10, 6))
    for (method, PROCESSES), group in df.groupby(['METHOD', 'PROCESSES']):
        plt.plot(group['THREADS'], group['TIME'], color=get_color(method), marker='o', label=f"{method} (PROCESSES: {PROCESSES})")

    plt.xlabel('Number of Threads')
    plt.ylabel('Time (seconds)')
    plt.title(
        f'Time per Method - (Strategy: {strategy})'
        if strategy
        else 'Time per Method'
    )
    plt.legend()
    plt.grid()
    
    # Save the plot
    filename = f'time_over_threads_{strategy}.png' if strategy else 'time_over_threads.png'
    plt.savefig(os.path.join(RES_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def plot_speed_up_over_processes(df, strategy=None):
    plt.figure(figsize=(10, 6))
    for (method, nodes), group in df.groupby(['METHOD', 'NODES']):
        plt.plot(group['PROCESSES'], group['SPEEDUP'], color=get_color(method), marker=get_marker(nodes), label=f"{method} (Nodes: {nodes})")

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Speedup')
    plt.title(
        f'Speedup per Method - (Strategy: {strategy})'
        if strategy
        else 'Speedup per Method'
    )
    plt.legend()
    plt.grid()
    
    # Save the plot
    filename = f'speedup_over_processes_{strategy}.png' if strategy else 'speedup_over_processes.png'
    plt.savefig(os.path.join(RES_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def load_data(glob_path):
    dfs = []
    for path in glob(glob_path):
        df = pd.read_csv(path,
            sep=',',
            header=None,
            names=['METHOD', 'NODES', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS', 'TIME', 'TOUR LEN']
        )
        df['STRATEGY'] = path.split('/')[-2]
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    return df

def plot_scalabilities(df):
    # We plot efficiency as the size of the graph increases
    # We fix threads to 4 for OMP and HYBRID, and 1 for SERIAL and MPI
    # We only consider runs with 1 nodes
    
    plt.figure(figsize=(10, 6))
    for method, group in df.groupby(['METHOD']):
        method = method[0]
        if method == 'SERIAL':
            continue
        elif method == 'HYBRID':
            group['EFFICIENCY'] = group['EFFICIENCY'] / 4
        group = group.sort_values('CITIES')
        plt.plot(group['PROCESSES'], group['EFFICIENCY'], color=get_color(method), marker='v', label=f"{method}")
        for i, row in group.iterrows():
            plt.text(row['PROCESSES'], row['EFFICIENCY'], f"{row['CITIES']}", fontsize=8, ha='right', va='bottom')

    plt.xlabel('Number of PROCESSES')
    plt.ylabel('Efficiency')
    plt.title('Scalability of Methods')
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(RES_DIR, 'scalability.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
def compute_stats(df, serial=None):
    serial_df = df[df['METHOD'] == 'SERIAL']
    for graph_size in df['CITIES'].unique():
        # Adjust serial time and speedup computation
        serial_time = serial_df[serial_df['CITIES'] == graph_size]['TIME'].mean() if serial is None else serial
        df.loc[df['CITIES'] == graph_size, 'SERIAL TIME'] = serial_time

    df['SPEEDUP'] = df['SERIAL TIME'] / df['TIME']
    df['EFFICIENCY'] = df['SPEEDUP'] / df['PROCESSES']

    return df

if __name__ == "__main__":
    # df = load_data('data/results/**/*.csv')
    # df = compute_stats(df)

    # # For each method, group if the following columns are the same:
    # # IMPLEMENTATION	CITIES	ANTS	PROCESSES	THREADS
    # # After grouping, update 'TIME' and 'TOUR LEN' columns to be the mean of the grouped values
    # # Ensure 'TIME' and 'TOUR LEN' are numeric
    # df['TIME'] = pd.to_numeric(df['TIME'], errors='coerce')
    # df['TOUR LEN'] = pd.to_numeric(df['TOUR LEN'], errors='coerce')
    # df = df.groupby(['METHOD','NODES', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS'], as_index=False)[['TIME', 'TOUR LEN']].mean().merge(
    #     df.drop(['TIME', 'TOUR LEN'], axis=1).drop_duplicates(), 
    #     on=['METHOD', 'NODES', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS']
    # )
    
    # df_scala = load_data('data/results/weak_scalability.csv')
    # df_scala = compute_stats(df_scala, serial=[])
    # plot_scalabilities(df_scala)

    # for strategy in df['STRATEGY'].unique():
    #     if strategy == 'serial':
    #         continue
    #     tmp_df = df[df['STRATEGY'] == strategy]
    #     # Add serial values as baseline
    #     serial_df = df[df['METHOD'] == 'SERIAL']
    #     tmp_df = tmp_df[tmp_df['CITIES'] == 1002]
    #     tmp_df = pd.concat([tmp_df, serial_df], ignore_index=True)
    #     plot_time_over_processes(tmp_df, strategy=strategy)
    #     # only plot results run on 64 PROCESSES
    #     tmp_df = tmp_df[tmp_df['PROCESSES'] == 32]
    #     tmp_df1 = df[df['METHOD'] == 'OMP']
    #     plot_time_over_threads(pd.concat([tmp_df, tmp_df1]), strategy=strategy)

    #     tmp_df = df[df['STRATEGY'] == strategy]
    #     tmp_df = tmp_df[tmp_df['CITIES'] == 1002]
    #     plot_speed_up_over_processes(tmp_df, strategy=strategy)
    #     plot_efficiency_over_processes(tmp_df, strategy=strategy)
    
    # print(f"All plots saved to {RES_DIR}")

    df = load_data('data/results/**/*.csv')
    # df = compute_stats(df)

    # For each method, group if the following columns are the same:
    # IMPLEMENTATION	CITIES	ANTS	PROCESSES	THREADS
    # After grouping, update 'TIME' and 'TOUR LEN' columns to be the mean of the grouped values
    # Ensure 'TIME' and 'TOUR LEN' are numeric
    df['TIME'] = pd.to_numeric(df['TIME'], errors='coerce')
    df['TOUR LEN'] = pd.to_numeric(df['TOUR LEN'], errors='coerce')
    df = df.groupby(['METHOD','NODES', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS'], as_index=False)[['TIME', 'TOUR LEN']].mean().merge(
        df.drop(['TIME', 'TOUR LEN'], axis=1).drop_duplicates(), 
        on=['METHOD', 'NODES', 'CITIES', 'ANTS', 'PROCESSES', 'THREADS']
    )
    plot_time_over_processes(df)
    plot_time_over_threads(df)