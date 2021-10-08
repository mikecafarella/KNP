import boto3

# sample url
#   s3://ai2-s2-pdfs/e423/977e8070a5037558ac9dfdd78a6db6a64d58.pdf

s3 = boto3.client('s3')

BUCKET_NAME = 'ai2-s2-pdfs'

with open("pdf_list.txt", "rt") as flist:
    for fullpath in flist:
        OBJECT_NAME = fullpath.strip().replace('s3://ai2-s2-pdfs/', '').replace('.pdf', '')


        FILE_NAME = 'pdfs_s3/{}.pdf'.format(OBJECT_NAME.replace('/','-'))

        with open(FILE_NAME, 'wb') as f:
            s3.download_fileobj(BUCKET_NAME, OBJECT_NAME, f)

        break
