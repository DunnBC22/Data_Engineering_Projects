# Employee Separation Forecast - Prefect Pipeline

## Description

- Retrieve all three datasets
- Join the "submit_example" and "test_noLabel" based on ID
- Concatenate the previously joined dataset with the train dataset
- Remove the following features:
	- StandardHours (single value feature)
	- Over18 (single value feature)
	- EmployeeNumber (no value for the purposes of data analysis)
- Rename columns
	- "ID": "Id",
	- "Age": "EmpAge",
	- "Department": "DepartmentName",
	- "Education": "EducationLevel",
	- "Gender": "EmpGender",
	- "MaritalStatus": "EmpMaritalStatus",
	- "PerformanceRating": "EmpPerformanceRating",
	- "YearsWithCurrManager": "YearsWithCurrentManager"
- Clean values as such:
	- Replace '&' with 'And' in the following features:
		- DepartmentName
	- Remove all underscores & dashes in the following features:
		- BusinessTravel
- There are NO missing values
- Remove all whitespace for the following features:
	- JobRole
	- EducationField
	- DepartmentName
- Clean other string values as such:
	- EmpGender
		- "Male": "M"
		- "Female": "F"

## Dataset Source
https://www.kaggle.com/datasets/marquis03/employee-separation-forecast