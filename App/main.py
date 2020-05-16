import pandas as pd
import os
import pyodbc
import time
import config as cf

'''
Function to retrieve data (dataframe) from the server
''' 
def getdata(query):
    sql_conn = pyodbc.connect(cf.SERVER_CONNECTION)
    sql_conn.autocommit = True
    
    try: 
        data_df = pd.read_sql(query, sql_conn)
    except:
        print("Query not found !")
    sql_conn.close()    
    return data_df

'''
Function to put data to the server
'''
def updata(query):
    sql_conn = pyodbc.connect(cf.SERVER_CONNECTION) 
    sql_conn.autocommit= True
    try:
        sql_conn.cursor().execute(query)        
    except:
        print("Query not found !")
    sql_conn.close()

'''
Function to create the folder containing all generated files
'''
def create_file_path(name_folder, filename):
    folder =  os.path.join(cf.PATH_BASE,name_folder)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder,filename)

'''
Function to display the dataframe retrieved from the getdata() function
'''
def display_data(input_query):
    get_data = getdata(input_query)
    return print(get_data.head(100))

'''
Iterator for SurveyID
'''
class iter_Survey():        
    def __init__(self, cursor_Survey):
        self.cursor_Survey = cursor_Survey

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count < len(self.cursor_Survey):
            SurveyId = self.cursor_Survey["SurveyId"].iloc[self.count]
            self.count +=1
            return SurveyId
        else:
            raise StopIteration
            
'''
Iterator for QuestionID
'''
class iter_Question():
    def __init__(self, cursor_Question):
        self.cursor_Question = cursor_Question

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count < len(self.cursor_Question):

            SurveyIdInQuestion = self.cursor_Question["SurveyId"].iloc[self.count]
            QuestionId = self.cursor_Question["QuestionId"].iloc[self.count]
            InSurvey = self.cursor_Question["InSurvey"].iloc[self.count]
            self.count += 1

            return SurveyIdInQuestion, QuestionId, InSurvey
        else:
            raise StopIteration

'''
Function of the final query for getting pivot table
'''
def get_query_AllSurvey():
    
    final_query = " "
    
    data_Survey = getdata(cf.QUERY_SURVEY)
    
    for CurrentSurveyID in iter_Survey(data_Survey):        
        
        # Replace string "SurveyID_value" in QUERY_IN_SURVEY by CurrentSurveyID 
        query_question = cf.QUERY_IN_SURVEY.replace("SurveyID_value", str(CurrentSurveyID))
        
        # Get data with query_question        
        data_in_survey = getdata(query_question)

        # Initialization of the iterator SurveyID
        iterator_Question = iter_Question(data_in_survey)
        
               
        # Query for block ANS_Q1, ANS_Q2, ANS_Q3        
        Query_ANSQ_column = " "
        
        for CurrentSurveyIDInQuestion, CurrentQuestionID, InSurvey in iterator_Question :
                        
            #Print the triple
            #print(CurrentSurveyIDInQuestion, CurrentQuestionID, InSurvey)
                            
            if InSurvey == 1:
                Query_ANSQ_column += cf.QUERY_ANS_QUESTION.replace("<QUESTION_ID>", str(CurrentQuestionID))
            elif InSurvey == 0:
                Query_ANSQ_column += cf.QUERY_ANS_QUESTION_NULL.replace("<QUESTION_ID>", str(CurrentQuestionID))
            
            Query_ANSQ_column += " ,"
            
        # Delete the last comma of the Query_ANSQ_column query                     
        Query_ANSQ_column = Query_ANSQ_column[:-1]            
        
        # Replace <DYNAMIC_QUESTION_ANSWERS> by the dynamic block Query_ANSQ_column
        Query_union = cf.QUERY_BLOCK_UNION.replace("<DYNAMIC_QUESTION_ANSWERS>", Query_ANSQ_column)
        Query_union = Query_union.replace("SurveyID_value", str(CurrentSurveyID))
        
        final_query += Query_union + " UNION "
    
    #Delete the last "UNION" of the final_query query
    final_query = final_query[:-6]
    
    return final_query

