from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import PyPDF2
import re

class ExtractResumeTextSchema(BaseModel):
    file_path: str = Field(description="Path to the PDF file to extract text from")

class ExtractResumeText(BaseTool):
    name: str = "extract_resume_text"
    description: str = "Extract text content from a PDF resume file and extract key information like name and mobile number"
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
            email = self._extract_email(text)
            
            structured_output = f"""
CANDIDATE INFORMATION:
Name: {name}
Mobile: {mobile}
Email: {email}

RESUME CONTENT:
{text}
"""
            
            return structured_output
            
        except Exception as e:
            return f"Error extracting text from {file_path}: {str(e)}"
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = ''.join(char for char in text if ord(char) < 127)
        text = re.sub(r'[^\w\s\.\,\-\@\(\)\+\/\:]', ' ', text)
        return text.strip()
    
    def _extract_name(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) > 2:
                skip_keywords = ['email', 'phone', 'mobile', 'address', 'resume', 'cv', 'objective', 'summary', 'profile', 'contact', 'linkedin', 'github']
                if not any(keyword in line.lower() for keyword in skip_keywords):
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line) and len(line.split()) <= 4:
                        return line
                    if re.match(r'^[A-Z]\.?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line):
                        return line

        words = text.split()[:20]
        potential_name = []
        for word in words:
            if word.istitle() and len(word) > 1 and word.isalpha():
                potential_name.append(word)
                if len(potential_name) >= 2:
                    break
        
        if potential_name:
            return ' '.join(potential_name)
        
        return "Not found"
    
    def _extract_mobile(self, text: str) -> str:
        patterns = [
            r'(?:\+91|91)[-\s]?[6-9]\d{9}',  
            r'[6-9]\d{9}', 
            r'\+\d{1,3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}', 
            r'\(\d{3}\)[-\s]?\d{3}[-\s]?\d{4}',
            r'\d{3}[-\s]?\d{3}[-\s]?\d{4}',
            r'\d{10}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                mobile = re.sub(r'[-\s]', '', matches[0])
                return mobile
        
        return "Not found"
    
    def _extract_email(self, text: str) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        if matches:
            return matches[0]
        return "Not found"