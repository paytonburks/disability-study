from mysklearn import myutils
import copy
import csv

class MyPyTable:
    """Represents a 2D table of data with column names.

    Attributes:
        column_names(list of str): M column names
        data(list of list of obj): 2D data structure storing mixed type data.
            There are N rows by M columns
    """

    def __init__(self, column_names=None, data=None):
        """Initializer for MyPyTable.

        Args:
            column_names(list of str): initial M column names (None if empty)
            data(list of list of obj): initial table data in shape NxM (None if empty)
        """
        if column_names is None:
            column_names = []
        self.column_names = copy.deepcopy(column_names)
        if data is None:
            data = []
        self.data = copy.deepcopy(data)

    def get_shape(self):
        """Computes the dimension of the table (N x M).

        Returns:
            int: number of rows in the table (N)
            int: number of cols in the table (M)
        """
        return len(self.data), len(self.column_names)

    def get_column(self, col_identifier, include_missing_values=True):
        """Extracts a column from the table data as a list.

        Args:
            col_identifier(str or int): string for a column name or int
                for a column index
            include_missing_values(bool): True if missing values ("NA")
                should be included in the column, False otherwise.

        Returns:
            list of obj: 1D list of values in the column

        Notes:
            Raise ValueError on invalid col_identifier
        """
        col = []
        index = self.column_names.index(col_identifier)
        
        for row in self.data:
            j = 0
            while j < len(row):
                if j == index and row[j] == '' and include_missing_values:
                    col.append('NA')
                    j+=1
                elif j == index:
                    col.append(row[j])
                    j+=1
                else:
                    j+=1
                    continue

        return col

    def convert_to_numeric(self):
        """Try to convert each value in the table to a numeric type (float).

        Notes:
            Leave values as is that cannot be converted to numeric.
        """
        newData = []

        for row in self.data:
            newRow = []
            for item in row:
                try:
                    newItem = float(item)
                    newRow.append(newItem)
                except:
                    newRow.append(item)
            newData.append(newRow)

        self.data = newData
                
    def drop_rows(self, row_indexes_to_drop):
        """Remove rows from the table data.

        Args:
            row_indexes_to_drop(list of int): list of row indexes to remove from the table data.
        """
        i=0 
        while i<len(row_indexes_to_drop):
            self.data.pop(row_indexes_to_drop[i])
            for j in range(len(row_indexes_to_drop)):
                row_indexes_to_drop[j]-=1
            i+=1
            
    def load_from_file(self, filename):
        """Load column names and data from a CSV file.

        Args:
            filename(str): relative path for the CSV file to open and load the contents of.

        Returns:
            MyPyTable: return self so the caller can write code like
                table = MyPyTable().load_from_file(fname)

        Notes:
            Use the csv module.
            First row of CSV file is assumed to be the header.
            Calls convert_to_numeric() after load
        """
        file = open(filename, 'r')
        csvRead = csv.reader(file)

        header = []
        header = next(csvRead)

        data = []
        for row in csvRead:
            data.append(row)

        file.close()

        self.data = data
        self.column_names = header
        self.convert_to_numeric()

        return self

    def save_to_file(self, filename):
        """Save column names and data to a CSV file.

        Args:
            filename(str): relative path for the CSV file to save the contents to.

        Notes:
            Use the csv module.
        """
        file = open(filename, 'w', newline='')

        with file:
            write = csv.writer(file)
            write.writerow(self.column_names)
            write.writerows(self.data)

    def find_duplicates(self, key_column_names):
        """Returns a list of indexes representing duplicate rows.
        Rows are identified uniquely based on key_column_names.

        Args:
            key_column_names(list of str): column names to use as row keys.

        Returns
            list of int: list of indexes of duplicate rows found

        Notes:
            Subsequent occurrence(s) of a row are considered the duplicate(s).
                The first instance of a row is not considered a duplicate.
        """
        key_indexes = []
        for item in key_column_names:
            index = self.column_names.index(item)
            key_indexes.append(index)

        unique_rows = []
        dupe_rows = []
        n=0

        for row in self.data:
            i=0
            unique_row = []
            for item in row:
                if i in key_indexes:
                    unique_row.append(item)
                else:
                    pass
                i+=1
            if unique_row in unique_rows:
                dupe_rows.append(n)
            else:
                unique_rows.append(unique_row)
            n+=1

        return dupe_rows

    def remove_rows_with_missing_values(self):
        """Remove rows from the table data that contain a missing value ("NA").
        """
        j=0
        while j < len(self.data):
            if "NA" in self.data[j] or "N/A" in self.data[j] or '' in self.data[j]:
                clear = self.data.pop(j)
                j-=1
            j+=1
                    
    def replace_missing_values_with_column_average(self, col_name):
        """For columns with continuous data, fill missing values in a column
            by the column's original average.

        Args:
            col_name(str): name of column to fill with the original average (of the column).
        """
        index = self.column_names.index(col_name)
        _data = []
        
        for row in self.data:
            j = 0
            while j < len(row):
                if j == index:
                    if row[j] == ("NA" or ''):
                        j+=1
                    else:
                        _data.append(row[j])
                        j+=1
                else:
                    j+=1

        avg = round(sum(_data)/len(_data), 2)

        newData = []
        for row in self.data:
            newRow = []
            for i in range(len(row)):
                if row[i] == ("NA" or '') and i == index:
                    newRow.append(avg)
                else:
                    newRow.append(row[i])
            newData.append(newRow)

        self.data = newData

    def compute_summary_statistics(self, col_names):
        """Calculates summary stats for this MyPyTable and stores the stats in a new MyPyTable.

        Args:
            col_names(list of str): names of the continuous columns to compute summary stats for.

        Returns:
            MyPyTable: stores the summary stats computed. The column names and their order
                is as follows: ["attribute", "min", "max", "mid", "avg", "median"]
        """
        def median(lst):
            n = len(lst)
            s = sorted(lst)
            return (s[n//2-1]/2.0+s[n//2]/2.0, s[n//2])[n % 2] if n else None
            '''
            retrieved median fxn from https://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
            '''

        newMyPyTable = MyPyTable(column_names=["attribute", "min", "max", "mid", "avg", "median"], data=None)
        
        col_data = []
        attributes = []
        for item in col_names:
            col_data.append(self.get_column(item))
            attributes.append(item)

        mins = []
        maxs = []
        mids = []
        avgs = []
        meds = []

        if len(col_data[0]) != 0:
            for row in col_data:
                mins.append(min(row))
                maxs.append(max(row))
                mids.append((max(row)+min(row))/2)
                avgs.append(round(sum(row)/len(row), 4))
                meds.append(median(row))

            finalData = []
            for item in attributes:
                finalData.append([item])

            for i in range(len(finalData)):
                finalData[i].append(mins[i])
                finalData[i].append(maxs[i])
                finalData[i].append(mids[i])
                finalData[i].append(avgs[i])
                finalData[i].append(meds[i])

            newMyPyTable.data = finalData

        return newMyPyTable

    def perform_inner_join(self, other_table, key_column_names):
        """Return a new MyPyTable that is this MyPyTable inner joined
            with other_table based on key_column_names.

        Args:
            other_table(MyPyTable): the second table to join this table with.
            key_column_names(list of str): column names to use as row keys.

        Returns:
            MyPyTable: the inner joined table.
        """
        newTable_cols = []
        for item in self.column_names:
            newTable_cols.append(item)
        for item in other_table.column_names:
            if item not in newTable_cols:
                newTable_cols.append(item)

        key_indexes_og = []
        for item in key_column_names:
            key_indexes_og.append(self.column_names.index(item))

        key_indexes_new = []
        for item in key_column_names:
            key_indexes_new.append(other_table.column_names.index(item))

        newTable = MyPyTable(column_names=newTable_cols, data=None)
           
        for row in self.data:

            key_temp_stuff = []
            non_key_stuff = []
            for i in range(len(row)):
                if i in key_indexes_og:
                    key_temp_stuff.append(row[i])
                if i not in key_indexes_og:
                    non_key_stuff.append(row[i])

            for row2 in other_table.data:
                key2_temp_stuff = []
                non_key_added_stuff = []
                for j in range(len(row2)):
                    if j in key_indexes_new:
                        key2_temp_stuff.append(row2[j])
                    if j not in key_indexes_new:
                        non_key_added_stuff.append(row2[j])
        
                keys_match = True
                for item in key2_temp_stuff:
                    if item not in key_temp_stuff:
                        keys_match = False
                        break
                
                if len(key2_temp_stuff) != len(key_temp_stuff):
                    keys_match = False
                        
                if keys_match:
                    newEntry = []
                    for item in row:
                        newEntry.append(item)
                    for item in non_key_added_stuff:
                        newEntry.append(item)
                    newTable.data.append(newEntry)

        return newTable

    def perform_full_outer_join(self, other_table, key_column_names):
        """Return a new MyPyTable that is this MyPyTable fully outer joined with
            other_table based on key_column_names.
        Args:
            other_table(MyPyTable): the second table to join this table with.
            key_column_names(list of str): column names to use as row keys.
        Returns:
            MyPyTable: the fully outer joined table.
        Notes:
            Pad the attributes with missing values with "NA".
        """
        newTable_cols = []
        for item in self.column_names:
            newTable_cols.append(item)
        for item in other_table.column_names:
            if item not in newTable_cols:
                newTable_cols.append(item)

        key_indexes_og = []
        for item in key_column_names:
            key_indexes_og.append(self.column_names.index(item))

        key_indexes_new = []
        for item in key_column_names:
            key_indexes_new.append(other_table.column_names.index(item))

        newTable = MyPyTable(column_names=newTable_cols, data=None)
        
        for row in self.data:
            matchFound = False

            key_temp_stuff = []
            non_key_stuff = []
            for i in range(len(row)):
                if i in key_indexes_og:
                    key_temp_stuff.append(row[i])
                if i not in key_indexes_og:
                    non_key_stuff.append(row[i])

            for row2 in other_table.data:
                key2_temp_stuff = []
                non_key_added_stuff = []
                for j in range(len(row2)):
                    if j in key_indexes_new:
                        key2_temp_stuff.append(row2[j])
                    if j not in key_indexes_new:
                        non_key_added_stuff.append(row2[j])
        
                keys_match = True
                for item in key2_temp_stuff:
                    if item not in key_temp_stuff:
                        keys_match = False
                        break
                
                if len(key2_temp_stuff) != len(key_temp_stuff):
                    keys_match = False

                if keys_match:
                    newEntry = []
                    for item in row:
                        newEntry.append(item)
                    for item in non_key_added_stuff:
                        newEntry.append(item)
                    newTable.data.append(newEntry)
                    matchFound = True

            # left
            if not matchFound:
                newEntry = []
                for item in row:
                    newEntry.append(item)
                for item in non_key_added_stuff:
                    newEntry.append("NA")
                newTable.data.append(newEntry)
                    
        # right
        for row in other_table.data:
            matchFound = False

            key_temp_stuff = []
            non_key_stuff = []
            for i in range(len(row)):
                if i in key_indexes_new:
                    key_temp_stuff.append(row[i])
                if i not in key_indexes_new:
                    non_key_stuff.append(row[i])

            for row2 in self.data:
                key2_temp_stuff = []
                non_key_added_stuff = []
                for j in range(len(row2)):
                    if j in key_indexes_og:
                        key2_temp_stuff.append(row2[j])
                    if j not in key_indexes_og:
                        non_key_added_stuff.append(row2[j])
        
                keys_match = True
                for item in key2_temp_stuff:
                    if item not in key_temp_stuff:
                        keys_match = False
                        break
                
                if len(key2_temp_stuff) != len(key_temp_stuff):
                    keys_match = False

                if keys_match:
                    matchFound = True

            # right 
            if not matchFound:
                i=0
                j=0
                newEntry = []
                for header in newTable.column_names:
                    if header in other_table.column_names:
                        index = other_table.column_names.index(header)
                        val = row[index]
                        newEntry.append(val)
                    else:
                        newEntry.append("NA")
        
                newTable.data.append(newEntry)

        return newTable

    def get_frequencies(self, header, col_name):
        col = MyPyTable.get_column(self, col_name)
        values = []
        counts = []
        try:
            col.sort()
            for value in col:
                if value in values:
                    counts[-1] += 1 # okay because col is sorted
                else: # haven't seen this value before
                    values.append(value)
                    counts.append(1)
        except:
            for value in col:
                if value in values:
                    counts[values.index(value)] += 1 # okay because col is sorted
                else: # haven't seen this value before
                    values.append(value)
                    counts.append(1)
        
        return values, counts # we can return multiple items
        # packaged into a tuple