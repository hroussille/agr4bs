import argparse
from matplotlib import pyplot as plt
import os
import pandas as pd
import seaborn as sns

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str, help='Folder containing CSV datas to visualize')
    args = parser.parse_args()

    sns.set()
    sns.set_style("whitegrid")

    # Load all csv files in the folder
    data = []

    # For each file, load the data
    files = os.listdir(args.folder)
    for file in files:
        data.append(pd.read_csv(os.path.join(args.folder, file)))

    # Add an epoch column to each dataframe, starting at 0 and incrementing by 1
    for i, d in enumerate(data):
        d['epoch'] = range(1, len(d) + 1)

    # Concatenate all dataframes into one
    df = pd.concat(data, axis=0, ignore_index=True)

    # Create a dataframe with the columns : epoch, value, type
    # Where type is either 'successfull_forks', 'failed_forks'
    df_forks = pd.DataFrame(columns=['epoch', 'value', 'type'])

    # Iterate over df to create the new dataframe
    for i in range(len(df)):
        df_forks = pd.concat([df_forks, pd.DataFrame({'epoch': [df['epoch'][i]], 'value': [df[df.columns[0]][i]], 'type': ['successfull forks']})], ignore_index=True)
        df_forks = pd.concat([df_forks, pd.DataFrame({'epoch': [df['epoch'][i]], 'value': [df[df.columns[1]][i]], 'type': ['failed forks']})], ignore_index=True)

    df_rewards = pd.DataFrame(columns=['epoch', 'value', 'type'])

    for i in range(len(df)):
        df_rewards = pd.concat([df_rewards, pd.DataFrame({'epoch': [df['epoch'][i]], 'value': [df[df.columns[2]][i]], 'type': ['honest reward']})], ignore_index=True)
        df_rewards = pd.concat([df_rewards, pd.DataFrame({'epoch': [df['epoch'][i]], 'value': [df[df.columns[3]][i]], 'type': ['malicious reward']})], ignore_index=True)
        
    # Print the columns
    # df = pd.melt(df, ['epoch'])

    # Plot the data
    sns.relplot(data=df_forks, kind='line', x='epoch', y='value', hue='type')
    plt.savefig('forks.png')

    sns.relplot(data=df_rewards, kind='line', x='epoch', y='value', hue='type')
    plt.savefig('rewards.png')

    # Display the plot
    plt.show()




if __name__ == '__main__':
    main()





