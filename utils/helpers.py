import requests
from bs4 import BeautifulSoup


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


# Example Usage
result = verify_lawyer_dl("2174/2015")
print(result)
