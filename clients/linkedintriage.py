#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union
from clients import Triage

class LinkedinTriage(Triage):
    name = 'linkedin'

    @property
    def linkedin_subdirectory_names(self):
        return {
            6: 'past_007_days',
            13: 'past_014_days',
            27: 'past_028_days',
            89: 'past_090_days',
            364: 'past_365_days'
        }
    
    def __init__(self):
        super().__init__()
        self.init_linkedin_folders()
        
    def init_linkedin_folders(self):

        for folder in self.linkedin_subdirectory_names.values():
            folder_path = self.triage_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

    def extract_dates_from_filename(self, filename: str) -> Tuple[str, str]:
        """
        Extracts start and end dates from a given filename in YYYY-MM-DD format.
        """
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, filename)
        
        if len(dates) != 2:
            raise ValueError("The filename should contain exactly two dates in YYYY-MM-DD format.")
        
        start_date, end_date = dates
        return start_date, end_date
    
    def days_between_dates(self, start_date: str, end_date: str) -> int:
        """
        Calc days between two dates in YYYY-MM-DD format.
        """
        date_format = "%Y-%m-%d"
        start_date_obj = datetime.strptime(start_date, date_format)
        end_date_obj = datetime.strptime(end_date, date_format)
        delta = end_date_obj - start_date_obj
        return delta.days
    
    def get_linkedin_output_directory(self, xlsx_filename: str) -> Path:
        """
        Get the appropriate directory for storing a given LinkedIn xlsx file.

        Args:
            xlsx_filename (str): The filename of the xlsx file.
        """
        start_date, end_date = self.extract_dates_from_filename(xlsx_filename)
        duration = self.days_between_dates(start_date, end_date)
        
        # Use a direct dictionary lookup since the duration will always match one of the keys
        folder_name = self.linkedin_subdirectory_names.get(duration)
        
        if folder_name is None:
            raise ValueError(f"No matching folder for a duration of {duration} days.")
        
        return self.triage_path / folder_name

    def triage(self, path: Union[str, Path], how='copy', overwrites='raise'):
        """
        Triage a single xlsx file or all xlsx files in a directory
        """
        
        super().triage_base() # This ensures that the data_ attribute is reset before triaging
        
        # Convert the path to a pathlib.Path object if it's not already one
        path = Path(path) if not isinstance(path, Path) else path

        # If the path is a directory, loop through all .xlsx files in the directory
        if path.is_dir():
            for i, file in enumerate(path.glob('*.xlsx')):
                self._triage_single_file(file, how=how, overwrites=overwrites)
            return f"{i+1} files processed in {path=}"
        elif path.is_file():
            # If it's a single file, just triage it
            return self._triage_single_file(path, how=how, overwrites=overwrites)
        else:
            raise ValueError("The specified path does not exist or is not a file/directory.")

    
    def _triage_single_file(self, filename: Path, how='copy', overwrites='raise'):
        """
        Triage a given xlsx filename by copying or moving it to the appropriate destination folder.
        """
        if how not in ['copy', 'move']:
            raise ValueError("The 'how' parameter must be either 'copy' or 'move'.")
        
        output_directory = self.get_linkedin_output_directory(filename.name)
        
        if how == 'copy':
            return self.copy(filename, output_directory, overwrites=overwrites)
        else:
            return self.move(filename, output_directory, overwrites=overwrites)



