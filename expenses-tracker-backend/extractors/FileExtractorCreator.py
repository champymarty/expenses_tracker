from fastapi import UploadFile
from database.Source import Source
from extractors.FileExtractor import FileExtractor
from extractors.NotSupportedFile import NotSupportedFile
from extractors.excel.BncFileExtractor import BncFileExtractor
from extractors.excel.RogerFileExtractor import RogerFileExtractor
from extractors.excel.TangerineFileExtractor import TangerineFileExtractor
from extractors.excel.TriangleFileExtractor import TriangleFileExtractor
from extractors.html.HtmlRogerExtractor import HtmlRogerExtractor

class FileExtractorCreator:

    extractors = [
        BncFileExtractor,
        RogerFileExtractor,
        TriangleFileExtractor,
        TangerineFileExtractor,
        HtmlRogerExtractor,
    ]

    @staticmethod
    async def create_extractor(file: UploadFile, source: Source | None) -> list[FileExtractor]:
        if not file or not file.filename:
            raise NotSupportedFile(filename=file.filename, message="No file provided or file is empty.")
        
        if source is None:
            found_extractors = []
            for extractor_class in FileExtractorCreator.extractors:
                extractor_instance: FileExtractor = extractor_class(file=file, source=source)
                if await extractor_instance.apply():
                    found_extractors.append(extractor_instance)
            return found_extractors
        
        if file.filename.lower().endswith(".csv"):
            if source.type.lower() == "BNC".lower():
                return [BncFileExtractor(file=file, source=source)]
            elif source.type.lower() == "ROGER".lower():
                return [RogerFileExtractor(file=file, source=source)]
            elif source.type.lower() == "TRIANGLE".lower():
                return [TriangleFileExtractor(file=file, source=source)]
            elif source.type.lower() == "TANGERINE".lower():
                return [TangerineFileExtractor(file=file, source=source)]
        elif file.filename.endswith(".html"):
            if source.type.lower() == "ROGER".lower():
                return [HtmlRogerExtractor(file=file, source=source)]
    
        raise NotSupportedFile(filename=file.filename, message=f"Invalid file type. {file.filename} is not supported.")