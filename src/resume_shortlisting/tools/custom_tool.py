from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import PyPDF2
import re

class ExtractResumeTextSchema(BaseModel):
    file_path: str = Field(description="Path to the PDF file to extract text from")

class ExtractResumeText(BaseTool):
    name: str = "extract_resume_text"
    description: str = "Extract text content from a PDF resume file"
    args_schema: Type[BaseModel] = ExtractResumeTextSchema
    
    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            text = self._clean_text(text)
            name = self._extract_name(text)
            mobile = self._extract_mobile(text)
            
            return f"Name: {name}\nMobile: {mobile}\n\n{text}"
            
        except Exception as e:
            return f"Error extracting text from {file_path}: {str(e)}"
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = ''.join(char for char in text if ord(char) < 127)
        return text.strip()
    
    def _extract_name(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'mobile', 'address']):
                if re.match(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*$', line):
                    return line
        return "Not found"
    
    def _extract_mobile(self, text: str) -> str:
        patterns = [
            r'(?:\+91|91)?\s?[6-9]\d{9}', 
            r'\+\d{1,3}\s?\d{3}\s?\d{3}\s?\d{4}',  
            r'\(\d{3}\)\s?\d{3}-\d{4}',  
            r'\d{3}-\d{3}-\d{4}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return "Not found"