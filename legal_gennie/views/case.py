from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from drf_spectacular.utils import extend_schema
from django.conf import settings
from ..serializers import CaseCreateSerializer, CaseResponseSerializer, JudgmentSerializer
from utils.helpers import generate_search_query_from_petition, fetch_indian_kanoon_judgments, fetch_judgment_details, analyze_petition_with_openai
import os
import concurrent.futures

class CaseCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.JSONParser]

    @extend_schema(
        request=CaseCreateSerializer,
        responses={201: CaseResponseSerializer},
        description="Get prediction, search query, and relevant judgments for the case"
    )
    def post(self, request, *args, **kwargs):
        serializer = CaseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        petition = serializer.validated_data['petition']
        search_query = generate_search_query_from_petition(petition)
        
        # Get token from request or environment variable
        token = serializer.validated_data.get('token')
        if not token:
            # Try to get from environment variable
            token = os.environ.get('INDIAN_KANOON_API_TOKEN', '')
        
        response_data = {
            "prediction": "[prediction_message]",
            "search_query": search_query,
            "judgments": []
        }
        
        # Only fetch judgments if token is available
        if token:
            judgments = fetch_indian_kanoon_judgments(search_query, token)
            
            # Check if there was an error
            if isinstance(judgments, dict) and 'error' in judgments:
                return Response({
                    "error": judgments['error'],
                    "search_query": search_query
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # For each judgment, fetch detailed information for enhanced citation
            enhanced_judgments = self.fetch_details_concurrent(judgments[:10], token)
            response_data["judgments"] = judgments
            
            # Analyze petition with OpenAI using the enhanced judgments
            analysis_result = analyze_petition_with_openai(petition, enhanced_judgments)
            if not isinstance(analysis_result, dict) or 'error' in analysis_result:
                # Log the error but continue with the response
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"OpenAI analysis failed: {analysis_result.get('error', 'Unknown error')}")
            else:
                # Add the analysis results to the response
                response_data["analysis"] = analysis_result
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    def fetch_details_concurrent(self, judgments, token, max_workers=3):
        """
        Fetches detailed information for multiple judgments concurrently
        with improved error handling and rate limiting

        Args:
            judgments (List[Dict]): List of judgment objects with TIDs
            token (str): Authorization token for the Indian Kanoon API
            max_workers (int): Maximum number of concurrent workers

        Returns:
            List[Dict]: Enhanced judgment objects with detailed information
        """
        import logging
        import time

        logger = logging.getLogger(__name__)
        enhanced_judgments = []

        # Reduce concurrency to avoid rate limiting
        # Setting a lower number of workers helps prevent API rate limiting
        max_workers = min(max_workers, 3)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a mapping of futures to judgment indices
            future_to_idx = {}

            # Submit jobs with a delay between submissions to avoid rate limiting
            for i, judgment in enumerate(judgments):
                if 'tid' in judgment:
                    # Add a small delay between submissions to reduce API load
                    if i > 0:
                        time.sleep(0.5)  # 500ms delay between submissions

                    future = executor.submit(fetch_judgment_details, judgment['tid'], token)
                    future_to_idx[future] = i

            logger.debug(f"Submitted {len(future_to_idx)} judgment detail requests")

            # Process completed futures as they complete
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                judgment = judgments[idx].copy()  # Make a copy to avoid modifying the original

                try:
                    details = future.result()
                    logger.debug(f"Received details for judgment {judgment.get('tid')}")

                    if not details:
                        # Handle empty result case
                        logger.warning(f"Empty details returned for judgment {judgment.get('tid')}")
                        judgment['detailed_citation'] = False
                        judgment['fetch_error'] = "Empty response"
                    elif isinstance(details, dict) and 'error' in details:
                        # Handle explicit error
                        logger.warning(f"Error in judgment details for {judgment.get('tid')}: {details['error']}")
                        judgment['detailed_citation'] = False
                        judgment['fetch_error'] = details['error']
                    elif isinstance(details, dict):
                        # Update citation with more comprehensive information
                        if 'doc' in details and details['doc']:
                            judgment['citation'] = details['doc']
                            judgment['detailed_citation'] = True

                            # Optionally add a preview of the full text
                            if 'full_text' in details and details['full_text']:
                                judgment['text_preview'] = details['full_text'][:200] + "..."

                            # Add any other metadata fields that were returned
                            for field in ['title', 'from', 'bench', 'author', 'date']:
                                if field in details:
                                    judgment[field] = details[field]
                        else:
                            logger.warning(f"Missing 'doc' field in judgment {judgment.get('tid')}")
                            judgment['detailed_citation'] = False
                            judgment['fetch_error'] = "Missing document content"
                    else:
                        # Unexpected response format
                        logger.warning(f"Unexpected format for judgment {judgment.get('tid')}: {type(details)}")
                        judgment['detailed_citation'] = False
                        judgment['fetch_error'] = "Unexpected response format"
                except Exception as e:
                    # If an error occurs, keep the original judgment data
                    error_msg = str(e)
                    logger.error(f"Exception for judgment {judgment.get('tid')}: {error_msg}")
                    judgment['detailed_citation'] = False
                    judgment['fetch_error'] = error_msg

                enhanced_judgments.append(judgment)

        # Sort to maintain original order
        enhanced_judgments.sort(key=lambda j: next((i for i, jdg in enumerate(judgments) if jdg.get('tid') == j.get('tid')), 0))

        # Log summary of results
        success_count = sum(1 for j in enhanced_judgments if j.get('detailed_citation', False))
        logger.info(f"Successfully fetched details for {success_count}/{len(enhanced_judgments)} judgments")

        return enhanced_judgments