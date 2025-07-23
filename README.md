# Resume Shortlisting Tool 🚀
An AI-powered resume shortlisting application that uses CrewAI and OpenAI to automatically analyze resumes against job descriptions, extract candidate information, and generate personalized interview questions.

## ✨ Features
- **AI-Powered Analysis**: Uses OpenAI GPT models through CrewAI for intelligent resume evaluation
- **Automatic Information Extraction**: Extracts candidate names, phone numbers, and emails from PDFs
- **Smart Scoring**: Scores candidates from 1-10 based on job requirement alignment
- **Interview Question Generation**: Creates personalized interview questions for each candidate
- **Multiple Export Formats**: Export results as CSV or professionally formatted PDF reports
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Configurable Thresholds**: Adjustable scoring thresholds and processing limits
- **Real-time Processing**: Live progress tracking during resume analysis

## 🛠️ Technology Stack
- **Frontend**: Streamlit
- **AI Framework**: CrewAI with OpenAI GPT-4o-mini
- **PDF Processing**: PyPDF2
- **Report Generation**: ReportLab
- **Data Processing**: Pandas
- **Configuration**: YAML

## 📋 Prerequisites
- Python ≥ 3.8
- OpenAI API Key ([Get one here](https://platform.openai.com/account/api-keys))

## 🚀 Installation

### Method 1: Using pip (Recommended)

```bash
git clone https://github.com/ajitashwath/resume-shortlister.git
cd resume-shortlister

pip install -e .

pip install -e ".[dev]"
```

### Method 2: Using Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -

git clone https://github.com/ajitashwath/resume-shortlister.git
cd resume-shortlister
poetry install
```

### Method 3: Manual Installation

```bash
git clone https://github.com/ajitashwath/resume-shortlister.git
cd resume-shortlister

# Create virtual environment
python -m venv venv
source venv/bin/activate

pip install streamlit crewai crewai-tools pandas PyPDF2 reportlab PyYAML pydantic openai
```

## 🏃‍♂️ Quick Start

1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Open in Browser**: The app will automatically open at `http://localhost:8501`

3. **Enter API Key**: Input your OpenAI API key in the configuration section

4. **Upload Resumes**: Upload PDF resumes (up to 20 files)

5. **Add Job Description**: Paste the complete job description

6. **Analyze**: Click "Analyze and Shortlist Resumes" to start processing

## 📊 Usage Guide

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| Maximum Resumes | Number of resumes to process | 10 |
| Score Threshold | Minimum score for qualification | 7.0 |
| API Model | OpenAI model to use | gpt-4o-mini |

### Input Requirements

**Job Description**: Include the following for best results:
- Required skills and technologies
- Experience level requirements
- Educational qualifications
- Job responsibilities
- Company culture fit criteria

**Resume Files**:
- Format: PDF only
- Size: No specific limit (reasonable file sizes recommended)
- Content: Should include contact information, skills, and experience

### Output Format

The tool generates a structured table with:
- **Name**: Extracted from resume
- **Mobile**: Phone number extracted from resume
- **Score**: 1-10 rating based on job fit
- **Questions for Interview**: 2-3 personalized questions
- **Reasoning**: Explanation for the score

## 🔧 Configuration Files

### agents.yaml
Defines the AI agents' roles and capabilities:
- `jd_interpreter`: Analyzes job descriptions
- `resume_analyst`: Evaluates resumes and generates questions

### tasks.yaml
Defines the workflow tasks:
- `analyze_jd`: Extracts key requirements from job descriptions
- `shortlist_resumes`: Analyzes and scores candidates

## 📁 Project Structure

```
resume-shortlisting-tool/
├── app.py                              # Main Streamlit application
├── src/
│   └── resume_shortlisting/
│       ├── __init__.py
│       ├── main.py                     # CLI entry point
│       ├── crew.py                     # CrewAI configuration
│       ├── config/
│       │   ├── agents.yaml             # AI agents configuration
│       │   └── tasks.yaml              # Task definitions
│       └── tools/
│           ├── __init__.py
│           └── custom_tool.py          # PDF text extraction tool
├── pyproject.toml                      # Project configuration
├── README.md                           # This file
└── requirements.txt                    # Dependencies (optional)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting


## 🙏 Acknowledgments

- [CrewAI](https://crewai.com/) for the multi-agent AI framework
- [Streamlit](https://streamlit.io/) for the web application framework
- [OpenAI](https://openai.com/) for the language model API
- [ReportLab](https://www.reportlab.com/) for PDF generation

