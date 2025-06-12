# ai_service.py
import google.generativeai as genai
import time
import streamlit as st # Used for st.error, st.warning

from config import GEMINI_API_KEY

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Failed to configure Gemini API in ai_service.py: {str(e)}. Please check your GOOGLE_API_KEY.")
    st.stop()


def call_gemini(prompt, pdf_content_parts, model_name='gemini-1.5-flash', max_retries=5):
    """
    Call Gemini API with retry logic and error handling.
    The pdf_content_parts is expected to be a list of dictionaries for multimodal input.
    """
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_name)

            # Combine image parts and prompt
            content = []
            if pdf_content_parts:
                content.extend(pdf_content_parts)
            content.append(prompt)

            response = model.generate_content(content, generation_config={"temperature": 0.2})

            if response and response.text:
                return response.text
            else:
                st.warning(f"Empty or invalid response from Gemini on attempt {attempt + 1}. Retrying...")
                raise Exception("Empty or invalid response received from Gemini")

        except genai.types.core.ClientResponseError as e:
            if e.response.status_code == 429: # Too many requests (Rate limit)
                st.warning(f"Rate limit hit on attempt {attempt + 1}. Retrying in {2 ** attempt} seconds.")
                time.sleep(2 ** attempt)
            elif e.response.status_code == 400 and "API key expired" in str(e):
                st.error("🚨 Your Google API key has expired or is invalid. Please renew it.")
                st.stop() # Stop further execution
            else:
                st.error(f"Gemini API error on attempt {attempt + 1}: Status {e.response.status_code}, Details: {e.response.text}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to get response from Gemini after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt) # Still wait and retry for other client errors
        except Exception as e:
            st.warning(f"General error calling Gemini on attempt {attempt + 1}: {str(e)}. Retrying in {2 ** attempt} seconds.")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to get response from Gemini after {max_retries} attempts: {str(e)}")
            time.sleep(2 ** attempt)

    return "Error: Unable to process request after multiple attempts."


# --- Analysis Functions (Prompts & Calls) ---

def analyze_resume(job_desc, pdf_content_parts, model_name):
    prompt = f"""
    You are an experienced HR manager and career consultant. Analyze this resume thoroughly based on the following job description:

    Job Description:
    {job_desc}

    Please provide a comprehensive evaluation covering:

    1. *STRENGTHS:*
        - Key qualifications that match the job requirements
        - Notable achievements and experiences
        - Skills that stand out

    2. *AREAS FOR IMPROVEMENT:*
        - Missing qualifications or skills
        - Weak sections that need enhancement
        - Formatting or presentation issues

    3. *SPECIFIC RECOMMENDATIONS:*
        - What to add or modify
        - How to better highlight relevant experience
        - Suggestions for improving impact

    4. *OVERALL RATING:*
        - Rate the resume on a scale of 1-10 for this specific job
        - Provide reasoning for the rating

    Be specific, actionable, and constructive in your feedback.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

def get_match_score(job_desc, pdf_content_parts, model_name):
    prompt = f"""
    Act as an Applicant Tracking System (ATS). Analyze this resume against the job description below:

    Job Description:
    {job_desc}

    Provide a detailed match analysis including:

    1. *MATCH SCORE: X%* (provide specific percentage, e.g., MATCH SCORE: 75%)

    2. *KEYWORD ALIGNMENT:*
        - Matched keywords and skills
        - Missing critical keywords
        - Keyword density analysis

    3. *EXPERIENCE ALIGNMENT:*
        - Relevant work experience match
        - Years of experience comparison
        - Industry experience relevance

    4. *SKILL MATCH BREAKDOWN:*
        - Technical skills alignment
        - Soft skills match
        - Certification/education match

    5. *RECOMMENDATIONS TO IMPROVE SCORE:*
        - Keywords to add
        - Experience to highlight
        - Skills to emphasize

    Be precise with the percentage and provide clear reasoning for the score.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error calculating match score: {str(e)}"

def optimize_resume(job_desc, pdf_content_parts, language="English", model_name='gemini-1.5-flash'):
    prompt = f"""
    You are a professional resume writer and career coach. Rewrite this resume in {language} to perfectly align with this job description:

    Job Description:
    {job_desc}

    Requirements for the optimized resume:

    1. *ATS-FRIENDLY FORMAT:*
        - Use standard section headers
        - Include relevant keywords naturally
        - Maintain clean, scannable structure

    2. *CONTENT OPTIMIZATION:*
        - Tailor the professional summary to match the role
        - Highlight most relevant experiences first
        - Quantify achievements with numbers/percentages
        - Use action verbs and industry terminology

    3. *STRUCTURE:*
        - Professional Summary/Objective
        - Core Competencies/Skills
        - Professional Experience (reverse chronological)
        - Education
        - Additional relevant sections

    4. *STYLE REQUIREMENTS:*
        - Professional and engaging tone
        - Consistent formatting
        - Appropriate length (1-2 pages)
        - Error-free grammar and spelling

    5. *KEYWORD INTEGRATION:*
        - Naturally incorporate job-specific keywords
        - Include industry-relevant terminology
        - Balance keyword density appropriately

    Please provide the complete, polished resume ready for submission. Format the output using Markdown (e.g., ## for sections, - for bullet points, ** for bold). Do not include any conversational filler, only the resume content.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error optimizing resume: {str(e)}"

def check_grammar(pdf_content_parts, model_name='gemini-1.5-flash'):
    prompt = """
    Act as a professional editor and grammar expert. Thoroughly review this resume for:

    1. *GRAMMATICAL ERRORS:*
        - Subject-verb agreement
        - Tense consistency
        - Punctuation mistakes
        - Sentence structure issues

    2. *LANGUAGE QUALITY:*
        - Word choice and vocabulary
        - Clarity and conciseness
        - Professional tone
        - Redundancy issues

    3. *FORMATTING CONSISTENCY:*
        - Consistent use of bullet points
        - Date formatting
        - Capitalization
        - Spacing and alignment

    4. *SPECIFIC CORRECTIONS:*
        - List each error found
        - Provide the corrected version
        - Explain why the change improves the text

    5. *OVERALL LANGUAGE ASSESSMENT:*
        - Rate the overall quality (1-10)
        - Suggest improvements for better impact
        - Recommend style enhancements

    Be thorough and provide specific, actionable feedback.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error checking grammar: {str(e)}"

def keyword_density(job_desc, pdf_content_parts, model_name='gemini-1.5-flash'):
    prompt = f"""
    Perform a comprehensive keyword analysis comparing this resume with the job description below:

    Job Description:
    {job_desc}

    Provide detailed analysis including:

    1. *TOP MATCHING KEYWORDS (with frequency):*
        - List keywords found in both documents
        - Show frequency count for each
        - Indicate importance level (High/Medium/Low)

    2. *MISSING CRITICAL KEYWORDS:*
        - Essential keywords from job description not in resume
        - Suggested placement locations
        - Context for natural integration

    3. *KEYWORD CATEGORIES:*
        - Technical Skills
        - Soft Skills
        - Industry Terms
        - Certifications/Tools
        - Action Verbs

    4. *OPTIMIZATION RECOMMENDATIONS:*
        - Keywords to add for better ATS performance
        - Keywords to emphasize more
        - Keywords that may be overused

    5. *KEYWORD DENSITY SCORE:*
        - Overall keyword alignment percentage
        - Comparison with industry standards
        - Recommendations for improvement

    Present findings in a clear, actionable format.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error analyzing keyword density: {str(e)}"

def suggest_roles(pdf_content_parts, model_name='gemini-1.5-flash'):
    prompt = """
    Based on this resume, act as a career counselor and suggest suitable job roles. Provide:

    1. *TOP 5 RECOMMENDED ROLES:*
        For each role, include:
        - Job title
        - Match percentage (how well suited)
        - Key qualifications that align
        - Potential career growth path

    2. *ROLE CATEGORIES:*
        - Primary roles (best fit)
        - Adjacent roles (with some upskilling)
        - Stretch roles (for career advancement)

    3. *INDUSTRY ANALYSIS:*
        - Best-fit industries
        - Emerging opportunities
        - Market demand insights

    4. *SKILL GAP ANALYSIS:*
        - Skills to develop for target roles
        - Certifications to consider
        - Experience areas to strengthen

    5. *CAREER PROGRESSION:*
        - Short-term role options (0-2 years)
        - Medium-term goals (2-5 years)
        - Long-term career trajectory

    Be specific about why each role is a good fit and provide actionable career advice.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error suggesting roles: {str(e)}"

def section_check(pdf_content_parts, model_name='gemini-1.5-flash'):
    prompt = """
    Analyze this resume for section completeness and structure. Evaluate:

    1. *PRESENT SECTIONS:*
        - List all sections currently in the resume
        - Rate each section's quality (1-10)
        - Identify strengths and weaknesses of each

    2. *MISSING ESSENTIAL SECTIONS:*
        - Professional Summary/Objective
        - Core Competencies/Skills
        - Work Experience
        - Education
        - Certifications (if applicable)
        - Projects (if relevant)

    3. *OPTIONAL BUT BENEFICIAL SECTIONS:*
        - Awards and Achievements
        - Professional Affiliations
        - Publications/Patents
        - Languages
        - Volunteer Experience
        - Professional References

    4. *SECTION-SPECIFIC IMPROVEMENTS:*
        For each section, suggest:
        - Content enhancements
        - Formatting improvements
        - Information to add or remove
        - Better organization methods

    5. *OVERALL STRUCTURE RECOMMENDATIONS:*
        - Optimal section order
        - Length and balance suggestions
        - Visual hierarchy improvements
        - ATS compatibility considerations

    6. *COMPLETENESS SCORE:*
        - Rate overall completeness (1-10)
        - Priority improvements needed
        - Timeline for implementing changes

    Provide specific, actionable recommendations for each section.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error checking sections: {str(e)}"

def generate_cover_letter(job_desc, pdf_content_parts, company_name="", hiring_manager="", model_name='gemini-1.5-flash'):
    prompt = f"""
    Based on this resume and the job description below, write a compelling cover letter:

    Job Description:
    {job_desc}

    Company Name: {company_name if company_name else "[Company Name]"}
    Hiring Manager: {hiring_manager if hiring_manager else "[Hiring Manager]"}

    Create a professional cover letter that:

    1. *OPENING PARAGRAPH:*
        - Hook the reader's attention
        - Mention the specific position
        - Brief value proposition

    2. *BODY PARAGRAPHS:*
        - Highlight most relevant experience
        - Connect skills to job requirements
        - Show knowledge of the company
        - Quantify achievements where possible

    3. *CLOSING PARAGRAPH:*
        - Reiterate interest and fit
        - Call to action
        - Professional closing

    4. *STYLE REQUIREMENTS:*
        - Professional but engaging tone
        - Appropriate length (3-4 paragraphs)
        - Industry-appropriate language
        - Error-free grammar and spelling

    Make it personalized, compelling, and aligned with the resume content.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def salary_insights(pdf_content_parts, location="", experience_level="", model_name='gemini-1.5-flash'):
    prompt = f"""
    Based on this resume, provide salary and market insights:

    Location: {location if location else "General Market"}
    Experience Level: {experience_level if experience_level else "Based on Resume"}

    Analyze and provide:

    1. *SALARY RANGE ESTIMATE:*
        - Entry level range
        - Mid-level range
        - Senior level range
        - Based on skills and experience shown

    2. *MARKET DEMAND:*
        - Demand for similar profiles
        - Growing vs. declining trends
        - Hot skills in the market

    3. *FACTORS AFFECTING SALARY:*
        - High-value skills present
        - Experience level impact
        - Industry standards
        - Geographic considerations

    4. *RECOMMENDATIONS TO INCREASE VALUE:*
        - Skills to develop
        - Certifications to pursue
        - Experience areas to focus on

    5. *NEGOTIATION INSIGHTS:*
        - Salary negotiation points
        - Non-salary benefits to consider
        - Market positioning strategy

    Provide realistic, data-informed insights based on current market trends.
    """
    try:
        return call_gemini(prompt, pdf_content_parts, model_name)
    except Exception as e:
        return f"Error generating salary insights: {str(e)}"

# NEW AI FUNCTIONS

def skill_gap_analysis(resume_content_parts, job_desc, model_name):
    prompt = f"""
    Act as a career development specialist. Compare the provided resume content with the following job description.

    Job Description:
    {job_desc}

    Based on this comparison, identify:

    1. *KEY SKILLS REQUIRED:* List the most critical skills mentioned in the job description.
    2. *SKILLS PRESENT IN RESUME:* List the skills explicitly visible in the resume.
    3. *SKILL GAPS IDENTIFIED:* Pinpoint specific skills from the job description that are missing or weakly represented in the resume.
    4. *LEARNING PATH SUGGESTIONS:* For each identified skill gap, suggest actionable steps to acquire or strengthen that skill. This could include:
        - Specific types of online courses (e.g., Coursera, Udemy, edX).
        - Relevant certifications (e.g., AWS Certified Developer, PMP).
        - Project ideas to gain practical experience.
        - Books or resources.
    5. *OVERALL STRENGTHENING ADVICE:* General advice to improve the resume for this role related to skills.

    Be very specific with your suggestions.
    """
    try:
        return call_gemini(prompt, resume_content_parts, model_name)
    except Exception as e:
        return f"Error performing skill gap analysis: {str(e)}"

def generate_interview_questions(resume_content_parts, job_desc, model_name):
    prompt = f"""
    You are an expert interviewer for the role described in the job description.
    Generate a list of challenging and insightful interview questions based on the provided resume content and the job description.

    Job Description:
    {job_desc}

    Focus on:
    1. *BEHAVIORAL QUESTIONS:* Questions that explore past experiences and behaviors relevant to the job.
    2. *TECHNICAL QUESTIONS:* Questions directly related to skills and technologies mentioned in the job description or inferred from the resume.
    3. *SITUATIONAL QUESTIONS:* Hypothetical scenarios relevant to the role.
    4. *QUESTIONS ABOUT GAPS/WEAKNESSES:* Questions that might arise from perceived weaknesses or gaps in the resume (e.g., short tenure, lack of specific experience).
    5. *QUESTIONS TO SHOW FIT:* Questions to assess cultural fit or motivation.

    For each question, briefly explain *why* it's a good question for this candidate/role. Provide at least 10 questions.
    """
    try:
        return call_gemini(prompt, resume_content_parts, model_name)
    except Exception as e:
        return f"Error generating interview questions: {str(e)}"

def generate_branding_statement(resume_content_parts, target_role_type="", model_name='gemini-1.5-flash'):
    prompt = f"""
    You are a professional career coach specializing in personal branding.
    Based on the provided resume content, generate compelling personal branding statements for the applicant.

    If a target role type is provided ('{target_role_type}'), tailor the statements towards that. Otherwise, make them general but impactful.

    Provide:
    1. *PROFESSIONAL HEADLINE (for LinkedIn/Resume Top):* Short, impactful statement (1-2 sentences).
    2. *PROFESSIONAL SUMMARY/BIO (short):* 3-5 sentences summarizing key strengths, experiences, and career goals.
    3. *KEY SKILL TAGS:* A list of 5-8 strong keyword/skill tags.
    4. *CORE VALUE PROPOSITION:* A short paragraph explaining what unique value this applicant brings to a role/company.
    5. *IMPACT STATEMENTS (3 examples):* Short, quantified statements highlighting achievements.

    Ensure the language is professional, confident, and action-oriented.
    """
    try:
        return call_gemini(prompt, resume_content_parts, model_name)
    except Exception as e:
        return f"Error generating branding statement: {str(e)}"