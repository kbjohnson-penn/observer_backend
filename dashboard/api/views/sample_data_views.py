import os
import csv
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from dashboard.api.viewsets.public.base import IsReadOnly


class SampleDataViewSet(ViewSet):
    """
    ViewSet to return all sample CSV data as JSON.
    This reads CSV files directly from the data directory.
    """
    permission_classes = [IsReadOnly]
    
    # Cache for 1 hour (3600 seconds)
    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        """
        Returns all sample data from CSV files.
        """
        try:
            # Path to the data directory - configurable via environment variable
            # Default to Django BASE_DIR/data
            default_data_path = os.path.join(settings.BASE_DIR, 'data')
            data_dir = config('SAMPLE_DATA_PATH', default=default_data_path)
            data_dir = os.path.abspath(data_dir)
            
            # Security: Prevent path traversal attacks
            base_path = os.path.abspath(settings.BASE_DIR)
            if not data_dir.startswith(base_path):
                return Response(
                    {'error': 'Invalid data directory configuration'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure the directory exists
            if not os.path.exists(data_dir):
                return Response(
                    {'error': 'Sample data directory not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Define CSV files and their keys
            csv_files = {
                'persons': 'PERSON.csv',
                'providers': 'PROVIDER.csv',
                'visits': 'VISIT_OCCURRENCE.csv',
                'notes': 'NOTE.csv',
                'conditions': 'CONDITION_OCCURRENCE.csv',
                'drugs': 'DRUG_EXPOSURE.csv',
                'procedures': 'PROCEDURE_OCCURRENCE.csv',
                'measurements': 'MEASUREMENT.csv',
                'observations': 'OBSERVATION.csv',
                'patient_surveys': 'PATIENT_SURVEY.csv',
                'provider_surveys': 'PROVIDER_SURVEY.csv',
                'audit_logs': 'AUDIT_LOGS.csv',
                'concepts': 'CONCEPT_FILTERED.csv'
            }
            
            response_data = {}
            
            for key, filename in csv_files.items():
                # Security: Validate filename to prevent path traversal
                if '..' in filename or '/' in filename or '\\' in filename:
                    response_data[key] = {'error': 'Invalid filename'}
                    continue
                    
                file_path = os.path.join(data_dir, filename)
                
                # Security: Ensure file is within the data directory
                if not os.path.abspath(file_path).startswith(data_dir):
                    response_data[key] = {'error': 'Invalid file path'}
                    continue
                
                if os.path.exists(file_path):
                    # Security: Check file size to prevent memory exhaustion
                    file_size = os.path.getsize(file_path)
                    max_file_size = 50 * 1024 * 1024  # 50MB limit
                    if file_size > max_file_size:
                        response_data[key] = {'error': 'File too large to process'}
                        continue
                    
                    data = []
                    max_rows = 100000  # Limit rows to prevent memory issues
                    row_count = 0
                    
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            row_count += 1
                            if row_count > max_rows:
                                data.append({'warning': f'File truncated at {max_rows} rows'})
                                break
                                
                            # Convert empty strings to None
                            cleaned_row = {k: (v if v != '' else None) for k, v in row.items()}
                            
                            # Convert numeric fields where appropriate
                            for field, value in cleaned_row.items():
                                if value is not None:
                                    # Try to convert to int or float if it looks numeric
                                    if value.isdigit():
                                        cleaned_row[field] = int(value)
                                    elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
                                        try:
                                            cleaned_row[field] = float(value)
                                        except ValueError:
                                            pass
                            
                            data.append(cleaned_row)
                    
                    response_data[key] = data
                else:
                    response_data[key] = []
            
            # Add metadata
            response_data['_metadata'] = {
                'description': 'Sample OMOP-formatted healthcare data',
                'source': 'CSV files from observer dataset',
                'count': {key: len(data) for key, data in response_data.items() if key != '_metadata'}
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except (IOError, OSError):
            return Response(
                {'error': 'Unable to access sample data files'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except UnicodeDecodeError:
            return Response(
                {'error': 'Invalid file encoding detected'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except Exception:
            return Response(
                {'error': 'Internal server error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )