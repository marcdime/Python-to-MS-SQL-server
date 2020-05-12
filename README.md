# Python-to-MS-SQL-server
Pilote pyodbc package to execute/send queries and retrieve data. 
The aim of this tutorial is to use pyodbc package to send a request to the server in order to extract a pivot table from the data survey_DB database. 
Second purpose is to create a trigger in the python program running behind which update the extracted information each time there is a change of the dababase structure

# Database backup in the MS SQL server : 
A dummy survey_DB (for illustration purpose only) contains tables **Survey, SurveyStructure, Question, Answer** and **User**. The features  of the tables  at a glance : 
- Survey : 
