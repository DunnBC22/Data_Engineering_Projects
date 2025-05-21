# Top Researchers & Scientists - Prefect Pipeline


## Description

- Remove columns: 
    - "Years of Experience" because it is redundant with "Start Year"
- Rename columns:
    - "id": "Id",
    - "Name": "ResearcherName",
    - "Department": "DepartmentName",
    - "University": "UnisersityName",
    - "Location": "WorkLocation",
    - "Profile URL": "PersonalProfileLink", 
    - "Qualification": "Qualifications",
    - "Honours and Awards": "HonorsAndAwards",
    - "Highest Qualification": "HighestQualification",
    - "Has Awards": "HasAwards",
    - "Start Year": "StartYear"
- Handle missing data
    - HonorsAndAwards -> null: "NoneListed"
    - WorkLocation -> None : "NotListed"
- Clean up strings (strip whitespace & titlecase)
    - ResearcherName
    - Position
    - DepartmentName
    - UniversityName
    - WorkLocation
    - WebsiteLink
    - PersonalProfile
    - HasAwards
- Clean up strings (strip whitespace & replace repeated whitespace values with single space)
    - HonorsAndAwards
    - HighestQualification
- Clean up values in the  "HighestQualification" as such:
    - "B.Tech": "BTech"
    - "M.Sc": "MSc"
    - "M.Tech": "MTech"
    - "Ph.D": "PhD"
- Clean up values in the "WorkLocation" feature as such (from: to):
    - "None": "NotListed",
    - "Haryana?": "Haryana",
    - "Chhattishgarh": "Chhattisgarh",
    - "Gujarat State": "Gujarat",
    - "Jammu & Kashmir": "Jammu And Kashmir",
    - "Maharasthra": "Maharashtra",
    - "Maharshtra": "Maharashtra",
    - "Orissa": "Odisha",
    - "TamilNadu": "Tamil Nadu",
    - "Tamilnadu": "Tamil Nadu",
    - "TN": "Tamil Nadu",
    - "Telagana": "Telangana",
    - "Utter Pradesh": "Uttar Pradesh"

- Clean up values in the "Position" feature as such:
    - "Assistant Professor (Grade-I)": "Assistant Professor",
    - "Assistant Professor (Grade-II)": "Assistant Professor",
    - "Assistant Professor (Grade-III)": "Assistant Professor",
    - "Assistant Professor (Senior Grade)": "Assistant Professor",
    - "Assistant Professor - Selection Grade": "Assistant Professor",
    - "Assistant Professor - Senior Scale": "Assistant Professor",
    - "Assistant professor": "Assistant Professor",
    - "Associate Professor (Senior Grade)": "Associate Professor",
    - "Associate Professor": "Associate Professor",
    - "Associate Professor G": "Associate Professor",
    - "Associate Professor": "Associate Professor",
    - "Associate Research Professor": "Associate Professor", 
    - "Associate Teaching Professor": "Associate Professor",
    - "Infosys Chair Professor": "Chair Professor",
    - "Chairman": "Chairperson",
    - "Directorate of Research": "Directorate",
    - "Head Of the Department": "Head of Department",
    - "Librarian (Associate Professor Scale)": "Librarian",
    - "Pro Vice-Chancellor": "Pro Vice Chancellor",
    - "Pro-Chancellor": "Pro Chancellor",
    - "Professor (HAG)": "Professor",
    - "Professor of Practice": "Professor", 
    - "professor": "Professor",
    - "Prof. Agharkar Chair": "Professor", 
    - "Institute Professor": "Professor",
    - "Scientific Officer D": "Scientific Officer",
    - "Scientific Officer E": "Scientific Officer",
    - "Scientific Officer F": "Scientific Officer",
    - "Scientific Officer G": "Scientific Officer",
    - "Scientific Officer H": "Scientific Officer",
    - "Scientist B": "Scientist",
    - "Scientist C": "Scientist",
    - "Scientist D": "Scientist",
    - "Scientist E": "Scientist",
    - "Scientist E1": "Scientist",
    - "Scientist E2": "Scientist",
    - "Scientist F": "Scientist",
    - "Scientist G": "Scientist",
    - "Scientist SG": "Scientist",
    - "Scientist V": "Scientist",
    - "Scientist VII": "Scientist"
- Cast StartYear to Integer

__Note:__
- For the following feartures, I would normally clean them similar to how I cleaned the Position and WorkLocation features; however, since there are many multiples more of unique values for each feature, I want it duly note that I understand, but am passing on the task to reduce the time required for this project:
    - Expertise
    - Experience 
    - Qualification 
    - Honours and Awards

## Dataset Source
https://www.kaggle.com/datasets/mannacharya/vidwan-indian-faculty-and-researcher-dataset