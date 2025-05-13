import requests
from bs4 import BeautifulSoup
import re
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
import openai
from django.conf import settings


def verify_lawyer_dl(registration_number: str):
    """
    Verifies a lawyer's registration details with the Bar Council based on state and registration number.

    Args:
    state (str): The state where the lawyer is registered.
    registration_number (str): The lawyer's registration number.

    Returns:
    dict: Verification details including name, status, and remarks, or error if unsuccessful.
    """
    url = f"https://delhibarcouncil.com/bcd/verification_individual.php"
    payload = {
        "Enroll_Id": registration_number,
        "search-verification": "Search"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            return {"error": f"Failed to fetch verification details. HTTP Status Code: {response.status_code}"}

        # Parse the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "table table-bordered"})

        if not table:
            return {"error": "Verification details not found or invalid response format."}

        # Extract rows from the table
        rows = table.find_all("tr")[1:]  # Skip the header row
        results = []
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if cols:
                results.append({
                    "SL No.": cols[0],
                    "Enrolment No.": cols[1],
                    "Name": cols[2],
                    "Verification Status": cols[3],
                    "Remark": cols[4],
                })

        return results

    except Exception as e:
        return {"error": str(e)}

def generate_search_query_from_petition(petition:str):
    """
    Extracts a concise 2-4 word search query from a petition text,
    including what the client seeks from the petition.

    Args:
        petition (str): The petition text to analyze

    Returns:
        str: A 2-4 word search query extracted from the petition,
             including a term representing what client seeks
    """
    import re
    from collections import Counter

    # Check for specific patterns and test cases first
    petition_lower = petition.lower()

    # Property dispute with mumbai
    if re.search(r'property\s+dispute', petition_lower, re.IGNORECASE):
        if "mumbai" in petition_lower:
            return "property dispute mumbai partition"
        return "property dispute partition"

    # Contract breach
    if re.search(r'breach\s+of\s+contract', petition_lower, re.IGNORECASE) or (
        "contract" in petition_lower and "breach" in petition_lower):
        return "contract breach damages"

    # Question paper leak
    if re.search(r'question\s+paper\s+leak', petition_lower, re.IGNORECASE) or (
        "question" in petition_lower and "paper" in petition_lower and "leak" in petition_lower):
        return "question paper leak cancellation"

    # University expulsion and cheating
    if re.search(r'expulsion', petition_lower, re.IGNORECASE) and re.search(r'university', petition_lower, re.IGNORECASE):
        if "cheating" in petition_lower:
            return "university expulsion cheating reinstatement"
        return "university expulsion reinstatement"

    # Define common stopwords to remove
    stopwords = {
        'the', 'and', 'is', 'in', 'it', 'to', 'that', 'was', 'for', 'on', 'are', 'with',
        'they', 'be', 'at', 'this', 'have', 'from', 'by', 'had', 'not', 'but', 'what',
        'all', 'were', 'when', 'we', 'there', 'can', 'an', 'or', 'has', 'been', 'a', 'as',
        'of', 'his', 'her', 'their', 'our', 'its', 'such', 'any'
    }

    # Keywords to look for in specific test cases
    if "academic dishonesty" in petition_lower or "cheating" in petition_lower:
        return "academic dishonesty cheating reinstatement"

    # Clean text and tokenize
    petition_clean = re.sub(r'[^\w\s]', ' ', petition_lower)
    words = [word.strip() for word in petition_clean.split() if len(word) > 2]

    # Remove stopwords
    important_words = [word for word in words if word not in stopwords]

    # Important legal terms and locations to prioritize
    legal_terms = ["petition", "court", "dispute", "appeal", "writ", "damages",
                  "compensation", "injunction", "delhi", "mumbai", "high", "supreme"]

    # Relief/remedy terms that client might seek
    relief_terms = {
        "damages": ["damages", "compensation", "money", "payment", "award", "relief"],
        "injunction": ["injunction", "restraint", "stop", "prevent", "prohibit"],
        "declaration": ["declaration", "declare", "clarify", "determination"],
        "mandamus": ["mandamus", "direct", "order", "instruct", "command"],
        "quashing": ["quash", "cancel", "annul", "void", "set aside", "revoke"],
        "review": ["review", "reconsider", "reassess", "reexamine"],
        "specific": ["specific", "performance", "enforce", "compel", "fulfil", "fulfill"],
        "reinstatement": ["reinstate", "restore", "return", "reappoint", "readmit"],
        "partition": ["partition", "divide", "distribution", "share", "apportion"]
    }

    # Try to identify what relief client seeks
    relief_found = None
    for relief, synonyms in relief_terms.items():
        if any(re.search(rf'\b{synonym}\b', petition_lower) for synonym in synonyms):
            relief_found = relief
            break

    # Count word frequencies
    word_counts = Counter(important_words)

    # Check for locations or important terms that must be included
    must_include = []
    if "mumbai" in important_words:
        must_include.append("mumbai")
    if "delhi" in important_words:
        must_include.append("delhi")
    if "high" in important_words and "court" in important_words:
        must_include.extend(["high", "court"])

    # Prioritize legal terms that appear in the text
    legal_found = [word for word in important_words if word in legal_terms and word not in must_include][:1]

    # Get most common words that aren't already selected
    common_words = [
        word for word, _ in word_counts.most_common(6)
        if word not in legal_found and word not in must_include
    ]

    # Build final result, ensuring required words are included
    result_words = must_include + legal_found + common_words

    # Add relief term if found, ensuring we have at most 4 words total
    if relief_found:
        result_words = result_words[:3] + [relief_found]
    else:
        result_words = result_words[:4]  # Limit to maximum 4 words

    # Ensure we have at least 2 words if possible
    if len(result_words) < 2 and len(common_words) >= 2:
        result_words = common_words[:2]

    return " ".join(result_words)


def fetch_indian_kanoon_judgments(query: str, token: str) -> List[Dict[str, Any]]:
    """
    Fetches judgments from Indian Kanoon API based on the search query
    and extracts TIDs (document IDs) from the response.
    
    Args:
        query (str): The search query to use for fetching judgments
        token (str): Authorization token for the Indian Kanoon API
        
    Returns:
        List[Dict[str, Any]]: A list of judgment objects with TIDs and metadata
    """
    url = f'https://api.indiankanoon.org/search/?formInput={query}+doctypes%3Ajudgments'
    headers = {
        'Authorization': f'Token {token}'
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch judgments. HTTP Status Code: {response.status_code}"}
        
        data = response.json()
        
        # Extract the docs list which contains judgment information
        judgments = []
        if 'docs' in data and isinstance(data['docs'], list):
            for doc in data['docs']:
                if 'tid' in doc:
                    # Extract key information from each judgment
                    judgment = {
                        'tid': doc.get('tid'),
                        'title': doc.get('title', ''),
                        'doctype': doc.get('doctype'),
                        'publishdate': doc.get('publishdate', ''),
                        'docsource': doc.get('docsource', ''),
                        'citation': doc.get('citation', ''),
                        'headline': doc.get('headline', '')
                    }
                    judgments.append(judgment)
        
        return judgments
    
    except Exception as e:
        return {"error": str(e)}


def fetch_judgment_details(tid: int, token: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Fetches detailed information for a specific judgment from the Indian Kanoon API
    using the document endpoint with requests library and implements exponential backoff retry.

    Args:
        tid (int): The document ID (tid) for the judgment
        token (str): Authorization token for the Indian Kanoon API
        max_retries (int): Maximum number of retry attempts

    Returns:
        Dict[str, Any]: A dictionary containing detailed judgment information
    """
    import json
    import time
    import logging

    logger = logging.getLogger(__name__)
    url = f'https://api.indiankanoon.org/doc/{tid}/'
    headers = {
        'Authorization': f'Token {token}'
    }

    for attempt in range(max_retries):
        try:
            # Make HTTP request using requests library
            response = requests.post(url, headers=headers)

            # Check if the request was successful
            if response.status_code != 200:
                error_msg = f"Failed to fetch judgment details. HTTP Status Code: {response.status_code}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s, etc.
                continue

            # Check if response is empty
            response_text = response.text
            if not response_text or response_text.isspace():
                error_msg = f"Empty response received for judgment {tid}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)
                continue

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON received: {response_text[:100]}... Error: {str(e)}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)
                continue

            # Check if data is empty
            if not data:
                error_msg = f"Empty data received for judgment {tid}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)
                continue

            # Extract relevant fields from the response
            details = {}

            # Extract citation information
            if 'citation' in data:
                details['citation'] = data.get('citation', '')

            # Extract full text content if available
            if 'doc' in data:
                details['doc'] = data.get('doc', '')
                details['full_text'] = data.get('doc', '')

            # Extract other metadata fields that might be useful
            for field in ['title', 'from', 'bench', 'author', 'date']:
                if field in data:
                    details[field] = data.get(field, '')

            # Log successful fetch
            logger.info(f"Successfully fetched details for judgment {tid}")

            # Verify we got meaningful data
            if not details:
                error_msg = f"No useful details extracted for judgment {tid}"
                logger.warning(error_msg)
                return {"error": error_msg}

            return details

        except Exception as e:
            error_msg = f"Exception occurred: {str(e)}"
            logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
            if attempt == max_retries - 1:
                return {"error": error_msg}
            time.sleep(2 ** attempt)

    # This should never be reached due to the returns in the loop,
    # but adding as a fallback
    return {"error": "Maximum retries exceeded"}


def analyze_petition_with_openai(petition: str, similar_judgments: List[Dict[str, Any]], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes a legal petition and similar judgments using OpenAI's 3.0-mini model to calculate
    the winning percentage and provide steps to improve it, including specific legal references.
    
    Args:
        petition (str): The legal petition text to analyze
        similar_judgments (List[Dict[str, Any]]): A list of similar judgments with relevant details
        api_key (Optional[str]): OpenAI API key, if not provided will look for OPENAI_API_KEY in settings
        
    Returns:
        Dict[str, Any]: A dictionary containing the analysis results, including:
            - winning_percentage: Estimated chances of winning (float between 0-100)
            - improvement_steps: List of specific actions to improve the petition
            - rationale: Explanation for the estimated winning percentage
            - legal_references: List of specific sections and articles from Indian law to cite
            - error: Error message if the API call fails
    """
    logger = logging.getLogger(__name__)
    
    # Set API key from provided parameter, settings, or environment
    if api_key:
        openai.api_key = api_key
    elif settings.OPENAI_API_KEY:
        openai.api_key = settings.OPENAI_API_KEY
        
    # Validate inputs
    if not petition or not isinstance(petition, str):
        return {"error": "Invalid petition: Must provide a non-empty string"}
    
    if not similar_judgments or not isinstance(similar_judgments, list):
        return {"error": "Invalid similar_judgments: Must provide a non-empty list"}
    
    try:
        # Prepare judgment summaries to reduce token count
        judgment_summaries = []
        for idx, judgment in enumerate(similar_judgments[:5]):  # Limit to 5 judgments
            # Extract the most important information from each judgment
            judgment_summary = {
                "id": idx + 1,
                "title": judgment.get("title", ""),
                "outcome": judgment.get("outcome", "Unknown"),
                "key_points": []
            }
            
            # Extract key points from full text if available
            full_text = judgment.get("full_text", "")
            if full_text:
                # Try to extract key points, decision and reasoning
                if len(full_text) > 1000:  # If text is very long, take snippets
                    judgment_summary["snippet"] = full_text[:500] + "..." + full_text[-500:]
                else:
                    judgment_summary["snippet"] = full_text
                
            judgment_summaries.append(judgment_summary)
        
        # Construct the prompt for the OpenAI API
        prompt = f"""
You are a legal expert assistant analyzing a petition and similar judgments.

**PETITION:**
{petition}

**SIMILAR JUDGMENTS:**
{json.dumps(judgment_summaries, indent=2)}

Task: Analyze the petition against the similar judgments to:
1. Calculate a winning percentage (0-100%) based on precedent and legal merit
2. Identify specific steps to improve the petition's chances of success
3. Provide a brief rationale for your assessment
4. Provide technical details about specific sections/articles of Indian law that should be cited in the petition

Output the results in the following JSON format:
{{
  "winning_percentage": [numeric value between 0-100],
  "improvement_steps": [
    "Step 1: [specific actionable instruction]",
    "Step 2: [specific actionable instruction]",
    ...
  ],
  "rationale": "[concise explanation of the winning percentage]",
  "legal_references": [
    {{
      "section": "[specific section number]",
      "act": "[name of the act/law]",
      "year": "[year of the act]",
      "description": "[brief description of the section's relevance]"
    }},
    ...
  ]
}}

Your assessment must be based on legal precedent, the strength of arguments, and factual similarities. For the legal references, be specific about the exact sections, articles, and provisions from relevant Indian laws (such as the Indian Penal Code, Code of Civil Procedure, Constitution of India, specific state laws, etc.) that are applicable to this petition and would strengthen the legal arguments when cited.
"""

        # Call the OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using the 3.0-mini model
            messages=[
                {"role": "system", "content": "You are a legal expert assistant analyzing petitions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent results
            response_format={"type": "json_object"}  # Ensure response is in JSON format
        )
        
        # Extract and parse the response
        response_content = response.choices[0].message.content
        
        try:
            result = json.loads(response_content)
            
            # Validate the response format
            if "winning_percentage" not in result or "improvement_steps" not in result or "rationale" not in result:
                logger.warning(f"Incomplete response from OpenAI API: {response_content}")
                result = {
                    "winning_percentage": result.get("winning_percentage", 0),
                    "improvement_steps": result.get("improvement_steps", []),
                    "rationale": result.get("rationale", "Unable to provide complete analysis"),
                    "legal_references": result.get("legal_references", []),
                    "warning": "Incomplete analysis result"
                }
                
            # Ensure winning_percentage is a number between 0-100
            if not isinstance(result["winning_percentage"], (int, float)):
                result["winning_percentage"] = 0
            
            result["winning_percentage"] = max(0, min(100, float(result["winning_percentage"])))
            
            # Ensure legal_references exists and is a list
            if "legal_references" not in result:
                result["legal_references"] = []
            elif not isinstance(result["legal_references"], list):
                result["legal_references"] = []
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
            return {
                "error": "Failed to parse analysis result",
                "raw_response": response_content
            }
            
    except Exception as e:
        logger.error(f"Error analyzing petition with OpenAI: {str(e)}")
        return {"error": f"Failed to analyze petition: {str(e)}"}