'''
trigger class:
- Method check_save_last_SurveyStructure()
- Method launch_trigger()
- Method stop()
'''
class class_trigger():

    def __init__(self, query_Alldata, warning):

        self.query_Alldata = query_Alldata
        self.warning = warning


    def check_save_last_SurveyStructure(self):    

        last_Survey_Structure = getdata(cf.QUERY_SURVEY_STRUCTURE)
      
        filepath = create_file_path(cf.NAME_FOLDER, cf.NAME_FILE_SS)

        if os.path.exists(filepath):

            # Check the new SurveyStructure table and the saved SurveyStrure.csv file :
            df = pd.read_csv(filepath, sep = ";").drop("Unnamed: 0", axis = 1)
            equal = df.equals(last_Survey_Structure)

            # If there are different values in the two tables:
            # We save the last SurveyStructure and return True
            if not equal:
                last_Survey_Structure.to_csv(filepath, sep=';')
                print("\n Your last SurveyStructure.csv file is updated !")
                return (self.warning is "y")
            else:
                print (" Your SurveyStructure.csv file is NOT updated. It is the same as SurveyStructure table in the server !")
                return (self.warning is "y")
            
        else:
            # Create  SurveyStructure.csv file
            last_Survey_Structure.to_csv(filepath, sep=';')
            print (" Your SurveyStructure.csv file is created !")
            return False

    '''
    Methode properties:
    - Build query for creating view_AllSurveyData table
    - Extract data from the view_AllSurveyData and save it into AllSurveyData.csv file.
    '''    
    def launch_trigger(self):

        # file path of the SurveyData.csv file
        filepath = create_file_path(cf.NAME_FOLDER, cf.NAME_FILE_DATA)      

        #Query to create SurveyData table in the DB (found in "VIEWS")
        query_create = cf.QUERY_CREATE_VIEW_ALLSURVEY + self.query_Alldata
        
        # Connect and post query_create query to the server
        try:
            updata(query_create)
        except:
            print("table is not updated on server")
        
        # Get data from the SurveyData table and save data into 
        try:
            data_AllSurvey = getdata(cf.QUERY_EXTRACT_VIEW_ALLSURVEY)
            print("\n Data is sucessfully extracted from SurveyData table.")
            print(" Here are first 5 rows requested (UserId order) from SurveyData table:")
            time.sleep(3)
            print(data_AllSurvey.head())
        except:
            print("\n SurveyData table does not exist. \n Try refresh 'VIEWS' on the server !")
            
        # Check if SurveyData.csv exists. If not, we create one          
        if os.path.exists(filepath):
            # Save data into SurveyData.csv :        
            data_AllSurvey.to_csv(filepath, sep=';')
            print(" Your 'always-fresh' SurveyData.csv file is updated with these data.")
            
        else:
            # Create AllSurveyData.csv file
            data_AllSurvey.to_csv(filepath, sep=';')
            print ("\n Your 'always-fresh' SurveyData.csv file with these data is created ! \n")

    '''
    Method returns boolean value based on input "warning" to construct the stopping condition in main() function
    '''
    def stop(self):
        if self.warning == "stop":
            return False
        else:
            return True

'''
main() function
'''
def main():

    # Get the query of the pivot table
    query_for_AllSurvey = get_query_AllSurvey()    

    # Read input with textbox
    announce = input("\n Do you want to use the trigger to update your output <yes/no> ?: \n")

    if announce =="yes":

        #Initialization of class_trigger()
        trigger = class_trigger(query_for_AllSurvey, "n")
        trigger.launch_trigger()

        # Loop until the stop condition is raised: 
        # warning = "stop", method .stop() returns False 

        while trigger.stop():          
            
            '''
            if-else: check if there is a modification of the SurveyStructure.csv file, 
            if no modification, wait few seconds
            '''
            check_SS = trigger.check_save_last_SurveyStructure()
            
            if check_SS:
                trigger.launch_trigger()
            else:
                time.sleep(2)
            
            # Read input with textbox
            print("\n Did you recently modify SurveyStructure table <y/n> ?: \n (hit <stop> if you want to stop the trigger)")            
            warning_box = input()
            
            # Check the input text      
            if warning_box not in ["y", "n", "stop"]:
                  print("Error: input is invalid ! ")
                
            else:
                # Update the query query_for_AllSurvey and instanciation of the updated trigger class 
                query_for_AllSurvey = get_query_AllSurvey()
                trigger = class_trigger(query_for_AllSurvey, warning_box)

    elif announce =="no":

        # Display the 100 first rows obtained from the query get_query_AllSurvey
        print("\n 100 first rows received from the server with query_for_AllSurvey : \n")
        display_data(query_for_AllSurvey)

    else:
        print("Error: your input is invalid ! ")     
