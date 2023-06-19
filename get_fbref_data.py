def pull_data_from_fb(link = 'https://fbref.com/en/comps/9/Premier-League-Stats', pd = None, show_frame = False):
    
    if pd == None:
        import pandas as pd

    df = pd.read_html(link)
    
    if show_frame:
        print(df)
    
    return df

def remove_duplicates(frame):

    #   Removes duplicate column names from each dataframe passed to the function -
    #   FBRef tables often have absolute and per 90 figures for certain stats so this
    #   function renames any later occurences of a column name (usually the p90 version)

    cols = pd.Series(frame.columns)

    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]

    frame.columns = cols
    
    return frame

def override_names(frames, names):

    import csv

    with open(names, mode = 'r') as infile:
        reader = csv.reader(infile)
        override_dict = {rows[0]: rows[1] for rows in reader}

    for key, value in override_dict.items():
        frames.replace(key, value, inplace = True)

def make_team_frames(master_frame, stat_type = 'team'):

    #   Creates and returns a series of Dataframe objects built from FB Ref

    #   Team stats - add 1 to each frame number to get frame for stats against a particular team

    #   team_2 -    Standard stats
    #   team_4 -    Goalkeeping
    #   team_6 -    Advanced keeping
    #   team_8 -    Shooting
    #   team_10 -   Passing
    #   team_12 -   Pass types
    #   team_14 -   Goal & shot creation
    #   team_16 -   Defensive actions
    #   team_18 -   Possession
    #   team_20 -   Playing time
    #   team_22 -   Miscellaneous    

    frames = {}
    start = 2
    master_length = len(master_frame)
    
    for x in range(start, master_length):

        override_names(master_frame[x], 'overrides.csv')

        master_frame[x].columns = master_frame[x].columns.droplevel(0)

        #   ^ FBref frames are parsed in multilevel column format so droplevel
        #   method is needed to remove this  

        frame_name = '{}_{}'.format(stat_type, str(x))

        #   ^ Build a name for each unique dataframe
        #   Name is derived from stat_type argument variable ('team' or 'player')
        #   plus interated number between start and end of requested frames

        frames[frame_name] = master_frame[x]

        #   ^ Builds collection of frames as a dictionary

        frame_name = remove_duplicates(master_frame[x])

    return frames 

def dump_frames(frames, stat_type = 'team', output_folder = ''):

    #   Dumps all dataframes into Excel spreadsheet

    dump_filename = '{}_sheets'.format(stat_type)
    dump_path = output_folder + dump_filename

    for key in frames:
        with pd.ExcelWriter(dump_filename + '.xlsx', engine = 'openpyxl', mode = 'a') as writer:
            frames[key].to_excel(writer, sheet_name = str(key))

if __name__ == '__main__':
    
    import pandas as pd
    import os 
      
    os.chdir('C:\\Users\\sturgeka')

    df = pull_data_from_fb(show_frame = False)
    frames = make_team_frames(master_frame = df)

    dump_frames(frames)