# Python-to-MS-SQL-server
Pilote pyodbc package to execute/send queries and retrieve data. 

The aim of this tutorial is to use pyodbc package to send a request to the server in order to extract a pivot table from the data survey_DB database (based on the table called SurveyStructure). 

Second purpose is to create a trigger in the python program running behind which update the extracted information each time there is an update of the dababase structure.

The python app will save  the last survey structure and the extracted table as .csv files in a folder.

# Database backup in the MS SQL server : 
A dummy survey_DB (for illustration purpose only) contains tables **Survey, SurveyStructure, Question, Answer** and **User**. Features  of the tables at a glance : 

- Answer table :
```java
SELECT TOP (1000) [QuestionId]
      ,[SurveyId]
      ,[UserId]
      ,[Answer_Value]
  FROM [Survey_DB].[dbo].[Answer]
  ```
- Survey table:  <mark>QuestionId, SurveyId, UserId, Answer_Value</mark>
- Question table : <mark>QuestionId, Question_Text</mark>
- SurveyStructure: SurveyId, QuestionId, OrdinalValue
 *This table is the key table that describes the survey structure based on which we can extract the data.* 
- User table : [UserId], [User_Name], [User_Email]
