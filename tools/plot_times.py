import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Settings for publication-quality plots
sns.set_theme(style="whitegrid", context="talk", font_scale=1.2)
palette = sns.color_palette("Set2")

# Read your data
df = pd.read_csv("data/results/times.csv", sep="\t")

# Clean numeric columns
for col in ['CITIES', 'ANTS', 'NODES', 'THREADS', 'TIME', 'TOUR LEN']:
    df[col] = df[col].astype(str).str.replace(",", "").astype(float)

# Function to plot lineplot with error bars
def plot_line_with_ci(x, y, hue, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        estimator='mean',
        ci='sd',
        marker='o',
        palette=palette
    )
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title=hue, loc='best')
    plt.tight_layout()
    plt.savefig(f"{filename}.pdf", bbox_inches='tight')
    plt.show()

# Function to plot violin + boxplot
def plot_violin(x, y, hue, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    sns.violinplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        palette=palette,
        inner=None,
        cut=0,
        linewidth=1
    )
    sns.boxplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        palette=palette,
        showcaps=True,
        boxprops={'facecolor':'none', 'edgecolor':'k'},
        showfliers=False,
        whiskerprops={'linewidth':2},
        width=0.2
    )
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:len(df['METHOD'].unique())], labels[:len(df['METHOD'].unique())], title=hue)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(f"{filename}.pdf", bbox_inches='tight')
    plt.show()

# ---- PLOTS ----

# Time vs Nodes - lineplot
plot_line_with_ci(
    x='NODES',
    y='TIME',
    hue='METHOD',
    title='Execution Time vs Processes',
    xlabel='Processes',
    ylabel='Time (s)',
    filename='time_vs_processes'
)

# Time vs Nodes - violin + boxplot
plot_violin(
    x='NODES',
    y='TIME',
    hue='METHOD',
    title='Execution Time Distribution by Nodes',
    xlabel='Nodes',
    ylabel='Time (s)',
    filename='violin_time_vs_nodes'
)

# Time vs Threads - lineplot
plot_line_with_ci(
    x='THREADS',
    y='TIME',
    hue='METHOD',
    title='Execution Time vs Threads',
    xlabel='Threads',
    ylabel='Time (s)',
    filename='time_vs_threads'
)

# Time vs Threads - violin + boxplot
plot_violin(
    x='THREADS',
    y='TIME',
    hue='METHOD',
    title='Execution Time Distribution by Threads',
    xlabel='Threads',
    ylabel='Time (s)',
    filename='violin_time_vs_threads'
)
