import boto3
import cv2
import numpy


def compare_faces(
        bucket,
        key,
        bucket_target,
        key_target,
        threshold=80,
        region='us-east-1'):
    rekognition = boto3.client('rekognition', region)
    response = rekognition.compare_faces(
        SourceImage={
            'S3Object': {
                'Bucket': bucket,
                'Name': key,
            }
        },
        TargetImage={
            'S3Object': {
                'Bucket': bucket_target,
                'Name': key_target,
            }
        },
        SimilarityThreshold=threshold,
    )
    return response['SourceImageFace'], response['FaceMatches']


if __name__ == '__main__':
    bucket_name = 'ec500j1-project-iseeu'
    source_name = ['source_1.jpg', 'source_2.jpg']
    target_name = 'target.jpg'

    image = cv2.imread('target.jpg')
    height, width, channels = image.shape

    s3 = boto3.client('s3')
    for img in source_name:
        s3.upload_file(img, bucket_name, img)
    s3.upload_file(target_name, bucket_name, target_name)
    while True:
        try:
            for img in source_name:
                boto3.resource('s3').Object(bucket_name, img).load()
            boto3.resource('s3').Object(bucket_name, target_name).load()
        except BaseException:
            continue
        break

    sources, matches = {}, {}
    for img in source_name:
        sources[img], matches[img] = compare_faces(
            bucket_name, img, bucket_name, target_name)

    for img in list(matches.keys()):
        for faceMatch in matches[img]:
            position = faceMatch['Face']['BoundingBox']
            x = int(position['Left'] * width)
            y = int(position['Top'] * height)
            w = int(position['Width'] * width)
            h = int(position['Height'] * height)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                image,
                '{}: {:.2f}%'.format(
                    img,
                    faceMatch['Face']['Confidence']),
                (x,
                 y),
                cv2.FONT_HERSHEY_PLAIN,
                1.5,
                (0,
                 255,
                 0),
                2)

    for img in source_name:
        s3.delete_object(Bucket=bucket_name, Key=img)
    s3.delete_object(Bucket=bucket_name, Key=target_name)

    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
