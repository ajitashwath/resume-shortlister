import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from crewai import Crew
from src.resume_shortlisting.tools.custom_tool import ExtractResumeText
from src.resume_shortlisting.crew import ResumeShortlistingCrew
import os
import re

st.set_page_config(
    page_title="Resume Shortlisting Tool",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #5c6bc0, #8e24aa);
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
    }

    .main-subtitle {
        color: #e0e0e0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    .stButton button {
        background: linear-gradient(90deg, #1e88e5, #3949ab);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 1rem;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.4);
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        background: linear-gradient(90deg, #1565c0, #283593);
    }

    .metric-container {
        background-color: #1e1e2f;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #3a3a55;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 8px rgba(138, 43, 226, 0.15);
    }

    .stProgress > div > div > div > div {
        background-color: #8e24aa;
    }
</style>
""", unsafe_allow_html=True)

def create_pdf_report(df, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
  
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1
    )
    story.append(Paragraph("Resume Shortlisting Report", title_style))
    story.append(Spacer(1, 12))
    table_data = [df.columns.tolist()]
    for _, row in df.iterrows():
        row_data = []
        for col in df.columns:
            cell_content = str(row[col])
            # Wrap long content
            if len(cell_content) > 100:
                cell_content = cell_content[:100] + "..."
            row_data.append(cell_content)
        table_data.append(row_data)
    
    table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 2.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer

def extract_resumes_data(uploaded_files):
    extract_tool = ExtractResumeText()
    resumes_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {file.name}...")
            temp_path = f"temp_{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            result = extract_tool._run(temp_path)
            resumes_data.append(result)
            os.remove(temp_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return resumes_data

def parse_ai_response(result_text):
    try:
        text = str(result_text)
        lines = text.split('\n')
        candidates = []
        
        for line in lines:
            line = line.strip()
            if '|' in line and len(line.split('|')) >= 4:
                if any(header in line.lower() for header in ['name', 'mobile', 'score', 'questions']):
                    continue
                if line.startswith('|---') or line.startswith('---'):
                    continue
                
                parts = [part.strip() for part in line.split('|')]
                
                while parts and not parts[0]:
                    parts.pop(0)
                while parts and not parts[-1]:
                    parts.pop()
                
                if len(parts) >= 4:
                    try:
                        name = parts[0]
                        mobile = parts[1]
                        
                        score_text = parts[2]
                        score_match = re.search(r'(\d+(?:\.\d+)?)', score_text)
                        score = float(score_match.group(1)) if score_match else 0.0
                        
                        questions = parts[3]
                        reasoning = parts[4] if len(parts) > 4 else "No reasoning provided"
                        if name and name.lower() not in ['name', 'example', 'sample']:
                            candidates.append({
                                "Name": name,
                                "Mobile": mobile,
                                "Score": score,
                                "Questions for Interview": questions,
                                "Reasoning": reasoning
                            })
                    except (ValueError, IndexError) as e:
                        st.warning(f"Skipping malformed row: {line[:50]}...")
                        continue
        
        if not candidates:
            blocks = re.split(r'\n\s*\n', text)
            
            for block in blocks:
                if any(keyword in block.lower() for keyword in ['name:', 'mobile:', 'score:', 'candidate']):
                    try:
                        name_match = re.search(r'name:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
                        mobile_match = re.search(r'(?:mobile|phone):\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
                        score_match = re.search(r'score:\s*(\d+(?:\.\d+)?)', block, re.IGNORECASE)
                        questions_match = re.search(r'(?:questions?|interview):\s*(.+?)(?:\n\n|$)', block, re.IGNORECASE | re.DOTALL)
                        reasoning_match = re.search(r'(?:reasoning|rationale|analysis):\s*(.+?)(?:\n\n|$)', block, re.IGNORECASE | re.DOTALL)
                        
                        if name_match:
                            name = name_match.group(1).strip()
                            mobile = mobile_match.group(1).strip() if mobile_match else "Not found"
                            score = float(score_match.group(1)) if score_match else 0.0
                            questions = questions_match.group(1).strip() if questions_match else "No questions provided"
                            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                            
                            candidates.append({
                                "Name": name,
                                "Mobile": mobile,
                                "Score": score,
                                "Questions for Interview": questions,
                                "Reasoning": reasoning
                            })
                    except Exception:
                        continue
        
        if not candidates:
            json_pattern = r'\{[^}]*"name"[^}]*\}'
            json_matches = re.findall(json_pattern, text, re.IGNORECASE)
            
            for match in json_matches:
                try:
                    name_match = re.search(r'"name":\s*"([^"]+)"', match, re.IGNORECASE)
                    mobile_match = re.search(r'"(?:mobile|phone)":\s*"([^"]+)"', match, re.IGNORECASE)
                    score_match = re.search(r'"score":\s*(\d+(?:\.\d+)?)', match, re.IGNORECASE)
                    
                    if name_match:
                        candidates.append({
                            "Name": name_match.group(1),
                            "Mobile": mobile_match.group(1) if mobile_match else "Not found",
                            "Score": float(score_match.group(1)) if score_match else 0.0,
                            "Questions for Interview": "Check detailed response",
                            "Reasoning": "Extracted from JSON format"
                        })
                except Exception:
                    continue
        
        if not candidates:
            name_score_pattern = r'(?:Name|Candidate):\s*([A-Za-z\s]+).*?(?:Score|Rating):\s*(\d+(?:\.\d+)?)'
            matches = re.findall(name_score_pattern, text, re.IGNORECASE | re.DOTALL)
            
            for name, score in matches:
                if name.strip():
                    candidates.append({
                        "Name": name.strip(),
                        "Mobile": "Not found",
                        "Score": float(score),
                        "Questions for Interview": "Please check the detailed response",
                        "Reasoning": "Extracted from text pattern"
                    })
        
        if not candidates:
            st.warning("Could not parse AI response into structured format. Check the raw response below.")
            candidates = [
                {
                    "Name": "Parse Error", 
                    "Mobile": "N/A", 
                    "Score": 0.0, 
                    "Questions for Interview": "Please check the raw AI response",
                    "Reasoning": "Could not parse response format"
                }
            ]
        
        return pd.DataFrame(candidates)
        
    except Exception as e:
        st.error(f"Error parsing AI response: {str(e)}")
        return pd.DataFrame([{
            "Name": "Error", 
            "Mobile": "Error", 
            "Score": 0.0, 
            "Questions for Interview": "Error parsing response",
            "Reasoning": str(e)
        }])

def validate_api_key(api_key):
    if not api_key:
        return False, "API key is required"
    
    if not api_key.startswith('sk-'):
        return False, "API key should start with 'sk-'"
    
    if len(api_key) < 40:
        return False, "API key seems too short"
    
    return True, "Valid format"

def main():
    st.markdown('<div class="main-header">Resume Shortlisting Tool<div class="main-subtitle">Upload resumes and job description to get AI-powered shortlisting with interview questions</div></div>', unsafe_allow_html=True)

    st.subheader("🔑 OpenAI API Configuration")
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        placeholder="sk-...",
        help="You can find your API key at https://platform.openai.com/account/api-keys"
    )

    if api_key:
        is_valid, message = validate_api_key(api_key)
        st.session_state.openai_api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key
        if is_valid:
            st.success("✅ API key format looks correct")
        else:
            st.error(f"❌ {message}")
            return
    else:
        st.warning("Please enter your OpenAI API key to continue.")
        return

    with st.sidebar:
        st.header("⚙️ Configuration")
        max_resumes = st.slider("Maximum resumes to process", 1, 20, 10)
        scoring_threshold = st.slider("Minimum score threshold", 1.0, 10.0, 7.0, 0.1)
        
        st.subheader("📊 Processing Info")
        st.info(f"Will process up to {max_resumes} resumes")
        st.info(f"Candidates need score ≥ {scoring_threshold}")
        
        st.subheader("🎯 Analysis Features")
        st.info("✅ Automatic name/mobile extraction")
        st.info("✅ Skills matching analysis")
        st.info("✅ Custom interview questions")
        st.info("✅ Experience level evaluation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Enter the job description:",
            height=250,
            placeholder="Paste the complete job description here...\n\nInclude:\n- Required skills\n- Experience level\n- Qualifications\n- Responsibilities",
            help="Provide a detailed job description for better candidate matching"
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.caption(f"📝 Word count: {word_count}")
    
    with col2:
        st.subheader("📄 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help=f"Upload up to {max_resumes} PDF resumes"
        )
        
        if uploaded_files:
            if len(uploaded_files) > max_resumes:
                st.error(f"❌ Please upload maximum {max_resumes} resumes")
            else:
                st.success(f"✅ Uploaded {len(uploaded_files)} resume(s)")
                
            with st.expander("📁 Uploaded Files"):
                for file in uploaded_files:
                    file_size = len(file.getbuffer()) / 1024  # KB
                    st.write(f"📄 {file.name} ({file_size:.1f} KB)")
    
    if st.button("🚀 Analyze and Shortlist Resumes", type="primary"):
        if not job_description.strip():
            st.error("❌ Please enter a job description.")
            return
        
        if not uploaded_files:
            st.error("❌ Please upload at least one resume.")
            return
        
        if len(uploaded_files) > max_resumes:
            st.error(f"❌ Maximum {max_resumes} resumes allowed.")
            return

        with st.spinner("🔄 Processing resumes... This may take a few minutes."):
            try:
                st.info("📝 Extracting text from resumes...")
                resumes_data = extract_resumes_data(uploaded_files)
                
                if not resumes_data:
                    st.error("❌ No resumes could be processed. Please check your files.")
                    return
            
                st.info("🤖 Running AI analysis...")
                crew_instance = ResumeShortlistingCrew(api_key=api_key)
                
                result = crew_instance.crew().kickoff(inputs={
                    'job_description': job_description,
                    'resumes': '\n\n'.join(resumes_data)
                })

                st.info("📊 Processing results...")
                df = parse_ai_response(result)
                df_filtered = df[df['Score'] >= scoring_threshold]
                
                st.success("✅ Analysis complete!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📄 Total Resumes", len(uploaded_files))
                with col2:
                    st.metric("🎯 Qualified Candidates", len(df_filtered))
                with col3:
                    if len(df_filtered) > 0:
                        st.metric("📈 Average Score", f"{df_filtered['Score'].mean():.1f}")
                    else:
                        st.metric("📈 Average Score", "N/A")
                if len(df_filtered) == 0:
                    st.warning(f"⚠️ No candidates met the minimum score threshold of {scoring_threshold}")
                    st.info("💡 Try lowering the scoring threshold in the sidebar")
                    
                    if len(df) > 0:
                        st.subheader("📋 All Analyzed Candidates")
                        st.dataframe(df.sort_values('Score', ascending=False), use_container_width=True)
                else:
                    st.subheader("🏆 Shortlisted Candidates")
                    col1, col2 = st.columns(2)
                    with col1:
                        sort_by = st.selectbox("Sort by:", ["Score", "Name"])
                    with col2:
                        ascending = st.checkbox("Ascending order", value=False)
                    
                    df_sorted = df_filtered.sort_values(by=sort_by, ascending=ascending) #type: ignore
                    st.dataframe(
                        df_sorted.style.format({'Score': '{:.1f}'})
                        .background_gradient(subset=['Score'], cmap='RdYlGn'), #type: ignore
                        use_container_width=True
                    )

                    st.subheader("📥 Export Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv = df_sorted.to_csv(index=False)
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv,
                            file_name=f"shortlisted_resumes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        pdf_buffer = create_pdf_report(df_sorted, "shortlisted_resumes.pdf")
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_buffer,
                            file_name=f"shortlisted_resumes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
    
                with st.expander("🔍 View Raw AI Response"):
                    st.text(str(result))
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Please check your OpenAI API key and try again.")

                with st.expander("🔧 Error Details"):
                    st.code(str(e))

if __name__ == "__main__":
    main()