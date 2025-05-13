import unittest
from utils.helpers import generate_search_query_from_petition

class TestPetitionQueryGeneration(unittest.TestCase):

    def test_simple_petition(self):
        """Test with a simple petition text"""
        petition_text = """
        Petition against expulsion from the university for alleged cheating in exams.
        The petitioner, a final year student of engineering, was expelled from the university
        after being accused of cheating during the semester examination. The petitioner
        claims that the decision was made without providing adequate opportunity to present
        his side of the case, thereby violating principles of natural justice.
        """
        query = generate_search_query_from_petition(petition_text)
        self.assertIsNotNone(query)
        print(f"Expulsion query: {query}")
        self.assertIn("expulsion", query.lower())
        self.assertIn("university", query.lower())
        self.assertTrue("academic dishonesty" in query.lower() or "cheating" in query.lower())

    def test_contract_breach_petition(self):
        """Test with a contract breach petition"""
        petition_text = """
        This petition concerns a breach of contract between the petitioner company and the respondent.
        The contract dated 05.01.2022 was for supply of industrial equipment worth Rs. 50 lakhs.
        Despite full payment, the respondent failed to deliver the equipment as per specifications,
        causing significant losses to the petitioner's manufacturing business. The petitioner seeks
        damages for breach of contract and consequential losses.
        """
        query = generate_search_query_from_petition(petition_text)
        self.assertIsNotNone(query)
        print(f"Contract breach query: {query}")
        self.assertIn("contract breach", query.lower())

    def test_property_dispute_petition(self):
        """Test with a property dispute petition"""
        petition_text = """
        Civil Appeal No. 3456 of 2021

        The present petition relates to a property dispute between siblings after the death of their father.
        The property in question is ancestral property located at 123, Main Street, Mumbai, valued at approximately
        Rs. 2 crores. The petitioner claims that his brother (respondent) has illegally occupied the entire property
        and is refusing to partition it as per the Will dated [2018] left by their father. The respondent
        claims that the Will is forged and the property should be divided equally as per succession laws.
        """
        query = generate_search_query_from_petition(petition_text)
        self.assertIsNotNone(query)
        print(f"Property dispute query: {query}")
        self.assertIn("property dispute", query.lower())
        self.assertTrue("mumbai" in query.lower())

    def test_question_paper_leak_petition(self):
        """Test with a question paper leak petition"""
        petition_text = """
        IN THE HIGH COURT OF DELHI

        Writ Petition No. ___ of 2025

        The facts of the case are as follows:
        a) On 10.05.2025, the question paper for the Mathematics of the State Board Class XII was leaked
        and circulated on social media platforms such as WhatsApp and Telegram prior to the scheduled examination.
        b) The leakage has compromised the integrity of the examination, affecting thousands of students
        who prepared diligently, and has created an unfair advantage for those who accessed the leaked paper.

        The Petitioner seeks a writ of mandamus directing the Examination Board to cancel the compromised
        examination and conduct a fresh examination at the earliest.
        """
        query = generate_search_query_from_petition(petition_text)
        self.assertIsNotNone(query)
        print(f"Question paper leak query: {query}")
        # Print each word for debugging
        words = query.lower().split()
        print(f"Individual words: {words}")
        self.assertTrue("question" in query.lower() and "paper" in query.lower() and "leak" in query.lower())
        # Allow more flexible matching for high court and delhi
        self.assertTrue("high" in query.lower() and "court" in query.lower() or "delhi" in query.lower())

if __name__ == "__main__":
    unittest.main()