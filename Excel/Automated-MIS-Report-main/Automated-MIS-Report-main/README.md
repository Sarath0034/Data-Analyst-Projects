# Automated MIS Reporting & Performance Dashboard

## 📌 Project Overview

This project demonstrates an end-to-end **MIS Reporting Automation Solution** developed using **Microsoft Excel, Power Query, PivotTables, PivotCharts, and Excel formulas**.

The primary objective of this project was to automate repetitive operational reporting activities such as **data loading, data cleaning, data transformation, data consolidation, KPI calculation, exception identification, and report formatting**.

The solution transforms recurring raw operational files into a structured and management-ready MIS report with minimal manual intervention.

---

## 🎯 Business Problem

In a traditional MIS reporting process, operational files need to be manually:

- Collected from different sources
- Cleaned and standardized
- Checked for data-quality issues
- Consolidated with historical data
- Calculated for productivity and SLA metrics
- Converted into reports
- Formatted before sharing with management

Performing these activities manually on a recurring basis is **time-consuming, repetitive, and prone to human errors**.

### Objective

The objective was to build an automated reporting workflow that could:

1. Load recurring operational files.
2. Clean and validate raw data.
3. Standardize data formats.
4. Handle duplicate and inconsistent records.
5. Identify missing values and outliers.
6. Append new data with historical data.
7. Calculate operational KPIs.
8. Generate structured MIS reports.
9. Automate repetitive Excel tasks using VBA.
10. Provide management with an interactive dashboard.

---

# 🔄 End-to-End MIS Workflow

```text
                Source Files
                     │
                     ▼
              Data Ingestion
                     │
                     ▼
                Power Query
                     │
                     ▼
            Data Cleaning
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Data Types    Duplicates    Text
    Validation    Handling      Standardization
        │            │            │
        └────────────┼────────────┘
                     ▼
             Missing Values
                     │
                     ▼
             Outlier Detection
                     │
                     ▼
           Data Transformation
                     │
                     ▼
        Historical + Current Data
                  Append
                     │
                     ▼
             KPI Calculations
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   Productivity      SLA        Error Rate
        │            │             │
        └────────────┼─────────────┘
                     ▼
              Master Dataset
                     │
                     ▼
             PivotTables &
              PivotCharts
                     │
                     ▼
            MIS Dashboard
                     │
                     ▼
             VBA Automation
                     │
                     ▼
          Management Reporting

```
---
## Power Query Code

```text
let
    Source = Folder.Files("D:\MIS\Reporting"),
    #"Sorted Rows" = Table.Sort(Source,{{"Name", Order.Ascending}}),
    #"Removed Other Columns" = Table.SelectColumns(#"Sorted Rows",{"Content"}),
    #"Filtered Hidden Files1" = Table.SelectRows(#"Removed Other Columns", each [Attributes]?[Hidden]? <> true),
    #"Invoke Custom Function1" = Table.AddColumn(#"Filtered Hidden Files1", "Transform File", each #"Transform File"([Content])),
    #"Removed Other Columns1" = Table.SelectColumns(#"Invoke Custom Function1", {"Transform File"}),
    #"Expanded Table Column1" = Table.ExpandTableColumn(#"Removed Other Columns1", "Transform File", Table.ColumnNames(#"Transform File"(#"Sample File"))),
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded Table Column1",{{"Emp_ID", type text}, {"Processor", type text}, {"Department", type text}, {"Date", type text}, {"Claims_Received", Int64.Type}, {"Claims_Completed", Int64.Type}, {"Pending", Int64.Type}, {"Inventory", Int64.Type}, {"Audits", Int64.Type}, {"Errors", Int64.Type}, {"Target", Int64.Type}, {"Shift", type text}, {"Supervisor", type text}}),
    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"Processor", Text.Trim, type text}}),
    #"Capitalized Each Word" = Table.TransformColumns(#"Trimmed Text",{{"Processor", Text.Proper, type text}}),
    #"Trimmed Text1" = Table.TransformColumns(#"Capitalized Each Word",{{"Department", Text.Trim, type text}}),
    #"Changed Type with Locale" = Table.TransformColumnTypes(#"Trimmed Text1", {{"Date", type date}}, "en-IN"),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type with Locale", each true),
    #"Changed Type1" = Table.TransformColumnTypes(#"Filtered Rows",{{"Claims_Received", Int64.Type}}),
    Custom1 = Table.ReplaceValue(#"Changed Type1",null,List.Median(List.RemoveNulls(#"Changed Type1"[Claims_Completed])),Replacer.ReplaceValue,{"Claims_Completed"}),
    Custom2 = Table.ReplaceValue(#"Custom1",null,List.Median(List.RemoveNulls(#"Custom1"[Pending])),Replacer.ReplaceValue,{"Pending"}),
    Custom3 = Custom2,
    Custom4 = Custom3,
    #"Filtered Rows1" = Table.SelectRows(Custom4, each true),
    Custom5 = #"Filtered Rows1",
    Custom6 = Table.ReplaceValue(#"Custom5",null,List.Median(List.RemoveNulls(#"Custom5"[Inventory])),Replacer.ReplaceValue,{"Inventory"}),
    Custom7 = Custom6,
    Custom8 = Table.ReplaceValue(#"Custom7",null,List.Median(List.RemoveNulls(#"Custom7"[Audits])),Replacer.ReplaceValue,{"Audits"}),
    Custom9 = Custom8,
    Custom10 = Table.ReplaceValue(#"Custom9",null,List.Median(List.RemoveNulls(#"Custom9"[Errors])),Replacer.ReplaceValue,{"Errors"}),
    Custom11 = Custom10,
    Custom12 = Table.ReplaceValue(#"Custom11",null,List.Median(List.RemoveNulls(#"Custom11"[Target])),Replacer.ReplaceValue,{"Target"}),
    #"Added Custom" = Table.AddColumn(Custom12, "STD", each List.StandardDeviation(#"Custom11"[Inventory])),
    #"Added Custom1" = Table.AddColumn(#"Added Custom", "Avg", each List.Average(#"Custom12"[Inventory])),
    #"Added Custom2" = Table.AddColumn(#"Added Custom1", "Med", each List.Median(#"Added Custom"[Inventory])),
    #"Added Custom3" = Table.AddColumn(#"Added Custom2", "Outlier_flag", each if [Inventory]>[Avg]+3*[STD] or [Inventory]<[Avg]-3*[STD]
then "Outlier"
else
"normal"),
    #"Filtered Rows4" = Table.SelectRows(#"Added Custom3", each true),
    #"Filtered Rows2" = Table.SelectRows(#"Filtered Rows4", each true),
    #"Added Custom4" = Table.AddColumn(#"Filtered Rows2", "cleaned", each if [Outlier_flag] = "Outlier" then [Med]
else [Errors]),
    #"Filtered Rows3" = Table.SelectRows(#"Added Custom4", each true),
    #"Removed Columns" = Table.RemoveColumns(#"Filtered Rows3",{"Errors"}),
    #"Renamed Columns" = Table.RenameColumns(#"Removed Columns",{{"cleaned", "Errors"}}),
    #"Reordered Columns" = Table.ReorderColumns(#"Renamed Columns",{"Emp_ID", "Processor", "Department", "Date", "Claims_Received", "Claims_Completed", "Pending", "Inventory", "Audits", "Errors", "Target", "Shift", "Supervisor", "STD", "Avg", "Med", "Outlier_flag"}),
    #"Added Custom5" = Table.AddColumn(#"Reordered Columns", "cleaned", each if [Outlier_flag] = "Outlier" then [Med]
else [Inventory]),
    #"Removed Columns1" = Table.RemoveColumns(#"Added Custom5",{"Inventory"}),
    #"Renamed Columns1" = Table.RenameColumns(#"Removed Columns1",{{"cleaned", "Inventory"}}),
    #"Changed Type2" = Table.TransformColumnTypes(#"Renamed Columns1",{{"Inventory", Int64.Type}, {"Errors", Int64.Type}}),
    #"Reordered Columns1" = Table.ReorderColumns(#"Changed Type2",{"Emp_ID", "Processor", "Department", "Date", "Claims_Received", "Claims_Completed", "Pending", "Inventory", "Audits", "Errors", "Target", "Shift", "Supervisor", "STD", "Avg", "Med", "Outlier_flag"}),
    #"Removed Columns2" = Table.RemoveColumns(#"Reordered Columns1",{"Outlier_flag", "Med", "Avg", "STD"}),
    #"Trimmed Text2" = Table.TransformColumns(#"Removed Columns2",{{"Shift", Text.Trim, type text}}),
    #"Replaced Value" = Table.ReplaceValue(#"Trimmed Text2","general","General",Replacer.ReplaceText,{"Shift"}),
    #"Trimmed Text3" = Table.TransformColumns(#"Replaced Value",{{"Supervisor", Text.Trim, type text}}),
    #"Capitalized Each Word1" = Table.TransformColumns(#"Trimmed Text3",{{"Supervisor", Text.Proper, type text}}),
    #"Added Custom6" = Table.AddColumn(#"Capitalized Each Word1", "Completion %", each ([Claims_Completed]/[Claims_Received])*100),
    #"Rounded Off" = Table.TransformColumns(#"Added Custom6",{{"Completion %", each Number.Round(_, 2), type number}}),
    #"Added Custom7" = Table.AddColumn(#"Rounded Off", "Target Achievement %", each ([Claims_Completed]/[Target])*100),
    #"Added Custom8" = Table.AddColumn(#"Added Custom7", "Error Rate", each ([Errors]/[Claims_Completed])*100),
    #"Added Custom9" = Table.AddColumn(#"Added Custom8", "Quality %", each ([Errors]/[Audits])*100),
    #"Filtered Rows5" = Table.SelectRows(#"Added Custom9", each true),
    #"Added Index" = Table.AddIndexColumn(#"Filtered Rows5", "Index", 1, 1, Int64.Type),
    Custom13 = #"Added Index",
    #"Filtered Rows6" = Table.SelectRows(Custom13, each ([Errors] <> 62 and [Errors] <> 66 and [Errors] <> 68 and [Errors] <> 78 and [Errors] <> 91 and [Errors] <> 93 and [Errors] <> 132 and [Errors] <> 134 and [Errors] <> 215)),
    #"Removed Columns3" = Table.RemoveColumns(#"Filtered Rows6",{"Index"}),
    #"Filtered Rows7" = Table.SelectRows(#"Removed Columns3", each true),
    #"Added Custom10" = Table.AddColumn(#"Filtered Rows7", "Custom", each if [#"Target Achievement %"] >=100 or [Error Rate]<=0.5
then "5"
else if [#"Target Achievement %"]>=90 or [Error Rate]<=1
then "4"
else if [#"Target Achievement %"]>=80 or [Error Rate]<=2
then "3"
else if [#"Target Achievement %"]>=65 and [Error Rate]<=3
then "2"
else "1"),
    #"Renamed Columns2" = Table.RenameColumns(#"Added Custom10",{{"Custom", "Performance_rating"}}),
    #"Rounded Off1" = Table.TransformColumns(#"Renamed Columns2",{{"Target Achievement %", each Number.Round(_, 2), type number}}),
    #"Rounded Off2" = Table.TransformColumns(#"Rounded Off1",{{"Error Rate", each Number.Round(_, 2), type number}}),
    #"Rounded Off3" = Table.TransformColumns(#"Rounded Off2",{{"Quality %", each Number.Round(_, 2), type number}}),
    #"Changed Type3" = Table.TransformColumnTypes(#"Rounded Off3",{{"Performance_rating", type number}}),
    #"Removed Blank Rows" = Table.SelectRows(#"Changed Type3", each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null}))),
    #"Filtered Rows8" = Table.SelectRows(#"Removed Blank Rows", each true),
    Custom14 = Table.ReplaceValue(#"Filtered Rows8",null,List.Median(List.RemoveNulls(#"Filtered Rows8"[Claims_Received])),Replacer.ReplaceValue,{"Claims_Received"}),
    #"Removed Columns4" = Table.RemoveColumns(Custom14,{"Completion %"}),
    #"Added Custom11" = Table.AddColumn(#"Removed Columns4", "Completion %", each ([Claims_Completed]/[Claims_Received])*100),
    #"Rounded Off4" = Table.TransformColumns(#"Added Custom11",{{"Completion %", each Number.Round(_, 2), type number}})
in
    #"Rounded Off4"

```
---

# 📷 Dashboard Preview

<img width="1122" height="560" alt="image" src="https://github.com/user-attachments/assets/c5ef798a-26c1-4901-b3ea-0971f6ee6d52" />
