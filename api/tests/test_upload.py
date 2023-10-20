import pytest
import io
from werkzeug.datastructures import FileStorage

def test_process_audio_no_fille_400(client):
    response = client.post('/api/process_audio')
    assert response.status_code == 400

def test_process_audio_bad_file_400(client):
    data = {}
    data['file'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    response = client.post('/api/process_audio', data=data)
    assert response.status_code == 400

def test_process_audio_good_file_200(client):
    my_file = FileStorage(
        stream=open("api/tests/resources/cpe-bach-solfeggietto.mp3", "rb"),
        filename="cpe-bach-solfeggietto.mp3",
        content_type="audio/mp3",
    )
    data = {}
    data['file'] = my_file
    response = client.post('/api/process_audio', data=data)
    assert response.status_code == 200
    assert response.data != None
    assert response.mimetype == 'image/png'