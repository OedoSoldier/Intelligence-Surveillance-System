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
    BUCKET = 'ec500j1-project-iseeu'
    KEY_SOURCE = 'test.jpg'
    KEY_TARGET = 'target.jpg'

    image = cv2.imread('target.jpg')
    height, width, channels = image.shape 

    s3 = boto3.client('s3')
    s3.upload_file(KEY_SOURCE, BUCKET, KEY_SOURCE)
    s3.upload_file(KEY_TARGET, BUCKET, KEY_TARGET)
    while True:
        try:
            boto3.resource('s3').Object(BUCKET, KEY_SOURCE).load()
            boto3.resource('s3').Object(BUCKET, KEY_TARGET).load()
        except BaseException:
            continue
        break

    source_face, matches = compare_faces(
        BUCKET, KEY_SOURCE, BUCKET, KEY_TARGET)

    # the main source face
    print('Source Face ({Confidence}%)'.format(**source_face))

    # one match for each target face
    for match in matches:
        print('Target Face ({Confidence}%)'.format(**match['Face']))
        print('  Similarity : {}%'.format(match['Similarity']))

    for faceMatch in matches:
        position = faceMatch['Face']['BoundingBox']
        x = int(position['Left'] * width)
        y = int(position['Top'] * height)
        w = int(position['Width'] * width)
        h = int(position['Height'] * height)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, str(faceMatch['Face']['Confidence']), (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

    s3.delete_object(Bucket=BUCKET, Key=KEY_SOURCE)
    s3.delete_object(Bucket=BUCKET, Key=KEY_TARGET)

    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()