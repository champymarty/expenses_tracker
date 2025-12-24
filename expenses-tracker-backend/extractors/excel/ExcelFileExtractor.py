from extractors.FileExtractor import FileExtractor


class ExcelFileExtractor(FileExtractor):

    async def apply(self) -> bool:
        """Extracts the content of the file."""
        return self.file.filename is not None and self.file.filename.lower().endswith(".csv")