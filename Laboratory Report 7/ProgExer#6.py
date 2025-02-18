import pandas as pd

def cleanStats(df):
    """
    Cleans the basketball stats dataset by splitting FG, 3PT, and FT columns
    into separate makes and attempts columns.
    """
    
    df[['FGM', 'FGA']] = df['FG'].str.split('-', expand=True).astype(int)

    
    df[['3PM', '3PA']] = df['3PT'].str.split('-', expand=True).astype(int)

 
    df[['FTM', 'FTA']] = df['FT'].str.split('-', expand=True).astype(int)

    
    df.drop(columns=['FG', '3PT', 'FT'], inplace=True)

  
    df.insert(df.columns.get_loc('FTA') + 1, ' ', '')

    return df

def main():
    """Loads the dataset, cleans it, and displays the cleaned data."""
    try:
        
        frame = pd.read_csv("cleanbrogdonstats.csv")

       
        frame = cleanStats(frame)

       
        frame = frame.drop(frame.columns[4:17], axis=1)

        
        print(frame.to_string(index=False))

    except FileNotFoundError:
        print("Error: File 'cleanbrogdonstats.csv' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
