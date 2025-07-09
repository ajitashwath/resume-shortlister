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

st.set_page_config(
    page_title="Resume Shortlisting Tool",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #5c6bc0, #8e24aa); /* Blue to purple gradient */
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
    for row in df.iterrows():
        table_data.append([str(row[col]) for col in df.columns])
    
    table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer

def extract_resumes_data(uploaded_files):
    extract_tool = ExtractResumeText()
    resumes_data = []
    
    for file in uploaded_files:
        try:
            temp_path = f"temp_{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            result = extract_tool._run(temp_path)
            resumes_data.append(result)
            os.remove(temp_path)
            
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
    
    return resumes_data

def process_shortlisting_results(result_text):
    # This function would parse the AI response and create a structured format
    # For now, we'll simulate the structure since the actual response format may vary
    # Example structure - in reality, you'd parse the actual LLM response
    # This is a simplified example
    sample_data = []
    candidates = [
        ("John Smith", "+1-555-0123", 8.5, "Tell me about your experience with React. How do you handle state management?"),
        ("Sarah Johnson", "+1-555-0124", 8.2, "Describe a challenging project you worked on. What was your approach?"),
        ("Mike Davis", "+1-555-0125", 7.8, "How do you ensure code quality in your projects? Do you use any testing frameworks?"),
        ("Emily Chen", "+1-555-0126", 8.0, "What's your experience with API integration? Can you give an example?"),
        ("David Wilson", "+1-555-0127", 7.5, "How do you stay updated with new technologies? What's your learning approach?"),
    ]
    
    for name, mobile, score, question in candidates:
        sample_data.append({
            "Name": name,
            "Mobile": mobile,
            "Score": score,
            "Questions for Interview": question
        })
    
    return pd.DataFrame(sample_data)

def main():
    st.markdown('<div class="main-header">Resume Shortlisting Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Upload resumes and job description to get AI-powered shortlisting with interview questions.</div>', unsafe_allow_html=True)

    st.subheader("🔑 OpenAI API Configuration")
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        placeholder="sk-...",
        help="Your API key will be used securely for this session only"
    )
    
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        return

    with st.sidebar:
        st.header("Configuration")
        max_resumes = st.slider("Maximum resumes to process", 1, 20, 10)
        scoring_threshold = st.slider("Minimum score threshold", 1, 10, 5)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Enter the job description:",
            height=200,
            placeholder="Paste the job description here..."
        )
    
    with col2:
        st.subheader("Upload Resumes")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help=f"Upload up to {max_resumes} PDF files"
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s)")
            for file in uploaded_files:
                st.write(f"📄 {file.name}")
    
    if st.button("🔍 Analyze and Shortlist", type="primary"):
        if not job_description:
            st.error("Please enter a job description.")
            return
        
        if not uploaded_files:
            st.error("Please upload at least one resume.")
            return
        
        if len(uploaded_files) > max_resumes:
            st.error(f"Maximum {max_resumes} resumes allowed.")
            return

        with st.spinner("Processing resumes... This may take a few minutes."):
            try:
                resumes_data = extract_resumes_data(uploaded_files)
                
                if not resumes_data:
                    st.error("No resumes could be processed. Please check your files.")
                    return
                crew_instance = ResumeShortlistingCrew(api_key=api_key)
                
                result = crew_instance.crew().kickoff(inputs={
                    'job_description': job_description,
                    'resumes': '\n\n'.join(resumes_data)
                })
                
                df = process_shortlisting_results(str(result))
                df_filtered = df[df['Score'] >= scoring_threshold]
                st.success("Analysis complete!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Resumes", len(uploaded_files))
                with col2:
                    st.metric("Candidates Above Threshold", len(df_filtered))
                with col3:
                    st.metric("Average Score", f"{df_filtered['Score'].mean():.1f}")
                
                st.subheader("Shortlisted Candidates")
                sort_by = st.selectbox("Sort by:", ["Score", "Name"])
                ascending = st.checkbox("Ascending order", value=False)
                
                df_sorted = df_filtered.sort_values(by=sort_by, ascending=ascending)  # type: ignore
                st.dataframe(df_sorted, use_container_width=True)

                st.subheader("Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df_sorted.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv,
                        file_name="shortlisted_resumes.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    pdf_buffer = create_pdf_report(df_sorted, "shortlisted_resumes.pdf")
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer,
                        file_name="shortlisted_resumes.pdf",
                        mime="application/pdf"
                    )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your OpenAI API key and try again.")

if __name__ == "__main__":
    main()