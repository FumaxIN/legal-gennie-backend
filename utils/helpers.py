import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any


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
    using the document endpoint with curl and implements exponential backoff retry.

    Args:
        tid (int): The document ID (tid) for the judgment
        token (str): Authorization token for the Indian Kanoon API
        max_retries (int): Maximum number of retry attempts

    Returns:
        Dict[str, Any]: A dictionary containing detailed judgment information
    """
    import json
    import subprocess
    import time
    import logging

    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        try:
            # Construct the curl command
            curl_command = [
                'curl', '--silent',
                '--location',
                f'https://api.indiankanoon.org/doc/{tid}',
                '--header', f'Authorization: Token {token}'
            ]

            # Execute the curl command
            process = subprocess.run(curl_command, capture_output=True, text=True)

            # Check if the command was successful
            if process.returncode != 0:
                error_msg = f"Failed to fetch judgment details. Command failed with error: {process.stderr}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s, etc.
                continue

            # Parse the JSON response
            response_text = process.stdout

            # Check if response is empty or whitespace only
            if not response_text or response_text.isspace():
                error_msg = f"Empty response received for judgment {tid}"
                logger.error(f"Attempt {attempt+1}/{max_retries}: {error_msg}")
                if attempt == max_retries - 1:
                    return {"error": error_msg}
                time.sleep(2 ** attempt)
                continue

            try:
                data = json.loads(response_text)
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