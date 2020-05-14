'''
All queries and constant strings for "main.py" file are listed below
'''

SERVER_CONNECTION = "DRIVER={SQL Server};SERVER=YOUR_SERVER_NAME;DATABASE=Survey_DB;Trusted_Connection=yes"

PATH_BASE = "./"

NAME_FOLDER ="X_PROJECT"

NAME_FILE_SS = "SurveyStructure.csv"

NAME_FILE_DATA = "SurveyData.csv"


QUERY_SURVEY = '''SELECT SurveyId FROM Survey'''


QUERY_IN_SURVEY = '''SELECT * FROM (
						SELECT
							SurveyId,
							QuestionId,
							1 as InSurvey
						FROM
							SurveyStructure
						WHERE
							SurveyId = SurveyID_value
						UNION
						SELECT 
							SurveyID_value as SurveyId,
							Q.QuestionId,
							0 as InSurvey
						FROM
							Question as Q
						WHERE NOT EXISTS
						(
							SELECT *
							FROM SurveyStructure as S
							WHERE S.SurveyId = SurveyID_value AND S.QuestionId = Q.QuestionId
						)
					) as t
					ORDER BY QuestionId'''

QUERY_ANS_QUESTION = '''COALESCE((SELECT a.Answer_Value 
								  FROM Answer as a Where a.UserId = u.UserId 
								       AND a.SurveyId = SurveyID_value AND a.QuestionId = <QUESTION_ID> 
							   ), -1) AS ANS_Q<QUESTION_ID> '''




QUERY_ANS_QUESTION_NULL = '''NULL AS ANS_Q<QUESTION_ID>'''


QUERY_BLOCK_UNION = '''SELECT
					UserId
					, SurveyID_value as SurveyId
					, <DYNAMIC_QUESTION_ANSWERS>
			FROM
				[User] as u
			WHERE EXISTS
			(
					SELECT *
					FROM Answer as a
					WHERE u.UserId = a.UserId
					AND a.SurveyId = SurveyID_value
			)
			'''

QUERY_SURVEY_STRUCTURE = ''' SELECT * FROM SurveyStructure '''

QUERY_CREATE_VIEW_ALLSURVEY = ''' CREATE OR ALTER VIEW view_AllSurveyData AS '''

QUERY_EXTRACT_VIEW_ALLSURVEY = '''SELECT * FROM view_AllSurveyData ORDER BY UserId '''