import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_to_cloud(file_path, storage_type='aws_s3', bucket_name=None):
    """
    Uploads a file to the specified cloud storage.
    
    Args:
        file_path (str): The path to the file to upload.
        storage_type (str): The cloud storage type, e.g., 'aws_s3'.
        bucket_name (str): The name of the cloud storage bucket.
    
    Returns:
        str: The name of the file stored in the cloud, or None if upload fails.
    """
    try:
        if storage_type == 'aws_s3':
            if not bucket_name:
                raise ValueError("Bucket name must be provided for AWS S3 uploads.")
            
            s3_client = boto3.client('s3')
            file_name = os.path.basename(file_path)
            s3_client.upload_file(file_path, bucket_name, file_name)
            logger.info(f"File {file_name} uploaded successfully to S3 bucket {bucket_name}.")
            return file_name
        else:
            raise NotImplementedError(f"Cloud storage type {storage_type} is not supported.")
    
    except FileNotFoundError as fnf_error:
        logger.error(f"File not found: {fnf_error}")
    except NoCredentialsError:
        logger.error("AWS credentials not available.")
    except ClientError as e:
        logger.error(f"Client error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred while uploading the file: {e}")
    
    return None

def generate_presigned_url(bucket_name, file_name, expiration=3600):
    """
    Generates a presigned URL to download a file from AWS S3.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        file_name (str): The name of the file to generate the URL for.
        expiration (int): Time in seconds for the presigned URL to remain valid.
    
    Returns:
        str: The presigned URL, or None if generation fails.
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': file_name},
                                                    ExpiresIn=expiration)
        logger.info(f"Presigned URL generated for file {file_name}.")
        return response
    except ClientError as e:
        logger.error(f"Client error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred while generating presigned URL: {e}")
    
    return None

if __name__ == "__main__":
    # Example usage
    file_path = "path_to_your_file.txt"
    bucket_name = "your_bucket_name"

    # Upload to AWS S3
    uploaded_file_name = upload_to_cloud(file_path, bucket_name=bucket_name)
    
    if uploaded_file_name:
        # Generate presigned URL for the uploaded file
        url = generate_presigned_url(bucket_name, uploaded_file_name)
        if url:
            logger.info(f"Presigned URL: {url}")
        else:
            logger.warning("Failed to generate presigned URL.")
    else:
        logger.warning("File upload failed.")