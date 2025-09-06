from fastapi import UploadFile
from database.Source import Source
from extractors.BncFileExtractor import BncFileExtractor
from extractors.RogerFileExtractor import RogerFileExtractor
from extractors.FileExtractor import FileExtractor
from extractors.NotSupportedFile import NotSupportedFile

class FileExtractorCreator:

    @staticmethod
    def create_extractor(file: UploadFile, source: Source) -> FileExtractor:
        if not file or not file.filename:
            raise NotSupportedFile(filename=file.filename, message="No file provided or file is empty.")
        if file.filename.endswith(".csv"):
            if source.type.lower() == "BNC".lower():
                return BncFileExtractor(file=file, source=source)
            elif source.type.lower() == "ROGER".lower():
                return RogerFileExtractor(file=file, source=source)
        
        raise NotSupportedFile(filename=file.filename, message=f"Invalid file type. {file.filename} is not supported.")