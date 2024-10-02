import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

class S3Downloader:
    def __init__(self):
        date = datetime.now().strftime('%Y-%m')
        load_dotenv()

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.s3_base_key = f'anoMes={date}/'

    def download_file(self, s3_key: str, local_path: str):
        """Faz o download de um arquivo do S3 para o caminho local especificado."""
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_path)
            print(f"Arquivo {s3_key} baixado com sucesso para {local_path}")
        except Exception as e:
            print(f"Erro ao baixar o arquivo {s3_key}: {e}")
            raise e

    def download_model(self):
        """Baixa o modelo de ML do S3"""
        local_model_dir = os.path.join(os.getcwd(), 'models')
        os.makedirs(local_model_dir, exist_ok=True)

        model_key = self.s3_base_key + 'game_recommender.pkl'
        local_path = os.path.join(local_model_dir, 'game_recommender.pkl')
        self.download_file(model_key, local_path)

    def download_csv(self):
        """Baixa o arquivo games.csv do S3"""
        local_data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(local_data_dir, exist_ok=True)

        data_key = self.s3_base_key + 'games.csv'
        local_path = os.path.join(local_data_dir, 'games.csv')
        self.download_file(data_key, local_path)


teste = S3Downloader()
teste.download_model()