import os
import csv
import mimetypes
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import HttpResponse, FileResponse, Http404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
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


class PublicVideoStreamView(APIView):
    """
    API view to stream media files (videos, documents, etc.) from local filesystem.
    Supports both HEAD requests (for file size checking) and GET requests (for streaming).
    """
    permission_classes = [IsReadOnly]
    
    def get_media_file_path(self, file_path):
        """
        Get the absolute path to the media file with security validation.
        """
        # Get media files directory from environment
        default_media_path = os.path.join(settings.BASE_DIR, 'media')
        media_dir = config('VIDEO_FILES_PATH', default=default_media_path)
        media_dir = os.path.abspath(media_dir)
        
        # Security: Prevent path traversal attacks
        base_path = os.path.abspath(settings.BASE_DIR)
        if not media_dir.startswith(base_path):
            raise Http404("Invalid media directory configuration")
        
        # Clean the file path (remove leading slashes, normalize)
        clean_file_path = file_path.strip('/')
        
        # Security: Check for dangerous path components
        path_parts = clean_file_path.split('/')
        for part in path_parts:
            if part in ('..', '.', '') or any(char in part for char in ['\\', ':', '*', '?', '"', '<', '>', '|']):
                raise Http404("Invalid file path")
        
        # Construct full file path
        full_path = os.path.join(media_dir, clean_file_path)
        full_path = os.path.abspath(full_path)
        
        # Security: Ensure the resolved path is still within media directory
        if not full_path.startswith(media_dir):
            raise Http404("Invalid file path")
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise Http404("Media file not found")
        
        # Check if it's actually a file (not directory)
        if not os.path.isfile(full_path):
            raise Http404("Path is not a file")
        
        return full_path
    
    def _get_file_info(self, file_path):
        """Get file info including size and content type."""
        full_path = self.get_media_file_path(file_path)
        file_size = os.path.getsize(full_path)
        content_type, _ = mimetypes.guess_type(full_path)
        
        # Default based on file extension if cannot determine
        if not content_type:
            file_ext = os.path.splitext(full_path)[1].lower()
            if file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm']:
                content_type = 'video/mp4'
            elif file_ext in ['.xlsx', '.xls']:
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_ext == '.json':
                content_type = 'application/json'
            else:
                content_type = 'application/octet-stream'
        
        return full_path, file_size, content_type
    
    def _add_common_headers(self, response):
        """Add common headers to response."""
        response['Accept-Ranges'] = 'bytes'
        response['Cache-Control'] = 'public, max-age=3600'
        return response

    def head(self, request, file_path):
        """Handle HEAD requests for file size checking."""
        try:
            full_path, file_size, content_type = self._get_file_info(file_path)
            
            response = HttpResponse(status=200, content='')
            response['Content-Type'] = content_type
            response['Content-Length'] = str(file_size)
            
            return self._add_common_headers(response)
            
        except Http404:
            raise
        except Exception:
            raise Http404("Error accessing media file")
    
    def get(self, request, file_path):
        """Handle GET requests for media file streaming with range support."""
        try:
            full_path, file_size, content_type = self._get_file_info(file_path)
            
            # Handle range requests
            range_header = request.META.get('HTTP_RANGE')
            if range_header:
                try:
                    range_match = range_header.replace('bytes=', '').split('-')
                    start = int(range_match[0]) if range_match[0] else 0
                    end = int(range_match[1]) if range_match[1] else file_size - 1
                    
                    # Ensure valid range
                    start = max(0, start)
                    end = min(file_size - 1, end)
                    
                    if start > end:
                        response = HttpResponse(status=416)
                        response['Content-Range'] = f'bytes */{file_size}'
                        return response
                    
                    # Create partial content response
                    with open(full_path, 'rb') as media_file:
                        media_file.seek(start)
                        chunk_size = end - start + 1
                        media_data = media_file.read(chunk_size)
                    
                    response = HttpResponse(media_data, status=206, content_type=content_type)
                    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                    response['Content-Length'] = str(chunk_size)
                    
                    return self._add_common_headers(response)
                    
                except (ValueError, IndexError):
                    pass  # Fall back to full file
            
            # Return full file
            response = FileResponse(open(full_path, 'rb'), content_type=content_type, as_attachment=False)
            response['Content-Length'] = str(file_size)
            
            return self._add_common_headers(response)
            
        except Http404:
            raise
        except Exception:
            raise Http404("Error streaming media file")