{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE FlexibleInstances #-}


{-
    PP Project 2021

    This is where you will write the implementation for the given tasks.
    You can add other modules aswell.
-}

module Tasks where

import Dataset
import Text.Printf
import Data.List
import Text.Read
import Data.Maybe
import Data.Array

type CSV = String
type Value = String
type Row = [Value]
type Table = [Row]

{-
    TASK SET 1
-}

--  Auxiliary functions

-- Reverse a list
reverseL :: [a] -> [a]
reverseL = foldl (\acc x -> [x]++acc) []

-- Convert float to string
printFloat :: Float -> String
printFloat = printf "%.2f"

-- Converst string to float
stringToFloat :: String -> Float
stringToFloat x = if x == "" then 0 else (read x :: Float)

-- Convert int to float
intToFloat :: Int -> Float
intToFloat x = (read (show x) :: Float)

-- Get number of students in a table
number_of_students :: Table -> Int
number_of_students = foldr (\row acc -> acc + 1) (-1) -- accumulator's initial value is -1 to ignore the columns names

-- Comparison of two strings (names):
--    - 0, if strings are equal
--    - 1, if first string is smaller than second string
--    - -1, otherwise
compareStr :: String -> String -> Integer
compareStr "" "" = 0            -- return 0, if strins are empty
compareStr "" _ = 1
compareStr _ "" = -1
compareStr (a:as) (b:bs)
  | (a:as) == (b:bs) = 0        -- return 0, if strings are equal
  | as == "" && bs /= "" = 1    -- return 1, if the first string is empty and the second one is not
  | as /= "" && bs == "" = -1   -- return -1, if the second string is empty and the first one is not
  | a == b = compareStr as bs   -- if both strings start with the same character, compare the rest of the strings
  | a < b = 1                   -- return 1, if first chracter of the first string is smaller than first character of the second
  | otherwise = -1              -- return 0, if first chracter of the first string is greater than first character of the second

-- Comparison of two floats (grades)
compareFloat :: Float -> Float -> Integer
compareFloat x y
  | x < y = 1
  | x > y = -1
  | otherwise = 0

-- Sort a table by a given rule (comparison function between two rows)
sortTable :: Table -> (Row -> Row -> Integer) -> Table
sortTable table rule = foldr insert [] table
                       where insert :: Row -> Table -> Table
                             insert r [] = [r]
                             insert r1 (r2 : res)
                                | ((rule r1 r2) == 1)  || ((rule r1 r2) == 0) = (r1 : r2 : res) -- if the new row is "smaller" than the head of the yable, add row at the beginning
                                | otherwise = r2 : (insert r1 res)    -- otherwise, insert row in the "tail" of the table

-- Convert a list of strings to float list
listToFloat :: Row -> [Float]
listToFloat = map stringToFloat

-- Compute the grade of the interview part of the exam from a table entry
computeInterviewAvg :: Row -> Float
computeInterviewAvg (writtenExam : questions) =  (foldr (+) 0.0 (listToFloat questions))/4

-- Get the grade of the written part of the exam from a table entry
getWrittenExamGrade :: Row -> Float
getWrittenExamGrade row = stringToFloat (head row)

-- Compute the exam average for a table entry
computeExamAvg :: Row -> Float
computeExamAvg row = (getWrittenExamGrade row) + (computeInterviewAvg row)

-- Task 1
compute_exam_grades :: Table -> Table
compute_exam_grades = ((foldl concatRow [["Nume", "Punctaj Exam"]])  -- compute the exam grade for each student
                      .(tail))                                       -- remove columns names row
                        where concatRow acc row = acc ++ [computeExamGradesRow row]
                              computeExamGradesRow (name : examGrades) = name : (printFloat $ computeExamAvg $ reverseL examGrades) : [] -- reverse exam grades list, so that the written exam grade is head of list, 
                                                                                                                                         -- and questions grades are tail of list

-- Task 2
-- Number of students who have passed the exam:
get_passed_students_num :: Table -> Int
get_passed_students_num = ((foldr checkAvg 0)     -- count the number of passed students
                          .(tail)                 -- remove columns names row
                          .(compute_exam_grades)) -- get exam grades
                            where checkAvg :: Row -> Int -> Int
                                  checkAvg (name : examGrade : []) total
                                    | (stringToFloat examGrade) >= 2.5 = total + 1
                                    | otherwise = total

-- Percentage of students who have passed the exam:
get_passed_students_percentage :: Table -> Float
get_passed_students_percentage = \table -> (intToFloat $ get_passed_students_num table) / (intToFloat $ number_of_students table)

-- Average exam grade
get_exam_avg :: Table -> Float
get_exam_avg = \table -> (sumGrades $ tail $ compute_exam_grades table) / (intToFloat $ number_of_students table)
                where sumGrades table = foldr addToSum 0.0 table
                        where addToSum (name : grade : []) total = total + (stringToFloat grade)

-- Number of students who gained at least 1.5p from homework:
get_passed_hw_num :: Table -> Int
get_passed_hw_num = ((foldr checkHwGrade 0)  -- count the number of students who gained at least 1.5p from homework
                    .(tail))                 -- remove columns names row
                    where checkHwGrade row acc
                            | (computeHwGrade row) >= 1.5 = acc + 1
                            | otherwise = acc
                          computeHwGrade (name : lab : t1 : t2 : t3 : _) = (stringToFloat t1) + (stringToFloat t2) + (stringToFloat t3)

-- Task 3
get_avg_responses_per_qs :: Table -> Table
get_avg_responses_per_qs = \table -> ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"] : 
                                     [((map printFloat).                                      -- convert to string all results
                                       (map (/ (intToFloat $ number_of_students table))).     -- get average, by dividing sum to number of students
                                       (foldr (zipWith (+)) [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).  -- compute sum of all points per question
                                       (getQuestionsGrades)) table]                           -- get only questions grades from exam grades table                       
                           where getQuestionsGrades = ((map removeLastColumn).     --  remove written exam grades from table
                                                       (map (map stringToFloat)).  -- convert all values from string to float
                                                       (map tail).                 -- remove names column
                                                       (tail))                     -- remove columns names row
                                                      where removeLastColumn = (reverseL).(tail).(reverseL)
                                 
-- Task 4
get_exam_summary :: Table -> Table
get_exam_summary = \table -> [["Q", "0", "1", "2"]] ++
                             [getQuestionSummary table 1] ++  -- get question 1 summary
                             [getQuestionSummary table 2] ++  -- get question 2 summary
                             [getQuestionSummary table 3] ++  -- get question 3 summary
                             [getQuestionSummary table 4] ++  -- get question 4 summary
                             [getQuestionSummary table 5] ++  -- get question 5 summary
                             [getQuestionSummary table 6]     -- get question 6 summary
                    where getQuestionSummary :: Table -> Int -> Row
                          getQuestionSummary = \table index -> ("Q" ++ (show index)) : (((map show).(foldr checkGrade [0, 0, 0]).(tail)) ((transpose table) !! index))
                                               where checkGrade x (n0:n1:n2:[])
                                                       | x == [] = ((n0 + 1):n1:n2:[])                  -- if grade slot is empty, mark as 0 points
                                                       | (read x :: Integer) == 0 = ((n0 + 1):n1:n2:[])
                                                       | (read x :: Integer) == 1 = (n0:(n1 + 1):n2:[])
                                                       | (read x :: Integer) == 2 = (n0:n1:(n2 + 1):[])
                                                       | otherwise = (n0:n1:n2:[])

-- Task 5

-- Auxiliary function (for comparison)
compareExamGradesRows :: Row -> Row -> Integer
compareExamGradesRows (name1 : examGrade1 : []) (name2 : examGrade2 : [])
  | (compareFloat (stringToFloat examGrade1) (stringToFloat examGrade2)) == 0 = compareStr name1 name2  -- if exam grades are equal, sort by name
  | otherwise = (compareFloat (stringToFloat examGrade1) (stringToFloat examGrade2))                    -- otherwise, sort by exam grade

get_ranking :: Table -> Table
get_ranking = \table -> ["Nume", "Punctaj Exam"] : (sortTable (tail $ compute_exam_grades table) compareExamGradesRows) -- get exam grades table, remove columns names row and sort

-- Task 6

-- Auxiliary function (for comparison)
compareDiffRows :: Row -> Row -> Integer
compareDiffRows (name1 : interview1 : writtenExam1 : diff1 : []) (name2 : interview2 : writtenExam2 : diff2 : [])
  | (compareFloat (stringToFloat diff1) (stringToFloat diff2)) == 0 = compareStr name1 name2            -- if differences are equal, sort by name
  | otherwise = compareFloat (stringToFloat diff1) (stringToFloat diff2)                                -- otherwise, sort by difference

get_exam_diff_table :: Table -> Table
get_exam_diff_table = \table -> ["Nume", "Punctaj interviu", "Punctaj scris", "Diferenta"] : (sortTable (foldl concatRow [] $ tail table) compareDiffRows)
                        where concatRow acc row = acc ++ [computeDifferenceRow row]
                              computeDifferenceRow (name:examGrades) = (name :                                                      -- add name
                                                                        (printFloat (computeInterviewAvg (reverseL examGrades))) :  -- add interview grade
                                                                        (printFloat (getWrittenExamGrade (reverseL examGrades))) :  -- add written exam grdae
                                                                        (printFloat diff) : [])                                     -- add difference
                                                                        where diff = abs ((computeInterviewAvg (reverseL examGrades)) - (getWrittenExamGrade (reverseL examGrades)))

{-
    TASK SET 2
-}
-- Auxiliary functions
-- Transpose a matrix
transpose_table :: [[a]] -> [[a]]
transpose_table = foldr row_to_column []
                  where row_to_column line [] = map (\elem -> [elem]) line                              -- if first line, create columns from line
                        row_to_column line matrix = zipWith (++) (map (\elem -> [elem]) line) matrix    -- otherwise, convert current line to columns and concatenate to transposed matrix

-- Get column from a table identified by name
get_column :: String -> Table -> Row
get_column column_name table = foldr search_column [] $ transpose_table table       -- transpose matrix, so columns become lines
                                     where search_column line result
                                            | (head line) == column_name = line     -- if column name (first value of line) matches the given column name, update accumulator
                                            | otherwise = result                    -- otherwise, don't change the accumulator

-- Convert String line to Row form
line_to_list :: String -> Row 
line_to_list = foldr separate_values [] 
               where separate_values c []
                        | c == ',' = "" : [[]]              -- if current character is ",", add a missing value string in table entry
                        | otherwise = [[c]]                 -- otherwise, add a value which contains just the current character in table entry
                     separate_values c (value : line)
                        | c == ',' = "" : (value : line)    -- if current character is ",", add a missing value string in table entry
                        | otherwise = (c : value) : line    -- otherwise, add current character to last value from table entry

-- Split lines separated by '\n'
parse_lines :: Char -> [String] -> [String]
parse_lines c (line : table)
    | c == '\n' = "" : (line : table)       -- if current character is '\n', add new empty string for the next line
    | otherwise = (c : line) : table        -- otherwise, add current character to the current line string

-- Read CSV
read_csv :: CSV -> Table
read_csv = (map line_to_list) . (foldr parse_lines [[]])    -- split input string into lines, then split string lines into table rows

-- Convert Row form line into String form line
list_to_line :: Row -> String
list_to_line row = foldr concat_values "" row 
                   where concat_values value line
                            | line == "" = value ++ "\n"        -- if line empty, add '\n' at the end
                            | otherwise = value ++ "," ++ line  -- otherwise, add ',' before adding the value

-- Write CSV
write_csv :: Table -> CSV
write_csv = foldr concat_lines "" 
            where concat_lines row str
                        | str == "" = reverse $ tail $ reverse $ list_to_line row       -- if it is the last row, convert it into String form and remove the '\n' at the
                        | otherwise = (list_to_line row) ++ str                         -- otherwise, add the current entry before the previous entries

-- Get column number by it's name
get_column_number :: String -> Row -> Int
get_column_number column_name header
    | (head header) == column_name = 0
    | otherwise = 1 + (get_column_number column_name $ tail header)

-- Get column value from a row, based on the column's number
get_column_value :: Row -> Int -> Value
get_column_value row number
  | number == 0 = head row
  | otherwise = get_column_value (tail row) (number - 1)

-- Function that generates an empty row with a given number of empty values
generate_empty_row :: Int -> Row
generate_empty_row nrCol
    | nrCol == 0 = []
    | otherwise = "" : (generate_empty_row (nrCol - 1))

-- Task 1
as_list :: String -> Table -> [String]
as_list = \column_name table -> tail (get_column column_name table)

-- Task 2
-- Function that compares two rows based on the values of a certain column
compare_rows :: Row -> Row -> Int -> Integer
compare_rows r1 r2 col_num
    -- if one of the values is empty, it goes before the other
    | ((get_column_value r1 col_num) == "") && ((get_column_value r2 col_num) /= "") = 1
    | ((get_column_value r1 col_num) /= "") && ((get_column_value r2 col_num) == "") = -1
    -- otherwise, if values are not numbers, use the string compare function
    | ((readMaybe (get_column_value r1 col_num) :: Maybe Float) == Nothing) = if (compareStr (get_column_value r1 col_num) (get_column_value r2 col_num) == 0)
                                                                              then (compareStr (head r1) (head r2))
                                                                              else (compareStr (get_column_value r1 col_num) (get_column_value r2 col_num))
    -- otherwise, convert values to float and use the float compare function
    | otherwise = if (compareFloat (stringToFloat $ get_column_value r1 col_num) (stringToFloat $ get_column_value r2 col_num) == 0) 
                  then (compareStr (head r1) (head r2))
                  else (compareFloat (stringToFloat $ get_column_value r1 col_num) (stringToFloat $ get_column_value r2 col_num))

-- Sort a table by a column with a certain name
tsort :: String -> Table -> Table
tsort column_name table = [head table] ++ (sortBy comparator (tail table))
                                            where comparator row1 row2
                                                    | (compare_rows row1 row2 (get_column_number column_name $ head table)) == 1 = LT
                                                    | (compare_rows row1 row2 (get_column_number column_name $ head table)) == -1 = GT
                                                    | otherwise = LT

-- Task 3
vmap :: (Value -> Value) -> Table -> Table
vmap function table = [head table] ++ (map (map function) $ tail table) -- apply the function to all values of table, except the header

-- Task 4
rmap :: (Row -> Row) -> [String] -> Table -> Table
rmap function header table = [header] ++ (map function (tail table))    -- apply the function to all rows of table, except the header

get_hw_grade_total :: Row -> Row
get_hw_grade_total row = [head row] ++ (compute_hw_sum $ tail $ tail row)   -- sum all values in a homework grades table entry, except from the name and lab grade
                                  where compute_hw_sum row = (printFloat $ foldr (+) 0.0 $ map stringToFloat row) : []

-- Task 5
-- The functions checks if the headers of two tables match.
-- If they do, the function return True, otherwise it returns False.
check_column_names :: Row -> Row -> Bool
check_column_names header1 header2 = foldr (&&) True $ zipWith (==) header1 header2

vunion :: Table -> Table -> Table
vunion t1 t2
    | (check_column_names (head t1) (head t2)) == True = t1 ++ (tail t2)    -- if the columns of the tables match, concatenate the tables
    | otherwise = t1                                                        -- otherwise, return the first table

-- Task 6
-- Function that adds a given number of empty rows in a table
add_empty_rows :: Table -> Int -> Table
add_empty_rows table n
    | n == 0 = table
    | otherwise = add_empty_rows (table ++ [generate_empty_row $ length $ head table]) (n - 1)

hunion :: Table -> Table -> Table
hunion t1 t2
    -- if tables are of different sizes, add empty rows to the smaller one to equalize sizes, then merge them
    | len_t1 < len_t2 = transpose_table ((transpose_table $ add_empty_rows t1 (len_t2 - len_t1)) ++ (transpose_table t2))
    | len_t1 > len_t2 = transpose_table ((transpose_table t1) ++ (transpose_table $ add_empty_rows t2 (len_t1 - len_t2)))
    -- if tables have the same size, merge them
    | otherwise = transpose_table ((transpose_table t1) ++ (transpose_table t2))
    where len_t1 = number_of_students t1
          len_t2 = number_of_students t2

-- Task 7
-- Function that searches an entry in a table, by it's value of a certain column
search_entry_by_column :: Value -> Int -> Table -> Row
search_entry_by_column key_value col_num table = foldr op [] table
                                                 where op row acc
                                                        | acc == [] = if (get_column_value row col_num) == key_value then row else acc
                                                        | otherwise = acc

-- Function that computes the header of a table resulting from joining two tables
get_header :: Table -> Table -> [String]
get_header t1 t2 = (head t1) ++ (foldr add_new_columns [] $ head t2)
                                 where add_new_columns column_name list
                                        | get_column column_name t1 == [] = [column_name] ++ list   -- if column doesn't already exista, add it to the header
                                        | otherwise = list                                          -- otherwise, don't add it again

-- Function that changes the value of a certain column of a row with a given value, if the given value is not ""
change_value :: Row -> Int -> Value -> Row
change_value row colNum newVal
    | newVal == "" = row                                                        -- if new value is "", return the row as it is
    | (colNum == 0) = [newVal] ++ (tail row)                                    -- if the current column is the one we were searching for, change the current value to the new value
    | otherwise = [head row] ++ (change_value (tail row) (colNum - 1) newVal)   -- otherwise, continue searching

-- Create an empty table which only has the key values on the corresponding column.
-- This table does not contain key values duplicates.
add_key_entries :: Table -> Table -> String -> Table
add_key_entries table resultT key = foldl op resultT (tail table)
                                    where op t row 
                                            -- if this key value doesn't already exist, create an empty row with that key value and add it to the table
                                            | search_entry_by_column key_value key_col_num_resultT resultT == [] = t ++ [change_value new_row key_col_num_resultT key_value]
                                            -- otherwise, leave the table as it is
                                            | otherwise = t
                                            where key_value = (get_column_value row key_col_num_table)          -- key value of the current table entry
                                                  key_col_num_table = (get_column_number key (head table))      -- number of the column with key values of table
                                                  key_col_num_resultT = (get_column_number key (head resultT))  -- number of the column with key values of result table
                                                  width_resultT = (length (head resultT))                       -- number of columns of the result table
                                                  new_row = (generate_empty_row width_resultT)                  -- new row with only empty values of the result table

-- Function that gathers information about a key value of a row from a table and updates the information of that row
complete_row :: Row -> Row -> String -> Table -> Row
complete_row header row key table = foldr add_value row column_value_pairs
                                    where key_value = get_column_value row $ get_column_number key header                               -- key value of the given row
                                          table_entry = search_entry_by_column key_value (get_column_number key (head table)) table     -- the entry of the table which corresponds to the key value
                                          column_value_pairs = if table_entry /= [] then zipWith (,) (head table) table_entry else []   -- list of column names and column values of the table entry
                                          add_value (col_name, value) row = change_value row (get_column_number col_name header) value  -- for each column value, update it in the corresponding column of the given row

tjoin :: String -> Table -> Table -> Table
tjoin column_name t1 t2 = [tableHead] ++ (foldr merge_information [] (tail emptyTable))
                            where emptyTable = add_key_entries t2 (add_key_entries t1 [get_header t1 t2] column_name) column_name   -- create empty table with key value entries from both t1 and t2
                                  tableHead = head emptyTable                                                                       -- result table header
                                  -- complete row with information from both tables, then add it to the result table
                                  merge_information row table = [complete_row tableHead (complete_row tableHead row column_name t1) column_name t2] ++ table

-- Task 8
cartesian :: (Row -> Row -> Row) -> [String] -> Table -> Table -> Table
cartesian f header t1 t2 = [header] ++ (foldr get_entries [] (tail t1)) 
                                        where get_entries row1 table = (foldr apply_f_on_entries [] (tail t2)) ++ table 
                                                                        where apply_f_on_entries row2 table = (f row1 row2) : table

-- Task 9
projection :: [String] -> Table -> Table
projection columns_names table = transpose_table $ foldr search_each_column [] columns_names 
                                                   where search_each_column column_name res = (get_column column_name table) : res


{-
    TASKSET 3
-}

data Query = FromCSV CSV
           | ToCSV Query
           | AsList String Query
           | Sort String Query
           | ValueMap (Value -> Value) Query
           | RowMap (Row -> Row) [String] Query
           | VUnion Query Query
           | HUnion Query Query
           | TableJoin String Query Query
           | Cartesian (Row -> Row -> Row) [String] Query Query
           | Projection [String] Query
           | forall a. FEval a => Filter (FilterCondition a) Query
           | Graph EdgeOp Query

type EdgeOp = Row -> Row -> Maybe Value

-- Query Evaluation
{-
    Task 3.1.
-}
data QResult = CSV CSV
             | Table Table
             | List [String]

instance Show QResult where
    show (CSV csv) = show csv
    show (Table table) = write_csv table
    show (List list) = show list

{-
    Task 3.2.
-}
class Eval a where
    eval :: a -> QResult

-- Auxiliary functions

-- Convert query to table
query_to_table :: Query -> Table
query_to_table query = read_csv $ show $ eval query

-- Check if a line already exists in a table
checkIfLineExistsInTable :: Row -> Table -> Bool
checkIfLineExistsInTable row table = foldr op1 False table
                                     where op1 line True = True 
                                           op1 line False = foldr (&&) True (zipWith (==) line row)
-- Remove duplicate lines in a table
removeTableDuplicates :: Table -> Table
removeTableDuplicates table = foldl op [] table
                              where op [] line = [line]                                     -- if resulting table is empty, add line
                                    op acc line
                                        | checkIfLineExistsInTable line acc == True = acc   -- if line already exists in table, skip it
                                        | otherwise = acc ++ [line]                         -- otherwise, add it to the table

-- Create a graph entry from "From", "To" and "Value" values
toGraphEntry :: Value -> Value -> Value -> Row
toGraphEntry from to value
    | compareStr from to == 1 = [from, to, value]   -- if "From" value lexicographically before "To" value, keep the order
    | otherwise = [to, from, value]                 -- otherwise, switch their places

instance Eval Query where
    eval (FromCSV str) = Table (read_csv str)
    eval (ToCSV query) = CSV $ show (Table $ query_to_table query)
    eval (AsList colname query) = List $ as_list colname $ query_to_table query
    eval (Sort colname query) = Table $ tsort colname $ query_to_table query
    eval (ValueMap op query) = Table $ vmap op $ query_to_table query
    eval (RowMap op colnames query) = Table $ rmap op colnames $ query_to_table query
    eval (VUnion query1 query2) = Table $ vunion (query_to_table query1) (query_to_table query2)
    eval (HUnion query1 query2) = Table $ hunion (query_to_table query1) (query_to_table query2)
    eval (TableJoin colname query1 query2) = Table $ tjoin colname (query_to_table query1) (query_to_table query2)
    eval (Cartesian op colnames query1 query2) = Table $ cartesian op colnames (query_to_table query1) (query_to_table query2)
    eval (Projection colnames query) = Table $ projection colnames $ query_to_table query
    eval (Filter filterCondition query) = Table $ [tableHeader] ++ (filter (feval tableHeader filterCondition) tableValues)
        where tableValues = tail (query_to_table query)
              tableHeader = (head (query_to_table query))
    eval (Graph edgeOp query) =  Table $ removeTableDuplicates $ [graphTableHeader] ++ (foldr getEveryLine [] tableValues)
        where graphTableHeader = ["From", "To", "Value"]
              tableValues = tail (query_to_table query)
              getEveryLine line1 acc = foldr addGraphLine acc tableValues
                                       where addGraphLine line2 acc = if isNothing $ edgeOp line1 line2
                                                                      then acc                                                                                      -- if value returned by edgeOp si Nothing, don't add line to graph table
                                                                      else  if head line1 == head line2
                                                                            then acc                                                                                -- if "To" and "From" values are equal, don't add line to graph table
                                                                            else (toGraphEntry (head line1) (head line2) $ fromJust $ edgeOp line1 line2) : acc     -- otherwise, create graph line and add to graph table

-- Filters & filter conditions
data FilterCondition a = Eq String a
                       | Lt String a
                       | Gt String a
                       | In String [a]
                       | FNot (FilterCondition a)
                       | FieldEq String String

type FilterOp = Row -> Bool

class FEval a where
    feval :: [String] -> (FilterCondition a) -> FilterOp

{-
    Task 3.3.
-}
instance FEval Float where
    feval header (Eq colname x) = \row -> (stringToFloat $ get_column_value row $ get_column_number colname header) == x
    feval header (Lt colname x) = \row -> (stringToFloat $ get_column_value row $ get_column_number colname header) < x
    feval header (Gt colname x) = \row -> (stringToFloat $ get_column_value row $ get_column_number colname header) > x
    feval header (In colname list) = \row -> foldr (\x acc -> if (x == stringToFloat (get_column_value row (get_column_number colname header))) then True else acc) False list  -- search value in ref list
    feval header (FNot condition) = \row -> not $ feval header condition row
    feval header (FieldEq colname1 colname2) = \row -> (stringToFloat $ get_column_value row $ get_column_number colname1 header) == (stringToFloat $ get_column_value row $ get_column_number colname2 header) -- get values from columns and compare them

instance FEval String where
    feval header (Eq colname str) = \row -> (compareStr (get_column_value row $ get_column_number colname header) str) == 0
    feval header (Lt colname str) = \row -> (compareStr (get_column_value row $ get_column_number colname header) str) == 1
    feval header (Gt colname str) = \row -> (compareStr (get_column_value row $ get_column_number colname header) str) == -1
    feval header (In colname list) = \row -> foldr (\str acc -> if (str == (get_column_value row $ get_column_number colname header)) then True else acc) False list            -- search value in ref list
    feval header (FNot condition) = \row -> not $ feval header condition row
    feval header (FieldEq colname1 colname2) = \row -> (get_column_value row $ get_column_number colname1 header) == (get_column_value row $ get_column_number colname2 header) -- get values from columns and compare them

{-
    Task 3.6.
-}

-- Auxiliary functions for task 3.6.

-- Convert lecture grade to float
-- If grade is empty, value is -1
lectureGradeToFloat :: String -> Float
lectureGradeToFloat x = if x == "" then -1 else (read x :: Float)

-- Edge operation for lecture grades query
edge_op (mail1 : grades1) (mail2 : grades2)
    | (mail1 == "") || (mail2 == "") = Nothing                                                                                                  -- is one or both first column values are empty, then return Nothing
    | otherwise = Just (show (foldr (\equal acc -> if (equal == True) then (acc + 1) else acc) 0 (zipWith (==) lectureGrades1 lectureGrades2))) -- compare each grade with zipWith then count number of equal grades and return it
                where lectureGrades1 = (map lectureGradeToFloat grades1)
                      lectureGrades2 = (map lectureGradeToFloat grades2)
{-
    similarities_query steps:
    1. FromCSV - convert CSV to query
    2. Graph - create graph query using edge opration defined before
    3. Filter - filter graph query so that it only has values greater or equal to 5
    4. Sort - sort query in "Value" ascending order
-}
similarities_query = Sort "Value" $ Filter ((Gt "Value" 4) :: (FilterCondition Float)) $ Graph edge_op $ FromCSV lecture_grades_csv

{-
    Task Set 4
-}

-- Function that replaces a value of a column
replace_value_of_col :: Row -> Int -> String -> Row
replace_value_of_col row col_num new_value = foldr op [] row
                                                where row_len = length row
                                                      op value acc
                                                        | (length acc) == (row_len - col_num - 1) = new_value : acc
                                                        | otherwise = value : acc

-- Function that corrects a table
correct_table :: String -> CSV -> CSV -> CSV
correct_table col_name csv ref_csv = write_csv ([header] ++ (map correct $ tail table))
                                        where table = read_csv csv                                      -- Source table
                                              header = head table                                       -- Header of source table
                                              table_col = as_list col_name table                        -- List of values of column with typos
                                              ref = as_list col_name (read_csv ref_csv)                 -- List of correct values
                                              ref_filtered = filter (\x -> not $ elem x table_col) ref  -- Correct values without values that have a perfect match in source table
                                              col_num_table = get_column_number col_name $ head table   -- Number of column with typos in source table
                                              correct line                                              -- Function that corrects a line
                                                | (elem (get_column_value line col_num_table) ref) == True = line                                   -- If value of problematic column has a perfect match, leave it as it is           
                                                | otherwise = replace_value_of_col line col_num_table (fst (foldr op ("", 0) ref_filtered))         -- Otherwise, search for the correct value
                                                                    where value = (get_column_value line col_num_table)                             -- Wrong value
                                                                          op str (correct, dist)                                                    -- Function that gets the closest correct value
                                                                            | dist == 0 = (str, (levenshteinDist str value))                         -- First iteration
                                                                            | dist > (levenshteinDist str value) = (str, (levenshteinDist str value)) -- If current distance between values is better, change the previous (value, distance) pair
                                                                            | otherwise = (correct, dist)                                           -- Otherwise, leave it as it is

-- Function that computes the Levenshtain distance
levenshteinDist :: String -> String -> Int
levenshteinDist w1 w2 = matrix ! (m, n)
                        where n = length w1
                              m = length w2
                              bounds = ((0,0), (m, n))
                              matrix = listArray bounds [distance i j | (i, j) <- range bounds]             -- Dinamyc programming matrix
                              distance i j
                                | j == 0 = i
                                | i == 0 = j
                                | (w1 !! (j - 1)) == (w2 !! (i - 1)) = minimum [(matrix ! (i-1,j)) + 1,
                                                                                (matrix ! (i,j-1)) + 1,
                                                                                (matrix ! (i-1,j-1))]
                                | otherwise = minimum [(matrix ! (i-1,j)) + 1,
                                                       (matrix ! (i,j-1)) + 1,
                                                       (matrix ! (i-1,j-1)) + 1]

-- Compute total homework grade for a homework table row
get_homework_grade_total :: Row -> Row
get_homework_grade_total row = [head row] ++ (compute_hw_sum $ tail row)   -- Sum all values in a homework grades table entry, except from the name
                                  where compute_hw_sum row = (printFloat $ foldr (+) 0.0 $ map stringToFloat row) : []

-- Compute total lecture grade for a lecture table row
get_lecture_grade_total :: Int -> Row -> Row
get_lecture_grade_total num_grades row = [head row] ++ (compute_lecture_grade $ tail row)   -- Sum all values in a lecture grades table entry, except from the email, multiply it by 2 and divide by the number of grades
                                        where compute_lecture_grade row = (printFloat (2.0 * ((foldr (+) 0.0 $ map stringToFloat row) / (intToFloat num_grades)))) : []

-- Compute total exam grade for an exam table row
get_exam_grade_total :: Row -> Row
get_exam_grade_total row = [head row] ++ [printFloat ((compute_qgrades q_grades) + written_ex)]                     -- Sum questions grades average with written exam grade
                                    where q_grades = reverse (tail (reverse (tail row)))                            -- Get questions grades as a list
                                          compute_qgrades line =  (foldr (+) 0.0 $ map stringToFloat line) / 4.0    -- Compute questions grades average
                                          written_ex = stringToFloat (row !! ((length row) - 1))                    -- Get written exam grade

-- Compute final grades
grades :: CSV -> CSV -> CSV -> CSV -> CSV
grades email_csv hw_csv exam_csv lecture_csv =  write_csv $ tsort "Nume" $ map compute_final_row grades_table                                   -- Sort final table by name column
                                                where hw_total = rmap get_homework_grade_total ["Nume", "Punctaj Teme"] $ read_csv hw_csv                                   -- Get table with students' names and final homework grades
                                                      lecture_grades_num = (length $ head $ read_csv lecture_csv) - 1                                                       -- Get number of lecture grades
                                                      lecture_total = rmap (get_lecture_grade_total lecture_grades_num) ["Email", "Punctaj Curs"] $ read_csv lecture_csv    -- Get table with students' emails and final lecture grades
                                                      exam_total = rmap get_exam_grade_total ["Nume", "Punctaj Exam"] $ read_csv exam_csv                                   -- Get table with students' names and final exam grades
                                                      correct_emails = transpose $ reverse $ transpose $ read_csv $ correct_table "Nume" email_csv hw_csv                   -- Get email names table: correct source table and switch columns so that the email comes first
                                                      lecture_with_names = tjoin "Email" correct_emails lecture_total                                                       -- Assign the names to the students from lecture grades table
                                                      lecture_with_just_names = transpose $ tail $ transpose lecture_with_names                                             -- Remove email column from lecture grades table
                                                      grades_table = filter (\(name : _) -> name /= "") (tjoin "Nume" (tjoin "Nume" hw_total lecture_with_just_names) exam_total)   -- Join all tables and remove all entries with empty names
                                                      compute_final_row row = row ++  [compute_total (tail row)]                                                            -- Function that adds the final grade for a final table entry
                                                      compute_total (hw : lecture : exam : [])                                                                              -- Function that computes the final grade for an entry
                                                        | hw == "Punctaj Teme" = "Punctaj Total"                                                                            -- If entry is table header, add the nre column's name
                                                        | ((stringToFloat hw) + (stringToFloat lecture)) < 2.5 = printFloat 4.0                                             -- Otherwise, compute final grade
                                                        | (stringToFloat exam) < 2.5 = printFloat 4.0
                                                        | otherwise = printFloat ((minimum [((stringToFloat hw) + (stringToFloat lecture)), 5.0]) + (stringToFloat exam))